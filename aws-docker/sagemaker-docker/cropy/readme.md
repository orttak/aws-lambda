
### CROPY SageMaker Docker 

This custom image uses the official Python 3.6 image from DockerHub as a custom image in SageMaker Studio and demostrates how to bundle a file along with the custom image and access it in SageMaker Studio.

### Building the image

Build the Docker image and push to Amazon ECR. 
```
# Modify these as required. The Docker registry endpoint can be tuned based on your current region from https://docs.aws.amazon.com/general/latest/gr/ecr.html#ecr-docker-endpoints
REGION=<aws-region>
ACCOUNT_ID=<account-id>
ECR_REPO_NAME=<ECR_REPO_NAME>

# Build the image
# AppImageConfigName which in app-image-config.json file should be equal >>>>> IMAGE_NAME
IMAGE_NAME=cropy-v01
aws --region ${REGION} ecr get-login-password | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}
docker build . -t ${IMAGE_NAME} -t ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_NAME}
```

```
docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_NAME}
```

### Using with SageMaker Studio

Create a SageMaker Image with the image in ECR. 

```
# Role in your account to be used for the SageMaker Image
ROLE_ARN=<role-arn>

aws --region ${REGION} sagemaker create-image \
    --image-name ${IMAGE_NAME} \
    --role-arn ${ROLE_ARN}

aws --region ${REGION} sagemaker create-image-version \
    --image-name ${IMAGE_NAME} \
    --base-image "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_NAME}"

# Verify the image-version is created successfully. Do NOT proceed if image-version is in CREATE_FAILED state or in any other state apart from CREATED.
aws --region ${REGION} sagemaker describe-image-version --image-name ${IMAGE_NAME}
```

Create a AppImageConfig for this image

```
aws --region ${REGION} sagemaker create-app-image-config --cli-input-json file://app-image-config-input.json

```

If you have an existing Domain, you can also use the `update-domain`

```
aws --region ${REGION} sagemaker update-domain --cli-input-json file://update-domain-input.json
```