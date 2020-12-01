from aws_cdk import core, aws_ec2, aws_ecs, aws_ecs_patterns


class CdkInfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = aws_ec2.Vpc(self, 'Vpc', nat_gateways=1)
        core.CfnOutput(self, 'vpcId', value=self.vpc.vpc_id, export_name='ExportedVpcId')
