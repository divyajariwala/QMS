import fitz  # PyMuPDF
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

MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

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
    with open("toolspec.json") as f:
        return json.load(f)


# =========================
# Claude – PDF Document First
# =========================
def extract_from_pdf_document(pdf_bytes, pdf_name="document.pdf"):
    pdf_name = pdf_name.replace(".pdf", "")
    print("pdf_name", pdf_name)
    try:
        bedrock = boto3.client("bedrock-runtime")
        tool_spec = load_tool_spec()

        with open("prompt.txt") as f:
            prompt_text = f.read()

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

    except Exception as e:
        logger.error(f"PDF document extraction failed: {str(e)}")
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

    try:
        pdf_bytes = fetch_pdf_from_s3(message["s3path"])

        # PDF document extraction
        extracted = extract_from_pdf_document(
            pdf_bytes,
            os.path.basename(message["s3path"])
        )

        # Fallback to vision
        if not extracted or extracted.get("description") in ("", None, "N/A"):
            logger.info(f"Fallback to vision for deviation {deviation_id}")
            images = pdf_to_images(pdf_bytes)

            if images:
                extracted = extract_from_images(images)
                extracted["_extraction_method"] = "vision"
                print("image_extracted", extracted)
            else:
                extracted = {
                    "title": "Empty PDF",
                    "description": "N/A",
                    "immediate_steps_taken": "N/A",
                    "quality_risk_evaluation": "N/A",
                    "investigation_summary": "N/A",
                    "capa_plan": "N/A",
                    "recurrence_check_details": "N/A",
                    "effectiveness_check_plan": "N/A",
                    "_extraction_method": "empty_pdf"
                }
        else:
            extracted["_extraction_method"] = "pdf_document"

        update_deviation_in_db(deviation_id, extracted, start_time)

        return {"success": True, "deviation_id": deviation_id, "extracted_data": extracted}

    except Exception as e:
        logger.error(f"Deviation {deviation_id} failed: {str(e)}")
        raise


# =========================
# Lambda Handler
# =========================
def lambda_handler(event, context):
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