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
        search_query = query_parameters.get('search') if query_parameters else None
        
        if complaint_id:
            # Handle single complaint request: /getComplaints?complaint_id=xxx
            return get_single_complaint(conn, complaint_id)
        else:
            # Handle all complaints request: /getComplaints
            return get_all_complaints(conn, page, status_filter, search_query)
            
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
            
            # Get category details based on complaint status
            category_details = []
            inference_result = None
            
            if complaint['status'].lower() == 'processed':
                # For processed complaints, get from processed_complaints table
                cursor.execute("""
                    SELECT approved_category_details FROM processed_complaints WHERE complaint_id = %s
                """, (complaint_id,))
                processed_result = cursor.fetchone()
                if processed_result and processed_result.get('approved_category_details'):
                    category_details = processed_result['approved_category_details']
                    inference_result = True  # Mark as classified
            else:
                # For pending complaints, get from inference_results table
                cursor.execute("""
                    SELECT * FROM inference_results WHERE complaint_id = %s ORDER BY created_at DESC LIMIT 1
                """, (complaint_id,))
                
                inference_result = cursor.fetchone()

                # Transform inference data to category details
                if inference_result and isinstance(inference_result, dict):
                    levels_raw = inference_result.get('levels')
                    subcategories_raw = inference_result.get('subcategories')
                    crl_codes_raw = inference_result.get('crl_codes')
                    
                    levels = levels_raw if isinstance(levels_raw, dict) else {}
                    subcategories = subcategories_raw if isinstance(subcategories_raw, dict) else {}
                    crl_codes = crl_codes_raw if isinstance(crl_codes_raw, dict) else {}
                    units = inference_result.get('units', 0)
                    priority = inference_result.get('priority', 0)
                    priority_str = "Low" if priority == 0 else "High" if priority <= 2 else "Medium" if priority <= 4 else "Low"
                    
                    # Convert to lists maintaining order
                    level_items = list(levels.items())
                    subcat_items = list(subcategories.items())
                    crl_items = list(crl_codes.items())
                    
                    # Create array with sequential IDs
                    for idx in range(len(subcat_items)):
                        level_key = level_items[idx][0] if idx < len(level_items) else ''
                        subcat_label = subcat_items[idx][0] if idx < len(subcat_items) else ''
                        subcat_pct = subcat_items[idx][1] if idx < len(subcat_items) else 0
                        crl_code = crl_items[idx][0] if idx < len(crl_items) else ''
                        
                        # Map CRL code to description using mapping
                        if crl_code == 'UNASSIGNED' or not crl_code:
                            crl_label = 'Unknown'
                        else:
                            crl_label = CRL_TO_LABEL.get(crl_code, 'Unknown')
                        
                        category_details.append({
                            "id": str(idx + 1),
                            "label": subcat_label,
                            "level": level_key,
                            "crl": crl_label,
                            "priority": priority_str,
                            "unit": units,
                            "percentage": subcat_pct * 100
                        })
        
            # Transform database record to response format
            complaint_details = {
                'case_id': complaint['complaint_id'],
                'receipt_date': complaint['receipt_date'].isoformat() if complaint['receipt_date'] else '',
                'created_at': complaint['created_at'].isoformat() if complaint.get('created_at') else '',
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
                'text_extracted': complaint.get('text_extracted', False),
                'complaintClassified': inference_result is not None,
                'category_details': category_details
            }
            
            # Add crl_list and label_list if complaint is classified
            if inference_result is not None:
                # Get label list from database and update with new subcategories
                label_list = _get_and_update_label_list(cursor, category_details)
                conn.commit()  # Commit new labels to database
                complaint_details['crl_list'] = CRL_DESCRIPTIONS
                complaint_details['label_list'] = label_list
        
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

def get_all_complaints(conn, page=1, status_filter=None, search_query=None):
    """
    Get all complaints with statistics and pagination
    """
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Update overdue complaints and refresh stats
            cursor.execute("SELECT update_complaints_and_stats()")
            conn.commit()
            # Get statistics from case_stats table
            cursor.execute("SELECT stat_name, stat_value FROM case_stats")
            stats_rows = cursor.fetchall()
            stats = {row['stat_name'].lower().replace(' ', '_'): row['stat_value'] for row in stats_rows}
            
            # Pagination parameters
            limit = 15
            offset = (page - 1) * limit
            
            # Build query with optional status filter and search
            where_conditions = []
            params = []
            
            if status_filter:
                where_conditions.append("status = %s")
                params.append(status_filter.title())
            
            if search_query:
                where_conditions.append("complaint_id ILIKE %s")
                params.append(f"%{search_query}%")
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM complaints {where_clause}", params)
            total_count = cursor.fetchone()['total']
            
            # Get paginated complaints
            cursor.execute(f"""
                SELECT complaint_id, criticality, report_type, receipt_date, case_type, status, text_extracted, created_at
                FROM complaints
                {where_clause}
                ORDER BY complaint_id DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            paginated_complaints = cursor.fetchall()
            
            # Get complaints for status grouping based on filters
            if status_filter or search_query:
                # When filtering, only return filtered results in caseStatus
                complaints_for_grouping = paginated_complaints
            else:
                # When no filter, get all complaints for status grouping
                cursor.execute("""
                    SELECT complaint_id, criticality, report_type, receipt_date, case_type, status, text_extracted, created_at
                    FROM complaints
                    ORDER BY complaint_id DESC
                """)
                complaints_for_grouping = cursor.fetchall()
            
            # Group complaints by status
            case_status = _group_by_status(complaints_for_grouping)
            
            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit
        
            response_data = {
                'caseStats': {
                    'total_complaints': stats.get('pending', 0) + stats.get('processed', 0) + stats.get('overdue', 0),
                    'pending': stats.get('pending', 0),
                    'processed': stats.get('processed', 0),
                    'overdue': stats.get('overdue', 0),
                    'avg_cycle_time': stats.get('avg_time', 0)
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
                    'status': c['status'].lower(),
                    'text_extracted': c.get('text_extracted', False),
                    'created_at': c['created_at'].isoformat() if c.get('created_at') else ''
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
            'case_id': complaint['complaint_id'],
            'criticality': complaint['criticality'] or 'NA',
            'report_type': complaint['report_type'] or 'NA',
            'receipt_date': complaint['receipt_date'].isoformat() if complaint['receipt_date'] else '',
            'case_type': complaint['case_type'].split(',') if complaint['case_type'] else [],
            'text_extracted': complaint.get('text_extracted', False),
            'created_at': complaint['created_at'].isoformat() if complaint.get('created_at') else ''
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

def _get_and_update_label_list(cursor, category_details):
    """
    Get label list from database and add any new subcategories from category_details
    """
    # Get current label list from database
    cursor.execute("SELECT label FROM label_list ORDER BY label")
    label_rows = cursor.fetchall()
    label_list = [row['label'] for row in label_rows]
    
    # Extract subcategories from category_details
    new_labels = [detail['label'] for detail in category_details if detail.get('label')]
    
    # Add new labels that don't exist
    for label in new_labels:
        if label and label not in label_list:
            cursor.execute("INSERT INTO label_list (label) VALUES (%s) ON CONFLICT (label) DO NOTHING", (label,))
            label_list.append(label)
    
    return sorted(label_list)

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