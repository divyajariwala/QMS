region                  = "us-east-1"
environment             = "dev"
short_name              = "qms"
project                 = "QMS AI"
owner                   = "Vatsal Shah"
vpc_id                  = "vpc-05eab34b7783f4710"
subnet1                 = "subnet-0289194ee67650645"
subnet2                 = "subnet-0948aa53dddc1752a"
subnet3                 = "subnet-0142513425585a3ec"
subnet4                 = "subnet-07cf57f40e705dc5b"
security_group_id       = "sg-073837aa58ac9dc40"
s3_buckets_list = [
  "initial-files",
]
static_website            = "ui"
lambda_execution_role_arn = "arn:aws:iam::120569648189:role/qms-dev-lambda-role"
step_function_role_arn    = "arn:aws:iam::120569648189:role/qms-dev-step-function-role"
event_bridge_role_arn     = "arn:aws:iam::120569648189:role/qms-dev-events-role"
sagemaker_role_arn = "arn:aws:iam::120569648189:role/qms-dev-sagemaker-execution-role"

serverless_min_acu        = "2"
serverless_max_acu        = "16"

lambda_configs = [
  {
    function_name = "create-complaint"
    path          = "src/app/create_complaint"
    environment_variables = {
      env                 = "dev"
      sqs_queue_base_name = "preload-complaints"
      db_secret_base_name = "aurora-postgres-master"
      db_region = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "createComplaint"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "upload-complaints"
    path          = "src/app/upload_complaints"
    environment_variables = {
      env                 = "dev"
      metadata_table_name = "complaints-metadata"
    }
    api_gateway_paths = [
      {
        path_name   = "uploadComplaints"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "extract-and-process-complaints"
    path          = "src/app/extract_and_process_complaints"
    environment_variables = {
      env                          = "dev"
      dynamodb_table_base_name     = "complaints-metadata"
      classify_sqs_queue_base_name = "classify-complaints"
      model_id = "arn:aws:bedrock:us-east-1:120569648189:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
      db_secret_base_name = "aurora-postgres-master"
      db_region = "us-east-1"
    }
    sqs_trigger = [
      {
        queue_name         = "preload-complaints"
        visibility_timeout = 900
        max_receive_count  = 3
        batch_size         = 10
        max_batch_window   = 5
        max_concurrency    = 10
      }
    ]
  },
  {
    function_name = "classify-complaints"
    path          = "src/app/classify_complaints"
    environment_variables = {
      env                       = "dev"
      step_function_base_name   = "classify-complaints"
      aws_region                = "us-east-1"
      audit_log_table_base_name = "complaints-audit-log"
      db_secret_base_name = "aurora-postgres-master"
      db_region = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "classifyComplaints"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "get-complaints"
    path          = "src/app/get_complaints"
    environment_variables = {
      env                 = "dev"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "getComplaints"
        http_method = "GET"
      }
    ]
  },
  {
    function_name = "approve-complaints"
    path          = "src/app/approve_complaints"
    environment_variables = {
      env                 = "dev"
      DYNAMODB_TABLE_NAME = "qms-dev-complaints-metadata"
    }
    api_gateway_paths = [
      {
        path_name   = "approveComplaints"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "auth-callback"
    path          = "src/app/auth_callback"
    environment_variables = {
      env                 = "dev"
    }
    api_gateway_paths = [
      {
        path_name   = "authCallback"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "calculate-complaints-level"
    path          = "src/app/calculate_complaints_level"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
      level_endpoint = "qms-dev-mounjaro-level"
    }
  },
  {
    function_name = "calculate-complaints-subcategory"
    path          = "src/app/calculate_complaints_subcategory"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
      subcategory_endpoint = "qms-dev-mounjaro-category"
    }
  },
  {
    function_name = "calculate-complaints-crl"
    path          = "src/app/calculate_complaints_crl"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
    }
  },
  {
    function_name = "calculate-complaints-priority"
    path          = "src/app/calculate_complaints_priority"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
      llm_model_id        = "anthropic.claude-3-5-sonnet-20240620-v1:0"
      db_secret_base_name = "aurora-postgres-master"
    }
  },
  {
    function_name = "modify-extracted-text"
    path          = "src/app/modify_extracted_text"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
      db_secret_base_name = "aurora-postgres-master"
    }
    api_gateway_paths = [
      {
        path_name   = "modifyExtractedDetails"
        http_method = "POST"
      },
    ]
  },
  {
    function_name = "upload-deviations"
    path          = "src/app/upload_deviations"
    environment_variables = {
      env                 = "dev"
      sqs_queue_base_name = "process-deviations"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "uploadDeviations"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "extract-and-process-deviations"
    path          = "src/app/extract_and_process_deviations"
    environment_variables = {
      env                 = "dev"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    sqs_trigger = [
      {
        queue_name         = "process-deviations"
        visibility_timeout = 900
        max_receive_count  = 3
        batch_size         = 10
        max_batch_window   = 5
        max_concurrency    = 10
      }
    ]
  },
  {
    function_name = "generate-rca"
    path          = "src/app/generate_rca"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
      llm_model_id        = "anthropic.claude-3-haiku-20240307-v1:0"
      db_secret_base_name = "aurora-postgres-master"
    }
    api_gateway_paths = [
      {
        path_name   = "generateRCA"
        http_method = "POST"
      },
    ]
  },
  {
    function_name = "add-investigation-summary"
    path          = "src/app/add_investigation_summary"
    environment_variables = {
      env                 = "dev"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "addInvestigationSummary"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "get-deviations-list"
    path          = "src/app/get_deviations"
    environment_variables = {
      env                 = "dev"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "getDeviation"
        http_method = "GET"
      }
    ]
  },
  {
    function_name = "get-rca-categories"
    path          = "src/app/get_rca_categories"
    environment_variables = {
      env                 = "dev"
    }
    api_gateway_paths = [
      {
        path_name   = "getRCACategories"
        http_method = "GET"
      }
    ]
  },
  {
    function_name = "submit-rca"
    path          = "src/app/submit_rca"
    environment_variables = {
      env                 = "dev"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "submitRCA"
        http_method = "POST"
      }
    ]
  },
  {
    function_name = "update-rca"
    path          = "src/app/update_rca"
    environment_variables = {
      env                 = "dev"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "updateRCA"
        http_method = "PUT"
      }
    ]
  },
  {
    function_name = "get-grading"
    path          = "src/app/get_grading"
    environment_variables = {
      env                 = "dev"
      db_secret_base_name = "aurora-postgres-master"
      db_region           = "us-east-1"
    }
    api_gateway_paths = [
      {
        path_name   = "getGrading"
        http_method = "GET"
      }
    ]
  },
  {
    function_name = "start-grading"
    path          = "src/app/start_grading"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
      llm_model_id        = "anthropic.claude-3-haiku-20240307-v1:0"
      db_secret_base_name = "aurora-postgres-master"
    }
    api_gateway_paths = [
      {
        path_name   = "startGrading"
        http_method = "POST"
      }
    ]
  }
]



