# complaints-queue-narrative Lambda Function

This project contains a AWS Lambda function receives a `complaint_id` as a parameter, constructs a message for AWS Simple Queue Service (SQS), and sends it to a specified queue. After successfully adding the message to the queue, the function returns operation details, including the SQS response data.

## Project structure

- `.github/workflows/`: Contains GitHub Actions workflows for CI/CD.
  - `clean.yml`: Workflow for first-time setup.
  - `lambda-deploy-dev.yml`: Workflow for deploying the Lambda function to the development environment.
- `src/`: Contains the source code for the Lambda function and utility modules.
  - `lambda_function.py`: Main Lambda function handler.

## Prerequisites

- Python
- AWS CLI configured with appropriate permissions
- `pip` for managing Python packages

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/EliLillyCo/complaints-queue-narrrative
    cd complaints-queue-narrrative
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

The main entry point for the Lambda function is the `lambda_handler` function in `src/lambda_function.py`. This function handles POST requests and processes the parameters received in the request body.

### Example Requests

```json
{
  "body": {
    "complaint_id": "VDE00000001R232",
  }
}
```

### Example Response

```json
{
  "response": {
    "MD5OfMessageBody": "1231abc1231123123123abc123123123",
    "MessageId": "123a123a-123a-123a-123a-123a123a123a",
    "ResponseMetadata": {
      "RequestId": "123a123a-123a-123a-123a-123a123a123a",
      "HTTPStatusCode": 200,
      "HTTPHeaders": {
        "x-amzn-requestid": "123a123a-123a-123a-123a-123a123a123a",
        "date": "Wed, 27 Nov 2024 18:34:42 GMT",
        "content-type": "application/x-amz-json-1.0",
        "content-length": "106",
        "connection": "keep-alive"
      },
      "RetryAttempts": 0
    }
  }
}
```

## Functions

### `lambda_handler(event, context)`

Handles the incoming POST request ans send a message to AWS SQS queue.

### `get_current_time()`

Get the current time in ISO format.

### `calculate_processing_time(start_time, end_time)`

Calculate the processing time between two timestamps.

### `handle_exception(exception, message, status_code=503)`

Handle exceptions in the Lambda function.

### `create_response(body, status_code=200)`

Create a formatted response.

### `send_to_queue(content)`

Send message to SQS queue.
