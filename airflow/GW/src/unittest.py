import config as cfg
import boto3

client = boto3.session.Session(profile_name='global').client('ecs')
config = cfg.config
ret = client.run_task(**config['run_task'])
print(ret)


