import json
import os
import logging
from utils import response, handle_cors_preflight

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def load_rca_categories():
    """
    Load RCA category options from rca-edit-data.json
    Excludes 'definition' and 'number' fields to reduce payload size
    
    Returns:
        Dict with category options for RCA dropdowns
    """
    try:
        # Try different possible paths for Lambda deployment
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'rca-edit-data.json'),
            os.path.join('/var/task', 'rca-edit-data.json'),
            'rca-edit-data.json'
        ]
        
        for json_path in possible_paths:
            if os.path.exists(json_path):
                logger.info(f"Loading RCA categories from: {json_path}")
                
                with open(json_path, 'r', encoding='utf-8') as file:
                    rca_data = json.load(file)
                    
                    # Process Factors (Problem Categories grouped by factor)
                    factors = []
                    for factor in rca_data.get('Factors', []):
                        factor_obj = {
                            'factor_name': factor['factor_name'],
                            'ProblemCategories': []
                        }
                        
                        for category in factor.get('ProblemCategories', []):
                            # Exclude 'definition' and 'number'
                            category_obj = {
                                'name': category['name']
                            }
                            factor_obj['ProblemCategories'].append(category_obj)
                        
                        factors.append(factor_obj)
                    
                    # Process Major Root Cause Categories
                    major_categories = []
                    for major_cat in rca_data.get('MajorRootCauseCategories', []):
                        major_obj = {
                            'description': major_cat['description'],
                            'properties': {
                                'details': []
                            }
                        }
                        
                        # Process details (Near Root Causes)
                        for detail in major_cat.get('properties', {}).get('details', []):
                            detail_obj = {
                                'NearRootCauses': detail['NearRootCauses'],
                                'rootcauses': []
                            }
                            
                            # Process root causes
                            for root_cause in detail.get('rootcauses', []):
                                # Exclude 'definition' and 'number'
                                root_cause_obj = {
                                    'name': root_cause['name']
                                }
                                detail_obj['rootcauses'].append(root_cause_obj)
                            
                            major_obj['properties']['details'].append(detail_obj)
                        
                        major_categories.append(major_obj)
                    
                    # Build response structure
                    categories = {
                        'Factors': factors,
                        'MajorRootCauseCategories': major_categories
                    }
                    
                    logger.info(f"✅ Successfully loaded {len(factors)} Factors and {len(major_categories)} Major Categories")
                    return categories
        
        logger.error("rca-edit-data.json not found in any expected location")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error loading RCA categories: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Lambda handler for GET /rca-categories endpoint
    
    Returns RCA category options for dropdown population in the UI
    
    Expected usage:
        GET /rca-categories
        
    Response:
        {
            "success": true,
            "message": "RCA categories retrieved successfully",
            "data": {
                "Factors": [...],
                "MajorRootCauseCategories": [...]
            }
        }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return handle_cors_preflight()
        
        # Only support GET method
        if event.get('httpMethod') != 'GET':
            return response(405, "Method not allowed. Use GET.")
        
        logger.info("Loading RCA categories...")
        
        # Load categories from JSON file
        categories = load_rca_categories()
        
        if not categories:
            return response(500, "Failed to load RCA categories")
        
        # Calculate statistics for logging
        total_problem_categories = sum(
            len(factor['ProblemCategories']) 
            for factor in categories['Factors']
        )
        
        total_near_causes = sum(
            len(major_cat['properties']['details'])
            for major_cat in categories['MajorRootCauseCategories']
        )
        
        logger.info(
            f"✅ Returning {len(categories['Factors'])} Factors, "
            f"{total_problem_categories} Problem Categories, "
            f"{len(categories['MajorRootCauseCategories'])} Major Categories, "
            f"{total_near_causes} Near Root Causes"
        )
        
        return response(200, "RCA categories retrieved successfully", categories)
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return response(500, "Internal server error", {"details": str(e)})
