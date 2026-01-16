import json
import os
import logging
import psycopg
from datetime import datetime, timezone

from utils import response, handle_cors_preflight, parse_event_body
from secrets_util import get_db_credentials

# =====================================================
# WORKFLOW LOGGER IMPORT
# =====================================================
try:
    from audit_logger import log_deviation_workflow
except ImportError:
    import sys

    sys.path.append(os.path.dirname(__file__))
    from audit_logger import log_deviation_workflow

# =====================================================
# LOGGING
# =====================================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# =====================================================
# ENV CONFIG
# =====================================================
ENV = os.environ.get("env", "dev")
AWS_REGION = os.environ.get("aws_region", "us-east-1")
DB_SECRET_BASE_NAME = os.environ.get(
    "db_secret_base_name", "aurora-postgres-master"
)
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"


# =====================================================
# UPDATE GRADING STATUS ONLY
# =====================================================
def update_grading_status(deviation_id: str):
    """
    Marks grading as completed for a deviation
    """
    start_time = datetime.now(timezone.utc)

    if not DB_SECRET_NAME:
        raise ValueError("DB_SECRET_NAME not configured")

    db_creds = get_db_credentials(DB_SECRET_NAME, AWS_REGION)

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
            logger.info(f"Updating grading status for deviation {deviation_id}")

            # ==============================
            # UPDATE DEVIATIONS TABLE
            # ==============================
            cur.execute(
                """
                UPDATE deviations
                SET grading_completed = TRUE,
                    grading_approved_date = CURRENT_TIMESTAMP
                WHERE deviation_id = %s
                """,
                (deviation_id,)
            )

            if cur.rowcount == 0:
                raise ValueError(f"Deviation ID not found: {deviation_id}")

            cur.execute(
                """
                UPDATE deviations
                SET deviation_status = 'Processed'
                WHERE deviation_id = %s
                AND grading_completed = true
                AND rca_approved = true
                AND deviation_status IS DISTINCT FROM 'Processed'
                """,
                (deviation_id,),
            )

            # ==============================
            # WORKFLOW LOG
            # ==============================
            log_deviation_workflow(
                conn,
                deviation_id,
                step="GRADING_SUBMITTED",
                input_data={
                    "action": "grading_completed",
                },
                output_data={
                    "deviation_id": deviation_id,
                    "grading_completed": True
                },
                start_time=start_time
            )

            conn.commit()

    logger.info(f"Grading status updated successfully for {deviation_id}")

    return {
        "deviation_id": deviation_id,
        "grading_completed": True
    }


# =====================================================
# LAMBDA HANDLER
# =====================================================
def lambda_handler(event, context):
    """
    POST /submit-grading
    Payload:
    {
        "deviation_id": "DV-00105",
        "created_by": "user@example.com"
    }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        if event.get("httpMethod") == "OPTIONS":
            return handle_cors_preflight()

        if event.get("httpMethod") != "POST":
            return response(405, "Method not allowed. Use POST.")

        body = parse_event_body(event)

        # ==============================
        # BASIC VALIDATION
        # ==============================
        deviation_id = body.get("deviation_id")
        if not deviation_id:
            return response(400, "deviation_id is required")

        result = update_grading_status(
            deviation_id=deviation_id
        )

        return response(
            200,
            "Grading status updated successfully",
            result
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return response(400, str(e))

    except Exception as e:
        logger.exception("Unexpected error")
        return response(
            500,
            "Internal server error",
            {"details": str(e)}
        )