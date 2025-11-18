import json
import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
from secrets_util import get_secret

# Environment variables
ENV = os.environ.get('env', 'dev')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')

def lambda_handler(event, context):
    """
    Lambda function handler to retrieve complaints data from PostgreSQL.
    Supports two endpoints:
    - GET /getComplaints - Returns all complaints with stats
    - GET /getComplaints?complaint_id=CAS-xxx - Returns specific complaint details
    """
    try:
        # Get database connection
        conn = get_db_connection()
        
        # Get query parameters
        query_parameters = event.get('queryStringParameters', {})
        complaint_id = query_parameters.get('complaint_id') if query_parameters else None
        page = int(query_parameters.get('page', 1)) if query_parameters and query_parameters.get('page') else 1
        status_filter = query_parameters.get('status') if query_parameters else None
        
        if complaint_id:
            # Handle single complaint request: /getComplaints?complaint_id=xxx
            return get_single_complaint(conn, complaint_id)
        else:
            # Handle all complaints request: /getComplaints
            return get_all_complaints(conn, page, status_filter)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': _get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def get_single_complaint(conn, complaint_id):
    """
    Get single complaint details by complaint_id
    """
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Query complaint with inference data
            cursor.execute("""
                SELECT c.*, f.file_name, f.s3_url
                FROM complaints c
                LEFT JOIN files f ON c.file_id = f.file_id
                WHERE c.complaint_id = %s
            """, (complaint_id,))
            
            complaint = cursor.fetchone()
            
            if not complaint:
                return {
                    'statusCode': 404,
                    'headers': _get_cors_headers(),
                    'body': json.dumps({
                        'success': False,
                        'error': 'Complaint not found'
                    })
                }
            
            # Get inference data
            cursor.execute("""
                SELECT * FROM inference WHERE complaint_id = %s ORDER BY priority
            """, (complaint_id,))
            
            inferences = cursor.fetchall()

            # Transform inference data to category details
            category_details = []
            for inf in inferences:
                category_details.append({
                    "id": inf['id'] or str(inf['priority']),
                    "label": inf['label'],
                    "level": inf['priority'],
                    "crl": inf['crl'],
                    "priority": "High" if inf['priority'] <= 2 else "Medium" if inf['priority'] <= 4 else "Low",
                    "unit": inf['unit'],
                    "percentage": inf['percentage']
                })
        
            # Transform database record to response format
            complaint_details = {
                'case_id': complaint['complaint_id'],
                'receipt_date': complaint['receipt_date'].isoformat() if complaint['receipt_date'] else '',
                'criticality': complaint['criticality'] or 'NA',
                'report_type': complaint['report_type'] or 'NA',
                'ai_summary': complaint['narrative_summary'] or '',
                'case_type': complaint['case_type'].split(',') if complaint['case_type'] else [],
                'narrative': complaint['narrative'] or '',
                'primary_reporter': {
                    'name': complaint['primary_reporter'] or '',
                    'address': complaint['primary_reporter_address'] or ''
                },
                'patient_name': complaint['patient_name'] or '',
                'physician_name': complaint['physician'] or '',
                'product_details': {
                    'drug': complaint['drug'] or '',
                    'lot_no': complaint['lot_no'] or '',
                    'dosage': complaint['dosage'] or '',
                    'expiration_date': complaint['expiration_date'].isoformat() if complaint['expiration_date'] else '',
                    'part_number': complaint['part_number'] or ''
                },
                'caseStatus': complaint['status'].lower(),
                'category_details': category_details
            }
        
            return {
                'statusCode': 200,
                'headers': _get_cors_headers(),
                'body': json.dumps(complaint_details, default=str)
            }
        
    except Exception as e:
        print(f"Error getting single complaint: {str(e)}")
        return {
            'statusCode': 500,
            'headers': _get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': 'Failed to retrieve complaint',
                'message': str(e)
            })
        }
    finally:
        if conn:
            conn.close()

def get_all_complaints(conn, page=1, status_filter=None):
    """
    Get all complaints with statistics and pagination
    """
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Get statistics from case_stats table
            cursor.execute("SELECT stat_name, stat_value FROM case_stats")
            stats_rows = cursor.fetchall()
            stats = {row['stat_name'].lower().replace(' ', '_'): row['stat_value'] for row in stats_rows}
            
            # Pagination parameters
            limit = 15
            offset = (page - 1) * limit
            
            # Build query with optional status filter
            where_clause = "WHERE status = %s" if status_filter else ""
            params = [status_filter.title()] if status_filter else []
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM complaints {where_clause}", params)
            total_count = cursor.fetchone()['total']
            
            # Get paginated complaints
            cursor.execute(f"""
                SELECT complaint_id, criticality, report_type, receipt_date, case_type, status
                FROM complaints
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            paginated_complaints = cursor.fetchall()
            
            # Get all complaints for status grouping (without pagination)
            cursor.execute("""
                SELECT complaint_id, criticality, report_type, receipt_date, case_type, status
                FROM complaints
                ORDER BY created_at DESC
            """)
            all_complaints = cursor.fetchall()
            
            # Group complaints by status
            case_status = _group_by_status(all_complaints)
            
            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit
        
            response_data = {
                'caseStats': {
                    'total_complaints': len(all_complaints),
                    'pending': stats.get('pending', 0),
                    'processed': stats.get('processed', 0),
                    'overdue': stats.get('overdue', 0),
                    'avg_cycle_time': stats.get('avg_time', 0),
                    'best_time': stats.get('best_time', 0),
                    'longest_time': stats.get('longest_time', 0)
                },
                'caseStatus': case_status,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total_count,
                    'items_per_page': limit,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                },
                'complaints': [{
                    'case_id': c['complaint_id'],
                    'criticality': c['criticality'] or 'NA',
                    'report_type': c['report_type'] or 'NA',
                    'receipt_date': c['receipt_date'].isoformat() if c['receipt_date'] else '',
                    'case_type': c['case_type'].split(',') if c['case_type'] else [],
                    'status': c['status'].lower()
                } for c in paginated_complaints]
            }
            
            return {
                'statusCode': 200,
                'headers': _get_cors_headers(),
                'body': json.dumps(response_data, default=str)
            }
        
    except Exception as e:
        print(f"Error getting all complaints: {str(e)}")
        return {
            'statusCode': 500,
            'headers': _get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': 'Failed to retrieve complaints',
                'message': str(e)
            })
        }
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """
    Get database connection using secrets manager
    """
    try:
        secret = get_secret(DB_SECRET_NAME, DB_REGION)
        
        conn = psycopg.connect(
            host=secret['host'],
            port=secret['port'],
            dbname=secret['dbname'],
            user=secret['username'],
            password=secret['password']
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise e

def _group_by_status(complaints):
    """
    Group complaints by status for response
    """
    status_groups = {
        'pending': [],
        'processed': [],
        'overdue': []
    }
    
    for complaint in complaints:
        case_status = complaint['status'].lower()
        
        complaint_summary = {
            'case_id': complaint['complaint_id'],
            'criticality': complaint['criticality'] or 'NA',
            'report_type': complaint['report_type'] or 'NA',
            'receipt_date': complaint['receipt_date'].isoformat() if complaint['receipt_date'] else '',
            'case_type': complaint['case_type'].split(',') if complaint['case_type'] else []
        }
        
        if case_status == 'pending':
            status_groups['pending'].append(complaint_summary)
        elif case_status == 'processed':
            status_groups['processed'].append(complaint_summary)
        elif case_status == 'overdue':
            status_groups['overdue'].append(complaint_summary)
    
    return status_groups

def _get_cors_headers():
    """
    Return CORS headers for API Gateway
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }