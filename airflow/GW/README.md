##关于运行 Python CDK
需要先安装node，安装方法参考：
https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-up-node-on-ec2-instance.html

ecs task definition 在定义的时候，有两个地方要注意：
1. 要使用 Optional IAM role
2. 要设置 task 的security group 确保能被VPC 里的其他服务所调用。  