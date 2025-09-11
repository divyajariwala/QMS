# complaints-errorness-check Lambda Function

This project contains an AWS Lambda function that processes data received from the `errorness check input queue` (Simple Queue Service, or SQS), which contains narratives. The function iterates through each narrative to prepare `audit_entries` data. It then sends a POST request to the `AEPC detector` endpoint to validate the narratives (complaints), retrieves a `message` response, updates the `audit_entries`  with this message, and sends the data to the `errorness check results queue` (Simple Queue Service, or SQS). The updated `audit_entries` is subsequently stored in an `audit` table, and the `message` is returned.

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
    git clone https://github.com/EliLillyCo/complaints-errorness-check
    cd complaints-errorness-check
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Environment Variables

The Lambda function requires the following environment variables to be set:

- `aws_region_name`: The AWS region where the secrets are stored.
- `audit_table_name`: The name of the audit table (DynameDB).

## Usage

The main entry point for the Lambda function is the `lambda_handler` function in `src/lambda_function.py`. This function receives complaints from the input queue, validates the complaints, sends them the data to the results queue, and stores the results in the audit table.

## Functions

### `lambda_handler(event, context)`

Process the received data from the input queue. Sends the data to the result queue. Stores the results in the audit table.

### `get_current_time()`

Get the current time in ISO format.

### `convert_floats_to_decimal(data)`

Recursively convert float values in a dictionary or list to Decimal.

### `parse_narratives(record)`

Parse the record body and return the narratives.

### `aepc_post(jwt, narratives, secret)`

Send a request to the AEPC Detector.

### `mule_post(secret, message)`

Send the message to the errorness queue.

### `generate_token(secret)`

Generates an access token using the provided secret.

### `init_audit_log(audit_item: dict)`

Initialize the audit log with the narratives.

### `update_audit_log_with_aespc_data(updated_data)`

Update audit entries with the updated data.

### `save_audit_log(audit_entries)`

Save the data into the audit table.
