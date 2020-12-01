from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds)


class GWAppHelper:

    def __init__(self):
        self.name='InfaHelper'

    @staticmethod
    def create_fagate_ALB_autoscaling(scope, vpc, image, name, port=None):
        cluster = ecs.Cluster(
            scope, 
            name+'fargate-service-autoscaling', 
            vpc=vpc
        )

        task = ecs.FargateTaskDefinition(
            scope,
            name+'-Task',
            memory_limit_mib=512,
            cpu=256,
        )

        if port is not None:
            task.add_container(
                name+'-Contaner',
                image=ecs.ContainerImage.from_registry(image)
            ).add_port_mappings(
                    ecs.PortMapping(container_port=port)
            )
        else:
            task.add_container(
                name+'-Contaner',
                image=ecs.ContainerImage.from_registry(image)
            )

        # Create Fargate Service
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            scope,
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
            scope, 
            name+'ServiceURL',    
            value='http://{}/'.format(fargate_service.load_balancer.load_balancer_full_name)
        )
        return fargate_service.load_balancer.load_balancer_full_name
