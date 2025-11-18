import json
import logging
import os

import boto3

# Logger setup
logger = logging.getLogger("calculate_complaints_priority")
logger.setLevel(logging.INFO)

# Environment variables
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
MODEL_ID = os.environ.get('llm_model_id', 'anthropic.claude-3-5-sonnet-20241022-v2:0')

# Initialize Bedrock Runtime client
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)


def load_prompt(filename):
    """Load prompt template from file"""
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {filename}")
        raise


def extract_top_value(probability_dict):
    """
    Extract the key with highest probability from a dict.

    Args:
        probability_dict: Dict with probabilities as values
        Example: {"0": "0.15", "1": "0.35", "2": "0.50"}

    Returns:
        The key with highest probability: "2"
    """
    if not probability_dict:
        return None

    # Convert string probabilities to float and find max
    max_key = max(probability_dict.items(), key=lambda x: float(x[1]))[0]
    return max_key


def call_bedrock(prompt_text):
    """
    Call Bedrock Claude model with a prompt using the Converse API.

    Args:
        prompt_text: The formatted prompt string

    Returns:
        Dict with parsed JSON response from Claude
    """
    try:
        # Use the modern Converse API (simpler than invoke_model)
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt_text}]
                }
            ],
            inferenceConfig={
                "maxTokens": 2048,
                "temperature": 0
            }
        )

        # Extract response text
        response_text = response['output']['message']['content'][0]['text']

        # Parse JSON from response
        result = json.loads(response_text)

        return result

    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Calculate complaint priority using Claude via Bedrock.

    Expected input from Step Function (can be list from parallel state or single object):
    {
        "complaint_id": "CAS-00001",
        "narrative": "Patient experienced severe side effects...",
        "level": {
            "0": "0.15",
            "1": "0.35",
            "2": "0.50"
        },
        "subcategory": {
            "Product Quality": "0.75",
            "Safety": "0.25"
        },
        "crl_value": null
    }

    OR as list (if coming from parallel execution):
    [
        {...level results...},
        {...subcategory results...}
    ]

    Two-step process:
    1. Check if complaint should be Level 3 (based on specific criteria)
    2. Calculate Priority (based on rules) + generate summary

    Returns:
    {
        "complaint_id": "CAS-00001",
        "narrative": "...",
        "level": {...},
        "subcategory": {...},
        "updated_level": "3",
        "priority": 1,
        "priority_reason": "Level 3 complaints must be Priority",
        "priority_summary": "Patient received product with foreign material..."
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Handle parallel state results (if CRL receives list, it might pass list)
        if isinstance(event, list):
            logger.info(f"Merging {len(event)} parallel results")

            # Merge all dicts into one
            merged_event = {}
            for item in event:
                if isinstance(item, dict):
                    merged_event.update(item)

            event = merged_event
            logger.info(f"Merged event: {json.dumps(event)}")

        # Extract inputs from Step Function
        complaint_id = event.get('complaint_id')
        narrative = event.get('narrative')
        level_dict = event.get('level', {})
        subcategory_dict = event.get('subcategory', {})

        if not complaint_id or not narrative:
            raise ValueError("Missing required fields: complaint_id or narrative")

        # Extract top level and subcategory (highest probability)
        level = extract_top_value(level_dict)
        subcategory = extract_top_value(subcategory_dict)

        logger.info(f"Processing complaint {complaint_id}")
        logger.info(f"Top level: {level}, Top subcategory: {subcategory}")

        # ============================================================
        # STEP 1: Check if should be Level 3
        # ============================================================
        logger.info("Step 1: Checking for Level 3 criteria...")

        prompt1_template = load_prompt('prompt_priority_level.txt')
        prompt1 = prompt1_template.format(
            narrative=narrative,
            level=level
        )

        level_result = call_bedrock(prompt1)
        updated_level = level_result.get('Level', level)

        logger.info(f"Level check result: {updated_level} (reason: {level_result.get('Reason', 'N/A')})")

        # ============================================================
        # STEP 2: Calculate Priority + Summary
        # ============================================================
        logger.info("Step 2: Calculating priority and summary...")

        prompt2_template = load_prompt('prompt_priority_calculation.txt')
        prompt2 = prompt2_template.format(
            narrative=narrative,
            updated_level=updated_level,
            subcategory=subcategory
        )

        priority_result = call_bedrock(prompt2)

        logger.info(f"Priority calculation result: {json.dumps(priority_result)}")

        # Build output for Step Function
        output = {
            'complaint_id': complaint_id,
            'narrative': narrative,
            'level': level_dict,
            'subcategory': subcategory_dict,
            'updated_level': priority_result.get('Level', updated_level),
            'priority': priority_result.get('Priority', 0),
            'priority_reason': priority_result.get('Priority Reason', ''),
            'priority_summary': priority_result.get('Priority Summary', '')
        }

        logger.info(f"✅ Priority calculated successfully for {complaint_id}")

        return output

    except Exception as e:
        logger.error(f"❌ Error calculating priority: {str(e)}")

        # Return safe default on error
        return {
            'complaint_id': event.get('complaint_id', 'unknown'),
            'narrative': event.get('narrative', ''),
            'level': event.get('level', {}),
            'subcategory': event.get('subcategory', {}),
            'updated_level': '0',
            'priority': 0,
            'priority_reason': f'Error: {str(e)}',
            'priority_summary': 'Error occurred during priority calculation',
            'error': str(e)
        }