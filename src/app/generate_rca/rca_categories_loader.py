"""
RCA Categories Loader
Loads and extracts categories from the official ABS Root Cause Map (rca-edit-data.json)
Copyright 2010 © ABSG Consulting Inc.
"""

import json
import os
import logging

logger = logging.getLogger()


def load_rca_data():
    """
    Load the official ABS Root Cause Map data from rca-edit-data.json
    
    Returns:
        Dict with Factors and MajorRootCauseCategories
    """
    try:
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'prompts', 'rca-edit-data.json'),
            os.path.join('/var/task', 'prompts', 'rca-edit-data.json'),
            os.path.join('/var/task', 'rca-edit-data.json'),
            'prompts/rca-edit-data.json'
        ]
        
        for json_path in possible_paths:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
        
        raise FileNotFoundError("rca-edit-data.json not found")
        
    except Exception as e:
        logger.error(f"Error loading RCA data: {str(e)}")
        raise


def extract_problem_categories():
    """
    Extract Problem Categories (Issues Categories) from official ABS map
    
    Returns:
        List of problem category names organized by factor
    """
    rca_data = load_rca_data()
    
    categories = []
    for factor in rca_data.get('Factors', []):
        factor_name = factor['factor_name']
        for category in factor.get('ProblemCategories', []):
            categories.append({
                'name': category['name'],
                'number': category['number'],
                'factor': factor_name
            })
    
    return categories


def extract_major_categories():
    """
    Extract Major Root Cause Categories from official ABS map
    
    Returns:
        List of major category names
    """
    rca_data = load_rca_data()
    
    categories = []
    for major_cat in rca_data.get('MajorRootCauseCategories', []):
        categories.append({
            'name': major_cat['description'],
            'number': major_cat['number']
        })
    
    return categories


def extract_near_root_causes():
    """
    Extract all Near Root Causes from official ABS map
    
    Returns:
        Dict mapping major category to list of near root causes
    """
    rca_data = load_rca_data()
    
    near_causes_by_major = {}
    
    for major_cat in rca_data.get('MajorRootCauseCategories', []):
        major_name = major_cat['description']
        near_causes = []
        
        for detail in major_cat.get('properties', {}).get('details', []):
            near_cause_name = detail.get('NearRootCauses')
            near_cause_number = detail.get('number', '')
            
            if near_cause_name and near_cause_name not in ['Uncertain', 'Not Applicable']:
                near_causes.append({
                    'name': near_cause_name,
                    'number': near_cause_number
                })
        
        if near_causes:
            near_causes_by_major[major_name] = near_causes
    
    return near_causes_by_major


def extract_root_causes():
    """
    Extract all Root Causes from official ABS map
    
    Returns:
        Dict mapping near root cause to list of root causes
    """
    rca_data = load_rca_data()
    
    root_causes_by_near = {}
    
    for major_cat in rca_data.get('MajorRootCauseCategories', []):
        for detail in major_cat.get('properties', {}).get('details', []):
            near_cause_name = detail.get('NearRootCauses')
            
            if near_cause_name and near_cause_name not in ['Uncertain', 'Not Applicable']:
                root_causes = []
                
                for root_cause in detail.get('rootcauses', []):
                    root_cause_name = root_cause.get('name')
                    root_cause_number = root_cause.get('number', '')
                    
                    if root_cause_name and root_cause_name not in ['Uncertain', 'Not Applicable']:
                        root_causes.append({
                            'name': root_cause_name,
                            'number': root_cause_number
                        })
                
                if root_causes:
                    root_causes_by_near[near_cause_name] = root_causes
    
    return root_causes_by_near


def get_categories_for_prompt():
    """
    Get formatted categories for use in prompts
    
    Returns:
        Dict with formatted category lists for prompts
    """
    problem_categories = extract_problem_categories()
    near_causes = extract_near_root_causes()
    root_causes = extract_root_causes()
    
    # Group problem categories by factor
    categories_by_factor = {}
    for cat in problem_categories:
        factor = cat['factor']
        if factor not in categories_by_factor:
            categories_by_factor[factor] = []
        categories_by_factor[factor].append(cat['name'])
    
    return {
        'problem_categories_by_factor': categories_by_factor,
        'near_causes_by_major': {k: [nc['name'] for nc in v] for k, v in near_causes.items()},
        'root_causes_by_near': {k: [rc['name'] for rc in v] for k, v in root_causes.items()}
    }


if __name__ == '__main__':
    # Test the loader
    print("Testing RCA Categories Loader...")
    
    problem_cats = extract_problem_categories()
    print(f"\nProblem Categories: {len(problem_cats)}")
    for cat in problem_cats[:5]:
        print(f"  - {cat['name']} (#{cat['number']})")
    
    major_cats = extract_major_categories()
    print(f"\nMajor Categories: {len(major_cats)}")
    for cat in major_cats[:5]:
        print(f"  - {cat['name']} (#{cat['number']})")
    
    near_causes = extract_near_root_causes()
    print(f"\nNear Root Causes: {sum(len(v) for v in near_causes.values())}")
    
    root_causes = extract_root_causes()
    print(f"\nRoot Causes: {sum(len(v) for v in root_causes.values())}")
