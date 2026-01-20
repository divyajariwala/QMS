import json
import os
import logging
import psycopg
from utils import response, handle_cors_preflight, parse_event_body
from secrets_util import get_db_credentials

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
ENV = os.environ.get('env', 'dev')
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"


def update_rca_in_database(rca_id: int, deviation_id: str, issues: str, issues_category: str,
                           major_category: str, near_cause: str, near_cause_category: str,
                           root_cause: str, root_cause_category: str, updated_by: str = 'system'):
    """
    Update an existing RCA analysis in the database.
    
    Args:
        rca_id: The RCA record ID to update
        deviation_id: The deviation ID
        issues: Issues text
        issues_category: Issues dropdown category
        major_category: Major root cause category text
        near_cause: Near root cause text
        near_cause_category: Near root cause dropdown category
        root_cause: Root cause text
        root_cause_category: Root cause dropdown category
        updated_by: User who triggered the RCA update
        
    Returns:
        Dict with updated RCA metadata if successful
        
    Raises:
        Exception: If database operation fails or RCA not found
    """
    if not DB_SECRET_NAME:
        raise ValueError("DB_SECRET_NAME not configured")
    
    logger.info(f"Updating RCA ID: {rca_id}")
    
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
        
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # First check if RCA exists
                cur.execute("""
                    SELECT id FROM deviation_rca_analysis WHERE id = %s
                """, (rca_id,))
                
                if cur.fetchone() is None:
                    raise ValueError(f"RCA with ID {rca_id} not found")
                
                # Update the RCA
                cur.execute("""
                    UPDATE deviation_rca_analysis
                    SET
                        deviation_id = %s,
                        issues = %s,
                        issues_category = %s,
                        major_root_cause_category = %s,
                        major_root_cause_category_explanation = %s,
                        near_root_cause = %s,
                        near_root_cause_category = %s,
                        root_cause = %s,
                        root_cause_category = %s,
                        created_by = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, deviation_id, created_at, updated_at
                """, (
                    deviation_id,
                    issues,
                    issues_category,
                    major_category,
                    major_category,  # Using same value for explanation
                    near_cause,
                    near_cause_category,
                    root_cause,
                    root_cause_category,
                    updated_by,
                    rca_id
                ))
                
                result = cur.fetchone()
                conn.commit()
                
                rca_id_returned = result[0]
                deviation_id_returned = result[1]
                created_at = result[2].isoformat() if result[2] else None
                updated_at = result[3].isoformat() if result[3] else None
                
                logger.info(f"✅ Updated RCA in database: ID={rca_id_returned}")
                
                return {
                    'rca_id': rca_id_returned,
                    'deviation_id': deviation_id_returned,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'updated_by': updated_by
                }
                
    except ValueError as e:
        # Re-raise ValueError (RCA not found)
        raise
    except Exception as e:
        logger.error(f"❌ Error updating RCA in database: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Lambda handler for PUT /updateRCA endpoint
    
    Updates an existing RCA analysis in the database
    
    Expected request body:
    {
        "rca_id": 123,
        "deviation_id": "DV-00001",
        "issues": "Updated issues text...",
        "issues_category": "Process/Manufacturing Equipment Issue",
        "major_root_cause_category": "Design Issue",
        "major_root_cause_category_validated": "Design Issue",
        "near_root_cause": "Updated near root cause text...",
        "near_root_cause_category": "Design Input Issue",
        "root_cause": "Updated root cause text...",
        "root_cause_category": "Design Scope Issue",
        "updated_by": "user@example.com"
    }
    
    Response:
    {
        "success": true,
        "message": "RCA updated successfully",
        "data": {
            "rca_id": 123,
            "deviation_id": "DV-00001",
            "created_at": "2025-12-22T10:30:00",
            "updated_at": "2025-12-23T15:45:00",
            "updated_by": "user@example.com"
        }
    }
    """
    try:
        logger.info(f"Environment: {ENV}, Region: {AWS_REGION}")
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()
        
        # Only support PUT method
        if event.get('httpMethod') != 'PUT':
            return response(405, "Method not allowed. Use PUT.")
        
        # Parse event body
        body = parse_event_body(event)
        
        # Validate required fields
        required_fields = [
            'rca_id',
            'deviation_id',
            'issues',
            'issues_category',
            'major_root_cause_category',
            'near_root_cause',
            'near_root_cause_category',
            'root_cause',
            'root_cause_category'
        ]
        
        missing_fields = [field for field in required_fields if field not in body or body.get(field) is None]
        
        if missing_fields:
            return response(
                400,
                f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Extract fields
        rca_id = body['rca_id']
        deviation_id = body['deviation_id']
        issues = body['issues']
        issues_category = body['issues_category']
        major_category = body.get('major_root_cause_category_validated') or body['major_root_cause_category']
        near_cause = body['near_root_cause']
        near_cause_category = body['near_root_cause_category']
        root_cause = body['root_cause']
        root_cause_category = body['root_cause_category']
        updated_by = body.get('updated_by', 'system')
        
        # Validate field types
        if not isinstance(rca_id, int) or rca_id <= 0:
            return response(400, "rca_id must be a positive integer")
        
        if not isinstance(deviation_id, str) or not deviation_id.strip():
            return response(400, "deviation_id must be a non-empty string")
        
        if not isinstance(issues, str) or not issues.strip():
            return response(400, "issues must be a non-empty string")
        
        if not isinstance(major_category, str) or not major_category.strip():
            return response(400, "major_root_cause_category must be a non-empty string")
        
        if not isinstance(near_cause, str) or not near_cause.strip():
            return response(400, "near_root_cause must be a non-empty string")
        
        if not isinstance(root_cause, str) or not root_cause.strip():
            return response(400, "root_cause must be a non-empty string")
        
        logger.info(f"Updating RCA ID: {rca_id} for deviation: {deviation_id}")
        
        # Update in database
        result = update_rca_in_database(
            rca_id=rca_id,
            deviation_id=deviation_id,
            issues=issues,
            issues_category=issues_category,
            major_category=major_category,
            near_cause=near_cause,
            near_cause_category=near_cause_category,
            root_cause=root_cause,
            root_cause_category=root_cause_category,
            updated_by=updated_by
        )
        
        logger.info(f"✅ RCA update completed successfully for ID {rca_id}")
        
        return response(200, "RCA updated successfully", result)
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        return response(404, str(e))
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
