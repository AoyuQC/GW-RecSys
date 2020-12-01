from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_iam as iam)
from .utils import GWAppHelper


class GWTrainHandlerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
                 vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_train_role = self.create_lambda_train_role(self)
        sagemaker_train_role = self.create_sagemaker_train_role(self)

        cfg_dict = {}
        cfg_dict['vpc'] = vpc
        cfg_dict['name'] = 'graph-train'
        cfg_dict['date'] = GWAppHelper.get_datetime_str()
        cfg_dict['trigger_bucket']= "{}-bucket-event-{}".format(cfg_dict['name'], cfg_dict['date'])
        cfg_dict['input_bucket']= "{}-bucket-great-wisdom-graph-model-input".format(cfg_dict['name'])
        cfg_dict['output_bucket']= "{}-bucket-great-wisdom-graph-model-output".format(cfg_dict['name'])
        cfg_dict['ecr'] = 'sagemaker-recsys-graph-train'
        cfg_dict['instance'] = "ml.g4dn.xlarge"
        cfg_dict['image_uri'] = '002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-train'
        cfg_dict['lambda_role'] = lambda_train_role
        cfg_dict['sagemaker_role'] = sagemaker_train_role
        
        self.graph_train = GWAppHelper.create_trigger_training_task(self, **cfg_dict)

        #cfg_dict['name'] = 'dkn-train'
        #cfg_dict['trigger_bucket']= "{}-bucket-event-{}".format(cfg_dict['name'], cfg_dict['date'])
        #cfg_dict['input_bucket']= "{}-bucket-model-{}".format(cfg_dict['name'], cfg_dict['date'])
        #cfg_dict['output_bucket']= "{}-bucket-model-{}".format(cfg_dict['name'], cfg_dict['date'])
        #cfg_dict['ecr'] = 'sagemaker-recsys-graph-train'
        #cfg_dict['image_uri'] = '002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-train'
        #cfg_dict['role'] = '002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-train'
        
        #self.dkn_train = GWAppHelper.create_trigger_training_task(self, **cfg_dict)

