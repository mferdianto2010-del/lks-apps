REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

API_ID=$(aws apigateway create-rest-api --name LKS-API-Users \
  --endpoint-configuration types=REGIONAL --query id --output text)
ROOT=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[0].id' --output text)
USERS=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT \
  --path-part users --query id --output text)
USERID=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $USERS \
  --path-part '{id}' --query id --output text)

add_method() {   # $1=resource-id  $2=HTTP method  $3=nama fungsi Lambda
  aws apigateway put-method --rest-api-id $API_ID --resource-id $1 \
    --http-method $2 --authorization-type NONE
  aws apigateway put-integration --rest-api-id $API_ID --resource-id $1 \
    --http-method $2 --type AWS_PROXY --integration-http-method POST \
    --uri arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$ACCOUNT:function:$3/invocations
  aws lambda add-permission --function-name $3 --statement-id apigw-$2-$RANDOM \
    --action lambda:InvokeFunction --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT:$API_ID/*/$2/*"
}

add_method $USERS  GET    lks-get-users
add_method $USERS  POST   lks-create-user
add_method $USERID GET    lks-get-user
add_method $USERID PUT    lks-update-user
add_method $USERID DELETE lks-delete-user

aws apigateway create-deployment --rest-api-id $API_ID --stage-name production
echo "URL: https://$API_ID.execute-api.$REGION.amazonaws.com/production"
