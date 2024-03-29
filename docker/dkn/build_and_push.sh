# FROM_ACCOUNT_ID 代表了引用的 docker image 在哪个账号下，这个763104351884的账号其实是固定的，SM用的都是这个账号
FROM_ACCOUNT_ID=763104351884
# 这个账号指的是想把 build 出来的 image 放到哪个 账号的 ECR 下，也就是当前使用者的account，跟 aws sts get-caller-identity 返回的 account 一致
ACCOUNT_ID=662566784674
REGION=ap-northeast-1
REPO_NAME=gw-dkn

TAG=`date '+%Y%m%d%H%M%S'`

$(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $FROM_ACCOUNT_ID)

docker build -f ./Dockerfile -t $REPO_NAME .

docker tag $REPO_NAME $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:${TAG}

$(aws ecr get-login --no-include-email --region ${REGION} --registry-ids $ACCOUNT_ID)
aws ecr describe-repositories --repository-names $REPO_NAME || aws ecr create-repository --repository-name $REPO_NAME

docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:${TAG}
