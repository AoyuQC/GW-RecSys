import json
import os

import boto3

#from sagemaker.estimator import Estimator

from iam_helper import IamHelper
from sagemaker_controller import create_training_job, create_endpoint, \
    describe_training_job, describe_training_job_artifact, describe_endpoint, \
    list_endpoints

bucket = os.environ['BUCKET']
jobname = os.environ['JOB_NAME']
instance = os.environ['INSTANCE']
image_uri = os.environ['IMAGE_URI']
task = os.environ['TASK']
_lambda = boto3.client('lambda')

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))

    # # resource = event.get("source", None)
    # resource = event["path"]
    # body_str = json.loads(event["body"])
    # print('body: {}'.format(body_str))

    # instance_type = instance

    # input_s3_path = "s3://{}/{}/".format(bucket, jobname)
    # helper = IamHelper
    # client = boto3.client("sagemaker")
    # job_name = "{}-{}".format(jobname.replace("_", "-"), get_datetime_str())
    # account = IamHelper.get_account_id()
    # region = IamHelper.get_region()
    # partition = IamHelper.get_partition()
    # role_name = "AmazonSageMaker-ExecutionRole-20200512T121482"
    # role_arn = "arn:{}:iam::{}:role/service-role/{}".format(partition, account, role_name)
    
    # hyperparameters = {'train-steps': 100}

    # estimator = Estimator(role=role_arn,
    #                     instance_count=1,
    #                     instance_type=instance_type,
    #                     image_name='sagemaker-recsys-graph-train:latest',
    #                     image_uri='002224604296.dkr.ecr.us-east-1.amazonaws.com/sagemaker-recsys-graph-train',
    #                     hyperparameters=hyperparameters)

    # estimator.fit(wait=False)

    msg = {}
    try:
        job_arn = create_training_job(bucket, jobname, task, image_uri, instance)["TrainingJobArn"]
        msg = {"Status": "Success", "TrainingJob": job_arn.split("/")[1]}
    except Exception as e:
        msg = {"Status": "Failure", "Message": str(e)}
    print(msg)

    response = {
        "statusCode": 200,
        "body": json.dumps(msg),
        "headers": {
            "Content-Type": "application/json",
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
    }
    print(response)

    return response
    # return json.loads(responce)