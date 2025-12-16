import json
import boto3
import os
from typing import Dict, Any
import logging
from utils import response, handle_cors_preflight, parse_event_body

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
ENV = os.environ.get('env', 'dev')
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
MODEL_ID = os.environ.get('llm_model_id', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"

# Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)

def load_prompt(prompt_file: str) -> str:
    """
    Load a prompt file from prompts/ folder
    """
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', prompt_file)
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading prompt file {prompt_file}: {str(e)}")
        raise

def call_bedrock_model(prompt: str, model_id: str = None) -> str:
    """
    Call the Bedrock model with the given prompt
    """
    try:
        # Use environment variable model ID if not provided
        if model_id is None:
            model_id = MODEL_ID
            
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        logger.error(f"Error calling Bedrock model: {str(e)}")
        raise

def generate_issues(investigation_summary: str) -> Dict[str, Any]:
    """
    Generates the Issues section of the RCA
    """
    prompt_template = load_prompt('issues_prompt.txt')
    prompt = prompt_template.format(investigation_summary=investigation_summary)
    
    response = call_bedrock_model(prompt)
    return json.loads(response)

def generate_major_root_cause_category(investigation_summary: str) -> Dict[str, Any]:
    """
    Generates the major root cause category of the root cause
    """
    prompt_template = load_prompt('major_root_cause_category_prompt.txt')
    prompt = prompt_template.format(investigation_summary=investigation_summary)
    
    response = call_bedrock_model(prompt)
    return json.loads(response)

def generate_near_root_cause(investigation_summary: str) -> Dict[str, Any]:
    """
    Generates the near root cause
    """
    prompt_template = load_prompt('near_root_cause_prompt.txt')
    prompt = prompt_template.format(investigation_summary=investigation_summary)
    
    response = call_bedrock_model(prompt)
    return json.loads(response)

def generate_root_cause(investigation_summary: str) -> Dict[str, Any]:
    """
    Generates the root cause
    """
    prompt_template = load_prompt('root_cause_prompt.txt')
    prompt = prompt_template.format(investigation_summary=investigation_summary)
    
    response = call_bedrock_model(prompt)
    return json.loads(response)

def lambda_handler(event, context):
    try:
        logger.info(f"Region: {AWS_REGION}, Model: {MODEL_ID}")
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()
        
        # Parse event body
        body = parse_event_body(event)
        investigation_summary = body.get('investigation_summary')
        
        if not investigation_summary:
            return response(400, "investigation_summary is required")
        
        logger.info("Starting RCA generation process")
        
        logger.info("Generating Issues section")
        issues = generate_issues(investigation_summary)
        
        logger.info("Generating Major Root Cause Category")
        major_category = generate_major_root_cause_category(investigation_summary)
        
        logger.info("Generating Near Root Cause")
        near_cause = generate_near_root_cause(investigation_summary)
        
        logger.info("Generating Root Cause")
        root_cause = generate_root_cause(investigation_summary)
        
        rca_result = {
            'deviation_id': body.get('deviation_id'),
            'rca_analysis': {
                'issues': issues.get('issues', []),
                'major_root_cause_category': major_category.get('major_root_cause_category', {}),
                'near_root_cause': near_cause.get('near_root_cause', {}),
                'root_cause': root_cause.get('root_cause', {}),
                'generated_timestamp': context.aws_request_id
            }
        }
        
        logger.info("RCA generation completed successfully")
        
        return response(200, "RCA generated successfully", rca_result)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return response(400, "Invalid JSON format", {"details": str(e)})
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
