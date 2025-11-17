import json
import boto3
import base64
import os
import uuid
import re
import io
from datetime import datetime, timezone
import pandas as pd
import psycopg
from psycopg.rows import dict_row

try:
    from secrets_util import get_secret
except ImportError:
    from .secrets_util import get_secret

# Environment variables
ENV = os.environ.get('env', 'dev')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'qms-dev-initial-files')
SQS_QUEUE_NAME = os.environ.get('SQS_QUEUE_NAME', 'qms-dev-preload-complaints')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.pdf', '.xls'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Cache for database credentials and connection string
_db_credentials = None
_connection_string = None


def lambda_handler(event, context):
    try:
        # Initialize AWS clients
        s3_client = boto3.client('s3')
        sqs_client = boto3.client('sqs')

        # Resolve Queue URL from name
        try:
            queue_url = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)["QueueUrl"]
        except Exception as e:
            print(f"Error resolving queue URL for {SQS_QUEUE_NAME}: {e}")
            return _response(500, f"Queue {SQS_QUEUE_NAME} not found")

        # Validate request has body
        if "body" not in event:
            return _response(400, "No file provided")

        # Validate content-type header
        headers = event.get("headers", {})
        content_type = headers.get("content-type") or headers.get("Content-Type")

        if not content_type or 'multipart/form-data' not in content_type.lower():
            return _response(400, "Content-Type must be multipart/form-data")

        # Handle body encoding - CRITICAL: Keep as bytes for binary files
        body_str = event["body"]

        # Debug: Log what we're receiving
        print(f"isBase64Encoded: {event.get('isBase64Encoded', False)}")
        print(f"Body type: {type(body_str)}")
        print(f"Body length: {len(body_str) if body_str else 0}")
        print(f"Content-Type: {content_type}")

        if event.get("isBase64Encoded", False):
            # Body is base64 encoded - decode it
            body_bytes = base64.b64decode(body_str)
            print("Decoded from base64")
        else:
            # Body is NOT marked as base64
            if isinstance(body_str, str):
                # Check if it looks like base64
                # Base64 strings only contain: A-Z, a-z, 0-9, +, /, =
                is_base64_like = all(
                    c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r' for c in
                    body_str[:100])

                if is_base64_like and len(body_str) > 100:
                    try:
                        # Likely base64 - try to decode
                        body_bytes = base64.b64decode(body_str)
                        print("Detected and decoded base64 (not marked)")
                    except Exception as e:
                        print(f"Base64 decode failed: {e}")
                        return _response(400,
                                         f"Cannot decode body. API Gateway binary media types may not be configured. Error: {str(e)}")
                else:
                    # Doesn't look like base64, try latin-1
                    try:
                        body_bytes = body_str.encode('iso-8859-1')
                        print("Encoded with iso-8859-1")
                    except Exception as e:
                        print(f"ISO-8859-1 encode failed: {e}")
                        # Last resort: try utf-8 with error handling
                        try:
                            body_bytes = body_str.encode('utf-8', errors='surrogateescape')
                            print("Encoded with utf-8 (with error handling)")
                        except Exception as e2:
                            print(f"All encoding attempts failed: {e2}")
                            return _response(400,
                                             "Invalid body encoding. Please ensure binary media types are configured in API Gateway.")
            else:
                # Already bytes
                body_bytes = body_str
                print("Body already in bytes")

        # Check file size
        if len(body_bytes) > MAX_FILE_SIZE:
            return _response(400, f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB")

        # Parse multipart manually (more reliable for binary files)
        file_info = parse_multipart_manual(body_bytes, content_type)

        if not file_info:
            return _response(400, "No valid file found in request")

        filename = file_info['filename']
        file_content = file_info['content']

        if not filename:
            return _response(400, "No filename provided")

        if not _is_allowed_file(filename):
            return _response(400, f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

        if len(file_content) == 0:
            return _response(400, "File is empty")

        # Generate S3 key with safe filename
        file_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        safe_filename = _sanitize_filename(filename)
        s3_key = f"uploads/{timestamp}/{file_id}_{safe_filename}"

        # Upload to S3
        s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=file_info.get('content_type', _get_content_type(filename)),
            Metadata={
                "original_filename": filename,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "file_size": str(len(file_content)),
                "file_id": file_id
            }
        )
        
        # Create record in files table
        create_file_record(file_id, filename, s3_uri, _get_user_from_event(event))

        # Process files based on type
        file_extension = _get_file_extension(filename)
        
        if file_extension == 'pdf':
            # For PDFs: Create complaint record and send to SQS
            complaint_id = create_complaint_in_db(file_id)
            
            # Create SQS message for extract and process complaints lambda
            complaint_message = {
                'complaint_id': complaint_id,
                'file_id': file_id,
                's3_uri': s3_uri
            }
            
            # Send to SQS for processing
            sqs_response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(complaint_message),
                MessageAttributes={
                    'Source': {
                        'StringValue': 'PDF Upload',
                        'DataType': 'String'
                    },
                    'ComplaintId': {
                        'StringValue': complaint_id,
                        'DataType': 'String'
                    },
                    'CreatedBy': {
                        'StringValue': _get_user_from_event(event),
                        'DataType': 'String'
                    }
                }
            )
            
            print(f"PDF uploaded to S3 and complaint queued for processing: {complaint_id}")
            
            return _response(200, "PDF file uploaded and queued for processing successfully", {
                "file_id": file_id,
                "complaint_id": complaint_id,
                "filename": filename,
                "file_size": len(file_content),
                "s3_key": s3_key,
                "status": "processing",
                "message_id": sqs_response['MessageId']
            })
        # Process CSV/Excel files
        elif file_extension in ['csv', 'xlsx', 'xls']:
            try:
                # Process CSV/Excel file
                complaints_data = process_csv_excel_file(file_content, file_extension, file_id)
                
                if not complaints_data['success']:
                    return _response(400, complaints_data['message'])
                
                complaint_messages = complaints_data['complaints']
                message_ids = []
                
                # Send each complaint to SQS
                for complaint_message in complaint_messages:
                    complaint_sqs_response = sqs_client.send_message(
                        QueueUrl=queue_url,
                        MessageBody=json.dumps(complaint_message),
                        MessageAttributes={
                            'Source': {
                                'StringValue': f'{file_extension.upper()} Upload',
                                'DataType': 'String'
                            },
                            'ComplaintId': {
                                'StringValue': complaint_message['complaint_id'],
                                'DataType': 'String'
                            },
                            'CreatedBy': {
                                'StringValue': _get_user_from_event(event),
                                'DataType': 'String'
                            }
                        }
                    )
                    message_ids.append(complaint_sqs_response['MessageId'])
                
                print(f"Processed {len(complaint_messages)} complaints from {file_extension.upper()} file")
                
                return _response(200, f"{file_extension.upper()} file processed and {len(complaint_messages)} complaints queued successfully", {
                    "file_id": file_id,
                    "filename": filename,
                    "file_size": len(file_content),
                    "s3_key": s3_key,
                    "complaints_processed": len(complaint_messages),
                    "complaint_message_ids": message_ids
                })
                
            except Exception as e:
                print(f"Error processing {file_extension} file: {str(e)}")
                return _response(400, f"Error processing {file_extension} file: {str(e)}")
        
        else:
            # For other file types, just return success
            return _response(200, "File uploaded successfully", {
                "file_id": file_id,
                "filename": filename,
                "file_size": len(file_content),
                "s3_key": s3_key
            })

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return _response(500, f"Internal server error: {str(e)}")


def parse_multipart_manual(body_bytes, content_type):
    """
    Manual multipart parsing that works reliably with binary files
    """
    try:
        # Extract boundary
        boundary_match = re.search(rb'boundary=([^;]+)', content_type.encode())
        if not boundary_match:
            # Try with string match
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if not boundary_match:
                raise ValueError("No boundary found in Content-Type")
            boundary = boundary_match.group(1).strip('"').encode()
        else:
            boundary = boundary_match.group(1).strip(b'"')

        # Split by boundary
        boundary_delimiter = b'--' + boundary
        parts = body_bytes.split(boundary_delimiter)

        print(f"Found {len(parts)} parts")

        # Process each part
        for i, part in enumerate(parts[1:-1], 1):  # Skip first empty and last closing parts
            if len(part) < 10:  # Skip very small parts
                continue

            print(f"Processing part {i}, size: {len(part)} bytes")

            # Find headers-content separator
            if b'\r\n\r\n' in part:
                headers_section, content = part.split(b'\r\n\r\n', 1)
            elif b'\n\n' in part:
                headers_section, content = part.split(b'\n\n', 1)
            else:
                print(f"Part {i}: No header separator found")
                continue

            # Decode headers only (not content!)
            try:
                headers_text = headers_section.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Part {i}: Cannot decode headers: {e}")
                continue

            print(f"Part {i} headers: {headers_text[:200]}...")

            # Parse Content-Disposition header
            content_disposition_match = re.search(
                r'Content-Disposition:\s*form-data;\s*name="([^"]+)"(?:;\s*filename="([^"]*)")?',
                headers_text,
                re.IGNORECASE
            )

            if not content_disposition_match:
                print(f"Part {i}: No Content-Disposition found")
                continue

            field_name = content_disposition_match.group(1)
            filename = content_disposition_match.group(2)

            print(f"Part {i}: field_name={field_name}, filename={filename}")

            # Only process file fields (with filename)
            if filename is not None and filename.strip():
                # Get content-type
                content_type_match = re.search(
                    r'Content-Type:\s*([^\r\n]+)',
                    headers_text,
                    re.IGNORECASE
                )
                file_content_type = content_type_match.group(1).strip() if content_type_match else _get_content_type(
                    filename)

                # Clean content (remove trailing CRLF)
                content = content.rstrip(b'\r\n')

                print(f"Found file: {filename}, size: {len(content)} bytes, type: {file_content_type}")

                return {
                    'filename': filename.strip(),
                    'content': content,
                    'content_type': file_content_type,
                    'field_name': field_name
                }

        print("No file found in any part")
        return None

    except Exception as e:
        print(f"Multipart parsing error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None


def _get_content_type(filename):
    """Get appropriate content type based on file extension"""
    ext = _get_file_extension(filename).lower()
    content_types = {
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'pdf': 'application/pdf'
    }
    return content_types.get(ext, 'application/octet-stream')


def _sanitize_filename(filename):
    """Sanitize filename for S3"""
    if not filename:
        return "unknown_file"

    # Remove or replace problematic characters
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized


def _get_file_extension(filename):
    """Get file extension without dot"""
    if not filename:
        return "unknown"
    return os.path.splitext(filename)[-1].lower().lstrip('.')


def _response(status_code, message, data=None):
    """Standardized HTTP response"""
    body = {
        "success": status_code < 400,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "86400"
        },
        "body": json.dumps(body)
    }


def _is_allowed_file(filename):
    """Check if file has allowed extension"""
    if not filename:
        return False
    ext = os.path.splitext(filename)[-1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_connection_string():
    """
    Build PostgreSQL connection string from credentials in Secrets Manager.
    Credentials are cached to avoid repeated API calls.
    """
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
        print(f"Error building connection string: {str(e)}")
        raise


def create_file_record(file_id, filename, s3_url, upload_by):
    """
    Create file record in database
    """
    try:
        conninfo = get_connection_string()
        
        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                insert_query = """
                INSERT INTO files (file_id, file_name, s3_url, upload_by) 
                VALUES (%s, %s, %s, %s)
                """
                
                cur.execute(insert_query, (file_id, filename, s3_url, upload_by))
                conn.commit()
                print(f"Created file record with ID: {file_id}")
                
    except Exception as e:
        print(f"Database error creating file record: {str(e)}")
        raise


def create_complaint_in_db(file_id, narrative=None):
    """
    Create complaint record in database and return auto-generated complaint_id
    """
    try:
        conninfo = get_connection_string()
        
        with psycopg.connect(conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if narrative:
                    insert_query = """
                    INSERT INTO complaints (file_id, narrative, status) 
                    VALUES (%s, %s, 'Pending') 
                    RETURNING complaint_id
                    """
                    cur.execute(insert_query, (file_id, narrative))
                else:
                    insert_query = """
                    INSERT INTO complaints (file_id, status) 
                    VALUES (%s, 'Pending') 
                    RETURNING complaint_id
                    """
                    cur.execute(insert_query, (file_id,))
                
                result = cur.fetchone()
                complaint_id = result['complaint_id']
                
                conn.commit()
                print(f"Created complaint in database with ID: {complaint_id}")
                return complaint_id
                
    except Exception as e:
        print(f"Database error creating complaint: {str(e)}")
        raise





def process_csv_excel_file(file_content, file_extension, file_id):
    """Process CSV/Excel file and extract complaints"""
    try:
        # Read file into pandas DataFrame
        if file_extension == 'csv':
            df = pd.read_csv(io.BytesIO(file_content))
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            return {'success': False, 'message': f'Unsupported file type: {file_extension}'}
        
        # Check row limit
        if len(df) > 20:
            return {'success': False, 'message': f'File has {len(df)} rows. Maximum allowed is 20 rows.'}
        
        # Check column limit
        if len(df.columns) > 2:
            return {'success': False, 'message': f'File has {len(df.columns)} columns. Maximum allowed is 2 columns.'}
        
        # Validate structure - expect exactly 2 columns: complaint_id and narrative_text
        if len(df.columns) != 2:
            return {'success': False, 'message': 'File must have exactly 2 columns: complaint_id and narrative_text'}
        
        # Get column names (first two columns)
        complaint_id_col = df.columns[0]
        narrative_col = df.columns[1]
        
        complaints = []
        
        # Process each row
        for index, row in df.iterrows():
            original_complaint_id = str(row[complaint_id_col]).strip() if pd.notna(row[complaint_id_col]) else ''
            narrative = str(row[narrative_col]).strip() if pd.notna(row[narrative_col]) else ''
            
            # Skip empty narratives
            if not narrative:
                continue
            
            # Create complaint record in database and get auto-generated ID
            complaint_id = create_complaint_in_db(file_id, narrative)
            
            # Create complaint message for SQS (compatible with extract and process lambda)
            complaint_message = {
                'complaint_id': complaint_id,
                'file_id': file_id,
                'narrative_text': narrative,
                'original_complaint_id': original_complaint_id
            }
            
            complaints.append(complaint_message)
        
        return {
            'success': True,
            'complaints': complaints,
            'total_rows': len(df),
            'processed_complaints': len(complaints)
        }
        
    except Exception as e:
        return {'success': False, 'message': f'Error processing file: {str(e)}'}

def _get_user_from_event(event):
    """Extract user information from event (Cognito, API Key, etc.)"""
    try:
        # From Cognito authorizer
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})

        if 'claims' in authorizer:
            return authorizer['claims'].get('email') or authorizer['claims'].get('sub')

        # From custom header
        headers = event.get('headers', {})
        return headers.get('x-user-email') or headers.get('x-user-id') or 'anonymous'

    except Exception:
        return 'anonymous'
