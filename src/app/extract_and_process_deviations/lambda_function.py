import fitz
import boto3
import json
import psycopg
from PIL import Image
import io
import base64
import logging
import os
from psycopg.rows import dict_row
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

try:
    from secrets_util import get_secret
except ImportError:
    from .secrets_util import get_secret

try:
    from audit_logger import log_deviation_workflow
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from audit_logger import log_deviation_workflow

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_PDF_SIZE_MB = 50
ENV = os.environ.get('env', 'dev')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')

_db_credentials = None
_connection_string = None

def get_connection_string():
    global _connection_string, _db_credentials
    if _connection_string is not None:
        return _connection_string
    try:
        _db_credentials = get_secret(DB_SECRET_NAME, DB_REGION)
        host = _db_credentials['host']
        port = _db_credentials.get('port', 5432)
        dbname = _db_credentials['dbname']
        user = _db_credentials['username']
        password = _db_credentials['password']
        _connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return _connection_string
    except Exception as e:
        logger.error(f"Error building connection string: {str(e)}")
        raise

def fetch_pdf_from_s3(s3_path):
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
    base64_images = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf8')
        base64_images.append(img_base64)
    return base64_images

def construct_prompt(base64_images):
    content = []
    for img_base64 in base64_images:
        content.append({
            "image": {
                "format": "png",
                "source": {"bytes": base64.b64decode(img_base64)}
            }
        })
    
    with open('prompt.txt', 'r') as file:
        prompt_text = file.read()
    
    content.append({"text": prompt_text})
    return [{"role": "user", "content": content}]

def load_tool_spec():
    try:
        with open('toolspec.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("Tool spec file not found")
        raise

def process_with_bedrock(messages):
    try:
        bedrock_runtime = boto3.client('bedrock-runtime')
        tool_spec = load_tool_spec()
        
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
        
        logger.warning("No tool use found in response")
        return {
            'title': 'N/A',
            'description': 'N/A',
            'immediate_steps_taken': 'N/A',
            'quality_risk_evaluation': 'N/A',
            'investigation_summary': 'N/A',
            'capa_plan': 'N/A',
            'recurrence_check_details': 'N/A',
            'effectiveness_check_plan': 'N/A'
        }
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}")
        raise

def update_deviation_in_db(deviation_id, extracted_data, start_time=None):
    try:
        conninfo = get_connection_string()
        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                update_query = """
                UPDATE deviations SET
                    title = %s,
                    description = %s,
                    immediate_steps_taken = %s,
                    quality_risk_evaluation = %s,
                    investigation_summary = %s,
                    capa_plan = %s,
                    recurrence_check_details = %s,
                    effectiveness_check_plan = %s,
                    text_extracted = TRUE
                WHERE deviation_id = %s
                """
                
                cur.execute(update_query, (
                    extracted_data.get('title'),
                    extracted_data.get('description'),
                    extracted_data.get('immediate_steps_taken'),
                    extracted_data.get('quality_risk_evaluation'),
                    extracted_data.get('investigation_summary'),
                    extracted_data.get('capa_plan'),
                    extracted_data.get('recurrence_check_details'),
                    extracted_data.get('effectiveness_check_plan'),
                    deviation_id
                ))
                # WORKFLOW LOG: extraction completed
                extracted_fields = [k for k, v in extracted_data.items() if v and v != 'N/A']
                log_deviation_workflow(
                    conn,
                    deviation_id,
                    step='TEXT_EXTRACTED',
                    input_data={
                        'source': 'pdf' if 's3path' in extracted_data else 'narrative'
                    },
                    output_data={
                        "extracted_fields": extracted_fields,
                        "description_length": len(extracted_data.get('description', '') or '')
                    },
                    start_time=start_time
                )
                
                conn.commit()
                logger.info(f"Updated deviation {deviation_id} in database")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise

def process_single_deviation(message_data):
    deviation_id = message_data.get('deviation_id', 'unknown')
    start_time = datetime.utcnow()
    try:
        logger.info(f"Processing deviation {deviation_id}")
        
        if 's3path' not in message_data:
            raise ValueError("Missing s3path in message")
        
        pdf_data = fetch_pdf_from_s3(message_data['s3path'])
        images = pdf_to_images(pdf_data)
        
        if not images:
            logger.warning(f"PDF has no pages for deviation {deviation_id}")
            extracted_data = {
                'title': 'Empty PDF - No Pages',
                'description': 'N/A',
                'immediate_steps_taken': 'N/A',
                'quality_risk_evaluation': 'N/A',
                'investigation_summary': 'N/A',
                'capa_plan': 'N/A',
                'recurrence_check_details': 'N/A',
                'effectiveness_check_plan': 'N/A'
            }
        else:
            base64_images = images_to_base64(images)
            messages = construct_prompt(base64_images)
            extracted_data = process_with_bedrock(messages)
        
        update_deviation_in_db(deviation_id, extracted_data, start_time)
        
        return {
            'success': True,
            'deviation_id': deviation_id,
            'extracted_data': extracted_data
        }
    except Exception as e:
        logger.error(f"Processing error for deviation {deviation_id}: {str(e)}")
        raise

def lambda_handler(event, context):
    try:
        logger.info("Deviation processing started")
        logger.info(f"Received event: {json.dumps(event)}")
        
        if 'Records' in event:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(process_single_deviation, json.loads(record['body']))
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
            result = process_single_deviation(event)
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
