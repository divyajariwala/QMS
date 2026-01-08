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


def generate_multiple_rcas(investigation_summary: str) -> list:
    """
    Generates multiple RCAs in a single AI call

    Returns:
        List of RCA dictionaries, each containing:
        - problem_category_validated
        - major_root_cause_category_validated
        - near_root_cause
        - root_cause
    """
    try:
        prompt_template = load_prompt('generate_multiple_rcas_prompt.txt')
        prompt = prompt_template.format(investigation_summary=investigation_summary)

        logger.info("Generating multiple RCAs in single call")

        # Call Bedrock and parse JSON response
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 4096,
                "temperature": 0
            }
        )

        response_text = response['output']['message']['content'][0]['text']
        logger.info(f"Multiple RCAs response received, length: {len(response_text)} chars")

        # Parse JSON response
        rcas = json.loads(response_text)

        if not isinstance(rcas, list):
            logger.error("Response is not a list, wrapping in array")
            rcas = [rcas]

        # Validate minimum 2 RCAs requirement
        if len(rcas) < 2:
            logger.warning(f"Only {len(rcas)} RCA(s) generated, minimum is 2. Falling back to sequential generation.")
            return generate_rcas_sequential(investigation_summary)

        logger.info(f"Successfully generated {len(rcas)} RCA(s)")
        return rcas

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse RCAs JSON: {str(e)}")
        logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
        # Fallback: try to generate single RCA using old method
        logger.info("Falling back to sequential generation")
        return generate_rcas_sequential(investigation_summary)
    except Exception as e:
        logger.error(f"Error generating multiple RCAs: {str(e)}")
        # Fallback: try to generate single RCA using old method
        logger.info("Falling back to sequential generation")
        return generate_rcas_sequential(investigation_summary)


def generate_rcas_sequential(investigation_summary: str) -> list:
    """
    Fallback method: Generate 2 RCAs using sequential AI calls (old method)
    Returns a list with 2 RCAs from different perspectives

    RCA 1: Immediate/Direct Cause
    RCA 2: Systemic/Organizational Cause
    """
    try:
        logger.info("Using sequential generation (fallback) - generating 2 RCAs")

        # Generate RCA 1: Immediate Cause
        problem_category_text_1 = generate_problem_category(investigation_summary)
        major_category_text_1 = generate_major_root_cause_category(investigation_summary)
        near_cause_text_1 = generate_near_root_cause(investigation_summary)
        root_cause_text_1 = generate_root_cause(investigation_summary)

        rca_1 = {
            'problem_category_validated': problem_category_text_1,
            'major_root_cause_category_validated': major_category_text_1,
            'near_root_cause': near_cause_text_1,
            'root_cause': root_cause_text_1
        }

        # Generate RCA 2: Systemic Perspective
        # Modify the investigation summary to ask for systemic/organizational perspective
        systemic_prompt = f"""
        Based on this investigation summary, identify the SYSTEMIC or ORGANIZATIONAL root cause 
        (not the immediate cause, but the underlying system/process/organizational failure that allowed this to happen):
        
        {investigation_summary}
        """
        
        problem_category_text_2 = generate_problem_category(systemic_prompt)
        major_category_text_2 = generate_major_root_cause_category(systemic_prompt)
        near_cause_text_2 = generate_near_root_cause(systemic_prompt)
        root_cause_text_2 = generate_root_cause(systemic_prompt)

        rca_2 = {
            'problem_category_validated': problem_category_text_2,
            'major_root_cause_category_validated': major_category_text_2,
            'near_root_cause': near_cause_text_2,
            'root_cause': root_cause_text_2
        }

        logger.info("Successfully generated 2 RCAs (immediate + systemic)")
        return [rca_1, rca_2]

    except Exception as e:
        logger.error(f"Error in sequential generation: {str(e)}")
        raise


def generate_problem_category(investigation_summary: str) -> str:
    """
    Generates the Problem Category section of the RCA
    
    Returns:
        Plain text description of problem category (causal factors)
    """
    try:
        prompt_template = load_prompt('problem_category_prompt_v2.txt')
        prompt = prompt_template.format(investigation_summary=investigation_summary)

        result = call_bedrock(prompt)
        logger.info("Successfully generated Problem Category section")
        return result

    except Exception as e:
        logger.error(f"Error generating Problem Category: {str(e)}")
        raise


def generate_major_root_cause_category(investigation_summary: str) -> str:
    """
    Generates the major root cause category

    Returns:
        Plain text category name
    """
    try:
        prompt_template = load_prompt('major_root_cause_category_prompt_v2.txt')
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
        prompt_template = load_prompt('near_root_cause_prompt_v2.txt')
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
        prompt_template = load_prompt('root_cause_prompt_v2.txt')
        prompt = prompt_template.format(investigation_summary=investigation_summary)

        result = call_bedrock(prompt)
        logger.info("Successfully generated Root Cause")
        return result

    except Exception as e:
        logger.error(f"Error generating Root Cause: {str(e)}")
        raise


def categorize_rca(investigation_summary: str, problem_category_text: str, major_category_text: str,
                   near_cause_text: str, root_cause_text: str) -> dict:
    """
    Categorizes the RCA analysis into specific ABS taxonomy categories

    Args:
        investigation_summary: Original investigation summary
        problem_category_text: Generated problem category text
        major_category_text: Generated major category text
        near_cause_text: Generated near cause text
        root_cause_text: Generated root cause text

    Returns:
        Dict with category assignments for each section
    """
    try:
        prompt_template = load_prompt('categorize_rca_prompt.txt')
        prompt = prompt_template.format(
            investigation_summary=investigation_summary,
            problem_category_text=problem_category_text,
            major_category_text=major_category_text,
            near_cause_text=near_cause_text,
            root_cause_text=root_cause_text
        )

        logger.info("Categorizing RCA analysis")

        # Call Bedrock and parse JSON response
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 1024,
                "temperature": 0
            }
        )

        response_text = response['output']['message']['content'][0]['text']
        logger.info(f"Categorization response: {response_text[:200]}...")

        # Parse JSON response
        categories = json.loads(response_text)
        logger.info(f"Successfully categorized RCA: {categories}")

        return categories

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse categorization JSON: {str(e)}")
        logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
        # Return default categories if parsing fails
        return {
            "problem_category": "Other",
            "major_root_cause_category": major_category_text,
            "near_root_cause_category": "Other",
            "root_cause_category": "Other"
        }
    except Exception as e:
        logger.error(f"Error categorizing RCA: {str(e)}")
        # Return default categories if categorization fails
        return {
            "problem_category": "Other",
            "major_root_cause_category": major_category_text,
            "near_root_cause_category": "Other",
            "root_cause_category": "Other"
        }


def lambda_handler(event, context):
    """
    Lambda handler for POST /generateRCA endpoint

    Generates RCA analysis using AI based on investigation summary.
    ALWAYS generates a MINIMUM of 2 RCAs to ensure comprehensive analysis from multiple perspectives.

    Expected request body:
    {
        "investigation_summary": "Investigation summary text...",
        "deviation_id": "DV-00001"  (optional, for reference)
    }

    Response (minimum 2 RCAs):
    {
        "success": true,
        "message": "2 RCA(s) generated successfully",
        "data": [
            {
                "deviation_id": "DV-00001",
                "problem_category": "Company Personnel Issue",
                "problem_category_validated": "Generated problem category text (60-65 words)...",
                "major_root_cause_category": "Personnel Issues",
                "major_root_cause_category_validated": "Long explanation text about the major root cause category (60-65 words)...",
                "near_root_cause": "Generated near root cause text (60-65 words)...",
                "near_root_cause_category": "Training/Personnel Qualification Issue",
                "root_cause": "Generated root cause text (60-65 words)...",
                "root_cause_category": "Training Not Performed",
                "is_ai_generated": true
            },
            {
                "deviation_id": "DV-00001",
                "problem_category": "Process/Manufacturing Equipment Issue",
                "problem_category_validated": "Second perspective problem category (60-65 words)...",
                "major_root_cause_category": "Equipment/Software Issues",
                "major_root_cause_category_validated": "Systemic explanation from different perspective (60-65 words)...",
                "near_root_cause": "Second perspective near cause (60-65 words)...",
                "near_root_cause_category": "Equipment Reliability Program Issue",
                "root_cause": "Second perspective root cause (60-65 words)...",
                "root_cause_category": "Preventive/Predictive Maintenance Issue",
                "is_ai_generated": true
            }
        ]
    }

    Field Descriptions:
    - problem_category: Auto-selected category name from official ABS map (e.g., "Company Personnel Issue")
    - problem_category_validated: AI-generated explanation text (60-65 words)
    - major_root_cause_category: Auto-selected category name from taxonomy (e.g., "Personnel Issues")
    - major_root_cause_category_validated: AI-generated explanation text (60-65 words)
    - near_root_cause: AI-generated explanation text (60-65 words)
    - near_root_cause_category: Auto-selected category name (e.g., "Training/Personnel Qualification Issue")
    - root_cause: AI-generated explanation text (60-65 words)
    - root_cause_category: Auto-selected category name (e.g., "Training Not Performed")
    - is_ai_generated: Boolean flag indicating this RCA was generated by AI (always true for this endpoint)

    Note: The response data is always an array with a MINIMUM of 2 RCAs.
    """
    try:
        logger.info(f"Environment: {ENV}, Region: {AWS_REGION}, Model: {MODEL_ID}")
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()

        # Only support POST method
        if event.get('httpMethod') != 'POST':
            return response(405, "Method not allowed. Use POST.")

        # Parse event body
        body = parse_event_body(event)
        investigation_summary = body.get('investigation_summary')
        deviation_id = body.get('deviation_id')

        # Validate required fields
        if not investigation_summary:
            return response(400, "investigation_summary is required")

        if not isinstance(investigation_summary, str):
            return response(400, "investigation_summary must be a string")

        if not investigation_summary.strip():
            return response(400, "investigation_summary cannot be empty")
        conn = get_db_connection()

        logger.info("Starting RCA generation process")
        start_time = datetime.now(timezone.utc)
        # Generate multiple RCAs in a single AI call
        logger.info("Generating multiple RCAs")
        try:
            rcas_list = generate_multiple_rcas(investigation_summary)

            log_deviation_workflow(
                conn=conn,
                entity_id=deviation_id,
                step="RCA_GENERATED",
                input_data={
                    "summary_length": len(investigation_summary),
                    "model": MODEL_ID
                },
                output_data={
                    "rca_count": len(rcas_list),
                    "is_ai_generated": True
                },
                start_time=start_time,
            )
        except Exception as e:
            logger.error(f"RCA_GENERATION_FAILED: {str(e)}")
            log_deviation_workflow(
                conn=conn,
                entity_id=deviation_id,
                step="RCA_GENERATION_FAILED",
                input_data={
                    "summary_length": len(investigation_summary),
                    "model": MODEL_ID
                },
                output_data={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                start_time=start_time,
            )

        conn.commit()
        # Categorize each RCA
        logger.info(f"Categorizing {len(rcas_list)} RCA(s)")
        result_rcas = []
        failed_indices = []
        categorization_failed = False
        for idx, rca in enumerate(rcas_list):
            logger.info(f"Categorizing RCA {idx + 1}/{len(rcas_list)}")
            try:
                categories = categorize_rca(
                    investigation_summary=investigation_summary,
                    problem_category_text=rca['problem_category_validated'],
                    major_category_text=rca['major_root_cause_category_validated'],
                    near_cause_text=rca['near_root_cause'],
                    root_cause_text=rca['root_cause']
                )
            except Exception as e:
                categorization_failed = True
                failed_indices.append(idx)
                logger.error(
                    f"RCA_CATEGORIZATION_FAILED deviation_id={deviation_id}, index={idx}, error={str(e)}"
                )

            # Structure result with generated text and auto-selected categories
            rca_result = {
                'problem_category': categories.get('problem_category', 'Other'),
                'problem_category_validated': rca['problem_category_validated'],
                'major_root_cause_category': categories.get('major_root_cause_category', 'Other'),
                'major_root_cause_category_validated': rca['major_root_cause_category_validated'],
                'near_root_cause_category': categories.get('near_root_cause_category', 'Other'),
                'near_root_cause': rca['near_root_cause'],
                'root_cause_category': categories.get('root_cause_category', 'Other'),
                'root_cause': rca['root_cause'],
                'is_ai_generated': True  # Flag to indicate this RCA was generated by AI
            }

            # Include deviation_id if provided
            if deviation_id:
                rca_result['deviation_id'] = deviation_id

            result_rcas.append(rca_result)
        # ================= WORKFLOW STATUS =================
        if categorization_failed:
            log_deviation_workflow(
                conn,
                deviation_id,
                "RCA_CATEGORIZATION_FAILED",
                {"total_rcas": len(result_rcas)},
                {
                    "failed_indices": failed_indices,
                    "fallback_used": True
                },
                start_time
            )
        else:
            log_deviation_workflow(
                conn,
                deviation_id,
                "RCA_CATEGORIZATION_COMPLETED",
                {"total_rcas": len(result_rcas)},
                {"categorized": True},
                start_time
            )

        conn.commit()
        logger.info(f"✅ RCA generation completed successfully: {len(result_rcas)} RCA(s) generated")
        return response(200, f"{len(result_rcas)} RCA(s) generated successfully", result_rcas)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
    finally:
        if conn:
            conn.close()
