import json
import boto3
import os
import logging
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timezone
from secrets_util import get_secret
from utils import response, handle_cors_preflight, parse_event_body

try:
    from audit_logger import log_deviation_workflow
except ImportError:
    import sys

    sys.path.append(os.path.dirname(__file__))
    from audit_logger import log_deviation_workflow

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
ENV = os.environ.get('env', 'dev')
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
MODEL_ID = os.environ.get('llm_model_id', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
DB_SECRET_BASE_NAME = os.environ.get(
    "db_secret_base_name", "aurora-postgres-master"
)
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get("db_region", "us-east-1")
# Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)


def get_deviation_info(deviation_id: str) -> dict:
    """
    Get deviation information from database
    
    Args:
        deviation_id: The deviation ID (e.g., "DV-00001")
        
    Returns:
        Dict with deviation fields:
        - investigation_summary
        - description
        - immediate_steps_taken
        - capa_plan
        
    Raises:
        ValueError: If deviation not found
        Exception: If database error occurs
    """
    try:
        logger.info(f"Fetching deviation info for: {deviation_id}")
        
        # Get database connection
        secret = get_secret(DB_SECRET_NAME, DB_REGION)
        conn = psycopg.connect(
            host=secret["host"],
            port=secret["port"],
            dbname=secret["dbname"],
            user=secret["username"],
            password=secret["password"],
            row_factory=dict_row
        )
        
        with conn.cursor() as cur:
            # Query to get the 4 required fields
            cur.execute("""
                SELECT 
                    deviation_id,
                    investigation_summary,
                    description,
                    immediate_steps_taken,
                    capa_plan
                FROM deviations
                WHERE deviation_id = %s
            """, (deviation_id,))
            
            result = cur.fetchone()
            
            if not result:
                logger.error(f"Deviation not found: {deviation_id}")
                raise ValueError(f"Deviation {deviation_id} not found in database")
            
            logger.info(f"✅ Successfully fetched deviation info for {deviation_id}")
            
            # Convert to dict and return
            deviation_info = {
                'deviation_id': result['deviation_id'],
                'investigation_summary': result['investigation_summary'] or '',
                'description': result['description'] or '',
                'immediate_steps_taken': result['immediate_steps_taken'] or '',
                'capa_plan': result['capa_plan'] or ''
            }
            
            return deviation_info
            
    except ValueError:
        # Re-raise ValueError (deviation not found)
        raise
    except Exception as e:
        logger.error(f"Error fetching deviation info: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


# DB CONNECTION
def get_db_connection():
    secret = get_secret(DB_SECRET_NAME, DB_REGION)
    return psycopg.connect(
        host=secret["host"],
        port=secret["port"],
        dbname=secret["dbname"],
        user=secret["username"],
        password=secret["password"],
    )


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


# TODO: Add grading functions here in future iterations
# def grade_investigation_summary(deviation_info: dict) -> dict:
#     """Grade the investigation summary"""
#     pass
#
# def grade_capa_plan(deviation_info: dict) -> dict:
#     """Grade the CAPA plan"""
#     pass


def lambda_handler(event, context):
    """
    Lambda handler for POST /start-grading endpoint

    Fetches deviation information from database and prepares it for grading.
    
    Expected request body:
    {
        "deviation_id": "DV-00001"
    }

    Response:
    {
        "success": true,
        "message": "Deviation information retrieved successfully",
        "data": {
            "deviation_id": "DV-00001",
            "investigation_summary": "Investigation summary text...",
            "description": "Deviation description...",
            "immediate_steps_taken": "Immediate steps text...",
            "capa_plan": "CAPA plan text..."
        }
    }

    Field Descriptions:
    - deviation_id: The deviation identifier
    - investigation_summary: Summary of the investigation conducted
    - description: Description of the deviation
    - immediate_steps_taken: Immediate corrective actions taken
    - capa_plan: Corrective and Preventive Action plan
    """
    try:
        logger.info(f"Environment: {ENV}, Region: {AWS_REGION}")
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()

        # Only support POST method
        if event.get('httpMethod') != 'POST':
            return response(405, "Method not allowed. Use POST.")

        # Parse event body
        body = parse_event_body(event)
        deviation_id = body.get('deviation_id')

        # Validate required fields
        if not deviation_id:
            return response(400, "deviation_id is required")

        if not isinstance(deviation_id, str):
            return response(400, "deviation_id must be a string")

        if not deviation_id.strip():
            return response(400, "deviation_id cannot be empty")

        logger.info(f"Starting grading process for deviation: {deviation_id}")
        
        # Get deviation information from database
        try:
            deviation_info = get_deviation_info(deviation_id)
        except ValueError as e:
            # Deviation not found
            return response(404, str(e))
        except Exception as e:
            # Database error
            logger.error(f"Database error: {str(e)}")
            return response(500, "Error fetching deviation information", {"details": str(e)})
        
        # Log successful retrieval
        logger.info(f"✅ Deviation info retrieved successfully for {deviation_id}")
        logger.info(f"Fields retrieved: investigation_summary={len(deviation_info['investigation_summary'])} chars, "
                   f"description={len(deviation_info['description'])} chars, "
                   f"immediate_steps_taken={len(deviation_info['immediate_steps_taken'])} chars, "
                   f"capa_plan={len(deviation_info['capa_plan'])} chars")
        
        # TODO: Add grading logic here in future iterations
        # For now, just return the deviation information
        
        return response(200, "Deviation information retrieved successfully", deviation_info)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
