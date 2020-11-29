from aws_cdk import (core, 
                     aws_ec2 as ec2, 
                     aws_ecs as ecs, 
                     aws_ecr as ecr,
                     aws_ecs_patterns as ecs_patterns, 
                     aws_elasticache as ec,
                     aws_rds as rds,
                     aws_iam as iam
                    )


class GWGraphStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "GWVpc", max_azs=3)     # default is all AZs in region

        ## Create Redis
        #self.create_redis(vpc)

        #Create NLB autoscaling
        self.create_fagate_NLB_autoscaling(vpc)


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
            self, "graph-inference-task-definition", execution_role=ecs_role, task_role=ecs_role
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


        ecs.FargateService(self, 'graph-inference-service',
            cluster=cluster, task_definition=fargate_task
        )

        ## Create Fargate Service
        #fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
        #    self, "graph-inference-service",
        #    cluster=cluster,
        #    task_image_options={
        #        'image': ecs.ContainerImage.from_registry("002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-inference")}
        #)

        #fargate_service.service.connections.security_groups[0].add_ingress_rule(
        #    peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
        #    connection = ec2.Port.tcp(8080),
        #    description="Allow http inbound from VPC"
        #)

        ## Setup AutoScaling policy
        #scaling = fargate_service.service.auto_scale_task_count(
        #    max_capacity=2
        #)
        #scaling.scale_on_cpu_utilization(
        #    "CpuScaling",
        #    target_utilization_percent=50,
        #    scale_in_cooldown=core.Duration.seconds(60),
        #    scale_out_cooldown=core.Duration.seconds(60),
        #)

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
    

