# complaints-upload-final-results  Lambda Function

This project contains an AWS Lambda function that handles a POST request containing a request body with properties `id` and `data`, where `data` includes the original model values and user-edited custom values. The function saves this data to the `final_results` and `audit` tables. Next, it sends the data to the Veeva API using the correct credentials. Finally, the function returns the data sent to the API as a JSON object.

## Project structure

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
  git clone https://github.com/EliLillyCo/complaints-upload-final-results
  cd complaints-upload-final-results
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
    "data": [
      {
        "model": {
          "category": "Leaking unspecified",
          "crl": "Leaking unspecified - CSC",
          "level": 1
        },
        "user": {
          "category": "Leaking unspecified",
          "crl": "Leaking unspecified - CSC",
          "level": 1,
          "unit": 1
        }
      }
    ]
  }
}
```

### Example Response

```json
{
  "data has been loaded": [
    {
      "model": {
        "category": "Leaking unspecified",
        "crl": "Leaking unspecified - CSC",
        "level": 1
      },
      "user": {
        "category": "Leaking unspecified",
        "crl": "Leaking unspecified - CSC",
        "level": 1,
        "unit": 1
      }
    }
  ],
  "status": "success"
}
```

## Functions

### `lambda_handler(event, context)`

Handles the incoming request, retrieves secrets, save data into final results and audit table. Also, send data to Veeva API.

### `insert_data(table_name, item_uuid, model_response, user_response, model_priority=None, priority=None)`

Put item into table

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

### `generate_token(secret)`

Generates an access token using the provided secret.

### `post_record(results, token, secret)`

Post the record to the AI Toolkit API.

### `post_record_with_http_client(results, token, secret)`

Post the record to the AI Toolkit API using http.client.

### `fetch_crl_code_from_lookup(category, crl_value)`

Fetch the crlCode from the lookup table based on the category (cscValue) and crlValue.
