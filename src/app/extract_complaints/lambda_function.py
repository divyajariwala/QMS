"""
QMS Product Complaints PDF Processing Lambda Function

This Lambda function processes PDF documents from S3, converts them to images,
and uses Amazon Bedrock to extract structured data using AI/ML models.

Key Features:
- Downloads PDF files from S3 with size validation
- Converts PDF pages to images with memory optimization
- Processes images through Amazon Bedrock Claude model
- Returns structured JSON response
- Comprehensive error handling and logging

Dependencies:
- PyMuPDF (fitz) for PDF processing
- Pillow (PIL) for image manipulation
- boto3 for AWS services
- prompt.txt file containing AI prompt
- toolspec.json file containing tool configuration

Author: QMS Team
Version: 1.0
"""

import fitz
import boto3
import json
from PIL import Image
import io
import base64
import logging
import os
import uuid
import random
import string
from datetime import datetime, timezone

# Configure logging for CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration constants
MAX_PDF_SIZE_MB = 50  # Maximum PDF file size in MB
MAX_PAGES = 20        # Maximum number of pages to process
SQS_QUEUE_NAME = os.environ.get('SQS_QUEUE_NAME', 'qms-dev-preload-complaints')

# Test event for local development
# event = {"s3path" : "s3://qms-textract-staging-bucket/s3testsample.pdf"}

def validate_event(event):
    """
    Validate the incoming Lambda event structure and S3 path format.
    
    Args:
        event (dict): Lambda event containing s3path field
        
    Returns:
        str: Validated S3 path
        
    Raises:
        ValueError: If event structure is invalid or s3path is missing/malformed
    """
    if not isinstance(event, dict) or 's3path' not in event:
        raise ValueError("Missing required field: s3path")
    s3path = event['s3path']
    if not s3path.startswith('s3://'):
        raise ValueError("Invalid S3 path format")
    return s3path

def load_prompt_from_file(file_path):
    """
    Load AI prompt text from a local file.
    
    Args:
        file_path (str): Path to the prompt text file
        
    Returns:
        str: Content of the prompt file
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
        Exception: For other file reading errors
        
    Note:
        The prompt file should be deployed with the Lambda function
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError as e:
        logger.error(f"Prompt file not found: {str(e)}")
        raise
    except IOError as e:
        logger.error(f"Error reading prompt file: {str(e)}")
        raise

def fetch_pdf_from_s3(s3_path):
    """
    Download PDF file from S3 with size validation.
    
    Args:
        s3_path (str): S3 URI in format s3://bucket-name/key
        
    Returns:
        bytes: PDF file content as bytes
        
    Raises:
        ValueError: If PDF file exceeds size limit
        ClientError: For S3 access errors (NoSuchBucket, NoSuchKey, etc.)
        Exception: For other download errors
        
    Note:
        - Validates file size before download to prevent memory issues
        - Maximum file size is controlled by MAX_PDF_SIZE_MB constant
    """
    try:
        s3_client = boto3.client('s3')
        path_parts = s3_path.replace('s3://', '').split('/')
        bucket_name = path_parts[0]
        key = '/'.join(path_parts[1:])
        
        # Validate bucket name and key
        if not bucket_name or '..' in key or key.startswith('/'):
            raise ValueError("Invalid S3 path")
        
        # Check file size before download
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
    """
    Convert PDF pages to PIL Image objects with memory optimization.
    
    Args:
        pdf_data (bytes): PDF file content as bytes
        
    Returns:
        list[PIL.Image]: List of PIL Image objects, one per page
        
    Raises:
        Exception: For PDF parsing or image conversion errors
        
    Features:
        - Limits processing to MAX_PAGES to prevent memory issues
        - Uses 1.5x zoom factor for good quality with reasonable memory usage
        - Properly closes PDF document to free memory
        - Converts each page to PNG format for consistent processing
    """
    doc = None
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        page_count = min(doc.page_count, MAX_PAGES)
        images = []
        
        for page_num in range(page_count):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # 1.5x zoom for balance
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
    """
    Convert PIL Image objects to base64-encoded strings.
    
    Args:
        images (list[PIL.Image]): List of PIL Image objects
        
    Returns:
        list[str]: List of base64-encoded image strings
        
    Note:
        - Images are saved as PNG format for lossless compression
        - Base64 encoding is required for Bedrock API image input
        - Each image is processed independently to handle potential errors
    """
    base64_images = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf8')
        base64_images.append(img_base64)
    return base64_images

def prompt_constructor(base64_images):
    """
    Construct Bedrock API message format with images and text prompt.
    
    Args:
        base64_images (list[str]): List of base64-encoded image strings
        
    Returns:
        list[dict]: Bedrock-compatible message structure
        
    Structure:
        - Each image is added as an image content block
        - Text prompt is loaded from prompt.txt and added as text content block
        - All content is wrapped in a user message for the conversation API
        
    Note:
        Images must be decoded from base64 for Bedrock API compatibility
    """
    content = []
    for img_base64 in base64_images:
        content.append({
            "image": {
                "format": "png",
                "source": {"bytes": base64.b64decode(img_base64)}
            }
        })
    
    content.append({
        "text": load_prompt_from_file('prompt.txt')
    })
    messages = [{"role": "user", "content": content}]
    return messages

def load_tool_spec():
    """
    Load tool specification from toolspec.json file.
    
    Returns:
        dict: Tool specification for Bedrock function calling
        
    Raises:
        FileNotFoundError: If toolspec.json doesn't exist
        json.JSONDecodeError: If JSON is malformed
        Exception: For other file reading errors
        
    Note:
        Tool specification defines the structure and parameters for
        function calling in Bedrock, enabling structured data extraction
    """
    try:
        with open('toolspec.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError as e:
        logger.error(f"Tool spec file not found: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in tool spec: {str(e)}")
        raise
    except IOError as e:
        logger.error(f"Error reading tool spec: {str(e)}")
        raise


def process_with_bedrock_conversations(messages, bedrock_runtime):
    """
    Process messages through Amazon Bedrock Claude model with function calling.
    
    Args:
        messages (list[dict]): Bedrock-compatible message structure
        bedrock_runtime: Boto3 Bedrock Runtime client
        
    Returns:
        dict: Extracted structured data from tool use response
        
    Raises:
        ClientError: For Bedrock API errors
        ValueError: If no tool use is found in response
        Exception: For other processing errors
        
    Features:
        - Uses Claude 3.5 Sonnet model for high-quality extraction
        - Implements function calling for structured output
        - Safe response parsing that doesn't assume array positions
        - Comprehensive error handling and logging
    """
    try:
        response = bedrock_runtime.converse(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            messages=messages,
            toolConfig={"tools": [load_tool_spec()]}
        )
        
        # Safe response parsing - iterate through content to find tool use
        content = response['output']['message']['content']
        for item in content:
            if isinstance(item, dict) and 'toolUse' in item:
                return item['toolUse']['input']
        
        raise ValueError("No tool use found in response")
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}")
        raise


def generate_complaint_code(strategy='timestamp_random'):
    """
    Generate unique complaint code with timestamp and random digits.
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y%m%d%H%M%S')
    microseconds = str(now.microsecond)[:3]
    random_suffix = ''.join(random.choices(string.digits, k=3))
    return f"CAS-{timestamp}{microseconds}{random_suffix}"

def create_complaint_message_from_output(output_data, file_id, filename, created_by):
    """
    Create complaint message from PDF extraction output.
    """
    result = output_data
    
    # Use case_id from PDF as complaint_id, fallback to generated code if not available
    case_id = result.get('case_id', '')
    complaint_id = case_id if case_id and case_id != 'N/A' else generate_complaint_code()
    now = datetime.now(timezone.utc)
    
    complaint_message = {
        'complaint_id': complaint_id,
        'narrative': result.get('narrative', ''),
        'short_description': result.get('narrative', '')[:100],
        'status': 'IN-REVIEW',
        'caseStatus': 'pending',
        'criticality': result.get('criticality', 'NA'),
        'report_type': result.get('report_type', 'NA'),
        'receipt_date': result.get('receipt_date', ''),
        'category': result.get('category', []),
        'case_type': result.get('case_type', []),
        'primary_reporter': result.get('primary_reporter', {}),
        'patient_name': result.get('patient_name', ''),
        'physician_name': result.get('physician_name', ''),
        'product_details': result.get('product_details', {}),
        'created_at': now.isoformat(),
        'updated_at': now.isoformat(),
        'created_by': created_by,
        'metadata': {
            'source': 'PDF Extraction',
            'version': '1.0',
            'original_case_id': result.get('case_id', ''),
            'file_id': file_id,
            'filename': filename
        }
    }
    
    return complaint_message

def lambda_handler(event, context):
    """
    Main Lambda function handler for PDF processing and data extraction.
    Now includes SQS message sending for complaint data.
    
    Args:
        event (dict): Lambda event containing:
            - s3path (str): S3 URI of PDF file to process
            - file_id (str): Unique file identifier
            - filename (str): Original filename
            - created_by (str): User who uploaded the file
        context: Lambda context object (unused)
        
    Returns:
        dict: HTTP response with status code and JSON body
    """
    try:
        logger.info("PDF extraction processing started")
        s3path = validate_event(event)
        file_id = event.get('file_id', str(uuid.uuid4()))
        filename = event.get('filename', 'unknown.pdf')
        created_by = event.get('created_by', 'system')
        
        # Extract data from PDF
        pdf_data = fetch_pdf_from_s3(s3path)
        images = pdf_to_images(pdf_data)
        base64_images = images_to_base64(images)
        messages = prompt_constructor(base64_images)
        bedrock_runtime = boto3.client('bedrock-runtime')
        output = process_with_bedrock_conversations(messages, bedrock_runtime)
        
        # Create complaint message
        complaint_message = create_complaint_message_from_output(output, file_id, filename, created_by)
        
        # Send complaint message to SQS
        sqs_client = boto3.client('sqs')
        queue_url = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)["QueueUrl"]
        
        sqs_response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(complaint_message),
            MessageAttributes={
                'Source': {
                    'StringValue': 'PDF Extraction',
                    'DataType': 'String'
                },
                'ComplaintCode': {
                    'StringValue': complaint_message['complaint_id'],
                    'DataType': 'String'
                },
                'CreatedBy': {
                    'StringValue': created_by,
                    'DataType': 'String'
                }
            }
        )
        
        logger.info(f"Complaint message sent to SQS: {complaint_message['complaint_id']}, MessageId: {sqs_response['MessageId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True, 
                'result': output,
                'complaint_id': complaint_message['complaint_id'],
                'message_id': sqs_response['MessageId']
            })
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'success': False, 'error': str(e)})
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'error': 'Internal error'})
        }
    
# def main():
#     """
#     Local testing function for development and debugging.
    
#     Simulates Lambda execution with test event and prints results.
#     Only runs when script is executed directly (not imported).
#     """
#     result = lambda_handler(event, None)
#     print(json.dumps(result, indent=2))

# if __name__ == "__main__":
#     main()
