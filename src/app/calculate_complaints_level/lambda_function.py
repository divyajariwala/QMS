import json
import logging
import os

import boto3
from botocore.config import Config

# Environment variables
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
LEVEL_ENDPOINT = os.environ.get('level_endpoint', 'roberta-level-model-v1')  # SageMaker endpoint name

# Setup logging
logger = logging.getLogger("calculate_complaints_level_lambda")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Calculate complaint level using SageMaker model.

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
        "level": {
            "0": "0.15",
            "1": "0.35",
            "2": "0.50"
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

        logger.info(f"Calling SageMaker endpoint: {LEVEL_ENDPOINT}")

        # Invoke SageMaker endpoint
        response = runtime.invoke_endpoint(
            EndpointName=LEVEL_ENDPOINT,
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
            'level': result.get('level', {})
        }

        logger.info(f"✅ Level calculated successfully for {complaint_id}")

        return output

    except Exception as e:
        logger.error(f"❌ Error calculating level: {str(e)}")

        # Return default level on error
        return {
            'complaint_id': event.get('complaint_id', 'unknown'),
            'narrative': event.get('narrative', ''),
            'level': {'0': '0.00'},
            'error': str(e)
        }
