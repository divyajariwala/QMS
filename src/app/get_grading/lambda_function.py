import json
import os
import logging
import psycopg
from psycopg.rows import dict_row
from secrets_util import get_secret

# =====================================================
# LOGGING CONFIGURATION
# =====================================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# =====================================================
# ENV CONFIG
# =====================================================
ENV = os.environ.get("env", "dev")
DB_SECRET_BASE_NAME = os.environ.get(
    "db_secret_base_name", "aurora-postgres-master"
)
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get("db_region", "us-east-1")


# =====================================================
# LAMBDA HANDLER
# =====================================================
def lambda_handler(event, context):
    """
    Lambda handler to fetch deviation grading details.

    Supported APIs:
    - GET /getGrading?deviation_id=DV-00001

    Query Parameters:
    - deviation_id (required)

    Returns:
    - 200 with grading details
    - 404 if deviation not found
    - 400 for bad request
    - 500 for internal server error
    """
    logger.info("Received event: %s", json.dumps(event))

    conn = None
    try:
        query_params = event.get("queryStringParameters") or {}
        deviation_id = query_params.get("deviation_id")

        if not deviation_id:
            return _response(
                400,
                {"error": "Missing required query parameter: deviation_id"}
            )

        conn = get_db_connection()
        return get_grading_by_deviation_id(conn, deviation_id)

    except psycopg.Error as db_err:
        logger.exception("Database error occurred")
        return _response(
            500,
            {
                "success": False,
                "error": "Database error",
                "message": str(db_err)
            }
        )

    except Exception as e:
        logger.exception("Unhandled exception occurred")
        return _response(
            500,
            {
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            }
        )

    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


# =====================================================
# GET GRADING DETAILS BY DEVIATION ID
# =====================================================
def get_grading_by_deviation_id(conn, deviation_id):
    """
    Fetch grading and RCA related details for a deviation.

    Args:
        conn (psycopg.Connection): Active DB connection
        deviation_id (str): Deviation ID (e.g., DV-00001)

    Returns:
        dict: API Gateway compatible response
    """
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT
                deviation_id,
                investigation_summary,
                description,
                immediate_steps_taken,
                capa_plan,
                created_at,
                deviation_status,
                title,
                quality_risk_evaluation,
                recurrence_check_details,
                effectiveness_check_plan,
                rca_generated,
                grading_completed,
                rca_approved,
                grading_approved,
                rca_approved_date,
                grading_approved_date
            FROM deviations
            WHERE deviation_id = %s
            """,
            (deviation_id,)
        )

        row = cursor.fetchone()

        if not row:
            return _response(
                404,
                {"error": "Deviation not found"}
            )

        return _response(
            200,
            {
                "deviation_id": row["deviation_id"],
                "title": row["title"],
                "description": row["description"],
                "investigation_summary": row["investigation_summary"],
                "immediate_steps_taken": row["immediate_steps_taken"],
                "capa_plan": row["capa_plan"],
                "deviation_status": row["deviation_status"],
                "quality_risk_evaluation": row["quality_risk_evaluation"],
                "recurrence_check_details": row["recurrence_check_details"],
                "effectiveness_check_plan": row["effectiveness_check_plan"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "rca_generated": row["rca_generated"],
                "grading_completed": row["grading_completed"],
                "rca_approved": row["rca_approved"],
                "grading_approved": row["grading_approved"]
            }
        )


# =====================================================
# DATABASE CONNECTION
# =====================================================
def get_db_connection():
    """
    Create and return a PostgreSQL database connection
    using credentials from AWS Secrets Manager.
    """
    secret = get_secret(DB_SECRET_NAME, DB_REGION)

    return psycopg.connect(
        host=secret["host"],
        port=secret["port"],
        dbname=secret["dbname"],
        user=secret["username"],
        password=secret["password"],
        connect_timeout=5
    )


# =====================================================
# RESPONSE & CORS HELPERS
# =====================================================
def _response(status_code, body):
    """
    Create a standard API Gateway response.
    """
    return {
        "statusCode": status_code,
        "headers": _get_cors_headers(),
        "body": json.dumps(body, default=str)
    }


def _get_cors_headers():
    """
    Return standard CORS headers.
    """
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }