# complaints-upload-narrative Lambda Function

This project contains a AWS Lambda function that handles a POST request. The function receives the parameters: `complaint_id`, `time`, `drugname`, and `narrative`. It saves this data into a DynamoDB table. Additionally, it calculates the processing time and stores both the data and the processing time into an audit table.

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
    git clone https://github.com/EliLillyCo/complaints-upload-narrrative
    cd complaints-upload-narrrative
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
    "time": "2024-11-27",
    "drugname": "DEVICE MOUNJARO",
    "narrative": "Patient has been on Mounjaro for a year. Patient states she is on 12.5mg and the pen didnt deploy...",
  }
}
```

### Example Response

```
"VDE00000001R232"
```

## Functions

### `lambda_handler(event, context)`

Handles the incoming POST request. Insert the received data into a DynamoDB table and stores the processing time and data into the audit table.

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

Check if the required table exists.

### `save_audit_log(uid4, content, start_server_time)`

Save the initial log in the audit table.

### `update_audit_log(uid4, end_server_time, processing_time_seconds)`

Update the audit log with processing time and end time.

### `insert_data(table_name, item_uuid, narrative, dt, drugname)`

Insert an item into the DynamoDB table.
