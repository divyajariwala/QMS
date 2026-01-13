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
DB_SECRET_BASE_NAME = os.environ.get("db_secret_base_name", "aurora-postgres-master")
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"


# =====================================================
# SECTION NORMALIZER
# =====================================================
def normalize_grading_sections(sections: list) -> dict:
    """
    Converts UI label-content array into DB-ready column dictionary
    """
    label_map = {
        "Title": "title",
        "Overview": "overview",
        "Immediate Actions": "immediate_actions",
        "Quality Risk Evaluation": "quality_risk_evaluation",
        "Investigation Summary": "investigation_summary",
        "CAPA Plan": "capa_plan",
        "Recurrence Check": "recurrence_check",
        "Effectiveness Check": "effectiveness_check"
    }

    result = {}
    for item in sections:
        label = item.get("label")
        content = item.get("content")

        if label in label_map:
            result[label_map[label]] = content

    return result


# =====================================================
# SAVE GRADING TO DATABASE
# =====================================================
def save_grading_to_database(payload: dict, created_by: str):
    """
    Inserts grading data into deviation_grading table
    Updates deviations table to mark grading completed & approved
    """
    deviation_id = payload["deviation_id"]
    sections = payload["sections"]

    grading_data = normalize_grading_sections(sections)
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
            logger.info(f"Saving grading for deviation {deviation_id}")

            cur.execute("""
                INSERT INTO deviation_grading (
                    deviation_id,
                    title,
                    overview,
                    immediate_actions,
                    quality_risk_evaluation,
                    investigation_summary,
                    capa_plan,
                    recurrence_check,
                    effectiveness_check,
                    created_by
                ) VALUES (
                    %(deviation_id)s,
                    %(title)s,
                    %(overview)s,
                    %(immediate_actions)s,
                    %(quality_risk_evaluation)s,
                    %(investigation_summary)s,
                    %(capa_plan)s,
                    %(recurrence_check)s,
                    %(effectiveness_check)s,
                    %(created_by)s
                )
                RETURNING id
            """, {
                "deviation_id": deviation_id,
                "title": grading_data.get("title"),
                "overview": grading_data.get("overview"),
                "immediate_actions": grading_data.get("immediate_actions"),
                "quality_risk_evaluation": grading_data.get("quality_risk_evaluation"),
                "investigation_summary": grading_data.get("investigation_summary"),
                "capa_plan": grading_data.get("capa_plan"),
                "recurrence_check": grading_data.get("recurrence_check"),
                "effectiveness_check": grading_data.get("effectiveness_check"),
                "created_by": created_by
            })

            grading_id = cur.fetchone()[0]

            # =====================================================
            # UPDATE DEVIATIONS TABLE
            # =====================================================
            cur.execute("""
                UPDATE deviations
                SET
                    grading_completed = true,
                    grading_approved_date = CURRENT_TIMESTAMP
                WHERE deviation_id = %s
            """, (deviation_id,))

            # =====================================================
            # WORKFLOW LOG
            # =====================================================
            log_deviation_workflow(
                conn=conn,
                deviation_id=deviation_id,
                step="GRADING_SUBMITTED",
                input_data={
                    "sections_saved": list(grading_data.keys())
                },
                output_data={
                    "grading_id": grading_id,
                    "grading_completed": True
                },
                start_time=start_time
            )

            conn.commit()

            logger.info(f"Grading saved successfully. ID={grading_id}")

            return {
                "grading_id": grading_id,
                "deviation_id": deviation_id
            }


# =====================================================
# LAMBDA HANDLER
# =====================================================
def lambda_handler(event, context):
    """
    POST /submit-grading
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
        if not body.get("deviation_id"):
            return response(400, "deviation_id is required")

        if not isinstance(body.get("sections"), list) or not body["sections"]:
            return response(400, "sections must be a non-empty array")

        for idx, section in enumerate(body["sections"]):
            if not section.get("label") or not section.get("content"):
                return response(
                    400,
                    f"Section at index {idx} must contain label and content"
                )

        created_by = body.get("created_by", "system")

        result = save_grading_to_database(
            payload=body,
            created_by=created_by
        )

        return response(
            200,
            "Grading saved successfully",
            result
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return response(400, str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})