import json
import os
import logging
import psycopg
from utils import response, handle_cors_preflight, parse_event_body
from secrets_util import get_db_credentials
from datetime import datetime, timezone

# =====================================================
# WORKFLOW LOGGER IMPORT
# =====================================================
try:
    from audit_logger import log_deviation_workflow
except ImportError:
    import sys

    sys.path.append(os.path.dirname(__file__))
    from audit_logger import log_deviation_workflow

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
ENV = os.environ.get('env', 'dev')
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"


def save_rca_batch_to_database(rca_list: list, created_by: str = 'system'):
    """
    Save multiple RCA analyses in the database in a single transaction.

    Multiple RCAs can be saved for the same deviation_id.
    Also updates the deviations table to mark RCA as generated and approved.

    Args:
        rca_list: List of RCA dictionaries, each containing:
            - deviation_id: The deviation ID
            - problem_category: Problem category dropdown selection
            - problem_category_validated: Problem category explanation text
            - major_root_cause_category: Major root cause category text
            - major_root_cause_category_validated: Validated major category
            - near_root_cause: Near root cause text
            - near_root_cause_category: Near root cause dropdown category
            - root_cause: Root cause text
            - root_cause_category: Root cause dropdown category
        created_by: User who triggered the RCA submission

    Returns:
        Dict with list of saved RCA IDs and metadata

    Raises:
        Exception: If database operation fails
    """
    if not DB_SECRET_NAME:
        raise ValueError("DB_SECRET_NAME not configured")

    logger.info(f"Saving batch of {len(rca_list)} RCAs")
    start_time = datetime.now(timezone.utc)
    attempted_deviation_ids = {
        rca.get("deviation_id") for rca in rca_list if rca.get("deviation_id")
    }
    try:
        # Get database credentials from Secrets Manager
        db_creds = get_db_credentials(DB_SECRET_NAME, AWS_REGION)

        # Build connection string
        conn_string = (
            f"host={db_creds['host']} "
            f"port={db_creds.get('port', 5432)} "
            f"dbname={db_creds['dbname']} "
            f"user={db_creds['username']} "
            f"password={db_creds['password']} "
            f"sslmode=require"
        )

        saved_rcas = []
        deviation_ids_updated = set()

        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Process each RCA in the batch
                for idx, rca in enumerate(rca_list):
                    deviation_id = rca.get('deviation_id')
                    problem_category = rca.get('problem_category')
                    problem_category_validated = rca.get('problem_category_validated')

                    # Separate short name from long explanation
                    major_category = rca.get(
                        'major_root_cause_category')  # Short name (e.g., "Documentation and Records Issue")
                    major_category_explanation = rca.get('major_root_cause_category_validated')  # Long explanation text

                    near_cause = rca.get('near_root_cause')
                    near_cause_category = rca.get('near_root_cause_category')
                    root_cause = rca.get('root_cause')
                    root_cause_category = rca.get('root_cause_category')

                    # is_ai_generated flag (default to False if not provided)
                    is_ai_generated = rca.get('is_ai_generated', False)

                    logger.info(
                        f"Processing RCA {idx + 1}/{len(rca_list)} for deviation: {deviation_id} (AI generated: {is_ai_generated})")

                    # Insert RCA into rca_analysis table
                    cur.execute("""
                        INSERT INTO rca_analysis (
                            deviation_id,
                            problem_category,
                            problem_category_validated,
                            major_root_cause_category,
                            major_root_cause_category_explanation,
                            near_root_cause,
                            near_root_cause_category,
                            root_cause,
                            root_cause_category,
                            is_ai_generated,
                            created_by,
                            created_at,
                            updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                        RETURNING id, created_at, updated_at
                    """, (
                        deviation_id,
                        problem_category,
                        problem_category_validated,
                        major_category,  # Short name for category
                        major_category_explanation,  # Long text for explanation
                        near_cause,
                        near_cause_category,
                        root_cause,
                        root_cause_category,
                        is_ai_generated,
                        created_by
                    ))

                    result = cur.fetchone()

                    rca_id = result[0]
                    created_at = result[1].isoformat() if result[1] else None
                    updated_at = result[2].isoformat() if result[2] else None

                    saved_rcas.append({
                        'rca_id': rca_id,
                        'deviation_id': deviation_id,
                        'created_at': created_at,
                        'updated_at': updated_at
                    })

                    # Track deviation_ids to update
                    deviation_ids_updated.add(deviation_id)

                    logger.info(f"✅ Saved RCA {idx + 1}/{len(rca_list)}: ID={rca_id}, deviation={deviation_id}")

                # Update deviations table for each unique deviation_id
                for deviation_id in deviation_ids_updated:
                    logger.info(f"Updating deviations table for deviation: {deviation_id}")

                    cur.execute("""
                        UPDATE deviations
                        SET 
                            rca_generated = true,
                            rca_approved = true,
                            rca_approved_date = CURRENT_TIMESTAMP
                        WHERE deviation_id = %s
                        RETURNING deviation_id, rca_generated, rca_approved, rca_approved_date
                    """, (deviation_id,))

                    deviation_result = cur.fetchone()

                    if deviation_result:
                        logger.info(
                            f"✅ Updated deviation {deviation_result[0]}: rca_generated={deviation_result[1]}, rca_approved={deviation_result[2]}, rca_approved_date={deviation_result[3]}")
                    else:
                        logger.warning(f"⚠️ Deviation {deviation_id} not found in deviations table")
                    log_deviation_workflow(
                        conn,
                        deviation_id,
                        step="RCA_SUBMITTED",
                        input_data={
                            "rca_count": len(rca_list),
                            "is_ai_generated": any(
                                r.get("is_ai_generated", False) for r in rca_list
                            ),
                        },
                        output_data={
                            "saved_count": len(saved_rcas),
                            "rca_generated": True,
                            "rca_approved": True,
                        },
                        start_time=start_time
                    )
                # Commit all inserts and updates in a single transaction
                conn.commit()

                logger.info(
                    f"✅ Successfully saved batch of {len(saved_rcas)} RCAs and updated {len(deviation_ids_updated)} deviation(s)")

                return {
                    'saved_count': len(saved_rcas),
                    'rcas': saved_rcas,
                    'deviations_updated': list(deviation_ids_updated),
                    'created_by': created_by
                }

    except Exception as e:
        logger.error(f"❌ Error saving RCA batch to database: {str(e)}")
        # ===============================
        # FAILED WORKFLOW LOG (NEW CONN)
        # ===============================
        with psycopg.connect(conn_string) as fail_conn:
            for deviation_id in attempted_deviation_ids:
                log_deviation_workflow(
                    fail_conn,
                    deviation_id=deviation_id,
                    step="RCA_SUBMITTED_FAILED",
                    input_data={
                        "rca_count": len(rca_list),
                        "is_ai_generated": any(
                            r.get("is_ai_generated", False)
                            for r in rca_list
                        )
                    },
                    output_data={
                        "status": "FAILED",
                        "error": str(e)
                    },
                    start_time=start_time
                )
            fail_conn.commit()
        raise


def lambda_handler(event, context):
    """
    Lambda handler for POST /submit-rca endpoint

    Saves or updates RCA analysis in the database.
    Accepts either a single RCA object or an array of RCA objects.

    Expected request body (single RCA):
    {
        "deviation_id": "DV-00001",
        "problem_category": "Company Personnel Issue",
        "problem_category_validated": "Problem category text (60-65 words)...",
        "major_root_cause_category": "Personnel Issues",
        "major_root_cause_category_validated": "Major category text (60-65 words)...",
        "near_root_cause": "Near root cause text (60-65 words)...",
        "near_root_cause_category": "Training/Personnel Qualification Issue",
        "root_cause": "Root cause text (60-65 words)...",
        "root_cause_category": "Training Not Performed",
        "is_ai_generated": true,
        "created_by": "user@example.com"
    }

    Expected request body (multiple RCAs):
    [
        {
            "deviation_id": "DV-00001",
            "problem_category": "Company Personnel Issue",
            "problem_category_validated": "Problem category text...",
            "major_root_cause_category": "Personnel Issues",
            "major_root_cause_category_validated": "Major category text...",
            "near_root_cause": "Near root cause text...",
            "near_root_cause_category": "Training/Personnel Qualification Issue",
            "root_cause": "Root cause text...",
            "root_cause_category": "Training Not Performed",
            "is_ai_generated": true
        },
        {
            "deviation_id": "DV-00001",
            "problem_category": "Process/Manufacturing Equipment Issue",
            "problem_category_validated": "Another problem category...",
            "is_ai_generated": false,
            ...
        }
    ]

    Response (single RCA):
    {
        "success": true,
        "message": "RCA saved successfully",
        "data": {
            "rca_id": 123,
            "deviation_id": "DV-00001",
            "created_at": "2025-12-22T10:30:00",
            "updated_at": "2025-12-22T10:30:00",
            "created_by": "user@example.com",
            "deviations_updated": ["DV-00001"]
        }
    }

    Response (multiple RCAs):
    {
        "success": true,
        "message": "3 RCAs saved successfully",
        "data": {
            "saved_count": 3,
            "rcas": [
                {
                    "rca_id": 123,
                    "deviation_id": "DV-00001",
                    "created_at": "2025-12-22T10:30:00",
                    "updated_at": "2025-12-22T10:30:00"
                },
                ...
            ],
            "created_by": "user@example.com",
            "deviations_updated": ["DV-00001"]
        }
    }

    Database Updates:
    1. Inserts RCA(s) into rca_analysis table
    2. Updates deviations table:
       - Sets rca_generated = true
       - Sets rca_approved = true
       - Sets rca_approved_date = CURRENT_TIMESTAMP

    Field Descriptions:
    - problem_category: Selected category from official ABS map (e.g., "Company Personnel Issue")
    - problem_category_validated: AI-generated or user-entered explanation text (60-65 words for AI)
    - major_root_cause_category: Selected major category (e.g., "Personnel Issues")
    - major_root_cause_category_validated: AI-generated or user-entered explanation text (60-65 words for AI)
    - near_root_cause: AI-generated or user-entered explanation text (60-65 words for AI)
    - near_root_cause_category: Selected near root cause category
    - root_cause: AI-generated or user-entered explanation text (60-65 words for AI)
    - root_cause_category: Selected root cause category
    - is_ai_generated: Boolean flag (true if generated by AI, false if manual/edited)
    """
    try:
        logger.info(f"Environment: {ENV}, Region: {AWS_REGION}")
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()

        # Only support POST method
        if event.get('httpMethod') != 'POST':
            return response(405, "Method not allowed. Use POST.")

        # Parse event body
        body = parse_event_body(event)

        # Check if body is a list (batch) or single object
        is_batch = isinstance(body, list)

        if is_batch:
            # Batch processing
            if len(body) == 0:
                return response(400, "Request body cannot be an empty array")

            logger.info(f"Processing batch of {len(body)} RCAs")

            # Validate each RCA in the batch
            required_fields = [
                'deviation_id',
                'problem_category',
                'major_root_cause_category',
                'near_root_cause',
                'near_root_cause_category',
                'root_cause',
                'root_cause_category'
            ]

            for idx, rca in enumerate(body):
                if not isinstance(rca, dict):
                    return response(400, f"Item at index {idx} must be an object")

                missing_fields = [field for field in required_fields if not rca.get(field)]

                if missing_fields:
                    return response(
                        400,
                        f"Item at index {idx} missing required fields: {', '.join(missing_fields)}"
                    )

                # Validate field types
                if not isinstance(rca.get('problem_category'), str) or not rca['problem_category'].strip():
                    return response(400, f"Item at index {idx}: problem_category must be a non-empty string")

                if not isinstance(rca.get('major_root_cause_category'), str) or not rca[
                    'major_root_cause_category'].strip():
                    return response(400, f"Item at index {idx}: major_root_cause_category must be a non-empty string")

                if not isinstance(rca.get('near_root_cause'), str) or not rca['near_root_cause'].strip():
                    return response(400, f"Item at index {idx}: near_root_cause must be a non-empty string")

                if not isinstance(rca.get('root_cause'), str) or not rca['root_cause'].strip():
                    return response(400, f"Item at index {idx}: root_cause must be a non-empty string")

            # Extract created_by from first item or use default
            created_by = body[0].get('created_by', 'system')

            # Save batch to database
            result = save_rca_batch_to_database(
                rca_list=body,
                created_by=created_by
            )

            logger.info(f"✅ Batch RCA submission completed successfully: {result['saved_count']} RCAs saved")

            return response(200, f"{result['saved_count']} RCAs saved successfully", result)

        else:
            # Single RCA processing (backward compatibility)
            logger.info("Processing single RCA")

            # Validate required fields
            required_fields = [
                'deviation_id',
                'problem_category',
                'major_root_cause_category',
                'near_root_cause',
                'near_root_cause_category',
                'root_cause',
                'root_cause_category'
            ]

            missing_fields = [field for field in required_fields if not body.get(field)]

            if missing_fields:
                return response(
                    400,
                    f"Missing required fields: {', '.join(missing_fields)}"
                )

            # Validate field types
            if not isinstance(body.get('problem_category'), str) or not body['problem_category'].strip():
                return response(400, "problem_category must be a non-empty string")

            if not isinstance(body.get('major_root_cause_category'), str) or not body[
                'major_root_cause_category'].strip():
                return response(400, "major_root_cause_category must be a non-empty string")

            if not isinstance(body.get('near_root_cause'), str) or not body['near_root_cause'].strip():
                return response(400, "near_root_cause must be a non-empty string")

            if not isinstance(body.get('root_cause'), str) or not body['root_cause'].strip():
                return response(400, "root_cause must be a non-empty string")

            created_by = body.get('created_by', 'system')

            logger.info(f"Submitting single RCA for deviation: {body['deviation_id']}")

            # Save single RCA as a batch of 1
            result = save_rca_batch_to_database(
                rca_list=[body],
                created_by=created_by
            )

            # Extract single RCA result for backward compatibility
            single_result = result['rcas'][0]
            single_result['created_by'] = created_by
            single_result['deviations_updated'] = result['deviations_updated']

            logger.info(f"✅ Single RCA submission completed successfully for {body['deviation_id']}")

            return response(200, "RCA saved successfully", single_result)

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        return response(400, str(e))

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
