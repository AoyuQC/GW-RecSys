from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds)
from .ecs_helper import GWEcsHelper


class GWSampleStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
            vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        image = "nginx"
        name = "Sample"
        port = 80

        self.url = GWEcsHelper.create_fagate_ALB_autoscaling(
            self,
            vpc,
            image,
            name,
            port=port
        )

