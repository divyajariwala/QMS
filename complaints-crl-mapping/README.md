# complaints-crl-mapping Lambda Function

This project contains an AWS Lambda function that that receives event data, which includes `uuid`, `complaint`, `level`, and `subcategory`. This data is then used to retrieve additional information from the `lookup` table, enriching the original dataset. The constructed dataset is subsequently stored in the `inference-results` and `audit` tables. Finally, the enriched dataset is utilized to generate priority data, which is returned.

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
  git clone https://github.com/EliLillyCo/complaints-crl-mapping
  cd complaints-crl-mapping
  ```

2. Install the required Python packages:
  ```sh
  pip install -r requirements.txt
  ```

## Usage

- Receive event data including uuid, complaint, level, and subcategory.
- Use the received data to retrieve additional information from the lookup table.
- Construct a dataset and store it in the inference-results and audit tables.
- Utilize the dataset to generate priority data and return the result.

## Functions

### `lambda_handler(event, context)`

Process the received event params and update the inference and audit table. Returns prioriy data.

### `extract_input_data(event)`

Extracts level and category values from the received event.

### `insert_data(table_name, item_uuid, result)`

Put item into table.

### `convert_to_dynamodb_compatible(data)`

Performs some data conversions to store the correct data in the DynamoDB table.

### `get_audit_item(partition_key)`

Retrieve the audit item from DynamoDB.

### `update_audit_log_with_results(audit_item, start_server_time, result, end_server_time)`

Update the audit log with CRL mapping results.

### `get_current_time()`

Get the current time in ISO format.

### `calculate_processing_time(start_time, end_time)`

Calculate the processing time between two timestamps.

### `handle_exception(exception, message, status_code=503)`

Handle exceptions in the Lambda function.

### `create_response(body, status_code=200)`

Create a formatted response.

### `fetch_crl_mappings(input_data)`

Fetch CRL mappings from the lookup_table for the provided categories.

### `perform_crl_mapping(input_data, crl_mappings)`

Perform CRL mapping based on input data and fetched CRL mappings.

### `parse_event_body(event)`

Parse and validate the event body.

### `table_exists(table_name)`

Check if an specific table already exists.

### `save_audit_log(uid4, content, start_server_time)`

Save the initial log in the audit table.

### `update_audit_log(uid4, end_server_time, processing_time_seconds)`

Update the audit log with processing time and end time.
