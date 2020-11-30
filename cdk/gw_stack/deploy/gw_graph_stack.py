from aws_cdk import (core, 
                     aws_ec2 as ec2, 
                     aws_ecs as ecs, 
                     aws_ecr as ecr,
                     aws_ecs_patterns as ecs_patterns, 
                     aws_elasticache as ec,
                     aws_rds as rds,
                     aws_apigateway as apigw,
                     aws_iam as iam,
                     aws_lambda as _lambda,    
                     aws_s3 as s3,
                     aws_lambda_event_sources as lambda_event_source
                    )


class GWGraphStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "GWVpc", max_azs=3)     # default is all AZs in region

        ## Create Redis
        #self.create_redis(vpc)

        #Create NLB autoscaling
        #self.create_fagate_NLB_autoscaling(vpc)

        cfg_dict = {}
        cfg_dict['function'] = 'graph_inference'
        cfg_dict['ecr'] = 'sagemaker-recsys-graph-inference'
        graph_inference_dns = self.create_fagate_NLB_autoscaling_custom(vpc, **cfg_dict)

        cfg_dict['function'] = 'graph_train'
        cfg_dict['ecr'] = 'sagemaker-recsys-graph-train'
        # self.create_lambda_trigger_task_custom(vpc, **cfg_dict)

        #
        #lambda_cfg_dict = {}
        #lambda_cfg_dict['graph_train_dns'] = graph_train_dns
        #lambda_cfg_dict['graph_inference_dns'] = graph_inference_dns
        #graph_interface = GraphInterface(
        #    self, "GraphInterface", **lambda_cfg_dict
        #)

        #apigw.LambdaRestApi(
        #    self, 'GraphEndpoint',
        #    handler=graph_interface.handler,
        #)


    def create_redis(self, vpc):
        subnetGroup = ec.CfnSubnetGroup(
            self,
            "RedisClusterPrivateSubnetGroup",
            cache_subnet_group_name="recommendations-redis-subnet-group",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            description="Redis subnet for recommendations"
        )

        redis_security_group = ec2.SecurityGroup(self, "redis-security-group", vpc=vpc)

        redis_connections = ec2.Connections(
            security_groups=[redis_security_group], default_port=ec2.Port.tcp(6379)
        )
        redis_connections.allow_from_any_ipv4(port_range=ec2.Port.tcp(6379))

        redis = ec.CfnCacheCluster(
            self,
            "RecommendationsRedisCacheCluster",
            engine="redis",
            cache_node_type="cache.t2.small",
            num_cache_nodes=1,
            cluster_name="redis-gw",
            vpc_security_group_ids=[redis_security_group.security_group_id],
            cache_subnet_group_name=subnetGroup.cache_subnet_group_name
        )
        redis.add_depends_on(subnetGroup)
    
    def create_fagate_ALB(self, vpc):
        # Create ECS
        cluster = ecs.Cluster(self, "GWCluster", vpc=vpc)

        ecs_patterns.ApplicationLoadBalancedFargateService(
            self, 
            "GWService",
            cluster=cluster,            # Required
            cpu=256,                    # Default is 256
            desired_count=1,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("856419311962.dkr.ecr.cn-north-1.amazonaws.com.cn/airflow_analyze"),
                container_port=80
            ),
            memory_limit_mib=512,      # Default is 512
            public_load_balancer=True
        )
    
    def create_fagate_NLB_autoscaling(self, vpc):
        cluster = ecs.Cluster(
            self, 'fargate-service-autoscaling',
            vpc=vpc
        )

        # config IAM role
        # add managed policy statement
        ecs_base_role = iam.Role(
            self,
            "ecs_service_role",
            assumed_by=iam.ServicePrincipal("ecs.amazonaws.com")
        )
        ecs_role = ecs_base_role.from_role_arn(self, 'gw-ecr-role-test', role_arn='arn:aws:iam::002224604296:role/ecsTaskExecutionRole')

        # Create Fargate Task Definition
        fargate_task = ecs.FargateTaskDefinition(
            self, "graph-inference-task-definition", execution_role=ecs_role, task_role=ecs_role, cpu=2048, memory_limit_mib=4096
        )

        #ecr_repo = ecr.IRepository(self, "002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-inference")
        ecr_repo = ecr.Repository.from_repository_name(self, id = "graph-inference-docker", repository_name = "sagemaker-recsys-graph-inference")

        port_mapping = ecs.PortMapping(
            container_port=8080,
            host_port=8080,
            protocol=ecs.Protocol.TCP
        )

        ecs_log = ecs.LogDrivers.aws_logs(stream_prefix='gw-inference-test')

        farget_container = fargate_task.add_container("graph-inference",image=ecs.ContainerImage.from_ecr_repository(ecr_repo), logging=ecs_log
        )
        farget_container.add_port_mappings(port_mapping)


        fargate_service = ecs.FargateService(self, 'graph-inference-service',
            cluster=cluster, task_definition=fargate_task, assign_public_ip=True
        )

        fargate_service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4('0.0.0.0/0'),
            connection = ec2.Port.tcp(8080),
            description = "Allow http inbound from VPC"
        )

        return fargate_service

    def create_fagate_NLB_autoscaling_custom(self, vpc, **kwargs):
        ####################
        # Unpack Value for name/ecr_repo
        app_name = kwargs['function'].replace("_","-")
        task_name = "{}-task-definition".format(app_name)
        log_name = app_name
        image_name = "{}-image".format(app_name)
        container_name = "{}-container".format(app_name)
        service_name = "{}-service".format(app_name)

        app_ecr = kwargs['ecr']

        ####################
        # Create Cluster
        cluster = ecs.Cluster(
            self, 'fargate-service-autoscaling',
            vpc=vpc
        )

        ####################
        # Config IAM Role
        # add managed policy statement
        ecs_base_role = iam.Role(
            self,
            "ecs_service_role",
            assumed_by=iam.ServicePrincipal("ecs.amazonaws.com")
        )
        ecs_role = ecs_base_role.from_role_arn(self, 'gw-ecr-role-test', role_arn='arn:aws:iam::002224604296:role/ecsTaskExecutionRole')

        ####################
        # Create Fargate Task Definition
        fargate_task = ecs.FargateTaskDefinition(
            self, task_name, 
            execution_role=ecs_role, task_role=ecs_role, 
            cpu=2048, memory_limit_mib=4096
        )
        # 0. config log
        ecs_log = ecs.LogDrivers.aws_logs(stream_prefix=log_name)
        # 1. prepare ecr repository
        ecr_repo = ecr.Repository.from_repository_name(self, id = image_name, repository_name = app_ecr)
        farget_container = fargate_task.add_container(container_name,image=ecs.ContainerImage.from_ecr_repository(ecr_repo), logging=ecs_log
        )
        # 2. config port mapping
        port_mapping = ecs.PortMapping(
            container_port=8080,
            host_port=8080,
            protocol=ecs.Protocol.TCP
        )
        farget_container.add_port_mappings(port_mapping)

        ####################
        # Config NLB service
        # fargate_service = ecs.FargateService(self, 'graph-inference-service',
        #     cluster=cluster, task_definition=fargate_task, assign_public_ip=True
        # )
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, service_name,
            cluster=cluster,
            task_definition=fargate_task,
            assign_public_ip=True
        )
        # 0. allow inbound in sg
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            # peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            peer = ec2.Peer.ipv4('0.0.0.0/0'),
            connection = ec2.Port.tcp(8080),
            description = "Allow http inbound from VPC"
        )
        # 1. setup autoscaling policy
        scaling = fargate_service.service.auto_scale_task_count(
            max_capacity=2
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )

        return fargate_service.load_balancer

    def create_lambda_trigger_task_custom(self, vpc, **kwargs):
        ####################
        # Unpack Value
        app_name = kwargs['function'].replace("_","-")
        lambda_name = "{}-lambda".format(app_name)
        code_name = "{}-handler".format(app_name)
        bucket_name = "{}-bucket-event".format(app_name)
        # Create Lambda
        lambda_app = _lambda.Function(self, lambda_name,
            handler='{}.handler'.format(code_name),
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda')
        )
        # Create an S3 event soruce for Lambda
        bucket = s3.Bucket(self, bucket_name)
        s3_event_source = lambda_event_source.S3EventSource(bucket, events=[s3.EventType.OBJECT_CREATED])

    def create_rds(self, vpc):
        # Create DB
        rds_cluster = rds.DatabaseCluster(
            self, 
            'Database', 
            engine=rds.DatabaseClusterEngine.AURORA,
            master_user=rds.Login(
                    username='admin'
            ),
            instance_props=rds.InstanceProps(
               instance_type=ec2.InstanceType.of(
                   ec2.InstanceClass.BURSTABLE2, 
                   ec2.InstanceSize.SMALL
                ),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE
                ),
                vpc = vpc 
            )
        )
        return rds_cluster

# function:
# 1. graph training
# 2. graph inference

class GraphInterface(core.Construct):

    @property
    def handler(self):
        return self._handler
    
    def __init__(self, scope: core.Construct, id: str, **kwargs):

        super().__init__(scope, id, **kwargs)
        ####################
        # Unpack for train/inference dns
        graph_train_dns = kwargs['graph_train_dns']
        graph_inference_dns = kwargs['graph_inference_dns']

        #
        # self._user_info_table = ddb.Table(
        #     self, 'UserInfoTable',
        #     partition_key={'name': 'user_id', 'type': ddb.AttributeType.STRING}
        # )

        # self._item_tag_table = ddb.Table(
        #     self, 'ItemTagTable',
        #     partition_key={'name': 'item_type', 'type': ddb.AttributeType.STRING}
        # )

        self._handler = _lambda.Function(
            self, 'GraphInterfaceHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            handler='graphinterface.handler',
            code=_lambda.Code.asset('lambda'),
            environment={
                'GRAPH_TRAIN_DNS': graph_train_dns,
                'GRAPH_INFERENCE_DNS':graph_inference_dns 
            }
        )

        # self._user_info_table.grant_read_write_data(self.handler)
        # self._item_tag_table.grant_read_write_data(self.handler)
    

