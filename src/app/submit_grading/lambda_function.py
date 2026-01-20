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
    from audit_logger import log_deviation_workflow, log_deviation_audit
except ImportError:
    import sys

    sys.path.append(os.path.dirname(__file__))
    from audit_logger import log_deviation_workflow, log_deviation_audit

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


def is_any_section_edited(sections: list) -> dict:
    """
    Returns True if any section has isEdited = True
    """
    updated_filed = []
    for section in sections:
        if section.get("isEdited") is True:
            updated_filed.append(section.get("label"))
    return {"labels": updated_filed}


# =====================================================
# UPDATE GRADING AUDIT LOG
# =====================================================

def save_grading_audit_log(conn, sections, deviation_id):
    """
    Save Grading-related audit logs for a deviation.

    This function extracts relevant grading lebels and logs an audit entry
    based on whether the Grading edited.
    """

    updated_labels = is_any_section_edited(sections)
    # If grading was edited, log EDITED audit
    if updated_labels['labels']:
        log_deviation_audit(
            conn=conn,
            entity_type="Grading",
            deviation_id=deviation_id,
            new_fields=updated_labels,
            audit_type="EDITED"
        )


# =====================================================
# SAVE EXECUTIVE SUMMARY
# =====================================================
def save_executive_summary(cur, deviation_id: str, sections: list):
    """
    Save executive summary sections to deviation_grading_executive table

    Args:
        cur: Database cursor
        deviation_id: The deviation ID (e.g., "DV-00001")
        sections: List of executive summary sections with format:
                 [{"label": "Title", "content": "<p>...</p>",
                   "isEdited": false}, ...]
    """
    if not sections:
        logger.info("No executive summary sections to save for %s",
                    deviation_id)
        return

    logger.info("Saving executive summary for %s with %d sections",
                deviation_id, len(sections))

    # Transform sections to match expected format (remove isEdited field)
    summary_data = [
        {"label": section["label"], "content": section["content"]}
        for section in sections
    ]

    # Update executive_summary column in deviation_grading_executive
    cur.execute("""
        UPDATE deviation_grading_executive
        SET
            executive_summary = %s::jsonb,
            updated_date = CURRENT_TIMESTAMP
        WHERE deviation_id = %s
    """, (json.dumps(summary_data), deviation_id))

    if cur.rowcount == 0:
        # If no record exists, insert one
        logger.warning("No grading record found for %s, inserting new record",
                       deviation_id)
        cur.execute("""
            INSERT INTO deviation_grading_executive (
                deviation_id,
                executive_summary,
                updated_date
            ) VALUES (%s, %s::jsonb, CURRENT_TIMESTAMP)
        """, (deviation_id, json.dumps(summary_data)))

    logger.info("✅ Executive summary saved successfully for %s",
                deviation_id)


# =====================================================
# UPDATE GRADING STATUS ONLY
# =====================================================
def update_grading_status(deviation_id: str, sections: list):
    """
    Marks grading as completed for a deviation and saves executive summary

    Args:
        deviation_id: The deviation ID
        sections: List of executive summary sections with format:
                 [{"label": "Title", "content": "<p>...</p>",
                   "isEdited": false}, ...]
                 Used for both audit logging and saving executive summary
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
            logger.info("Updating grading status for deviation %s",
                        deviation_id)

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
            # SAVE EXECUTIVE SUMMARY
            # ==============================
            save_executive_summary(cur, deviation_id, sections)

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
            save_grading_audit_log(conn, sections, deviation_id)

            conn.commit()

    logger.info("Grading status updated successfully for %s", deviation_id)

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
        "created_by": "user@example.com",
        "sections": [
            {"label": "Title", "content": "<p>HTML content</p>",
             "isEdited": false},
            {"label": "Overview", "content": "<p>HTML content</p>",
             "isEdited": false},
            {"label": "Immediate Actions",
             "content": "<ul><li>Action 1</li></ul>", "isEdited": false},
            {"label": "Quality Risk Evaluation",
             "content": "<ol><li>Risk 1</li></ol>", "isEdited": false},
            {"label": "Investigation Summary",
             "content": "<p>Investigation details</p>", "isEdited": false},
            {"label": "CAPA Plan",
             "content": "<ul><li>CAPA 1</li></ul>", "isEdited": false},
            {"label": "Recurrence Check",
             "content": "<p>Recurrence check</p>", "isEdited": false},
            {"label": "Effectiveness Check",
             "content": "<p>Effectiveness check</p>", "isEdited": false}
        ]
    }

    The sections field contains the executive summary content and is saved
    to the deviation_grading_executive table. The isEdited field is used
    for audit logging to track which sections were modified by the user.
    """
    try:
        logger.info("Received event: %s", json.dumps(event))

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
            deviation_id=deviation_id,
            sections=body.get("sections", [])
        )

        return response(
            200,
            "Grading status updated successfully",
            result
        )

    except ValueError as e:
        logger.error("Validation error: %s", str(e))
        return response(400, str(e))

    except Exception as e:
        logger.exception("Unexpected error")
        return response(
            500,
            "Internal server error",
            {"details": str(e)}
        )
