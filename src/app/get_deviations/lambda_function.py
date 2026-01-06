import json
import os
import psycopg
from psycopg.rows import dict_row
from secrets_util import get_secret

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
    Supported APIs:
    - GET /getDeviation
    - GET /getDeviation?status=Pending
    - GET /getDeviation?deviation_id=DV-XXX
    - GET /getDeviation?page=1&search=DV
    """
    conn = None

    try:
        # Create DB connection
        conn = get_db_connection()

        # Read query parameters
        query_params = event.get("queryStringParameters") or {}
        deviation_id = query_params.get("deviation_id")
        status = query_params.get("status")
        page = int(query_params.get("page", 1))
        search = query_params.get("search")

        # If deviation_id is provided → fetch single record
        if deviation_id:
            return get_deviation_by_id(conn, deviation_id)

        # Otherwise → fetch paginated deviation list
        return get_all_deviations(conn, page, status, search)

    except Exception as e:
        print("Lambda error:", str(e))
        return {
            "statusCode": 500,
            "headers": _get_cors_headers(),
            "body": json.dumps({
                "success": False,
                "error": "Internal server error",
                "message": str(e)
            })
        }

    finally:
        if conn:
            conn.close()


# =====================================================
# GET ALL DEVIATIONS (LIST + SEARCH + PAGINATION)
# =====================================================
def get_all_deviations(conn, page=1, status_filter=None, search_query=None):
    try:
        with conn.cursor(row_factory=dict_row) as cursor:

            # Refresh deviation statistics
            cursor.execute("SELECT update_deviations_and_stats()")
            conn.commit()
            # Refresh avg cycle time
            cursor.execute("SELECT approved_avg_cycle_time()")
            conn.commit()

            # Fetch deviation statistics
            cursor.execute(
                "SELECT stat_name, stat_value FROM deviations_case_stats"
            )
            stats = {
                r["stat_name"].lower().replace(" ", "_"): int(r["stat_value"])
                for r in cursor.fetchall()
            }

            # Pagination config
            limit = 15
            offset = (page - 1) * limit

            # =================================================
            # SEARCH FLOW
            # =================================================
            if search_query:
                where_clauses = ["deviation_id ILIKE %s"]
                params = [f"%{search_query}%"]

                if status_filter:
                    where_clauses.append(
                        "LOWER(deviation_status) = LOWER(%s)"
                    )
                    params.append(status_filter)

                where = "WHERE " + " AND ".join(where_clauses)

                # Count query
                cursor.execute(
                    f"""
                    SELECT COUNT(*) AS total
                    FROM deviations
                    {where}
                    """,
                    params
                )
                total_count = cursor.fetchone()["total"]

                # Data query
                cursor.execute(
                    f"""
                    SELECT
                        deviation_id,
                        created_at,
                        deviation_status,
                        description,
                        grading_approved,
                        rca_approved,
                        grading_completed,
                        rca_generated,
                        text_extracted
                    FROM deviations
                    {where}
                    ORDER BY deviation_id DESC
                    LIMIT %s OFFSET %s
                    """,
                    params + [limit, offset]
                )
                rows = cursor.fetchall()

            # =================================================
            # NORMAL LIST FLOW (NO SEARCH)
            # =================================================
            else:
                where = ""
                params = []

                if status_filter:
                    where = "WHERE LOWER(deviation_status) = LOWER(%s)"
                    params.append(status_filter)

                # Count query
                cursor.execute(
                    f"SELECT COUNT(*) AS total FROM deviations {where}",
                    params
                )
                total_count = cursor.fetchone()["total"]

                # Data query
                cursor.execute(
                    f"""
                    SELECT
                        deviation_id,
                        created_at,
                        deviation_status,
                        description,
                        grading_approved,
                        rca_approved,
                        grading_completed,
                        rca_generated,
                        text_extracted
                    FROM deviations
                    {where}
                    ORDER BY deviation_id DESC
                    LIMIT %s OFFSET %s
                    """,
                    params + [limit, offset]
                )
                rows = cursor.fetchall()

            # Calculate total pages
            total_pages = (total_count + limit - 1) // limit
            # Final API response
            response = {
                "deviationStats": {
                    "total_deviations": (
                            stats.get("pending", 0)
                            + stats.get("processed", 0)
                            + stats.get("overdue", 0)
                    ),
                    "pending": stats.get("pending", 0),
                    "processed": stats.get("processed", 0),
                    "overdue": stats.get("overdue", 0),
                    "avg_cycle_time": stats.get("avg_cycle_time", 0),
                    "rca_pending": stats.get("rca_pending", 0),
                    "rca_done": stats.get("rca_done", 0),
                    "grading_pending": stats.get("grading_pending", 0),
                    "grading_done": stats.get("grading_done", 0),
                    "workflow_progress": stats.get("workflow_progress", 0),
                },
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_items": total_count,
                    "items_per_page": limit,
                    "has_next": page < total_pages,
                    "has_previous": page > 1,
                },
                "deviations": [
                    {
                        "deviation_id": r["deviation_id"],
                        "created_date": (
                            r["created_at"].isoformat()
                            if r["created_at"]
                            else ""
                        ),
                        "deviation_description": r["description"],
                        "status": r["deviation_status"].lower(),
                        "grading_approved": r["grading_approved"],
                        "rca_approved": r["rca_approved"],
                        "grading_completed": r["grading_completed"],
                        "rca_generated": r["rca_generated"],
                        "text_extracted": r["text_extracted"],
                    }
                    for r in rows
                ],
            }

            return {
                "statusCode": 200,
                "headers": _get_cors_headers(),
                "body": json.dumps(response, default=str),
            }

    except Exception as e:
        print("get_all_deviations error:", str(e))
        raise


# =====================================================
# GET DEVIATION BY ID
# =====================================================
def get_deviation_by_id(conn, deviation_id):
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT
                deviation_id,
                investigation_summary,
                created_at,
                deviation_status,
                grading_approved,
                rca_approved,
                grading_completed,
                rca_generated
            FROM deviations
            WHERE deviation_id = %s
            """,
            (deviation_id,),
        )

        row = cursor.fetchone()
        if not row:
            return {
                "statusCode": 404,
                "headers": _get_cors_headers(),
                "body": json.dumps({"error": "Deviation not found"}),
            }

        return {
            "statusCode": 200,
            "headers": _get_cors_headers(),
            "body": json.dumps({
                "deviation_id": row["deviation_id"],
                "investigation_summary": row["investigation_summary"],
                "created_date": (
                            row["created_at"].isoformat()
                            if row["created_at"]
                            else ""
                        ),
                "status": row["deviation_status"].lower(),
                "grading_approved": row["grading_approved"],
                "rca_approved": row["rca_approved"],
                "grading_completed": row["grading_completed"],
                "rca_generated": row["rca_generated"],
            }, default=str),
        }


# =====================================================
# DATABASE CONNECTION
# =====================================================
def get_db_connection():
    secret = get_secret(DB_SECRET_NAME, DB_REGION)

    return psycopg.connect(
        host=secret["host"],
        port=secret["port"],
        dbname=secret["dbname"],
        user=secret["username"],
        password=secret["password"],
    )


# =====================================================
# CORS HEADERS
# =====================================================
def _get_cors_headers():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
