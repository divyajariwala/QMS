import json
import boto3
import base64
import os
import uuid
import re
from datetime import datetime, timezone

# Environment variables
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'qms-dev-initial-files')
SQS_QUEUE_NAME = os.environ.get('SQS_QUEUE_NAME', 'qms-dev-preload-complaints')
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.pdf', '.xls'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


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

        ##Extract PDF Data
        file_extension = _get_file_extension(filename)
        if file_extension == 'pdf':
            s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
            lambda_payload = {
                "s3_uri": s3_uri
            }
            lambda_response = lambda_client.invoke(
                FunctionName='qms-dev-extract-complaints',
                InvocationType='RequestResponse',
                Payload=json.dumps(lambda_payload)
            )
            pdf_contents = json.loads(lambda_response['Payload'].read().decode('utf-8'))


        # Send to SQS
        message = {
            "file_id": file_id,
            "filename": filename,
            "s3_key": s3_key,
            "s3_bucket": S3_BUCKET_NAME,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "file_size": len(file_content),
            "content_type": file_info.get('content_type', _get_content_type(filename)),
            "file_extension": _get_file_extension(filename),
            "pdf_contents": pdf_contents if file_extension == 'pdf' else None
        }

        # Send to SQS
        message = {
            "file_id": file_id,
            "filename": filename,
            "s3_key": s3_key,
            "s3_bucket": S3_BUCKET_NAME,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "file_size": len(file_content),
            "content_type": file_info.get('content_type', _get_content_type(filename)),
            "file_extension": _get_file_extension(filename)
        }

        sqs_response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                'FileType': {
                    'StringValue': _get_file_extension(filename),
                    'DataType': 'String'
                },
                'FileSize': {
                    'StringValue': str(len(file_content)),
                    'DataType': 'Number'
                }
            }
        )

        return _response(200, "File uploaded successfully", {
            "file_id": file_id,
            "filename": filename,
            "file_size": len(file_content),
            "s3_key": s3_key,
            "message_id": sqs_response['MessageId']
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
