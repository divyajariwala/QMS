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
            # Query to get all 8 required fields for grading
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


def get_section_requirements(section_label: str) -> str:
    """
    Get requirements for a specific section
    
    Args:
        section_label: Name of the section (e.g., "Title", "Description")
        
    Returns:
        Requirements text for that section
    """
    requirements = {
        "Title": """
1. Clearly state the type of deviation (e.g., "Deviation", "Non-conformance")
2. Include the affected system, process, or product
3. Be concise (ideally under 100 characters)
4. Use action-oriented language
5. Avoid vague terms like "issue" or "problem"
Example: "Deviation ABC - QA Verification Gap in Batch Release Process"
        """,
        
        "Description": """
1. Provide clear context of what happened
2. Explain the specific gap or issue identified
3. State when and where the deviation occurred
4. Identify who discovered the deviation
5. Use clear, professional language
6. Avoid overly technical jargon without explanation
7. Keep sentences concise and well-structured
        """,
        
        "Immediate Steps Taken": """
1. List all immediate containment actions taken
2. Specify who was notified and when
3. Describe any temporary controls implemented
4. Present actions in chronological order
5. Use bullet points or numbered lists for clarity
6. Include verification that actions were effective
7. Maintain consistent verb tense throughout
        """,
        
        "Quality Risk Evaluation": """
1. Identify potential impact pathways (e.g., data integrity, compliance, patient safety)
2. Assess severity of potential consequences
3. Evaluate detectability of the issue
4. Consider regulatory implications
5. Reference risk assessment methodology if applicable
6. Provide clear rationale for risk level assigned
7. Include both immediate and long-term risks
        """,
        
        "Investigation Details": """
1. Provide detailed timeline of events
2. Identify all personnel involved and their roles
3. List evidence collected (documents, records, interviews)
4. Describe investigation methodology used
5. Present findings in logical sequence
6. Include root cause analysis results
7. Reference specific procedures or documents
8. Ensure traceability of all information
        """,
        
        "CAPA Plan": """
1. List specific corrective actions to address immediate issue
2. List preventive actions to prevent recurrence
3. Assign clear ownership for each action
4. Set realistic target completion dates
5. Define measurable success criteria
6. Link each action to identified root cause
7. Include verification and validation steps
8. Specify resources required
        """,
        
        "Recurrence Check Details": """
1. Define scope of retrospective review
2. Specify time period to be reviewed
3. Identify sample size and selection criteria
4. Set clear acceptance criteria
5. Describe methodology for review
6. Define escalation process if issues found
7. Assign responsibility for conducting review
8. Set timeline for completion
        """,
        
        "Effectiveness Check Plan": """
1. Define what constitutes effective CAPA implementation
2. Specify data sources for verification
3. Set timeline for effectiveness checks
4. Identify audit checkpoints
5. Define metrics to measure success
6. Establish criteria for recurrence
7. Include contingency actions if effectiveness not met
8. Assign responsibility for monitoring
        """
    }
    
    return requirements.get(section_label, "No specific requirements defined for this section.")


def grade_single_section(section_label: str, content: str, requirements: str) -> dict:
    """
    Grade a single section using field_grading.txt prompt
    
    Args:
        section_label: Name of the section (e.g., "Title", "Description")
        content: Content of the section to grade
        requirements: Requirements for this section
        
    Returns:
        Dict in UI format:
        {
            "section_label": "Title",
            "text": "Original content from database",
            "improvement_suggestion": "AI-generated improvement suggestion",
            "score": 7
        }
    """
    try:
        logger.info(f"Grading section: {section_label}")
        
        # Load prompt template
        prompt_template = load_prompt('field_grading.txt')
        
        # Replace placeholders
        prompt = prompt_template.replace('{{field_name}}', section_label)
        prompt = prompt.replace('{{field}}', content)
        prompt = prompt.replace('{{req}}', requirements)
        
        # Call Bedrock
        response_text = call_bedrock(prompt)
        
        # Parse JSON response
        result = json.loads(response_text)
        
        # Transform to UI format (snake_case)
        ui_result = {
            "section_label": section_label,
            "text": content,  # Original content from database
            "improvement_suggestion": result.get('grade_explanation', ''),  # AI suggestion
            "score": int(result.get('grade', 0))
        }
        
        logger.info(f"✅ Graded {section_label}: score={ui_result['score']}")
        return ui_result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON for {section_label}: {str(e)}")
        logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
        # Return default if parsing fails
        return {
            "section_label": section_label,
            "text": content,
            "improvement_suggestion": "Unable to parse grading response for this section.",
            "score": 0
        }
    except Exception as e:
        logger.error(f"Error grading section {section_label}: {str(e)}")
        # Return default if grading fails
        return {
            "section_label": section_label,
            "text": content,
            "improvement_suggestion": "Unable to grade this section due to an error.",
            "score": 0
        }


def grade_all_sections(deviation_info: dict) -> list:
    """
    Grade all sections of the deviation report
    
    Args:
        deviation_info: Dict with all deviation fields
        
    Returns:
        List of grading results in UI format:
        [
            {
                "section_label": "Title",
                "text": "Original content from database",
                "improvement_suggestion": "AI-generated suggestion",
                "score": 7
            },
            ...
        ]
    """
    try:
        logger.info("Starting grading of all sections")
        
        # Define sections to grade (8 sections)
        sections_to_grade = [
            ("Title", deviation_info.get('title', '')),
            ("Description", deviation_info.get('description', '')),
            ("Immediate Steps Taken", deviation_info.get('immediate_steps_taken', '')),
            ("Quality Risk Evaluation", deviation_info.get('quality_risk_evaluation', '')),
            ("Investigation Details", deviation_info.get('investigation_summary', '')),
            ("CAPA Plan", deviation_info.get('capa_plan', '')),
            ("Recurrence Check Details", deviation_info.get('recurrence_check_details', '')),
            ("Effectiveness Check Plan", deviation_info.get('effectiveness_check_plan', ''))
        ]
        
        grading_results = []
        
        # Grade each section
        for section_label, content in sections_to_grade:
            logger.info(f"Processing section: {section_label}")
            
            # Skip if content is empty
            if not content or content.strip() == '':
                logger.warning(f"Section {section_label} is empty, assigning score 0")
                grading_results.append({
                    "section_label": section_label,
                    "text": "",
                    "improvement_suggestion": "This section is empty and needs to be completed.",
                    "score": 0
                })
                continue
            
            # Get requirements for this section
            requirements = get_section_requirements(section_label)
            
            # Grade the section
            result = grade_single_section(section_label, content, requirements)
            grading_results.append(result)
        
        logger.info(f"✅ Completed grading of {len(grading_results)} sections")
        return grading_results
        
    except Exception as e:
        logger.error(f"Error grading all sections: {str(e)}")
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

    Fetches deviation information from database and grades all sections.
    
    Expected request body:
    {
        "deviation_id": "DV-00001"
    }

    Response:
    {
        "success": true,
        "message": "Grading completed successfully",
        "data": [
            {
                "section_label": "Title",
                "text": "Original content from database",
                "improvement_suggestion": "AI-generated improvement suggestion",
                "score": 7
            },
            {
                "section_label": "Description",
                "text": "Original content from database",
                "improvement_suggestion": "AI-generated improvement suggestion",
                "score": 5
            },
            ...
        ]
    }

    Field Descriptions:
    - section_label: Name of the section being graded
    - text: Original content from the database
    - improvement_suggestion: AI-generated improvement suggestion
    - score: Grade from 1-10 (1=worst, 10=best)
    
    Sections Graded (8 total):
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
        
        # Log field lengths
        logger.info(f"Fields retrieved: title={len(deviation_info['title'])} chars, "
                   f"description={len(deviation_info['description'])} chars, "
                   f"immediate_steps_taken={len(deviation_info['immediate_steps_taken'])} chars, "
                   f"quality_risk_evaluation={len(deviation_info['quality_risk_evaluation'])} chars, "
                   f"investigation_summary={len(deviation_info['investigation_summary'])} chars, "
                   f"capa_plan={len(deviation_info['capa_plan'])} chars, "
                   f"recurrence_check_details={len(deviation_info['recurrence_check_details'])} chars, "
                   f"effectiveness_check_plan={len(deviation_info['effectiveness_check_plan'])} chars")
        
        # Grade all sections
        try:
            grading_results = grade_all_sections(deviation_info)
        except Exception as e:
            logger.error(f"Grading error: {str(e)}")
            return response(500, "Error grading deviation sections", {"details": str(e)})
        
        # Log successful completion
        logger.info(f"✅ Grading completed successfully for {deviation_id}")
        logger.info(f"Graded {len(grading_results)} sections")
        
        # Log scores summary
        scores = [r['score'] for r in grading_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        logger.info(f"Scores: {scores}, Average: {avg_score:.1f}")
        
        return response(200, "Grading completed successfully", grading_results)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
