# complaints-inference Lambda Function

This project contains an **Amazon Web Services (AWS) Lambda** function that processes data received from a `complaint queue` **(Simple Queue Service, or SQS)**. The function extracts a **Universally Unique Identifier (UUID)** from the received data and uses it to retrieve the corresponding narrative from a `metadata` table. It then builds inference data based on the retrieved narrative, stores the resulting inference data into an `audit` table, and initiates the execution of the **AWS Step Functions** state machine using the inference data.

## Project Structure

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
    git clone https://github.com/EliLillyCo/complaints-inference
    cd complaints-preload-inference
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Environment Variables

The Lambda function requires the following environment variables to be set:

- `aws_region_name`: The AWS region where the secrets are stored.
- `metadata_table_name`: The metada DynamoDB table name.
- `state_machine_name`: The name of the AWS state machine.

## Usage

The main entry point for the Lambda function is the `lambda_handler` function in `src/lambda_function.py`. This function handles the message received from the `complaints queue` and uses this data to generate inference data and store it in the `audit` table. Then, starts the execution of the step functions using the infence data.

## Functions

### `lambda_handler(event, context)`

Handle the received data from the queue. Obtain narrative from `metadata` table. Save inference data in the `audit` table. Starts the execution of the step functions using the inference data.

### `get_narrative_from_dynamodb(uuid)`

Obtain the narrative from DynamoDB table.

### `update_audit_table(partition_key, inference_dict)`

Update the audit table with the new inference data.

### `get_current_time()`

Get the current time in ISO format.

### `calculate_processing_time(start_time, end_time)`

Calculate the processing time between two timestamps.

### `handle_exception(exception, message, status_code=503)`

Handle exceptions in the Lambda function.

### `create_response(body, status_code=200)`

Create a formatted response.
