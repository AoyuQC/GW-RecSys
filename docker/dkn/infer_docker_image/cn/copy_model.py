import boto3, sys

## python copy_model.py s3://leigh-gw/dkn_model/dkn-2020-11-28-06-41-17-782/output/model.tar.gz ./

s3client = boto3.client('s3')

s3_key = sys.argv[1]
path = sys.argv[2]

print('file on the s3 location:' + s3_key)
print('local file path: ' + path)

bucket, key = s3_key.split('/', 2)[-1].split('/', 1)

print(bucket, key)
s3client.download_file(bucket, key, path + '/model.tar.gz')
