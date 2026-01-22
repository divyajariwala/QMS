import json
import io
import base64
import logging
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import fitz  # PyMuPDF
import boto3
import psycopg
from PIL import Image

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

# =========================
# Config
# =========================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_PDF_SIZE_MB = 50
ENV = os.environ.get('env', 'dev')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

_db_credentials = None
_connection_string = None


# =========================
# DB Utilities
# =========================
def get_connection_string():
    global _connection_string, _db_credentials
    if _connection_string:
        return _connection_string

    _db_credentials = get_secret(DB_SECRET_NAME, DB_REGION)
    _connection_string = (
        f"postgresql://{_db_credentials['username']}:"
        f"{_db_credentials['password']}@"
        f"{_db_credentials['host']}:"
        f"{_db_credentials.get('port', 5432)}/"
        f"{_db_credentials['dbname']}"
    )
    return _connection_string


# =========================
# S3
# =========================
def fetch_pdf_from_s3(s3_path):
    s3 = boto3.client("s3")
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts[0]
    key = "/".join(path_parts[1:])

    head = s3.head_object(Bucket=bucket, Key=key)
    size_mb = head["ContentLength"] / (1024 * 1024)
    if size_mb > MAX_PDF_SIZE_MB:
        raise ValueError(f"PDF too large: {size_mb:.1f} MB")

    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()


# =========================
# PDF → Images (Vision fallback)
# =========================
def pdf_to_images(pdf_bytes):
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)
        return images
    finally:
        doc.close()


def images_to_base64(images):
    encoded = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        encoded.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
    return encoded


def construct_vision_prompt(base64_images):
    content = []

    for img in base64_images:
        content.append({
            "image": {
                "format": "png",
                "source": {"bytes": base64.b64decode(img)}
            }
        })

    with open("prompt.txt") as f:
        content.append({"text": f.read()})

    return [{"role": "user", "content": content}]


# =========================
# Tool Spec
# =========================
def load_tool_spec():
    try:
        toolspec_path = os.path.join(os.path.dirname(__file__), "toolspec.json")
        logger.info(f"Loading toolspec from: {toolspec_path}")
        with open(toolspec_path) as f:
            spec = json.load(f)
            logger.info("Toolspec loaded successfully")
            return spec
    except Exception as e:
        logger.error(f"Failed to load toolspec: {str(e)}", exc_info=True)
        raise


# =========================
# Claude – PDF Document First (with timeout)
# =========================
def extract_from_pdf_document(pdf_bytes, pdf_name="document.pdf", timeout_seconds=480):
    """
    Extract data from PDF using Bedrock Document API.
    
    Args:
        pdf_bytes: PDF file bytes
        pdf_name: Name of the PDF file
        timeout_seconds: Maximum time to wait for Bedrock response (default 4 minutes)
    
    Returns:
        Extracted data dict or None if failed
    """
    pdf_name = pdf_name.replace(".pdf", "")
    logger.info(f"Starting PDF extraction for: {pdf_name}")
    logger.info(f"Timeout set to: {timeout_seconds} seconds")
    
    try:
        # Try to create client with config (production)
        try:
            bedrock = boto3.client(
                "bedrock-runtime",
                config=boto3.session.Config(
                    read_timeout=timeout_seconds,
                    connect_timeout=10,
                    retries={'max_attempts': 1}
                )
            )
        except TypeError:
            # Fallback for mocked boto3 in tests (doesn't accept config)
            bedrock = boto3.client("bedrock-runtime")
        
        tool_spec = load_tool_spec()

        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        logger.info(f"Loading prompt from: {prompt_path}")
        with open(prompt_path) as f:
            prompt_text = f.read()

        logger.info(f"Calling Bedrock Converse API with model: {MODEL_ID}")
        logger.info(f"PDF size: {len(pdf_bytes)} bytes ({len(pdf_bytes)/1024:.2f} KB)")
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "document": {
                        "name": pdf_name,
                        "format": "pdf",
                        "source": {"bytes": pdf_bytes}
                    }
                },
                {"text": prompt_text}
            ]
        }]

        # Call Bedrock with explicit timeout handling
        import time
        start_time = time.time()
        
        logger.info("Waiting for Bedrock response...")
        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=messages,
            toolConfig={
                "tools": [tool_spec],
                "toolChoice": {"auto": {}}
            }
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"✓ Bedrock response received in {elapsed_time:.2f} seconds")
        logger.info(f"Stop reason: {response.get('stopReason')}")
        logger.info(f"Usage: {response.get('usage', {})}")
        
        for item in response["output"]["message"]["content"]:
            if isinstance(item, dict) and "toolUse" in item:
                extracted_data = item["toolUse"]["input"]
                logger.info(f"✓ Successfully extracted data with {len(extracted_data)} fields")
                logger.info(f"Extracted fields: {list(extracted_data.keys())}")
                return extracted_data

        logger.warning("⚠ No toolUse found in response content")
        logger.warning(f"Response content: {response['output']['message']['content']}")
        return None

    except Exception as e:
        logger.error(f"✗ PDF document extraction failed: {str(e)}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        
        # Check if it's a timeout error
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            logger.error(f"⏱ TIMEOUT: Bedrock took longer than {timeout_seconds} seconds")
        
        return None


# =========================
# Claude – Vision Fallback
# =========================
def extract_from_images(images):
    bedrock = boto3.client("bedrock-runtime")
    tool_spec = load_tool_spec()

    base64_images = images_to_base64(images)
    messages = construct_vision_prompt(base64_images)

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=messages,
        toolConfig={
            "tools": [tool_spec],
            "toolChoice": {"auto": {}}
        }
    )

    for item in response["output"]["message"]["content"]:
        if isinstance(item, dict) and "toolUse" in item:
            return item["toolUse"]["input"]

    return None


# =========================
# DB Update
# =========================
def update_deviation_in_db(deviation_id, extracted, start_time):
    conninfo = get_connection_string()

    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute("""
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
            """, (
                extracted.get("title"),
                extracted.get("description"),
                extracted.get("immediate_steps_taken"),
                extracted.get("quality_risk_evaluation"),
                extracted.get("investigation_summary"),
                extracted.get("capa_plan"),
                extracted.get("recurrence_check_details"),
                extracted.get("effectiveness_check_plan"),
                deviation_id
            ))

            log_deviation_workflow(
                conn,
                deviation_id,
                step="TEXT_EXTRACTED",
                input_data={"source": extracted.get("_extraction_method")},
                output_data={"fields": list(extracted.keys())},
                start_time=start_time
            )

        conn.commit()


# =========================
# Main Processor
# =========================
def process_single_deviation(message):
    deviation_id = message.get("deviation_id")
    start_time = datetime.utcnow()

    logger.info(f"{'='*60}")
    logger.info(f"Processing deviation: {deviation_id}")
    logger.info(f"S3 path: {message.get('s3path')}")
    logger.info(f"{'='*60}")

    try:
        pdf_bytes = fetch_pdf_from_s3(message["s3path"])
        pdf_size_kb = len(pdf_bytes) / 1024
        logger.info(
            "✓ PDF fetched successfully. Size: %d bytes (%.2f KB)",
            len(pdf_bytes), pdf_size_kb
        )

        # Try PDF document extraction with timeout
        extracted = None
        extraction_method = None

        logger.info("→ Attempting PDF document extraction (timeout: 8 minutes)...")
        try:
            extracted = extract_from_pdf_document(
                pdf_bytes,
                os.path.basename(message["s3path"]),
                timeout_seconds=480  # 8 minutes timeout
            )
            
            if extracted and extracted.get("description") not in ("", None, "N/A"):
                extraction_method = "pdf_document"
                logger.info("✓ PDF document extraction successful!")
            else:
                logger.warning("⚠ PDF extraction returned empty/invalid data")
                extracted = None
                
        except Exception as e:
            logger.warning(f"⚠ PDF document extraction failed: {str(e)}")
            extracted = None

        # Fallback to vision if PDF extraction failed
        if not extracted:
            logger.info("→ Falling back to Vision API...")
            try:
                images = pdf_to_images(pdf_bytes)
                logger.info(f"✓ Converted PDF to {len(images)} images")

                if images:
                    logger.info("→ Calling Vision API...")
                    extracted = extract_from_images(images)
                    
                    if extracted and extracted.get("description") not in ("", None, "N/A"):
                        extraction_method = "vision"
                        logger.info("✓ Vision extraction successful!")
                    else:
                        logger.warning("⚠ Vision extraction returned empty/invalid data")
                        extracted = None
                else:
                    logger.error("✗ No images extracted from PDF")
                    
            except Exception as e:
                logger.error(f"✗ Vision extraction failed: {str(e)}", exc_info=True)
                extracted = None

        # Last resort: use default values
        if not extracted:
            logger.warning("⚠ All extraction methods failed, using default values")
            extracted = {
                "title": "Extraction Failed",
                "description": "Unable to extract data from PDF",
                "immediate_steps_taken": "N/A",
                "quality_risk_evaluation": "N/A",
                "investigation_summary": "N/A",
                "capa_plan": "N/A",
                "recurrence_check_details": "N/A",
                "effectiveness_check_plan": "N/A",
            }
            extraction_method = "failed"

        extracted["_extraction_method"] = extraction_method
        
        logger.info(f"→ Updating database for deviation: {deviation_id}")
        logger.info(f"Extraction method: {extraction_method}")
        update_deviation_in_db(deviation_id, extracted, start_time)
        logger.info(f"✓ Database updated successfully!")
        logger.info(f"{'='*60}")

        return {"success": True, "deviation_id": deviation_id, "extracted_data": extracted}

    except Exception as e:
        logger.error(f"{'='*60}")
        logger.error(f"✗ Deviation {deviation_id} processing failed!")
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error(f"{'='*60}")
        raise


# =========================
# Lambda Handler
# =========================
def lambda_handler(event, context):  # pylint: disable=unused-argument
    """
    AWS Lambda handler for processing deviation PDF extraction.

    Args:
        event: Lambda event containing deviation information
        context: Lambda context (unused)

    Returns:
        dict: Response with statusCode and body
    """
    try:
        if "Records" in event:
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(
                    executor.map(
                        lambda r: process_single_deviation(json.loads(r["body"])),
                        event["Records"]
                    )
                )
            return {"statusCode": 200, "body": json.dumps(results)}

        result = process_single_deviation(event)
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception:
        logger.exception("Lambda execution failed")
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False})
        }
