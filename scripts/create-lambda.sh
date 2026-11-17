set +H   # matikan history expansion supaya tanda ! di password aman
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
STACK=lks-infra
out() { aws cloudformation describe-stacks --stack-name $STACK --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }

SUBNETS=$(out PrivateSubnet1),$(out PrivateSubnet2)
SG=$(out SGAppsId)
DBHOST=$(out RDSEndpoint)
LAYER=$(aws lambda list-layer-versions --layer-name lks-pymysql --query 'LayerVersions[0].LayerVersionArn' --output text)

for pair in get_users:lks-get-users create_user:lks-create-user get_user:lks-get-user update_user:lks-update-user delete_user:lks-delete-user; do
  f=${pair%%:*}
  n=${pair##*:}
  cp lambda/$f.py lambda_function.py
  zip -q $n.zip lambda_function.py
  aws lambda create-function --function-name $n \
    --runtime python3.13 --handler lambda_function.lambda_handler \
    --role arn:aws:iam::$ACCOUNT:role/LabRole \
    --zip-file fileb://$n.zip --timeout 15 --layers $LAYER \
    --vpc-config SubnetIds=$SUBNETS,SecurityGroupIds=$SG \
    --environment "Variables={DB_HOST=$DBHOST,DB_USER=admin,DB_PASSWORD=Technobrain2025!,DB_NAME=techno-rds}" \
    --query FunctionName --output text
done
