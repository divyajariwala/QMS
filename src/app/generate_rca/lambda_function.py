import json
import boto3
import os
import logging
import psycopg
from utils import response, handle_cors_preflight, parse_event_body
from secrets_util import get_db_credentials

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


def get_rca_from_database(deviation_id: str):
    """
    Retrieve existing RCA analysis from the database.
    
    Args:
        deviation_id: The deviation ID
        
    Returns:
        Dict with RCA data or None if not found
    """
    if not DB_SECRET_NAME:
        logger.warning("DB_SECRET_NAME not set, skipping database fetch")
        return None
    
    logger.info(f"Fetching RCA for deviation: {deviation_id}")
    
    try:
        # Get database credentials from Secrets Manager
        db_creds = get_db_credentials(DB_SECRET_NAME, AWS_REGION)
        
        # Build connection string
        conn_string = (
            f"host={db_creds['host']} "
            f"port={db_creds.get('port', 5432)} "
            f"dbname={db_creds['dbname']} "
            f"user={db_creds['username']} "
            f"password={db_creds['password']} "
            f"sslmode=require"
        )
        
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id,
                        deviation_id,
                        issues,
                        issues_category,
                        major_root_cause_category,
                        near_root_cause,
                        near_root_cause_category,
                        root_cause,
                        root_cause_category,
                        created_at,
                        updated_at,
                        created_by
                    FROM rca_analysis
                    WHERE deviation_id = %s
                """, (deviation_id,))
                
                row = cur.fetchone()
                
                if not row:
                    logger.info(f"No RCA found for deviation: {deviation_id}")
                    return None
                
                rca_data = {
                    'rca_id': row[0],
                    'deviation_id': row[1],
                    'issues': row[2],
                    'issues_category': row[3],
                    'major_root_cause_category': row[4],
                    'near_root_cause': row[5],
                    'near_root_cause_category': row[6],
                    'root_cause': row[7],
                    'root_cause_category': row[8],
                    'created_at': row[9].isoformat() if row[9] else None,
                    'updated_at': row[10].isoformat() if row[10] else None,
                    'created_by': row[11]
                }
                
                logger.info(f"✅ Found RCA with id: {rca_data['rca_id']}")
                return rca_data
                
    except Exception as e:
        logger.error(f"❌ Error fetching RCA from database: {str(e)}")
        raise


def save_rca_to_database(deviation_id: str, issues: str, issues_category: str,
                         major_category: str, near_cause: str, near_cause_category: str,
                         root_cause: str, root_cause_category: str, created_by: str = 'system'):
    """
    Save or update RCA analysis in the database.
    
    Args:
        deviation_id: The deviation ID
        issues: Issues text
        issues_category: Issues dropdown category
        major_category: Major root cause category text
        near_cause: Near root cause text
        near_cause_category: Near root cause dropdown category
        root_cause: Root cause text
        root_cause_category: Root cause dropdown category
        created_by: User who triggered the RCA generation
        
    Returns:
        RCA ID if successful
    """
    if not DB_SECRET_NAME:
        logger.warning("DB_SECRET_NAME not set, skipping database save")
        return None
    
    logger.info(f"Saving RCA for deviation: {deviation_id}")
    
    try:
        # Get database credentials from Secrets Manager
        db_creds = get_db_credentials(DB_SECRET_NAME, AWS_REGION)
        
        # Build connection string
        conn_string = (
            f"host={db_creds['host']} "
            f"port={db_creds.get('port', 5432)} "
            f"dbname={db_creds['dbname']} "
            f"user={db_creds['username']} "
            f"password={db_creds['password']} "
            f"sslmode=require"
        )
        
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Use INSERT ... ON CONFLICT to handle both insert and update
                cur.execute("""
                    INSERT INTO rca_analysis (
                        deviation_id,
                        issues,
                        issues_category,
                        major_root_cause_category,
                        major_root_cause_category_explanation,
                        near_root_cause,
                        near_root_cause_category,
                        root_cause,
                        root_cause_category,
                        created_by,
                        created_at,
                        updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (deviation_id) 
                    DO UPDATE SET
                        issues = EXCLUDED.issues,
                        issues_category = EXCLUDED.issues_category,
                        major_root_cause_category = EXCLUDED.major_root_cause_category,
                        major_root_cause_category_explanation = EXCLUDED.major_root_cause_category_explanation,
                        near_root_cause = EXCLUDED.near_root_cause,
                        near_root_cause_category = EXCLUDED.near_root_cause_category,
                        root_cause = EXCLUDED.root_cause,
                        root_cause_category = EXCLUDED.root_cause_category,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id, created_at
                """, (
                    deviation_id,
                    issues,
                    issues_category,
                    major_category,
                    major_category,  # Using same value for explanation
                    near_cause,
                    near_cause_category,
                    root_cause,
                    root_cause_category,
                    created_by
                ))
                
                result = cur.fetchone()
                conn.commit()
                
                logger.info(f"✅ Saved RCA to database: ID={result[0]}, created_at={result[1]}")
                return result[0]
                
    except Exception as e:
        logger.error(f"❌ Error saving RCA to database: {str(e)}")
        # Don't raise - we still want to return results even if DB save fails
        # This makes the system more resilient
        return None


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


def load_category_options():
    """
    Load category options from rca-edit-data.json for dropdown population
    Excludes 'definition' and 'number' fields from the response
    
    Returns:
        Dict with category options for each dropdown
    """
    try:
        # Try different possible paths for Lambda deployment
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'rca-edit-data.json'),
            os.path.join('/var/task', 'rca-edit-data.json'),
            'rca-edit-data.json'
        ]
        
        for json_path in possible_paths:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as file:
                    rca_data = json.load(file)
                    
                    # Process Factors (Problem Categories grouped by factor)
                    factors = []
                    for factor in rca_data.get('Factors', []):
                        factor_obj = {
                            'factor_name': factor['factor_name'],
                            'ProblemCategories': []
                        }
                        
                        for category in factor.get('ProblemCategories', []):
                            # Exclude 'definition' and 'number'
                            category_obj = {
                                'name': category['name']
                            }
                            factor_obj['ProblemCategories'].append(category_obj)
                        
                        factors.append(factor_obj)
                    
                    # Process Major Root Cause Categories
                    major_categories = []
                    for major_cat in rca_data.get('MajorRootCauseCategories', []):
                        major_obj = {
                            'description': major_cat['description'],
                            'properties': {
                                'details': []
                            }
                        }
                        
                        # Process details (Near Root Causes)
                        for detail in major_cat.get('properties', {}).get('details', []):
                            detail_obj = {
                                'NearRootCauses': detail['NearRootCauses'],
                                'rootcauses': []
                            }
                            
                            # Process root causes
                            for root_cause in detail.get('rootcauses', []):
                                # Exclude 'definition' and 'number'
                                root_cause_obj = {
                                    'name': root_cause['name']
                                }
                                detail_obj['rootcauses'].append(root_cause_obj)
                            
                            major_obj['properties']['details'].append(detail_obj)
                        
                        major_categories.append(major_obj)
                    
                    # Build response structure
                    options = {
                        'Factors': factors,
                        'MajorRootCauseCategories': major_categories
                    }
                    
                    logger.info("Successfully loaded category options from rca-edit-data.json")
                    return options
        
        logger.warning("rca-edit-data.json not found, returning empty options")
        return {
            'Factors': [],
            'MajorRootCauseCategories': []
        }
        
    except Exception as e:
        logger.error(f"Error loading category options: {str(e)}")
        return {
            'Factors': [],
            'MajorRootCauseCategories': []
        }


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
        prompt_template = load_prompt('issues_prompt_v2.txt')
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


def categorize_rca(investigation_summary: str, issues_text: str, major_category_text: str,
                   near_cause_text: str, root_cause_text: str) -> dict:
    """
    Categorizes the RCA analysis into specific ABS taxonomy categories
    
    Args:
        investigation_summary: Original investigation summary
        issues_text: Generated issues text
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
            issues_text=issues_text,
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
            "issues_category": "Other",
            "major_root_cause_category": major_category_text,
            "near_root_cause_category": "Other",
            "root_cause_category": "Other"
        }
    except Exception as e:
        logger.error(f"Error categorizing RCA: {str(e)}")
        # Return default categories if categorization fails
        return {
            "issues_category": "Other",
            "major_root_cause_category": major_category_text,
            "near_root_cause_category": "Other",
            "root_cause_category": "Other"
        }


def lambda_handler(event, context):
    try:
        logger.info(f"Environment: {ENV}, Region: {AWS_REGION}, Model: {MODEL_ID}")
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()
        
        # Handle GET request to retrieve existing RCA
        if event.get('httpMethod') == 'GET':
            query_params = event.get('queryStringParameters', {})
            deviation_id = query_params.get('deviation_id') if query_params else None
            
            if not deviation_id:
                return response(400, "deviation_id query parameter is required")
            
            logger.info(f"GET request for deviation: {deviation_id}")
            
            try:
                rca_data = get_rca_from_database(deviation_id)
                
                if not rca_data:
                    return response(404, f"No RCA found for deviation: {deviation_id}")
                
                return response(200, "RCA retrieved successfully", rca_data)
                
            except Exception as e:
                logger.error(f"Error retrieving RCA: {str(e)}")
                return response(500, "Error retrieving RCA", {"details": str(e)})
        
        # Handle POST request to generate new RCA
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
        
        # Categorize the RCA analysis
        logger.info("Categorizing RCA analysis")
        categories = categorize_rca(
            investigation_summary=investigation_summary,
            issues_text=issues_text,
            major_category_text=major_category_text,
            near_cause_text=near_cause_text,
            root_cause_text=root_cause_text
        )
        
        # Save to database with categories
        logger.info("Saving RCA to database")
        rca_id = save_rca_to_database(
            deviation_id=deviation_id,
            issues=issues_text,
            issues_category=categories.get('issues_category', 'Other'),
            major_category=major_category_text,
            near_cause=near_cause_text,
            near_cause_category=categories.get('near_root_cause_category', 'Other'),
            root_cause=root_cause_text,
            root_cause_category=categories.get('root_cause_category', 'Other'),
            created_by=body.get('created_by', 'system')
        )
        
        # Load category options from JSON file
        category_options = load_category_options()
        
        # Structure result with text, categories, and dropdown options
        rca_result = {
            'deviation_id': deviation_id,
            'issues': issues_text,
            'issues_category': categories.get('issues_category'),
            'major_root_cause_category': major_category_text,
            'major_root_cause_category_validated': categories.get('major_root_cause_category'),
            'near_root_cause': near_cause_text,
            'near_root_cause_category': categories.get('near_root_cause_category'),
            'root_cause': root_cause_text,
            'root_cause_category': categories.get('root_cause_category'),
            'category_options': category_options  # Include dropdown options
        }
        
        # Add rca_id if save was successful
        if rca_id:
            rca_result['rca_id'] = rca_id
            logger.info(f"✅ RCA generation and save completed successfully for {deviation_id}")
            return response(200, "RCA generated and saved successfully", rca_result)
        else:
            logger.warning(f"⚠️ RCA generated but not saved to database for {deviation_id}")
            return response(200, "RCA generated successfully (database save skipped)", rca_result)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
