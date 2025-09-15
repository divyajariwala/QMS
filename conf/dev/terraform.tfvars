region = "us-east-1"
environment = "dev"
short_name = "qms"
project = "QMS AI"
owner = "Vatsal Shah"
vpc_id = "vpc-05eab34b7783f4710"
subnet1 = "subnet-0289194ee67650645"
subnet2 = "subnet-022b19502393472ea"
subnet3 = "subnet-0103978437a4a0f44"
subnet4 = "subnet-00f8e1be5df54b3d4"
security_group_id = "sg-073837aa58ac9dc40"
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
    sqs_trigger = [
      {
        queue_name = "preload-narratives"
        visibility_timeout = 5000
        max_receive_count = 1000
        batch_size = 500
        max_batch_window = 20
        max_concurrency = 20
      }
    ]
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
  {
    function_name = "narrative-get-classified-narratives"
    path = "src/app/narrative_get_classified_narratives"
    environment_variables = {
      env = "dev"
    }
    api_gateway_paths = [
      {
        path_name = "getClassifiedNarratives"
        http_method = "GET"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "narrative-classify-narratives"
    path = "src/app/narrative_classify_narratives"
    environment_variables = {
      env = "dev"
    }
    api_gateway_paths = [
      {
        path_name = "classifyNarratives"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "complaints-get-product-complaints"
    path = "src/app/complaints_get_product_complaints"
    environment_variables = {
      env = "dev"
    }
    api_gateway_paths = [
      {
        path_name = "getProductComplaints"
        http_method = "GET"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "complaints-classify-complaints"
    path = "src/app/complaints_classify_complaints"
    environment_variables = {
      env = "dev"
    }
    api_gateway_paths = [
      {
        path_name = "classifyComplaints"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
]


