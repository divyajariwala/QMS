import json
import logging
import os

# Logger setup
logger = logging.getLogger("calculate_complaints_crl")
logger.setLevel(logging.INFO)

# Environment variables
AWS_REGION = os.environ.get('aws_region', 'us-east-1')


def lambda_handler(event, context):
    """
    CRL (Complaint Report Labeling) Mapping - PLACEHOLDER

    TODO: Future implementation will map subcategories to official CRL codes
    by querying a lookup table in PostgreSQL/DynamoDB.

    Expected input from Step Function (Parallel State results):
    [
        {
            "complaint_id": "CAS-00001",
            "narrative": "...",
            "level": {...}
        },
        {
            "complaint_id": "CAS-00001",
            "narrative": "...",
            "subcategory": {...}
        }
    ]

    OR (if not coming from parallel state):
    {
        "complaint_id": "CAS-00001",
        "narrative": "...",
        "level": {...},
        "subcategory": {...}
    }

    This Lambda receives a LIST when Level and Subcategory run in parallel.
    It merges the results into a single object.

    Future behavior:
    - Query lookup table for each subcategory
    - Map subcategory names to official CRL codes
    - Example: "Product Quality" → "PQ-001"

    Current behavior (placeholder):
    - Merge parallel results if needed
    - Pass through all data unchanged
    - Ready for future CRL mapping implementation

    Returns (for now):
    {
        "complaint_id": "CAS-00001",
        "narrative": "...",
        "level": {...},
        "subcategory": {...},
        "crl_value": null  ← Will be populated in future
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Handle parallel state results (list of dicts from Level + Subcategory)
        if isinstance(event, list):
            logger.info(f"Merging {len(event)} parallel results")

            # Merge all dicts into one
            merged_event = {}
            for item in event:
                if isinstance(item, dict):
                    merged_event.update(item)

            event = merged_event
            logger.info(f"Merged event: {json.dumps(event)}")

        complaint_id = event.get('complaint_id')

        if not complaint_id:
            raise ValueError("Missing required field: complaint_id")

        logger.info(f"Processing CRL mapping for complaint {complaint_id} (PLACEHOLDER - no mapping yet)")

        # TODO: Future implementation
        # 1. Extract subcategories from event
        # 2. Query PostgreSQL lookup table for CRL codes:
        #    SELECT crl_code FROM crl_mapping WHERE subcategory = %s
        # 3. Map each subcategory to its CRL code
        # 4. Return mapped CRL values

        # For now: pass through all data unchanged
        output = {
            **event,  # Keep all existing fields
            'crl_value': None  # Placeholder for future CRL mapping
        }

        logger.info(f"✅ CRL placeholder processed for {complaint_id}")

        return output

    except Exception as e:
        logger.error(f"❌ Error in CRL placeholder: {str(e)}")

        # Try to extract complaint_id even on error
        complaint_id = 'unknown'
        try:
            if isinstance(event, list) and len(event) > 0:
                complaint_id = event[0].get('complaint_id', 'unknown')
            elif isinstance(event, dict):
                complaint_id = event.get('complaint_id', 'unknown')
        except:
            pass

        # Return safe default
        return {
            'complaint_id': complaint_id,
            'crl_value': None,
            'error': str(e)
        }

# ============================================================================
# FUTURE IMPLEMENTATION REFERENCE
# ============================================================================
#
# def map_subcategories_to_crl(subcategories: dict) -> dict:
#     """
#     Map subcategories to CRL codes using lookup table.
#
#     Args:
#         subcategories: Dict with subcategory names as keys, probabilities as values
#         Example: {"Product Quality": "0.75", "Safety": "0.25"}
#
#     Returns:
#         Dict with CRL codes as keys, probabilities as values
#         Example: {"PQ-001": "0.75", "SF-002": "0.25"}
#     """
#     conninfo = get_connection_string()
#     crl_mapping = {}
#
#     with psycopg.connect(conninfo) as conn:
#         with conn.cursor() as cur:
#             for subcategory, probability in subcategories.items():
#                 # Query lookup table
#                 cur.execute(
#                     "SELECT crl_code FROM crl_mapping WHERE subcategory_name = %s",
#                     (subcategory,)
#                 )
#                 row = cur.fetchone()
#
#                 if row:
#                     crl_code = row[0]
#                     crl_mapping[crl_code] = probability
#                 else:
#                     # Unassigned CRL for unknown subcategories
#                     crl_mapping["UNASSIGNED"] = probability
#
#     return crl_mapping
# ============================================================================