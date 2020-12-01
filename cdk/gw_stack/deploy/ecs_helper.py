from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds)


class GWEcsHelper:

    def __init__(self):
        self.name='AppHelper'

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

