# complaints-subcategory Lambda Function

This project includes an AWS Lambda function that processes data by retrieving information from the `metadata` table, obtaining model routing details from the `lookup` table, and invoking the SageMaker `modelCategoryEndpoint` for data processing. The resulting output is stored in the `audit` table, and the processed result is returned.

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
  git clone https://github.com/EliLillyCo/complaints-subcategory
  cd complaints-subcategory
  ```

2. Install the required Python packages:
  ```sh
  pip install -r requirements.txt
  ```

## Usage

## Functions

### `lambda_handler(event, context)`

Retrieves data from the metadata table, fetches model routing information from the lookup table, and invokes a SageMaker endpoint. It then saves the result in the audit table before returning the result.

### `get_current_time()`

Get the current time in ISO format.

### `calculate_processing_time(start_time, end_time)`

Calculate the processing time between two timestamps.

### `handle_exception(exception, message, status_code=503)`

Handle exceptions in the Lambda function.

### `get_item_from_dynamodb(table, key)`

Get an item from a DynamoDB table.

### `get_model_routing_from_lookup(drug_name)`

Fetch model routing information from lookup table using the SK (Sort Key).

### `update_audit_log_initial(partition_key, subcategory_dict)`

Initial update of the audit log with the base subcategory information.

### `update_audit_log_results(partition_key, result, end_server_time, processing_time_seconds)`

Update the audit log with the results, processing time, and end time.

### `invoke_sagemaker_endpoint(endpoint_name, payload)`

Invoke a SageMaker endpoint and return the result.