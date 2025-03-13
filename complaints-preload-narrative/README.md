# complaints-preload-narrative Lambda Function

This project contains an AWS Lambda function that handles GET requests using a `complaintId` received in the query parameters. The function retrieves secrets from AWS Secrets Manager and uses them to generate a token and fetch records.

## Project Structure

- `.github/workflows/`: Contains GitHub Actions workflows for CI/CD.
  - `clean.yml`: Workflow for first-time setup.
  - `lambda-deploy-dev.yml`: Workflow for deploying the Lambda function to the development environment.
- `src/`: Contains the source code for the Lambda function and utility modules.
  - `lambda_function.py`: Main Lambda function handler.
  - `secrets_util.py`: Utility module for retrieving secrets from AWS Secrets Manager.

## Prerequisites

- Python
- AWS account with access to Secrets Manager
- AWS CLI configured with appropriate permissions
- `pip` for managing Python packages

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/EliLillyCo/complaints-preload-narrrative
    cd complaints-preload-narrrative
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Environment Variables

The Lambda function requires the following environment variables to be set:

- `aws_region_name`: The AWS region where the secrets are stored.
- `secrets_name`: The name of the secret in AWS Secrets Manager.

## Usage

The main entry point for the Lambda function is the `lambda_handler` function in `src/lambda_function.py`. This function handles GET requests and processes the `complaintId` received in the query parameters.

### Example Event

```json
{
  "queryStringParameters": {
    "complaintId": "VDE00000001R232"
  }
}
```

### Example Response

```json
{
  "status_code": 200,
  "body": {
    "complaint_id": "VDE00000001R232",
    "complaint_narrative": "Patient has been on Mounjaro for a year...",
    "drugname": null
  }
}
```

## Functions

### `lambda_handler(event, context)`

Handles the incoming request, retrieves secrets, generates a token, and fetches the record.

### `generate_token(secret)`

Generates an access token using the provided secret.

### `get_record(record_id, token, secret)`

Fetches a record using the provided `record_id`, `token`, and secret.

### `get_secret(secret_name, region)`

Retrieves a secret from AWS Secrets Manager.

## Logging

The Lambda function uses Python's built-in `logging` module to log information and errors.
