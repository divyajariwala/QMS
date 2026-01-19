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

def update_audit_workflow(deviation_id, start_time):
    # add logs in db table
    # successfully generated executive summary

    secret = get_secret(DB_SECRET_NAME, DB_REGION)
    conn = psycopg.connect(
        host=secret["host"],
        port=secret["port"],
        dbname=secret["dbname"],
        user=secret["username"],
        password=secret["password"],
        row_factory=dict_row
    )
    log_deviation_workflow(
        conn,
        deviation_id,
        step=f"GENERATED EXECUTIVE SUMMARY",
        input_data={
            "deviation_id": deviation_id,
            "status": "generated summary"
        },
        output_data={
            "status": "generated summary",
        },
        start_time=start_time
    )
    conn.commit()
    conn.close()


def get_deviation_info(deviation_id: str) -> dict:
    """
    Get deviation information from database
    
    Args:
        deviation_id: The deviation ID (e.g., "DV-00001")
        
    Returns:
        Dict with deviation fields (8 fields):
        - title
        - description
        - immediate_steps_taken
        - quality_risk_evaluation
        - investigation_summary
        - capa_plan
        - recurrence_check_details
        - effectiveness_check_plan
        
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
            # Query to get all 8 required fields
            cur.execute("""
                SELECT 
                    deviation_id,
                    title,
                    description,
                    immediate_steps_taken,
                    quality_risk_evaluation,
                    investigation_summary,
                    capa_plan,
                    recurrence_check_details,
                    effectiveness_check_plan
                FROM deviations
                WHERE deviation_id = %s
            """, (deviation_id,))
            
            result = cur.fetchone()
            
            if not result:
                logger.error(f"Deviation not found: {deviation_id}")
                raise ValueError(f"Deviation {deviation_id} not found in database")
            
            logger.info(f"✅ Successfully fetched deviation info for {deviation_id}")
            
            # Convert to dict and return (handle NULL values)
            deviation_info = {
                'deviation_id': result['deviation_id'],
                'title': result['title'] or '',
                'description': result['description'] or '',
                'immediate_steps_taken': result['immediate_steps_taken'] or '',
                'quality_risk_evaluation': result['quality_risk_evaluation'] or '',
                'investigation_summary': result['investigation_summary'] or '',
                'capa_plan': result['capa_plan'] or '',
                'recurrence_check_details': result['recurrence_check_details'] or '',
                'effectiveness_check_plan': result['effectiveness_check_plan'] or ''
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
                "maxTokens": 4096,
                "temperature": 0
            }
        )

        response_text = response['output']['message']['content'][0]['text']
        logger.info(f"Response received, length: {len(response_text)} chars")

        return response_text.strip()

    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        raise


def generate_executive_summary(deviation_info: dict) -> list:
    """
    Generate executive summary from deviation information
    
    Args:
        deviation_info: Dict with all deviation fields
        
    Returns:
        List of summary sections in format:
        [
            {
                "label": "Title",
                "content": "Deviation: QA Oversight Gap..."
            },
            ...
        ]
    """
    try:
        logger.info("Generating executive summary")
        
        # Load prompt template
        prompt_template = load_prompt('executive_summary.txt')
        
        # Replace placeholders with actual data
        prompt = prompt_template.replace('{{title}}', deviation_info.get('title', ''))
        prompt = prompt.replace('{{description}}', deviation_info.get('description', ''))
        prompt = prompt.replace('{{immediate_steps_taken}}', deviation_info.get('immediate_steps_taken', ''))
        prompt = prompt.replace('{{quality_risk_evaluation}}', deviation_info.get('quality_risk_evaluation', ''))
        prompt = prompt.replace('{{investigation_summary}}', deviation_info.get('investigation_summary', ''))
        prompt = prompt.replace('{{capa_plan}}', deviation_info.get('capa_plan', ''))
        prompt = prompt.replace('{{recurrence_check_details}}', deviation_info.get('recurrence_check_details', ''))
        prompt = prompt.replace('{{effectiveness_check_plan}}', deviation_info.get('effectiveness_check_plan', ''))
        
        # Call Bedrock
        response_text = call_bedrock(prompt)
        
        # Parse JSON response
        result = json.loads(response_text)
        
        # Validate response structure
        if not isinstance(result, list):
            logger.error("Response is not a list")
            raise ValueError("Invalid response format: expected list")
        
        # Validate each section has label and content
        for section in result:
            if 'label' not in section or 'content' not in section:
                logger.error(f"Invalid section format: {section}")
                raise ValueError("Invalid section format: missing label or content")
        
        logger.info(f"✅ Generated executive summary with {len(result)} sections")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
        raise
    except Exception as e:
        logger.error(f"Error generating executive summary: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Lambda handler for POST /generate-executive-summary endpoint

    Fetches deviation information from database and generates executive summary.
    
    Expected request body:
    {
        "deviation_id": "DV-00001"
    }

    Response:
    {
        "success": true,
        "message": "Executive summary generated successfully",
        "data": [
            {
                "label": "Title",
                "content": "Deviation: QA Oversight Gap in Non-Routine Analytical Results Verification"
            },
            {
                "label": "Description",
                "content": "On 01Nov2023 during periodic review..."
            },
            {
                "label": "Immediate Steps Taken",
                "content": "Cleaning representatives were notified..."
            },
            {
                "label": "Quality Risk Evaluation",
                "content": "Preliminary risk assessment indicates..."
            },
            {
                "label": "Investigation Details",
                "content": "It was discovered during the investigation..."
            },
            {
                "label": "CAPA Plan",
                "content": "1) Harmonize approval requirements..."
            },
            {
                "label": "Recurrence Check Details",
                "content": "Retrospective review of the last 12 months..."
            },
            {
                "label": "Effectiveness Check Plan",
                "content": "Effectiveness will be measured by zero recurrences..."
            }
        ]
    }

    Field Descriptions:
    - label: Section name (Title, Description, etc.)
    - content: Executive summary content for that section
    
    Sections Generated (8 total):
    1. Title
    2. Description
    3. Immediate Steps Taken
    4. Quality Risk Evaluation
    5. Investigation Details
    6. CAPA Plan
    7. Recurrence Check Details
    8. Effectiveness Check Plan
    """
    try:
        start_time = datetime.now(timezone.utc)
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

        logger.info(f"Generating executive summary for deviation: {deviation_id}")
        
        # Fetch deviation info from database
        try:
            deviation_info = get_deviation_info(deviation_id)
        except ValueError as e:
            # Deviation not found
            return response(404, str(e))
        except Exception as e:
            # Database error
            logger.error(f"Database error: {str(e)}")
            return response(500, "Error fetching deviation information", {"details": str(e)})
        
        # Log field lengths
        logger.info(f"Fields retrieved: title={len(deviation_info['title'])} chars, "
                   f"description={len(deviation_info['description'])} chars, "
                   f"immediate_steps_taken={len(deviation_info['immediate_steps_taken'])} chars, "
                   f"quality_risk_evaluation={len(deviation_info['quality_risk_evaluation'])} chars, "
                   f"investigation_summary={len(deviation_info['investigation_summary'])} chars, "
                   f"capa_plan={len(deviation_info['capa_plan'])} chars, "
                   f"recurrence_check_details={len(deviation_info['recurrence_check_details'])} chars, "
                   f"effectiveness_check_plan={len(deviation_info['effectiveness_check_plan'])} chars")
        
        # Generate executive summary
        try:
            summary = generate_executive_summary(deviation_info)
            update_audit_workflow(deviation_id, start_time)
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            secret = get_secret(DB_SECRET_NAME, DB_REGION)
            conn = psycopg.connect(
                host=secret["host"],
                port=secret["port"],
                dbname=secret["dbname"],
                user=secret["username"],
                password=secret["password"],
                row_factory=dict_row
            )
            log_deviation_workflow(
                conn,
                deviation_id,
                step="GENERATED EXECUTED SUMMARY FAILED ",
                input_data={
                    "deviation_id": deviation_id,
                },
                output_data={
                    "error": str(e)
                },
                start_time=start_time
            )
            conn.commit()
            conn.close()
            return response(500, "Error generating executive summary", {"details": str(e)})
        
        # Log successful completion
        logger.info(f"✅ Executive summary generated successfully for {deviation_id}")
        logger.info(f"Generated {len(summary)} sections")
        
        return response(200, "Executive summary generated successfully", summary)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
