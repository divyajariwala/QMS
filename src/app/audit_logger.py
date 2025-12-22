import json
from datetime import datetime
import psycopg

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
            conn.commit()
    except Exception as e:
        print(f"Workflow logging error: {str(e)}")

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
            conn.commit()
    except Exception as e:
        print(f"Audit logging error: {str(e)}")

def get_user_from_event(event):
    """Extract user from event context"""
    try:
        claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        return claims.get('email') or claims.get('cognito:username') or 'system'
    except:
        return 'system'
