import json
import logging
import os

import boto3
from botocore.config import Config

# Environment variables
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
SUBCATEGORY_ENDPOINT = os.environ.get('subcategory_endpoint', 'roberta-mounjaro-category-12-model-v1')  # SageMaker endpoint name

# Setup logging
logger = logging.getLogger("calculate_complaints_subcategory_lambda")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Calculate complaint subcategory using SageMaker model.

    Expected input from Step Function:
    {
        "complaint_id": "CAS-00001",
        "narrative": "Patient experienced severe side effects...",
        "status": "IN-REVIEW",
        "triggered_at": "2025-11-18T03:06:32.000Z"
    }

    Returns:
    {
        "complaint_id": "CAS-00001",
        "narrative": "...",
        "subcategory": {
            "Product Quality": "0.75",
            "Safety": "0.20",
            "Efficacy": "0.05"
        }
    }
    """
    logger.info("Received event: %s", json.dumps(event, indent=2))

    try:
        # Initialize AWS clients
        runtime = boto3.client(
            'runtime.sagemaker',
            config=Config(retries={'max_attempts': 3}),
            region_name=AWS_REGION
        )

        # Extract inputs from Step Function
        complaint_id = event.get('complaint_id')
        narrative = event.get('narrative')

        if not complaint_id or not narrative:
            raise ValueError("Missing required fields: complaint_id or narrative")

        logger.info(f"Processing complaint {complaint_id} - narrative length: {len(narrative)} chars")

        # Prepare payload for SageMaker
        input_data = [{
            "modelInput": {
                "Complaint": narrative
            }
        }]
        payload = json.dumps(input_data)

        logger.info(f"Calling SageMaker endpoint: {SUBCATEGORY_ENDPOINT}")

        # Invoke SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName=SUBCATEGORY_ENDPOINT,
            ContentType='application/json',
            Body=payload
        )

        # Parse response
        result = json.loads(response['Body'].read().decode())
        logger.info(f"SageMaker response: {json.dumps(result)}")

        # Build output for next step
        output = {
            'complaint_id': complaint_id,
            'narrative': narrative,
            'subcategory': result.get('category', {})
        }

        logger.info(f"✅ Subcategory calculated successfully for {complaint_id}")

        return output

    except Exception as e:
        logger.error(f"❌ Error calculating subcategory: {str(e)}")

        # Return default subcategory on error
        return {
            'complaint_id': event.get('complaint_id', 'unknown'),
            'narrative': event.get('narrative', ''),
            'subcategory': {'null': 'error'},
            'error': str(e)
        }
