"""
Refactored QMS Complaints Processing Lambda Function

Handles multiple input types:
- PDF files from S3 (existing functionality)
- Direct narrative text from manual uploads, CSV, Excel
- Database operations for Aurora PostgreSQL
"""

import fitz
import boto3
import json
import psycopg
from PIL import Image
import io
import base64
import logging
import os
import uuid
from datetime import datetime, timezone
from psycopg.rows import dict_row
from concurrent.futures import ThreadPoolExecutor

try:
    from secrets_util import get_secret
except ImportError:
    from .secrets_util import get_secret

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration
MAX_PDF_SIZE_MB = 50
ENV = os.environ.get('env', 'dev')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')

# Cache for database credentials and connection string
_db_credentials = None
_connection_string = None

def get_connection_string():
    """
    Build PostgreSQL connection string from credentials in Secrets Manager.
    Credentials are cached to avoid repeated API calls.
    """
    global _connection_string, _db_credentials

    if _connection_string is not None:
        return _connection_string

    try:
        # Use the superior secrets_util function
        _db_credentials = get_secret(DB_SECRET_NAME, DB_REGION)

        # Build connection string
        host = _db_credentials['host']
        port = _db_credentials.get('port', 5432)
        dbname = _db_credentials['dbname']
        user = _db_credentials['username']
        password = _db_credentials['password']

        _connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

        logger.info(f"Database connection string built from secret: {DB_SECRET_NAME}")
        return _connection_string

    except Exception as e:
        logger.error(f"Error building connection string: {str(e)}")
        raise

def validate_event(event):
    """Validate event structure for different input types"""
    required_fields = ['complaint_id', 'file_id']
    
    if not all(field in event for field in required_fields):
        raise ValueError(f"Missing required fields: {required_fields}")
    
    # Check input type
    if 'narrative_text' in event:
        return 'narrative'
    elif 's3path' in event:
        if not event['s3path'].startswith('s3://'):
            raise ValueError("Invalid S3 path format")
        return 'pdf'
    else:
        raise ValueError("Must provide either 'narrative_text' or 's3path'")

def load_tool_spec(spec_type='pdf', step=1):
    """Load appropriate tool specification for given step"""
    if step == 1:
        filename = 'toolspec_step1.json' if spec_type == 'pdf' else 'toolspec_narrative_step1.json'
    elif step == 2:
        filename = 'toolspec_narrative_step2.json'
    elif step == 3:
        filename = 'toolspec_narrative_step3.json'
    else:
        filename = 'toolspec.json' if spec_type == 'pdf' else 'toolspec_narrative.json'
    
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Tool spec file not found: {filename}")
        raise

def get_default_extraction_data(spec_type='pdf', narrative_text=''):
    """Return default extraction data with NA values"""
    return {
        'case_id': 'N/A',
        'receipt_date': 'N/A',
        'criticality': 'N/A',
        'category': [],
        'case_type': [],
        'report_type': 'N/A',
        'narrative': narrative_text,  # Preserve input narrative
        'narrative_summary': 'N/A',
        'primary_reporter': {'name': 'N/A', 'address': 'N/A'},
        'patient_name': 'N/A',
        'physician_name': 'N/A',
        'product_details': {
            'drug_name': 'N/A',
            'dosage': 'N/A',
            'lot_no': 'N/A',
            'part_no': 'N/A',
            'expiration_date': 'N/A'
        }
    }

def fetch_pdf_from_s3(s3_path):
    """Download PDF from S3 with size validation"""
    try:
        s3_client = boto3.client('s3')
        path_parts = s3_path.replace('s3://', '').split('/')
        bucket_name = path_parts[0]
        key = '/'.join(path_parts[1:])
        
        head_response = s3_client.head_object(Bucket=bucket_name, Key=key)
        file_size_mb = head_response['ContentLength'] / (1024 * 1024)
        if file_size_mb > MAX_PDF_SIZE_MB:
            raise ValueError(f"PDF too large: {file_size_mb:.1f}MB")
        
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        return response['Body'].read()
    except Exception as e:
        logger.error(f"Error fetching PDF: {str(e)}")
        raise

def pdf_to_images(pdf_data):
    """Convert all PDF pages to PIL Images"""
    doc = None
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        images = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)
        
        return images
    except Exception as e:
        logger.error(f"Error converting PDF: {str(e)}")
        raise
    finally:
        if doc:
            doc.close()

def images_to_base64(images):
    """Convert PIL Images to base64 strings"""
    base64_images = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf8')
        base64_images.append(img_base64)
    return base64_images

def construct_pdf_prompt(base64_images, step=1):
    """Construct Bedrock message for PDF processing"""
    content = []
    for img_base64 in base64_images:
        content.append({
            "image": {
                "format": "png",
                "source": {"bytes": base64.b64decode(img_base64)}
            }
        })
    
    prompt_file = 'prompt_step1.txt' if step == 1 else 'prompt.txt'
    with open(prompt_file, 'r') as file:
        prompt_text = file.read()
    
    content.append({"text": prompt_text})
    return [{"role": "user", "content": content}]

def construct_narrative_prompt(narrative_text, step=1):
    """Construct Bedrock message for narrative processing"""
    if step == 1:
        prompt_file = 'prompt_narrative_step1.txt'
        prompt_suffix = f"\n\nNarrative: {narrative_text}"
    elif step == 2:
        prompt_file = 'prompt_narrative_step2_criticality.txt'
        prompt_suffix = f"\n\n{narrative_text}"
    elif step == 3:
        prompt_file = 'prompt_narrative_step3_classification.txt'
        prompt_suffix = f"\n\n{narrative_text}"
    else:
        prompt_file = 'prompt_narrative.txt'
        prompt_suffix = f"\n\nNarrative: {narrative_text}"
    
    with open(prompt_file, 'r') as file:
        prompt_text = file.read()
    
    prompt = f"{prompt_text}{prompt_suffix}"
    
    return [{"role": "user", "content": [{"text": prompt}]}]

def process_with_bedrock(messages, spec_type='pdf', narrative_text='', step=1):
    """Process messages through Bedrock with appropriate tool spec"""
    try:
        bedrock_runtime = boto3.client('bedrock-runtime')
        tool_spec = load_tool_spec(spec_type, step)
        
        response = bedrock_runtime.converse(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            messages=messages,
            toolConfig={
                "tools": [tool_spec],
                "toolChoice": {"auto": {}}
            }
        )
        
        content = response['output']['message']['content']
        for item in content:
            if isinstance(item, dict) and 'toolUse' in item:
                return item['toolUse']['input']
        
        # If no tool use found, return default with preserved narrative text
        logger.warning(f"No tool use found in response for {spec_type} step {step}")
        if step == 1:
            return get_default_extraction_data(spec_type, narrative_text)
        elif step == 2:
            return {'criticality': 'N/A'}
        elif step == 3:
            return {'category': [], 'case_type': []}
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}")
        raise

def update_complaint_in_db(complaint_id, extracted_data):
    """Update complaint record in PostgreSQL database"""
    try:
        conninfo = get_connection_string()
        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                # Parse extracted data
                result = extracted_data
                logger.info(f"Extracted data keys: {result.keys()}")
                logger.info(f"Narrative summary from LLM: {result.get('narrative_summary', 'NOT FOUND')}")
                
                # Safely handle missing or malformed nested objects
                primary_reporter = result.get('primary_reporter') if isinstance(result.get('primary_reporter'), dict) else {}
                product_details = result.get('product_details') if isinstance(result.get('product_details'), dict) else {}
                
                # Extract part number
                part_number = product_details.get('part_no') if product_details.get('part_no') != 'N/A' else None
                
                # Convert arrays to strings
                category = ', '.join(result.get('category', [])) if result.get('category') else None
                case_type = ', '.join(result.get('case_type', [])) if result.get('case_type') else None
                
                # Parse dates
                receipt_date = None
                expiration_date = None
                
                if result.get('receipt_date') and result.get('receipt_date') != 'N/A':
                    try:
                        receipt_date = datetime.strptime(result.get('receipt_date'), '%Y-%m-%d').date()
                    except:
                        receipt_date = None
                
                if product_details.get('expiration_date') and product_details.get('expiration_date') != 'N/A':
                    try:
                        expiration_date = datetime.strptime(product_details.get('expiration_date'), '%Y-%m-%d').date()
                    except:
                        expiration_date = None
                
                # Update complaint record
                update_query = """
                UPDATE complaints SET
                    narrative = %s,
                    narrative_summary = %s,
                    receipt_date = %s,
                    primary_reporter = %s,
                    primary_reporter_address = %s,
                    patient_name = %s,
                    physician = %s,
                    drug = %s,
                    lot_no = %s,
                    dosage = %s,
                    expiration_date = %s,
                    part_number = %s,
                    criticality = %s,
                    case_type = %s,
                    report_type = %s,
                    category = %s,
                    status = 'Pending',
                    text_extracted = TRUE
                WHERE complaint_id = %s
                """
                
                narrative_summary = result.get('narrative_summary', '')
                logger.info(f"Storing narrative_summary in DB: {narrative_summary[:100] if narrative_summary else 'EMPTY'}")
                
                cur.execute(update_query, (
                    result.get('narrative', ''),
                    narrative_summary,
                    receipt_date,
                    primary_reporter.get('name') if primary_reporter.get('name') != 'N/A' else None,
                    primary_reporter.get('address') if primary_reporter.get('address') != 'N/A' else None,
                    result.get('patient_name') if result.get('patient_name') != 'N/A' else None,
                    result.get('physician_name') if result.get('physician_name') != 'N/A' else None,
                    product_details.get('drug_name') if product_details.get('drug_name') != 'N/A' else None,
                    product_details.get('lot_no') if product_details.get('lot_no') != 'N/A' else None,
                    product_details.get('dosage') if product_details.get('dosage') != 'N/A' else None,
                    expiration_date,
                    part_number,
                    result.get('criticality') if result.get('criticality') != 'N/A' else None,
                    case_type,
                    result.get('report_type') if result.get('report_type') != 'N/A' else None,
                    category,
                    complaint_id
                ))
                
                # Check if case_type is adverse event only BEFORE committing
                case_types = result.get('case_type', [])
                is_adverse_event_only = case_types and len(case_types) == 1 and case_types[0].lower() in ['adverse event', 'adverse events']
                
                if is_adverse_event_only:
                    logger.info(f"Complaint {complaint_id} is adverse event only - will move to adverse_events table")
                    # Commit the update first
                    conn.commit()
                    # Then move to adverse_events table
                    move_to_adverse_events(cur, complaint_id)
                    conn.commit()
                    logger.info(f"Successfully moved complaint {complaint_id} to adverse_events table")
                else:
                    # Just commit the update
                    conn.commit()
                    logger.info(f"Updated complaint {complaint_id} in database")
                
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise

def move_to_adverse_events(cur, complaint_id):
    """Move complaint to adverse_events table and delete from complaints"""
    try:
        # Insert into adverse_events
        cur.execute("""
            INSERT INTO adverse_events 
            SELECT * FROM complaints WHERE complaint_id = %s
        """, (complaint_id,))
        
        # Delete from complaints
        cur.execute("DELETE FROM complaints WHERE complaint_id = %s", (complaint_id,))
        
        logger.info(f"Successfully moved complaint {complaint_id} to adverse_events table")
    except Exception as e:
        logger.error(f"Error moving complaint to adverse_events: {str(e)}")
        raise

def lambda_handler(event, context):
    """Main Lambda handler for SQS-triggered complaint processing with parallel processing"""
    try:
        logger.info("Complaint processing started")
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle SQS batch events
        if 'Records' in event:
            # OPTIMIZED: Parallel batch processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(process_single_complaint, json.loads(record['body']))
                    for record in event['Records']
                ]
                results = []
                for future in futures:
                    try:
                        results.append(future.result())
                    except Exception as e:
                        logger.error(f"Error processing record: {str(e)}")
                        results.append({'success': False, 'error': str(e)})
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'processed_count': len(results),
                    'results': results
                })
            }
        else:
            # Direct invocation (for testing)
            result = process_single_complaint(event)
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': 'Internal error'})
        }


def process_single_complaint(message_data):
    """Process a single complaint from SQS message"""
    complaint_id = message_data.get('complaint_id', 'unknown')
    try:
        # Validate and determine input type
        input_type = validate_event(message_data)
        
        logger.info(f"Processing complaint {complaint_id} with input type: {input_type}")
        
        # Process based on input type
        if input_type == 'pdf':
            # PDF processing - 3-step chaining
            pdf_data = fetch_pdf_from_s3(message_data['s3path'])
            images = pdf_to_images(pdf_data)
            
            # Handle empty PDF
            if not images:
                logger.warning(f"PDF has no pages for complaint {complaint_id}")
                extracted_data = get_default_extraction_data('pdf', 'Empty PDF - No Pages')
            else:
                # Step 1: Extract basic info and narrative summary
                logger.info(f"Step 1: Extracting basic info from PDF for complaint {complaint_id}")
                base64_images = images_to_base64(images)
                messages = construct_pdf_prompt(base64_images, step=1)
                extracted_data = process_with_bedrock(messages, 'pdf', 'PDF Extraction Failed', step=1)
                
                # Check if document is not a complaint
                narrative = extracted_data.get('narrative', '')
                if 'Not a Product Complaint' in narrative or not narrative:
                    extracted_data['narrative'] = 'Not a Product Complaint Document'
                    extracted_data['criticality'] = 'N/A'
                    extracted_data['category'] = []
                    extracted_data['case_type'] = []
                
                # Only proceed with steps 2 and 3 if we have a valid summary
                if extracted_data.get('narrative_summary') and 'Not a Product Complaint' not in extracted_data.get('narrative', ''):
                    narrative_summary = extracted_data['narrative_summary']
                    
                    # Step 2: Extract criticality from summary
                    logger.info(f"Step 2: Extracting criticality from PDF for complaint {complaint_id}")
                    messages_step2 = construct_narrative_prompt(narrative_summary, step=2)
                    criticality_data = process_with_bedrock(messages_step2, 'pdf', narrative_summary, step=2)
                    extracted_data['criticality'] = criticality_data.get('criticality', 'N/A')
                    
                    # Step 3: Extract category and case_type from summary
                    logger.info(f"Step 3: Extracting classification from PDF for complaint {complaint_id}")
                    messages_step3 = construct_narrative_prompt(narrative_summary, step=3)
                    classification_data = process_with_bedrock(messages_step3, 'pdf', narrative_summary, step=3)
                    extracted_data['category'] = classification_data.get('category', [])
                    extracted_data['case_type'] = classification_data.get('case_type', [])
                else:
                    # Set defaults if no valid summary
                    extracted_data['criticality'] = 'N/A'
                    extracted_data['category'] = []
                    extracted_data['case_type'] = []
            
        elif input_type == 'narrative':
            # Direct narrative processing - 3-step chaining
            narrative_text = message_data.get('narrative_text', '').strip()
            
            # Handle empty narrative
            if not narrative_text:
                logger.warning(f"Empty narrative text for complaint {complaint_id}")
                extracted_data = get_default_extraction_data('narrative', 'Empty Narrative')
            else:
                # Step 1: Extract basic info and narrative summary
                logger.info(f"Step 1: Extracting basic info for complaint {complaint_id}")
                messages = construct_narrative_prompt(narrative_text, step=1)
                extracted_data = process_with_bedrock(messages, 'narrative', narrative_text, step=1)
                
                # Check if text is not a complaint
                if 'Not a Product Complaint' in extracted_data.get('narrative_summary', ''):
                    extracted_data['narrative'] = narrative_text
                    extracted_data['narrative_summary'] = 'Not a Product Complaint'
                    extracted_data['criticality'] = 'N/A'
                    extracted_data['category'] = []
                    extracted_data['case_type'] = []
                elif not extracted_data.get('narrative'):
                    extracted_data['narrative'] = narrative_text
                
                # Only proceed with steps 2 and 3 if we have a valid summary
                if extracted_data.get('narrative_summary') and extracted_data['narrative_summary'] != 'Not a Product Complaint':
                    narrative_summary = extracted_data['narrative_summary']
                    
                    # Step 2: Extract criticality from summary
                    logger.info(f"Step 2: Extracting criticality for complaint {complaint_id}")
                    messages_step2 = construct_narrative_prompt(narrative_summary, step=2)
                    criticality_data = process_with_bedrock(messages_step2, 'narrative', narrative_summary, step=2)
                    extracted_data['criticality'] = criticality_data.get('criticality', 'N/A')
                    
                    # Step 3: Extract category and case_type from summary
                    logger.info(f"Step 3: Extracting classification for complaint {complaint_id}")
                    messages_step3 = construct_narrative_prompt(narrative_summary, step=3)
                    classification_data = process_with_bedrock(messages_step3, 'narrative', narrative_summary, step=3)
                    extracted_data['category'] = classification_data.get('category', [])
                    extracted_data['case_type'] = classification_data.get('case_type', [])
                else:
                    # Set defaults if no valid summary
                    extracted_data['criticality'] = 'N/A'
                    extracted_data['category'] = []
                    extracted_data['case_type'] = []
        
        # Update database
        update_complaint_in_db(complaint_id, extracted_data)
        
        return {
            'success': True,
            'complaint_id': complaint_id,
            'input_type': input_type,
            'extracted_data': extracted_data
        }
        
    except ValueError as e:
        logger.error(f"Validation error for complaint {complaint_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Processing error for complaint {complaint_id}: {str(e)}")
        raise