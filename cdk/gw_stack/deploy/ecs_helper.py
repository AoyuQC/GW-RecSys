from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3)


class GWEcsHelper:

    def __init__(self):
        self.name='EcsHelper'

    @staticmethod
    def create_fagate_ALB_autoscaling(stack, vpc, image, name, env=None, port=None):
        cluster = ecs.Cluster(
            stack, 
            name+'fargate-service-autoscaling', 
            vpc=vpc
        )

        task = ecs.FargateTaskDefinition(
            stack,
            name+'-Task',
            memory_limit_mib=512,
            cpu=256,
        )

        if env is None:
            env = {}
        if port is not None:
            task.add_container(
                name+'-Contaner',
                image=ecs.ContainerImage.from_registry(image),
                environment=env
            ).add_port_mappings(
                    ecs.PortMapping(container_port=port)
            )
        else:
            task.add_container(
                name+'-Contaner',
                image=ecs.ContainerImage.from_registry(image),
                environment=env
            )

        # Create Fargate Service
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            stack,
            name+"-Service",
            cluster=cluster,
            task_definition=task
        )

        fargate_service.service.connections.security_groups[
            0].add_ingress_rule(peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
                                connection=ec2.Port.tcp(port),
                                description="Allow http inbound from VPC")

        # Setup AutoScaling policy
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=2)
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )

        core.CfnOutput(
            stack, 
            name+'ServiceURL',    
            value='http://{}/'.format(fargate_service.load_balancer.load_balancer_full_name),
            export_name=name+'URL'
        )
        
        return fargate_service.load_balancer.load_balancer_full_name

    def create_trigger_training_task(self, **kwargs):
        ####################
        # Unpack Value
        name = kwargs['name'].replace("_","-")
        lambda_name = "{}-lambda".format(name)
        code_name = "{}".format(name)
        job_name = "{}-job".format(name)
        task = "{}-task".format(name)
        instance = kwargs['instance']
        image_uri = kwargs['image_uri']
        date = kwargs['date']
        trigger_bucket = kwargs['trigger_bucket']
        input_bucket = kwargs['input_bucket']
        output_bucket = kwargs['output_bucket']
        lambda_train_role = kwargs['lambda_role']
        sagemaker_train_role = kwargs['sagemaker_role'].role_arn

        # Create Lambda
        lambda_app = _lambda.Function(self, lambda_name,
            handler='{}.handler'.format(code_name),
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            role=lambda_train_role,
            environment={
                'INPUT_BUCKET': input_bucket,
                'OUTPUT_BUCKET': output_bucket,
                'DATE': date,
                'NAME': name,
                'IMAGE_URI': image_uri,
                'SAGEMAKER_ROLE': sagemaker_train_role,
                'INSTANCE': instance
            }
        )
        # Create an S3 event soruce for Lambda
        bucket = s3.Bucket(self, trigger_bucket)
        s3_event_source = lambda_event_source.S3EventSource(bucket, events=[s3.EventType.OBJECT_CREATED])
        lambda_app.add_event_source(s3_event_source)

        return lambda_app

    def get_datetime_str():
        from datetime import datetime
        now = datetime.now()
        tt = now.timetuple()
        prefix = tt[0]
        name = '-'.join(['{:02}'.format(t) for t in tt[1:-3]])
        suffix = '{:03d}'.format(now.microsecond)[:3]
        job_name_suffix = "{}-{}-{}".format(prefix, name, suffix)
        return job_name_suffix

