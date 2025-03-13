# complaints-fetch-results Lambda Function

This project contains an AWS Lambda function that receives a `complaint_id` as a parameter. The function retrieves data from the inference and priority tables, saves relevant information into the audit table, and combines the data before returning the final result.

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
  "results": {
    "uuid": "VDE00000001R232",
    "summary": "The patient developed skin lesions after starting a new medication. This adverse reaction to the medication is the core issue related to the product...",
    "details": [
      {
        "category": "Miscellaneous Sub-Category",
        "category_confidence_score": 0.83,
        "crl_value": null,
        "level": 1
      },
      {
        "category": "Leaking unspecified",
        "category_confidence_score": 0.05,
        "crl_value": "Leaking unspecified - CSC",
        "level": 1
      },
      {
        "category": "Needle bent",
        "category_confidence_score": 0.02,
        "crl_value": "Needle bent - CSC",
        "level": 1
      }
    ]
  },
  "crl_values": [
    "Base cap difficult to remove - CSC",
    "Clicks - CSC",
    "Device activated before placement on skin - CSC",
    "Device activated before pressing button - CSC",
    ...
  ],
  "csc_values": [
    "Device activated before placement on skin",
    "Device activated before pressing button",
    "Device activated with base cap attached",
    "Device defective",
    ...
  ]
}
```

## Functions

### `lambda_handler(event, context)`

- Get data from inference_results table.
- Get data from priority_results table.
- Save data into audit table.
- Save data into final results table.
- Returns the combined data.

### `convert_to_dynamodb_compatible(data)`

Performs some data conversions to store the correct data in the DynamoDB table.

### `update_levels(data)`

If `updated_level` is present in the data, set `original_lavel` and `level` values.

### `fetch_crl_values()`

Fetch list of crlValue values from lookup table where PK is 'LOOKUP#CrlMapping'.

### `fetch_csc_values(drugname)`

Fetch csc values from lookup table where PK is 'LOOKUP#CrlMapping' and drugname is in drugNames list.
