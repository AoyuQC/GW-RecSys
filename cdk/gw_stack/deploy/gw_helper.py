from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as
                     ecs_patterns, aws_elasticache as ec, aws_rds as rds, aws_lambda as _lambda,
                     aws_s3 as s3, aws_lambda_event_sources as lambda_event_source, aws_iam as iam)


class GWAppHelper:

    def __init__(self):
        self.name='GWAppHelper'

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



    def create_lambda_train_role(self):
        # Config role
        base_role = iam.Role(
            self,
            "gw_lambda_train_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))

        return base_role 
        
    def create_sagemaker_train_role(self):
        # Config role
        base_role = iam.Role(
            self,
            "gw_sagemaker_train_role",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com")
        )
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        base_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))

        return base_role    