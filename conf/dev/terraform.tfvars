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
sagemaker_endpoint_name = "internal-pwc-mounjaro-12-categorization-model-v1"
s3_buckets_list = [
  "initial-files",
]
static_website            = "ui"
lambda_execution_role_arn = "arn:aws:iam::120569648189:role/qms-dev-lambda-role"
step_function_role_arn    = "arn:aws:iam::120569648189:role/qms-dev-step-function-role"
event_bridge_role_arn     = "arn:aws:iam::120569648189:role/qms-dev-events-role"
serverless_min_acu        = "2"
serverless_max_acu        = "16"

# dynamodb_configs = [
#   {
#     table_name = "complaints-metadata"
#     part_key = {
#       key_name = "PK"
#       key_type = "S"
#     }
#     sort_key = {
#       key_name = "SK"
#       key_type = "S"
#     }
#     global_secondary_indexes = [
#       {
#         name = "GSI1"
#         hash_key = "GSI1PK"
#         range_key = "GSI1SK"
#         projection_type = "ALL"
#       }
#     ]
#   },
#   {
#     table_name = "complaints-audit-log"
#     part_key = {
#       key_name = "PK"
#       key_type = "S"
#     }
#     sort_key = {
#       key_name = "SK"
#       key_type = "S"
#     }
#     global_secondary_indexes = [
#       {
#         name = "GSI1"
#         hash_key = "GSI1PK"
#         range_key = "GSI1SK"
#         projection_type = "ALL"
#       },
#       {
#         name = "GSI2"
#         hash_key = "GSI2PK"
#         range_key = "GSI2SK"
#         projection_type = "ALL"
#       }
#     ]
#   },
#   {
#     table_name = "complaints-unified-lookup"
#     part_key = {
#       key_name = "PK"
#       key_type = "S"
#     }
#     sort_key = {
#       key_name = "SK"
#       key_type = "S"
#     }
#   }
# ]

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
        visibility_timeout = 5000
        max_receive_count  = 1000
        batch_size         = 500
        max_batch_window   = 20
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
      level_endpoint = "roberta-level-model-v1"
    }
  },
  {
    function_name = "calculate-complaints-subcategory"
    path          = "src/app/calculate_complaints_subcategory"
    environment_variables = {
      env                 = "dev"
      aws_region          = "us-east-1"
      subcategory_endpoint = "roberta-mounjaro-category-12-model-v1"
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
  },
    api_gateway_paths = [
      {
        path_name   = "modifyExtractedDetails"
        http_method = "POST"
      }
    ]
]


