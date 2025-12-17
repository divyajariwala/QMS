import json
import boto3
import os
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
        # Try different possible paths for Lambda deployment
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'prompts', prompt_file),
            os.path.join('/var/task', 'prompts', prompt_file),
            os.path.join('/var/task', prompt_file),
            prompt_file
        ]
        
        for prompt_path in possible_paths:
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    logger.info(f"Loaded prompt file: {prompt_file}")
                    return content
        
        raise FileNotFoundError(f"Prompt file {prompt_file} not found")
        
    except Exception as e:
        logger.error(f"Error loading prompt file {prompt_file}: {str(e)}")
        raise


def call_bedrock(prompt_text: str) -> str:
    """
    Call Bedrock Claude model with a prompt using the Converse API.
    
    Args:
        prompt_text: The formatted prompt string
        
    Returns:
        Plain text response from Claude
    """
    try:
        logger.info(f"Calling Bedrock model: {MODEL_ID}")
        
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt_text}]
                }
            ],
            inferenceConfig={
                "maxTokens": 2048,
                "temperature": 0
            }
        )
        
        response_text = response['output']['message']['content'][0]['text']
        logger.info(f"Response received, length: {len(response_text)} chars")
        
        return response_text.strip()
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        raise


def generate_issues(investigation_summary: str) -> str:
    """
    Generates the Issues section of the RCA
    
    Returns:
        Plain text description of issues
    """
    try:
        prompt_template = load_prompt('issues_prompt.txt')
        prompt = prompt_template.format(investigation_summary=investigation_summary)
        
        result = call_bedrock(prompt)
        logger.info("Successfully generated Issues section")
        return result
        
    except Exception as e:
        logger.error(f"Error generating Issues: {str(e)}")
        raise


def generate_major_root_cause_category(investigation_summary: str) -> str:
    """
    Generates the major root cause category
    
    Returns:
        Plain text category name
    """
    try:
        prompt_template = load_prompt('major_root_cause_category_prompt.txt')
        prompt = prompt_template.format(investigation_summary=investigation_summary)
        
        result = call_bedrock(prompt)
        logger.info("Successfully generated Major Root Cause Category")
        return result
        
    except Exception as e:
        logger.error(f"Error generating Major Category: {str(e)}")
        raise


def generate_near_root_cause(investigation_summary: str) -> str:
    """
    Generates the near root cause
    
    Returns:
        Plain text description of near root cause
    """
    try:
        prompt_template = load_prompt('near_root_cause_prompt.txt')
        prompt = prompt_template.format(investigation_summary=investigation_summary)
        
        result = call_bedrock(prompt)
        logger.info("Successfully generated Near Root Cause")
        return result
        
    except Exception as e:
        logger.error(f"Error generating Near Root Cause: {str(e)}")
        raise


def generate_root_cause(investigation_summary: str) -> str:
    """
    Generates the root cause
    
    Returns:
        Plain text description of root cause
    """
    try:
        prompt_template = load_prompt('root_cause_prompt.txt')
        prompt = prompt_template.format(investigation_summary=investigation_summary)
        
        result = call_bedrock(prompt)
        logger.info("Successfully generated Root Cause")
        return result
        
    except Exception as e:
        logger.error(f"Error generating Root Cause: {str(e)}")
        raise


def lambda_handler(event, context):
    try:
        logger.info(f"Environment: {ENV}, Region: {AWS_REGION}, Model: {MODEL_ID}")
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()
        
        # Parse event body
        body = parse_event_body(event)
        investigation_summary = body.get('investigation_summary')
        deviation_id = body.get('deviation_id')
        
        if not investigation_summary:
            return response(400, "investigation_summary is required")
        
        if not isinstance(investigation_summary, str):
            return response(400, f"investigation_summary must be a string")
        
        if not investigation_summary.strip():
            return response(400, "investigation_summary cannot be empty")
        
        logger.info("Starting RCA generation process")
        
        # Generate each section as plain text
        logger.info("Generating Issues section")
        issues_text = generate_issues(investigation_summary)
        
        logger.info("Generating Major Root Cause Category")
        major_category_text = generate_major_root_cause_category(investigation_summary)
        
        logger.info("Generating Near Root Cause")
        near_cause_text = generate_near_root_cause(investigation_summary)
        
        logger.info("Generating Root Cause")
        root_cause_text = generate_root_cause(investigation_summary)
        
        # Structure result as plain text fields
        rca_result = {
            'deviation_id': deviation_id,
            'issues': issues_text,
            'major_root_cause_category': major_category_text,
            'near_root_cause': near_cause_text,
            'root_cause': root_cause_text
        }
        
        logger.info("RCA generation completed successfully")
        
        return response(200, "RCA generated successfully", rca_result)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
