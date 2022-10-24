# 1950 Census Textract Script
Custom Amazon Textract script to extract name data from the 1950 Census records.
The script uses the AWS Textract service to extract the text and utilize Serverless solution to spin
up hundreds of processes to process the images in parallel.

## Requirements
The nodejs and python3 need to be installed on the development server.  All the following npm and python packages need to be installed as well.

```bash
npm install serverless

pip3 install sagemaker ipython scikit-build opencv-python matplotlib editdistance fuzzywuzzy python-Levenshtein
```
The AWS account access credential environment variables need to be setup to access the required AWS resources

```bash
export AWS_ACCESS_KEY_ID=AWS_ACCESS_ID

export AWS_SECRET_ACCESS_KEY=AWS_ACCESS_SECRET_KEY

export AWS_DEFAULT_REGION=us-gov-east-1 
```

## Test Runs
Set up S3 bucket environment variables
```bash
export BUCKET_SRC=source_s3_bucket
export BUCKET_DST=output_s3_bucket
export REGION=us-gov-east-1
```

run "./scripts/test.sh --debug --s3 1950census/43290879-Kansas/43290879-Kansas-045836/43290879-Kansas-045836-0009.jpg" to extract text from the 1950census/43290879-Kansas/43290879-Kansas-045836/43290879-Kansas-045836-0009.jpg in the source S3 bucket.

## Cloud Deployment
Update the source and destination S3 bucket names in the serverless.yml file to point to the correct S3 buckets. The securityGroupIds and subnetIds under VPC section need to be updated as well.

Run ./scripts/build-layer.sh to create the Lambda layer dependencies.zip file

Run "serverless deploy" to deploy the Lambda functions to AWS 

Run "python3 ./scripts/addtosqs.py path/to/full/path/image/list/file.txt" to add image list to the Lambda Function process queue 

