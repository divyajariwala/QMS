# complaints-priority Lambda Function

This project contains an AWS Lambda function that generates a dataset called `final_results` by invoking LLM models using custom prompts. This prompts vary if the priority params is present or not. Once generated, the final results dataset is stored in both the `priority-results` table and the `audit` table. Finally, the results are returned as a JSON object.

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
  git clone https://github.com/EliLillyCo/complaints-priority
  cd complaints-priority
  ```

2. Install the required Python packages:
  ```sh
  pip install -r requirements.txt
  ```

## Usage

- Generate a dataset called final_results by invoking LLM models using custom prompts, which vary depending on whether the priority parameter is present.
- Save the final_results dataset in both the priority-results table and the audit table.
- Additionally, return the results as a JSON object.

## Functions

### `lambda_handler(event, context)`

Invoke LLM models to generate the final results. Stores the result in the database and returns it.

### `insert_data(table_name, item_uuid, result)`

Put item into table.

### `convert_to_dynamodb_compatible(data)`

Performs some data conversions to store the correct data in the DynamoDB table.

### `get_current_time()`

Get the current time in ISO format.

### `calculate_processing_time(start_time, end_time)`

Calculate the processing time between two timestamps.

### `handle_exception(exception, message, status_code=503)`

Handle exceptions in the Lambda function.

### `create_response(body, status_code=200)`

Create a formatted response.

### `parse_event_body(event)`

Parse and validate the event body.

### `table_exists(table_name)`

Check if an specific table already exists.

### `save_audit_log(uid4, content, start_server_time)`

Save the initial log in the audit table.

### `update_audit_log(uid4, end_server_time, processing_time_seconds)`

Update the audit log with processing time and end time.
