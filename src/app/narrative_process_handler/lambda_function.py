import json
import boto3
import base64
import os
import uuid
import re
from datetime import datetime, timezone

# Environment variables
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'narrative-upload-bucket')
SQS_QUEUE_URL = os.environ.get('SQS_QUEUE_URL',
                               'https://sqs.REGION.amazonaws.com/ACCOUNT_ID/narrative-processing-queue')
ALLOWED_EXTENSIONS = {'.csv', '.xlsx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def lambda_handler(event, context):
    try:
        # Initialize AWS clients
        s3_client = boto3.client('s3')
        sqs_client = boto3.client('sqs')

        # Validate request
        if "body" not in event:
            return _response(400, "No file provided")

        headers = event.get("headers", {})
        content_type = headers.get("content-type") or headers.get("Content-Type")

        if not content_type or 'multipart/form-data' not in content_type.lower():
            return _response(400, "Content-Type must be multipart/form-data")

        # Handle body encoding - CRITICAL: Keep as bytes for binary files
        if event.get("isBase64Encoded", False):
            body_bytes = base64.b64decode(event["body"])
        else:
            # For multipart with binary files, the body should already be bytes
            # If it's a string, it means API Gateway encoded it incorrectly
            body_str = event["body"]
            if isinstance(body_str, str):
                # Try to encode as latin-1 to preserve bytes
                body_bytes = body_str.encode('latin-1')
            else:
                body_bytes = body_str

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
            QueueUrl=SQS_QUEUE_URL,
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
        'xls': 'application/vnd.ms-excel'
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