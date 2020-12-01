from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds)
from utills import GWAppHelper


class GWInferHandlerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
                 vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        image = ""
        name = "InferHandler"
        port = 80
        
        GWAppHelper.create_fagate_ALB_autoscaling(
            self,
            vpc,
            image,
            name,
            port
        )
