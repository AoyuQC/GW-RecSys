import json
import os

import boto3

from sagemaker.estimator import Estimator

from iam_helper import IamHelper

bucket = os.environ['BUCKET']
jobname = os.environ['JOB_NAME']
instance = os.environ['INSTANCE']
image_uri = os.environ['IMAGE_URI']
_lambda = boto3.client('lambda')

def get_datetime_str():
    from datetime import datetime
    now = datetime.now()
    tt = now.timetuple()
    prefix = tt[0]
    name = '-'.join(['{:02}'.format(t) for t in tt[1:-3]])
    suffix = '{:03d}'.format(now.microsecond)[:3]
    job_name_suffix = "{}-{}-{}".format(prefix, name, suffix)
    return job_name_suffix

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))

    # resource = event.get("source", None)
    resource = event["path"]
    body_str = json.loads(event["body"])
    print('body: {}'.format(body_str))

    instance_type = instance

    input_s3_path = "s3://{}/{}/".format(bucket, jobname)
    helper = IamHelper
    client = boto3.client("sagemaker")
    job_name = "{}-{}".format(jobname.replace("_", "-"), get_datetime_str())
    account = IamHelper.get_account_id()
    region = IamHelper.get_region()
    partition = IamHelper.get_partition()
    role_name = "AmazonSageMaker-ExecutionRole-20200512T121482"
    role_arn = "arn:{}:iam::{}:role/service-role/{}".format(partition, account, role_name)
    
    hyperparameters = {'train-steps': 100}

    estimator = Estimator(role=role_arn,
                        instance_count=1,
                        instance_type=instance_type,
                        image_name='sagemaker-recsys-graph-train:latest',
                        image_uri='002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-train',
                        hyperparameters=hyperparameters)

    estimator.fit(wait=False)

    responce_body = 'finish_train'

    responce = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': responce_body
    }
    print(responce)

    return responce
    # return json.loads(responce)
