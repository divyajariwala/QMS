region = "us-east-1"
environment = "dev"
short_name = "tema"
component = "insights"
project = "Tech-enabled Medical Affairs"
owner = "Vatsal Shah"
vpc_id = 	"vpc-08ffe2676f2941397"
subnet1 = "subnet-0facf8765ffbd54c7"
subnet2 = "subnet-0448c3f6d4100a29b"
subnet3 = "subnet-0ffd0a1fd724ddfec"
subnet4 = "subnet-0df3b976f0417863e"
subnet5 = "subnet-075ab04be1a272e64"
s3_buckets_list = [
    "medical-insights-crm",
    "medical-insights",
    "medical-insights-ops"
]
static_website = "medical-insights-ui"
lambda_execution_role_arn = "arn:aws:iam::273354627018:role/tema-dev-insights-lambda-role"
ecs_task_role_arn = "arn:aws:iam::273354627018:role/tema-dev-medical-insights-ecs"
step_function_role_arn = "arn:aws:iam::273354627018:role/tema-dev-insights-step-function-role"
event_bridge_role_arn = "arn:aws:iam::273354627018:role/tema-dev-insights-events-role"
step_function_configs = [
  {
    step_function_name = "generate-briefs"
    definition_yaml_path = "conf/dev/definitions/generate-briefs.yaml"
    event_trigger = [
      {
        trigger_name = "tema-dev-generate-briefs"
        trigger_description = "Trigger lambda for S3 PutObject events"
        trigger_bucket = "tema-dev-medical-insights"
        trigger_path = "mi-brief-linked-insights/*"
      }
    ]
  },
  {
    step_function_name = "process-insights"
    definition_yaml_path = "conf/dev/definitions/process-insights.yaml"
    event_trigger = [
      {
        trigger_name = "tema-dev-process-insights"
        trigger_description = "Trigger lambda for S3 PutObject events"
        trigger_bucket = "tema-dev-medical-insights"
        trigger_path = "mi-uploaded-insight-files/uploaded/*"
      }
    ]
  }
]

dynamodb_configs = [
  {
    table_name = "activities"
    part_key = {
      key_name = "activity_id"
      key_type = "S"
    }
  },
  {
    table_name = "briefs"
    part_key = {
      key_name = "brief_id"
      key_type = "S"
    }
  },
  {
    table_name = "config-file-status"
    part_key = {
      key_name = "uuid"
      key_type = "S"
    }
  },
  {
    table_name = "generate-brief-status"
    part_key = {
      key_name = "uuid"
      key_type = "S"
    }
  },
  {
    table_name = "insights"
    part_key = {
      key_name = "insight_id"
      key_type = "S"
    }
  },
  {
    table_name = "insights-file-status"
    part_key = {
      key_name = "uuid"
      key_type = "S"
    }
  },
  {
    table_name = "insight-configuration"
    part_key = {
      key_name = "file_uuid"
      key_type = "S"
    }
  },
  {
    table_name = "product"
    part_key = {
      key_name = "product_id"
      key_type = "S"
    }
  },
  {
    table_name = "region"
    part_key = {
      key_name = "region_id"
      key_type = "S"
    }
  },
  {
    table_name = "therapeutic-area"
    part_key = {
      key_name = "ta_id"
      key_type = "S"
    }
  }
]
lambda_configs = [
  {
    function_name = "generate-brief"
    path = "src/app/generate_brief"
    environment_variables = {
      env = "dev"
      INSIGHTS_TABLE_NAME = "tema-dev-insights"
      BRIEFS_TABLE_NAME = "tema-dev-briefs"
      GENERATE_BRIEF_STATUS_TABLE = "tema-dev-generate-brief-status"
      BRIEF_SERVICE_URL = "http://ECS_ALB_DNS_NAME/summarization"
    }
    api_gateway_paths = []
    event_trigger = []
  },
  {
    function_name = "download-config"
    path = "src/app/download_config"
    environment_variables = {
      env = "dev"
      CONFIG_FILE_STATUS_TABLE_NAME = "tema-dev-config-file-status"
    }
    api_gateway_paths = [
      {
        path_name = "getLatestConfig"
        http_method = "GET"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "fetch-category-config"
    path = "src/app/fetch_category_config"
    environment_variables = {
      env = "dev"
      TA_TABLE = "tema-dev-therapeutic-area"
      REGION_TABLE = "tema-dev-region"
      PRODUCT_TABLE = "tema-dev-product"
    }
    api_gateway_paths = [
      {
        path_name = "fetchCategories"
        http_method = "GET"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "remove-insights"
    path = "src/app/remove_insights"
    environment_variables = {
      env = "dev"
      INSIGHTS_TABLE_NAME = "tema-dev-insights"
    }
    api_gateway_paths = [
      {
        path_name = "removeInsights"
        http_method = "DELETE"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "fetch-insight-file"
    path = "src/app/fetch_insight_file"
    environment_variables = {
      env = "dev"
      CRM_BUCKET_NAME = "tema-dev-medical-insights-crm"
    }
    api_gateway_paths = [
      {
        path_name = "fetchFiles"
        http_method = "GET"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "save-insights-to-db"
    path = "src/app/save_insights_to_db"
    environment_variables = {
      env = "dev"
      FILE_STATUS_TABLE_NAME = "tema-dev-insights-file-status"
      INSIGHTS_TABLE_NAME = "tema-dev-insights"
      INSIGHT_CONFIGURATION_TABLE_NAME = "tema-dev-insight-configuration"
    }
    api_gateway_paths = []
    event_trigger = []
  },
  {
    function_name = "validate-insight-file"
    path = "src/app/validate_insight_file"
    environment_variables = {
      env = "dev"
      CATEGORY_VALIDATED_COLUMNS = "Category Tag Column"
      SOURCE_VALIDATED_COLUMNS = "Insight Source File Columns"
      UPLOADED_INSIGHT_PREFIX = "mi-uploaded-insight-files"
      MEDICAL_INSIGHT_BUCKET = "tema-dev-medical-insights"
      FILE_STATUS_TABLE_NAME = "tema-dev-insights-file-status"
      INSIGHT_CONFIGURATION_TABLE_NAME = "tema-dev-insight-configuration"
      INSIGHTS_VALIDATE_CONFIG_SUFFIX = "mi-uploaded-config-files/Medical Insights Config.xlsx"
    }
    api_gateway_paths = [
      {
        path_name = "uploadInsightFile"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "get-config-status"
    path = "src/app/get_config_status"
    environment_variables = {
      env = "dev"
      CONFIG_FILE_STATUS_TABLE_NAME = "tema-dev-config-file-status"
    }
    api_gateway_paths = [
      {
        path_name = "getConfigStatus"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "move-insight-file-to-s3"
    path = "src/app/move_insight_file_to_s3"
    environment_variables = {
      env = "dev"
      FILE_STATUS_TABLE_NAME = "tema-dev-insights-file-status"
      MEDICAL_INSIGHT_BUCKET = "tema-dev-medical-insights"
      UPLOADED_INSIGHT_PREFIX = "mi-uploaded-insight-files"
    }
    api_gateway_paths = [
      {
        path_name = "confirmLoadInsights"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "generate-briefs-trigger"
    path = "src/app/generate_briefs_trigger"
    environment_variables = {
      env = "dev"
      BRIEFS_TABLE_NAME = "tema-dev-briefs"
      BRIEF_INSIGHTS_PREFIX = "mi-brief-linked-insights"
      GENERATE_BRIEF_STATUS_TABLE = "tema-dev-generate-brief-status"
      INSIGHTS_TABLE_NAME = "tema-dev-insights"
      MEDICAL_INSIGHT_BUCKET = "tema-dev-medical-insights"
    }
    api_gateway_paths = [
      {
        path_name = "generateBrief"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "fetch-activities"
    path = "src/app/fetch_activities"
    environment_variables = {
      env = "dev"
      ACTIVITIES_TABLE_NAME = "tema-dev-activities"
    }
    api_gateway_paths = [
      {
        path_name = "fetchActivities"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "extend-insight-category"
    path = "src/app/extend_insight_category"
    environment_variables = {
      env = "dev"
      CATEGORY_SERVICE_URL = "http://ECS_ALB_DNS_NAME/category_append"
      FILE_STATUS_TABLE_NAME = "tema-dev-insights-file-status"
      INSIGHT_CONFIGURATION_TABLE_NAME = "tema-dev-insight-configuration"
    }
    api_gateway_paths = []
    event_trigger = []
  },
  {
    function_name = "insights-send-mail"
    path = "src/app/insights_send_mail"
    environment_variables = {
      env = "dev"
      ACTIVITIES_TABLE_NAME = "tema-dev-activities"
      SENDER_EMAIL = "tema_sender@outlook.com"
    }
    api_gateway_paths = [
      {
        path_name = "insightsSendMail"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "fetch-insights"
    path = "src/app/fetch_insights"
    environment_variables = {
      env = "dev"
      INSIGHTS_FILE_STATUS = "tema-dev-insights-file-status"
      INSIGHTS_TABLE_NAME = "tema-dev-insights"
      INSIGHT_CONFIGURATION_TABLE_NAME = "tema-dev-insight-configuration"
    }
    api_gateway_paths = [
      {
        path_name = "fetchInsights"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "fetch-briefs"
    path = "src/app/fetch_briefs"
    environment_variables = {
      env = "dev"
      BRIEFS_TABLE_NAME = "tema-dev-briefs"
      GENERATE_BRIEF_STATUS_TABLE = "tema-dev-generate-brief-status"
    }
    api_gateway_paths = [
      {
        path_name = "fetchBriefs"
        http_method = "POST"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "process-config-file"
    path = "src/app/process_config_file"
    environment_variables = {
      env = "dev"
      CONFIG_FILE_STATUS_TABLE_NAME = "tema-dev-config-file-status"
      INSIGHT_CONFIGURATION_TABLE_NAME = "tema-dev-insight-configuration"
      TA_TABLE = "tema-dev-therapeutic-area"
      REGION_TABLE = "tema-dev-region"
      PRODUCT_TABLE = "tema-dev-product"
    }
    event_trigger = [
      {
        trigger_name = "tema-dev-insights-config-process-trigger"
        trigger_description = "Trigger lambda for S3 PutObject events"
        trigger_bucket = "tema-dev-medical-insights"
        trigger_path = "mi-uploaded-config-files/*"
      }
    ]
  },
  {
    function_name = "request-temp"
    path = "src/app/request_temp"
    environment_variables = {
      env = "dev"
      BRIEF_INSIGHTS_PREFIX = "mi-brief-linked-insights"
      MEDICAL_INSIGHT_BUCKET = "tema-dev-medical-insights"
      FILE_STATUS_TABLE_NAME = "tema-dev-insights-file-status"
      GENERATE_BRIEF_STATUS_TABLE = "tema-dev-generate-brief-status"
      INSIGHTS_TABLE_NAME = "tema-dev-insights"
      INSIGHT_CONFIGURATION_TABLE_NAME = "tema-dev-insight-configuration"
      SOURCE_VALIDATED_COLUMNS = "Insight Source File Columns"
    }
    api_gateway_paths = []
    event_trigger = []
  },
  {
    function_name = "update-insight"
    path = "src/app/update_insight"
    environment_variables = {
      env = "dev"
      ACTIVITIES_TABLE_NAME = "tema-dev-activities"
      INSIGHTS_TABLE_NAME = "tema-dev-insights"
    }
    api_gateway_paths = [
      {
        path_name = "updateInsight"
        http_method = "PUT"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "update-brief"
    path = "src/app/update_brief"
    environment_variables = {
      env = "dev"
      ACTIVITIES_TABLE_NAME = "tema-dev-activities"
      BRIEFS_TABLE_NAME = "tema-dev-briefs"
    }
    api_gateway_paths = [
      {
        path_name = "updateBrief"
        http_method = "PUT"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "remove-briefs"
    path = "src/app/remove_briefs"
    environment_variables = {
      env = "dev"
      BRIEFS_TABLE_NAME = "tema-dev-briefs"
    }
    api_gateway_paths = [
      {
        path_name = "removeBriefs"
        http_method = "DELETE"
      }
    ]
    event_trigger = []
  },
  {
    function_name = "insights-generate-upload-urls"
    path = "src/app/insights_generate_upload_urls"
    environment_variables = {
      env = "dev"
      CONFIG_FILE_STATUS_TABLE_NAME = "tema-dev-config-file-status"
      INSIGHT_FILE_STATUS_TABLE_NAME = "tema-dev-insights-file-status"
      INSIGHT_CONFIG_PREFIX = "mi-uploaded-config-files"      
      MEDICAL_INSIGHT_BUCKET = "tema-dev-medical-insights"
      UPLOADED_INSIGHT_PREFIX = "mi-uploaded-insight-files/uploaded"
    }
    api_gateway_paths = [
      {
        path_name = "insightsGenerateUploadUrls"
        http_method = "POST"
      }
    ]
    event_trigger = []
  }
]
