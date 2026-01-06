import json
import boto3
import base64
import os
import uuid
import re
from datetime import datetime, timezone
import psycopg
from psycopg.rows import dict_row

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

# Environment variables
ENV = os.environ.get('env', 'dev')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'qms-dev-initial-files')
SQS_QUEUE_NAME = os.environ.get('SQS_QUEUE_NAME', 'qms-dev-process-deviations')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (API Gateway limit)

# Cache for database credentials and connection string
_db_credentials = None
_connection_string = None


def lambda_handler(event, context):
    try:
        s3_client = boto3.client('s3')
        sqs_client = boto3.client('sqs')

        # Resolve Queue URL
        try:
            queue_url = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)["QueueUrl"]
        except Exception as e:
            print(f"Error resolving queue URL for {SQS_QUEUE_NAME}: {e}")
            return _response(500, f"Queue {SQS_QUEUE_NAME} not found")

        if "body" not in event:
            return _response(400, "No file provided")

        headers = event.get("headers", {})
        content_type = headers.get("content-type") or headers.get("Content-Type")

        if not content_type or 'multipart/form-data' not in content_type.lower():
            return _response(400, "Content-Type must be multipart/form-data")

        body_str = event["body"]

        if event.get("isBase64Encoded", False):
            body_bytes = base64.b64decode(body_str)
        else:
            if isinstance(body_str, str):
                is_base64_like = all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r' for c in body_str[:100])
                if is_base64_like and len(body_str) > 100:
                    try:
                        body_bytes = base64.b64decode(body_str)
                    except Exception as e:
                        return _response(400, f"Cannot decode body: {str(e)}")
                else:
                    try:
                        body_bytes = body_str.encode('iso-8859-1')
                    except Exception:
                        body_bytes = body_str.encode('utf-8', errors='surrogateescape')
            else:
                body_bytes = body_str

        if len(body_bytes) > MAX_FILE_SIZE:
            return _response(400, f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB")

        file_info = parse_multipart_manual(body_bytes, content_type)

        if not file_info:
            return _response(400, "No valid file found in request")

        filename = file_info['filename']
        file_content = file_info['content']

        if not filename or not filename.lower().endswith('.pdf'):
            return _response(400, "Only PDF files are allowed")

        if len(file_content) == 0:
            return _response(400, "File is empty")

        # Generate S3 key
        file_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        safe_filename = _sanitize_filename(filename)
        s3_key = f"deviations/{timestamp}/{file_id}_{safe_filename}"

        # Upload to S3
        s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType='application/pdf',
            Metadata={
                "original_filename": filename,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "file_size": str(len(file_content)),
                "file_id": file_id
            }
        )

        # Create record in deviation_files table
        create_deviation_file_record(file_id, filename, s3_uri, _get_user_from_event(event))

        # Create deviation record
        deviation_id = create_deviation_in_db(file_id)

        # Send to SQS for processing
        deviation_message = {
            'deviation_id': deviation_id,
            'file_id': file_id,
            's3path': s3_uri
        }

        sqs_response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(deviation_message),
            MessageAttributes={
                'Source': {
                    'StringValue': 'PDF Upload',
                    'DataType': 'String'
                },
                'DeviationId': {
                    'StringValue': deviation_id,
                    'DataType': 'String'
                },
                'CreatedBy': {
                    'StringValue': _get_user_from_event(event),
                    'DataType': 'String'
                }
            }
        )

        print(f"PDF uploaded to S3 and deviation queued for processing: {deviation_id}")

        return _response(200, "PDF file uploaded and queued for processing successfully", {
            "file_id": file_id,
            "deviation_id": deviation_id,
            "filename": filename,
            "file_size": len(file_content),
            "s3_key": s3_key,
            "status": "processing",
            "message_id": sqs_response['MessageId']
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return _response(500, f"Internal server error: {str(e)}")


def parse_multipart_manual(body_bytes, content_type):
    try:
        boundary_match = re.search(rb'boundary=([^;]+)', content_type.encode())
        if not boundary_match:
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if not boundary_match:
                raise ValueError("No boundary found in Content-Type")
            boundary = boundary_match.group(1).strip('"').encode()
        else:
            boundary = boundary_match.group(1).strip(b'"')

        boundary_delimiter = b'--' + boundary
        parts = body_bytes.split(boundary_delimiter)

        for i, part in enumerate(parts[1:-1], 1):
            if len(part) < 10:
                continue

            if b'\r\n\r\n' in part:
                headers_section, content = part.split(b'\r\n\r\n', 1)
            elif b'\n\n' in part:
                headers_section, content = part.split(b'\n\n', 1)
            else:
                continue

            try:
                headers_text = headers_section.decode('utf-8', errors='ignore')
            except Exception:
                continue

            content_disposition_match = re.search(
                r'Content-Disposition:\s*form-data;\s*name="([^"]+)"(?:;\s*filename="([^"]*)")?',
                headers_text,
                re.IGNORECASE
            )

            if not content_disposition_match:
                continue

            field_name = content_disposition_match.group(1)
            filename = content_disposition_match.group(2)

            if filename is not None and filename.strip():
                content_type_match = re.search(
                    r'Content-Type:\s*([^\r\n]+)',
                    headers_text,
                    re.IGNORECASE
                )
                file_content_type = content_type_match.group(1).strip() if content_type_match else 'application/pdf'

                content = content.rstrip(b'\r\n')

                return {
                    'filename': filename.strip(),
                    'content': content,
                    'content_type': file_content_type,
                    'field_name': field_name
                }

        return None

    except Exception as e:
        print(f"Multipart parsing error: {str(e)}")
        return None


def _sanitize_filename(filename):
    if not filename:
        return "unknown_file.pdf"
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized


def _response(status_code, message, data=None):
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
        print(f"Error building connection string: {str(e)}")
        raise


def create_deviation_file_record(file_id, filename, s3_url, upload_by):
    try:
        conninfo = get_connection_string()

        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                insert_query = """
                INSERT INTO deviation_files (file_id, file_name, s3_url, upload_by) 
                VALUES (%s, %s, %s, %s)
                """

                cur.execute(insert_query, (file_id, filename, s3_url, upload_by))
                conn.commit()
                print(f"Created deviation file record with ID: {file_id}")

    except Exception as e:
        print(f"Database error creating deviation file record: {str(e)}")
        raise


def create_deviation_in_db(file_id):
    start_time = datetime.utcnow()
    try:
        conninfo = get_connection_string()

        with psycopg.connect(conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                insert_query = """
                INSERT INTO deviations (file_id) 
                VALUES (%s) 
                RETURNING deviation_id
                """
                cur.execute(insert_query, (file_id,))

                result = cur.fetchone()
                deviation_id = result['deviation_id']
                # ✅ LOG WORKFLOW STEP
                log_deviation_workflow(
                    conn,
                    deviation_id,
                    step="DEVIATION_CREATED",
                    input_data={
                        "file_id": file_id
                    },
                    output_data={
                        "deviation_id": deviation_id,
                        "status": "Pending"
                    },
                    start_time=start_time
                )

                conn.commit()
                print(f"Created deviation in database with ID: {deviation_id}")
                return deviation_id

    except Exception as e:
        print(f"Database error creating deviation: {str(e)}")
        raise


def _get_user_from_event(event):
    try:
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})

        if 'claims' in authorizer:
            return authorizer['claims'].get('email') or authorizer['claims'].get('sub')

        headers = event.get('headers', {})
        return headers.get('x-user-email') or headers.get('x-user-id') or 'anonymous'

    except Exception:
        return 'anonymous'
