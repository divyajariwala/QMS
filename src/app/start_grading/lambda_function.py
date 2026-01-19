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
3. Be concise and specific
4. Use action-oriented language
5. Avoid vague terms like "issue" or "problem"
6. Ensure the title is descriptive enough to understand the deviation at a glance
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


def save_grading_results(deviation_id: str, grading_results: list, is_regeneration: bool = False) -> None:
    """
    Save or update grading results in deviation_grading_executive table
    
    Args:
        deviation_id: The deviation ID (e.g., "DV-00001")
        grading_results: List of grading results from grade_all_sections()
        is_regeneration: True if this is a regeneration (update), False if initial (insert)
        
    Table structure:
        - deviation_id (PK)
        - title (text)
        - overview (text)
        - immediate_actions (text)
        - quality_risk_evaluation (text)
        - investigation_summary (text)
        - capa_plan (text)
        - recurrence_check (text)
        - effectiveness_check (text)
        - isedited (boolean, default false)
        - updated_date (timestamp, default CURRENT_TIMESTAMP)
    """
    try:
        logger.info(f"Saving grading results for {deviation_id} (regeneration={is_regeneration})")
        
        # Map section_label to database column names
        section_to_column = {
            "Title": "title",
            "Description": "overview",
            "Immediate Steps Taken": "immediate_actions",
            "Quality Risk Evaluation": "quality_risk_evaluation",
            "Investigation Details": "investigation_summary",
            "CAPA Plan": "capa_plan",
            "Recurrence Check Details": "recurrence_check",
            "Effectiveness Check Plan": "effectiveness_check"
        }
        
        # Build data dict for database
        data = {}
        for result in grading_results:
            section_label = result.get('section_label')
            improvement_suggestion = result.get('improvement_suggestion', '')
            
            if section_label in section_to_column:
                column_name = section_to_column[section_label]
                data[column_name] = improvement_suggestion
        
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
            if is_regeneration:
                # UPDATE existing record
                logger.info(f"Updating existing grading record for {deviation_id}")
                
                cur.execute("""
                    UPDATE deviation_grading_executive
                    SET 
                        title = %s,
                        overview = %s,
                        immediate_actions = %s,
                        quality_risk_evaluation = %s,
                        investigation_summary = %s,
                        capa_plan = %s,
                        recurrence_check = %s,
                        effectiveness_check = %s,
                        isedited = true,
                        updated_date = CURRENT_TIMESTAMP
                    WHERE deviation_id = %s
                """, (
                    data.get('title', ''),
                    data.get('overview', ''),
                    data.get('immediate_actions', ''),
                    data.get('quality_risk_evaluation', ''),
                    data.get('investigation_summary', ''),
                    data.get('capa_plan', ''),
                    data.get('recurrence_check', ''),
                    data.get('effectiveness_check', ''),
                    deviation_id
                ))
                
                if cur.rowcount == 0:
                    logger.warning(f"No existing record found for {deviation_id}, inserting new record")
                    # If no record was updated, insert instead
                    cur.execute("""
                        INSERT INTO deviation_grading_executive (
                            deviation_id,
                            title,
                            overview,
                            immediate_actions,
                            quality_risk_evaluation,
                            investigation_summary,
                            capa_plan,
                            recurrence_check,
                            effectiveness_check,
                            isedited,
                            updated_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """, (
                        deviation_id,
                        data.get('title', ''),
                        data.get('overview', ''),
                        data.get('immediate_actions', ''),
                        data.get('quality_risk_evaluation', ''),
                        data.get('investigation_summary', ''),
                        data.get('capa_plan', ''),
                        data.get('recurrence_check', ''),
                        data.get('effectiveness_check', ''),
                        True
                    ))
                    logger.info(f"✅ Inserted new grading record for {deviation_id}")
                else:
                    logger.info(f"✅ Updated grading record for {deviation_id}")
            else:
                # INSERT new record (initial grading)
                logger.info(f"Inserting new grading record for {deviation_id}")
                
                # Check if record already exists
                cur.execute("""
                    SELECT deviation_id FROM deviation_grading_executive
                    WHERE deviation_id = %s
                """, (deviation_id,))
                
                existing = cur.fetchone()
                
                if existing:
                    # Record exists, update instead
                    logger.warning(f"Record already exists for {deviation_id}, updating instead")
                    cur.execute("""
                        UPDATE deviation_grading_executive
                        SET 
                            title = %s,
                            overview = %s,
                            immediate_actions = %s,
                            quality_risk_evaluation = %s,
                            investigation_summary = %s,
                            capa_plan = %s,
                            recurrence_check = %s,
                            effectiveness_check = %s,
                            isedited = false,
                            updated_date = CURRENT_TIMESTAMP
                        WHERE deviation_id = %s
                    """, (
                        data.get('title', ''),
                        data.get('overview', ''),
                        data.get('immediate_actions', ''),
                        data.get('quality_risk_evaluation', ''),
                        data.get('investigation_summary', ''),
                        data.get('capa_plan', ''),
                        data.get('recurrence_check', ''),
                        data.get('effectiveness_check', ''),
                        deviation_id
                    ))
                    logger.info(f"✅ Updated existing grading record for {deviation_id}")
                else:
                    # Insert new record
                    cur.execute("""
                        INSERT INTO deviation_grading_executive (
                            deviation_id,
                            title,
                            overview,
                            immediate_actions,
                            quality_risk_evaluation,
                            investigation_summary,
                            capa_plan,
                            recurrence_check,
                            effectiveness_check,
                            isedited,
                            updated_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """, (
                        deviation_id,
                        data.get('title', ''),
                        data.get('overview', ''),
                        data.get('immediate_actions', ''),
                        data.get('quality_risk_evaluation', ''),
                        data.get('investigation_summary', ''),
                        data.get('capa_plan', ''),
                        data.get('recurrence_check', ''),
                        data.get('effectiveness_check', ''),
                        False
                    ))
                    logger.info(f"✅ Inserted new grading record for {deviation_id}")
            
            # Commit transaction
            conn.commit()
            logger.info(f"✅ Successfully saved grading results for {deviation_id}")
            
    except Exception as e:
        logger.error(f"Error saving grading results: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'conn' in locals():
            conn.close()


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
    Supports regeneration with existing results.
    
    Expected request body:
    {
        "deviation_id": "DV-00001",
        "existing_results": [  // Optional: for regeneration
            {
                "section_label": "Title",
                "text": "...",
                "improvement_suggestion": "...",
                "score": 7
            },
            ...
        ]
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
    
    Regeneration:
    - If existing_results is provided, the system will regenerate the grading
    - Useful for improving specific sections or regenerating all sections
    - The text field from existing_results is used as the content to grade
    """
    deviation_id = None  # Initialize to avoid UnboundLocalError in exception handler
    try:
        logger.info(f"Environment: {ENV}, Region: {AWS_REGION}")
        logger.info(f"Received event: {json.dumps(event)}")
        workflow_start_time = datetime.now(timezone.utc)
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()

        # Only support POST method
        if event.get('httpMethod') != 'POST':
            return response(405, "Method not allowed. Use POST.")

        # Parse event body
        body = parse_event_body(event)
        deviation_id = body.get('deviation_id')
        existing_results = body.get('existing_results')  # Optional for regeneration

        # Validate required fields
        if not deviation_id:
            return response(400, "deviation_id is required")

        if not isinstance(deviation_id, str):
            return response(400, "deviation_id must be a string")

        if not deviation_id.strip():
            return response(400, "deviation_id cannot be empty")

        # Validate existing_results if provided
        if existing_results is not None:
            if not isinstance(existing_results, list):
                return response(400, "existing_results must be an array")
            logger.info(f"Regeneration mode: {len(existing_results)} existing results provided")

        logger.info(f"Starting grading process for deviation: {deviation_id}")
        conn = get_db_connection()
        log_deviation_workflow(
            conn,
            deviation_id,
            step="GRADING_STARTED",
            input_data={
                "Status": "Grading Started",
                "mode": "regeneration" if existing_results else "initial"
            },
            output_data={"status": "started"},
            start_time=workflow_start_time
        )
        conn.commit()
        conn.close()
        start_time = datetime.now(timezone.utc)
        # Determine if this is a regeneration or initial grading
        if existing_results:
            # Regeneration mode: use existing_results
            logger.info("Using existing_results for regeneration")
            
            # Convert existing_results to deviation_info format
            deviation_info = {
                'deviation_id': deviation_id
            }
            
            # Map existing results to deviation_info fields
            section_mapping = {
                "Title": "title",
                "Description": "description",
                "Immediate Steps Taken": "immediate_steps_taken",
                "Quality Risk Evaluation": "quality_risk_evaluation",
                "Investigation Details": "investigation_summary",
                "CAPA Plan": "capa_plan",
                "Recurrence Check Details": "recurrence_check_details",
                "Effectiveness Check Plan": "effectiveness_check_plan"
            }
            
            for result in existing_results:
                section_label = result.get('section_label')
                text = result.get('text', '')
                
                if section_label in section_mapping:
                    field_name = section_mapping[section_label]
                    deviation_info[field_name] = text
            
            # Fill missing fields with empty strings
            for field_name in section_mapping.values():
                if field_name not in deviation_info:
                    deviation_info[field_name] = ''
            
            logger.info("Deviation info constructed from existing_results")
            
        else:
            # Initial grading mode: get from database
            logger.info("Fetching deviation info from database")
            
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
        
        # Save grading results to database
        try:
            is_regeneration = existing_results is not None
            save_grading_results(deviation_id, grading_results, is_regeneration)
        except Exception as e:
            logger.error(f"Error saving grading results: {str(e)}")
            # Don't fail the request if saving fails, just log the error
            logger.warning("Grading completed but failed to save to database")
        # Log successful completion
        mode = "regenerated" if existing_results else "completed"
        conn = get_db_connection()
        log_deviation_workflow(
            conn,
            deviation_id,
            step=f"GRADING_{mode.upper()}",
            input_data={
                "deviation_id": deviation_id,
                "sections_graded": len(grading_results)
            },
            output_data={
                "status": mode,
            },
            start_time=start_time
        )
        conn.commit()
        conn.close()
        logger.info(f"✅ Grading {mode} successfully for {deviation_id}")
        logger.info(f"Graded {len(grading_results)} sections")
        
        # Log scores summary
        scores = [r['score'] for r in grading_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        logger.info(f"Scores: {scores}, Average: {avg_score:.1f}")
        
        message = f"Grading {mode} successfully" if existing_results else "Grading completed successfully"
        return response(200, message, grading_results)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        
        # Only log to database if we have a deviation_id
        if deviation_id:
            conn = get_db_connection()
            log_deviation_workflow(
                conn,
                deviation_id,
                step="GRADING_FAILED",
                input_data={
                    "deviation_id": deviation_id,
                },
                output_data={
                    "error": str(e)
                },
                start_time=workflow_start_time
            )
            conn.commit()
        
        return response(500, "Internal server error", {"details": str(e)})
