import boto3, sys

s3client = boto3.client('s3')

s3_key = sys.argv[1]
path = sys.argv[2]

print(s3_key)
print(path)

bucket, key = s3_key.split('/', 2)[-1].split('/', 1)

print(bucket, key)
s3client.download_file(bucket, key, path + '/model.tar.gz')
