region = "us-east-1"
environment = "dev"
short_name = "qms"
project = "QMS AI"
owner = "Vatsal Shah"
vpc_id = ""
subnet1 = ""
subnet2 = ""
subnet3 = ""
subnet4 = ""
subnet5 = ""
security_group_id = ""
api_image_uri = "120569648189.dkr.ecr.us-east-1.amazonaws.com/qms-ai-model"
s3_buckets_list = [
  "narrative-initial-files",
]
static_website = ""
lambda_execution_role_arn = "arn:aws:iam::120569648189:role/qms-dev-lambda-role"
ecs_task_role_arn = "arn:aws:iam::120569648189:role/qms-dev-ecs-role"
step_function_role_arn = "arn:aws:iam::120569648189:role/qms-dev-step-function-role"
event_bridge_role_arn = "arn:aws:iam::120569648189:role/qms-dev-events-role"
step_function_configs = []
dynamodb_configs = [
  {
    table_name = "narrative-metadata"
    part_key = {
      key_name = "ta_id"
      key_type = "S"
    }
  }
]
lambda_configs = [
  {
    function_name = "narrative-upload-handler"
    path = "src/app/narrative_upload_handler"
    environment_variables = {
      env = "dev"
    }
    api_gateway_paths = [
      {
        path_name = "narrativeFiles"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "narrative-process-handler"
    path = "src/app/narrative_process_handler"
    environment_variables = {
      env = "dev"
    }
    api_gateway_paths = []
    event_trigger = []
  },
  {
    function_name = "narrative-aepc-detector"
    path = "src/app/narrative_aepc_detector"
    environment_variables = {
      env = "dev"
    }
    api_gateway_paths = []
    event_trigger = []
  },
]


