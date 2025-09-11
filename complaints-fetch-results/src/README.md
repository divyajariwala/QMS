# complaints-fetch-results
- **mq-qms-complaints-fetch-results** is an AWS Lambda whose:
    - Purpose: Processes inference results in S3 and dynamo db after all the Step Functions are triggered. 
    - Input: SQS message. 
    - Output: Inference results saved in DynamoDB. 
