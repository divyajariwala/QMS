# complaints-bulk-insert-dynamodb-data

## Overview
This project contains an AWS Lambda function written in Python that performs bulk inserts of complaint data into a DynamoDB table.

## Project Structure
- `src/lambda_function.py`: The main Lambda function code.

## Requirements
- Python 3.x
- boto3 library

## Deployment
Deploy the Lambda function using AWS CLI or any deployment tool of your choice.

## Usage
The Lambda function expects an event with the following structure:
```json
{
  "items": [
    {
      "attribute1": "value1",
      "attribute2": "value2"
    },
    ...
  ]
}