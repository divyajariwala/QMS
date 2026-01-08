import json
from datetime import datetime
import psycopg
import logging

logger = logging.getLogger(__name__)

def log_workflow(conn, entity_id, step, input_data=None, output_data=None, start_time=None):
    """Log workflow step execution"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO workflow_logs (complaint_id, step, start_date, end_date, input, output)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                entity_id,
                step,
                start_time or datetime.utcnow(),
                datetime.utcnow(),
                json.dumps(input_data) if input_data else None,
                json.dumps(output_data) if output_data else None
            ))
    except Exception as e:
        logger.error(f"Workflow logging error: {str(e)}")
        raise

def log_audit(conn, entity_type, entity_id, changed_field, old_value, new_value, changed_by='system'):
    """Log audit trail for field changes"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO unified_audit (entity_type, entity_id, changed_field, old_value, new_value, changed_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                entity_type,
                entity_id,
                changed_field,
                str(old_value) if old_value is not None else None,
                str(new_value) if new_value is not None else None,
                changed_by
            ))
    except Exception as e:
        logger.error(f"Audit logging error: {str(e)}")
        raise

def get_user_from_event(event):
    """Extract user from event context"""
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        return claims.get('email') or claims.get('cognito:username') or 'system'
    except:
        return 'system'

def log_deviation_workflow(conn, entity_id, step, input_data=None, output_data=None, start_time=None):
    """Log workflow step execution"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO deviation_workflow_logs (deviation_id, step, start_date, end_date, input, output)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                entity_id,
                step,
                start_time or datetime.utcnow(),
                datetime.utcnow(),
                json.dumps(input_data) if input_data else None,
                json.dumps(output_data) if output_data else None
            ))
    except Exception as e:
        logger.error(f"Workflow logging error: {str(e)}")
        raise


def log_deviation_audit(conn, entity_type, deviation_id, new_fields, audit_type):
    """
    Log audit trail for deviation RCA / Grading updates

    """

    if entity_type not in ("RCA", "Grading"):
        raise ValueError("entity_type must be 'RCA' or 'Grading'")

    if not isinstance(new_fields, dict):
        raise ValueError("new_fields must be a dictionary")

    audit_timestamp = datetime.utcnow()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO deviation_field_audit (
                    entity_type,
                    deviation_id,
                    new_fields,
                    timestamp,
                    audit_type
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    entity_type,
                    deviation_id,
                    json.dumps(new_fields),
                    audit_timestamp,
                    audit_type
                )
            )
    except Exception as e:
        logger.error(f"Deviation audit logging error: {str(e)}")
        raise

