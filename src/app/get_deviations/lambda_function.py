# Lambda function code here
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

# Load CRL mapping from JSON file
CRL_MAPPING_FILE = os.path.join(os.path.dirname(__file__), 'crl_mapping_lookup.json')
with open(CRL_MAPPING_FILE, 'r') as f:
    LABEL_TO_CRL = json.load(f)

# Create reverse mapping: CRL code -> Description
CRL_TO_LABEL = {v: k for k, v in LABEL_TO_CRL.items()}

# Get list of all CRL descriptions for frontend
CRL_DESCRIPTIONS = sorted(LABEL_TO_CRL.keys())


def lambda_handler(event, context):
    """
    Lambda function handler to retrieve deviation data from PostgreSQL.
    Supports three endpoints:
    - GET /getDeviation - Returns all complaints with stats
    - GET /getDeviation?deviation_status=Pending - Returns specific deviation details
    - GET /getDeviation?deviation_id=DV-XXX - Returns adverse events only and mixed cases
    """
    try:
        # Get database connection
        conn = get_db_connection()

        # Get query parameters
        query_parameters = event.get('queryStringParameters', {})
        deviation_status = query_parameters.get('deviation_status') if query_parameters else None
        deviation_id = query_parameters.get('deviation_id') if query_parameters else None
        page = int(query_parameters.get('page', 1)) if query_parameters and query_parameters.get('page') else 1
        status_filter = query_parameters.get('status') if query_parameters else None
        search_query = query_parameters.get('search') if query_parameters else None

        if deviation_status:
            # Handle single deviation request: /getDeviation?deviation_status=Pending
            return get_deviation_details_by_status(conn, deviation_status)
        elif deviation_id:
            # Handle adverse events request: /getDeviation?deviation_id=DV-XXX
            return get_case_by_deviationid(conn, deviation_id)
        else:
            # Handle all complaints request: getDeviation
            return get_all_deviation(conn, page, status_filter, search_query)

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

def get_all_deviation(conn, page=1, status_filter=None, search_query=None):
    """
    Get all deviation with statistics and pagination
    """
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            # # Update overdue deviations and refresh stats
            cursor.execute("SELECT update_deviations_and_stats()")
            conn.commit()
            # Get statistics from case_stats table
            cursor.execute("SELECT stat_name, stat_value FROM case_stats")
            stats_rows = cursor.fetchall()
            stats = {row['stat_name'].lower().replace(' ', '_'): row['stat_value'] for row in stats_rows}
            
            # Pagination parameters
            limit = 15
            offset = (page - 1) * limit
            
            # Handle search separately - search ignores status filter
            if search_query:
                # Get total count for search (exclude pure adverse events)
                cursor.execute("""
                    SELECT COUNT(*) as total FROM deviations 
                    WHERE deviation_id ILIKE %s
                    AND NOT (case_type NOT LIKE '%%,%%' AND (case_type ILIKE '%%adverse event%%' OR case_type ILIKE '%%adverse events%%'))
                """, (f"%{search_query}%",))
                total_count = cursor.fetchone()['total']

                # Get paginated search results (exclude pure adverse events)
                cursor.execute("""
                    SELECT deviation_id, created_at, deviation_status, description, grading_approved, rca_approved, grading_completed
                    FROM deviations
                    WHERE deviation_id ILIKE %s
                    AND NOT (case_type NOT LIKE '%%,%%' AND (case_type ILIKE '%%adverse event%%' OR case_type ILIKE '%%adverse events%%'))
                    ORDER BY deviation_id DESC
                    LIMIT %s OFFSET %s
                """, (f"%{search_query}%", limit, offset))
                search_results = cursor.fetchall()
                
                # Calculate pagination info
                total_pages = (total_count + limit - 1) // limit
                
                response_data = {
                    'caseStats': {
                        'total_complaints': stats.get('pending', 0) + stats.get('processed', 0) + stats.get('overdue', 0),
                        'pending': stats.get('pending', 0),
                        'processed': stats.get('processed', 0),
                        'overdue': stats.get('overdue', 0),
                        'avg_cycle_time': stats.get('avg_time', 0),
                        "rca_pending": stats.get('rca_pending', 0),
                        "rca_done": stats.get('rca_done', 0),
                        "grading_pending": stats.get('grading_pending', 0),
                    },
                    'pagination': {
                        'current_page': page,
                        'total_pages': total_pages,
                        'total_items': total_count,
                        'items_per_page': limit,
                        'has_next': page < total_pages,
                        'has_previous': page > 1
                    },
                    'search_results': [{
                        'case_id': c['deviation_id'],
                        'receipt_date': c['created_at'].isoformat() if c['created_at'] else '',
                        'deviation_description': c['description'],
                        'grading_approved': c.get('grading_approved', False),
                        'rca_approved': c.get('rca_approved', False),
                        'status': c['deviation_status'].lower(),
                        'grading_completed': c.get('grading_completed', False),
                    } for c in search_results]
                }
            else:
                # Normal flow - with optional status filter
                where_clause = "WHERE deviation_status = %s" if status_filter else ""
                params = [status_filter.title()] if status_filter else []
                
                # Get total count
                cursor.execute(f"SELECT COUNT(*) as total FROM deviations {where_clause}", params)
                total_count = cursor.fetchone()['total']
                
                # Get paginated complaints
                cursor.execute(f"""
                    SELECT deviation_id, created_at, deviation_status, description, grading_approved, rca_approved, grading_completed
                    FROM deviations
                    {where_clause}
                    ORDER BY deviation_id DESC
                    LIMIT %s OFFSET %s
                """, params + [limit, offset])
                paginated_complaints = cursor.fetchall()
                
                # Get complaints for status grouping
                if status_filter:
                    deviation_for_grouping = paginated_complaints
                else:
                    cursor.execute("""
                        SELECT deviation_id, created_at, deviation_status, description, grading_approved, rca_approved, grading_completed
                        FROM deviations
                        ORDER BY deviation_id DESC
                    """)
                    deviation_for_grouping = cursor.fetchall()
                
                # Group complaints by status
                case_status = _group_by_status(deviation_for_grouping)
                
                # Calculate pagination info
                total_pages = (total_count + limit - 1) // limit
            
                response_data = {
                    'caseStats': {
                        'total_complaints': stats.get('pending', 0) + stats.get('processed', 0) + stats.get('overdue', 0),
                        'pending': stats.get('pending', 0),
                        'processed': stats.get('processed', 0),
                        'overdue': stats.get('overdue', 0),
                        'avg_cycle_time': stats.get('avg_time', 0),
                        "rca_pending": stats.get('rca_pending', 0),
                        "rca_done": stats.get('rca_done', 0),
                        "grading_pending": stats.get('grading_pending', 0),
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
                    'deviations': [{
                        'case_id': c['deviation_id'],
                        'receipt_date': c['created_at'].isoformat() if c['created_at'] else '',
                        'deviation_description': c['description'],
                        'status': c['deviation_status'].lower(),
                        'grading_approved': c.get('grading_approved', False),
                        'rca_approved': c.get('rca_approved', False),
                        'grading_completed': c.get('grading_completed', False),
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

def get_case_by_deviationid(conn, deviation_id):
    """
        Fetch count of deviations grouped by deviation_status.
        Include all statuses: Pending, Overdue, Processed
    """
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            query = """
            SELECT
                deviation_status,
                COUNT(*) AS total_count
            FROM deviations
            GROUP BY deviation_status
            ORDER BY deviation_status;
            """

            cursor.execute(query)
            result = cursor.fetchall()
            print(result)
            return {
                        'statusCode': 200,
                        'headers': _get_cors_headers(),
                        'body': json.dumps(result, default=str)
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


def _group_by_status(complaints):
    """
    Group complaints by status for response, maintaining descending order by case_id
    """
    status_groups = {
        'pending': [],
        'processed': [],
        'overdue': []
    }

    for complaint in complaints:
        case_status = complaint['status'].lower()

        complaint_summary = {
                        'case_id': complaint['deviation_id'],
                        'receipt_date': complaint['created_at'].isoformat() if c['created_at'] else '',
                        'deviation_description': complaint['description'],
                        'status': complaint['deviation_status'].lower(),
                        'grading_approved': complaint.get('grading_approved', False),
                        'rca_approved': complaint.get('rca_approved', False),
                        'grading_completed': complaint.get('grading_completed', False),
                    }

        if case_status == 'pending':
            status_groups['pending'].append(complaint_summary)
        elif case_status == 'processed':
            status_groups['processed'].append(complaint_summary)
        elif case_status == 'overdue':
            status_groups['overdue'].append(complaint_summary)

    # Sort each status group by case_id in descending order
    for status in status_groups:
        status_groups[status].sort(key=lambda x: x['case_id'], reverse=True)

    return status_groups

def get_deviation_details_by_status(conn, status):
    """
    Get deviation details by deviation_status from both deviation and adverse_events tables
    """
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            query = """
               SELECT
                   deviation_id,
                   created_at,
                   deviation_status,
                   description,
                   grading_approved,
                   rca_approved
               FROM deviations
               WHERE deviation_status = %s
               ORDER BY created_at DESC;
               """

            cursor.execute(query, (status,))
            result = cursor.fetchall()
            print(result)
            return {
                        'statusCode': 200,
                        'headers': _get_cors_headers(),
                        'body': json.dumps(result, default=str)
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