import json
import logging
import os

# Logger setup
logger = logging.getLogger("calculate_complaints_crl")
logger.setLevel(logging.INFO)

# Environment variables
AWS_REGION = os.environ.get('aws_region', 'us-east-1')

# Load CRL mapping lookup (cached at module level)
_crl_lookup = None


def load_crl_lookup():
    """
    Load CRL mapping from JSON file.
    Cached at module level to avoid repeated file reads.

    Returns:
        dict: Mapping of subcategory names to CRL codes
        Example: {"Dose confirmation": "CRL-000100", ...}
    """
    global _crl_lookup

    if _crl_lookup is not None:
        return _crl_lookup

    try:
        with open('crl_mapping_lookup.json', 'r') as f:
            _crl_lookup = json.load(f)
        logger.info(f"Loaded {len(_crl_lookup)} CRL mappings from lookup file")
        return _crl_lookup
    except FileNotFoundError:
        logger.error("CRL mapping lookup file not found")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing CRL mapping JSON: {str(e)}")
        raise


def map_subcategories_to_crl(subcategories):
    """
    Map subcategories to CRL codes using JSON lookup.

    Args:
        subcategories: Dict with subcategory names as keys, probabilities as values
        Example: {"Dose confirmation": 0.949, "Needle not fully extended": 0.028}

    Returns:
        Dict with CRL codes as keys, probabilities as values
        Example: {"CRL-000100": 0.949, "CRL-000108": 0.028}

    Notes:
        - CRL-999999 means "null" (no CRL code assigned) - these are skipped
        - Unknown subcategories are mapped to "UNASSIGNED"
    """
    crl_lookup = load_crl_lookup()
    crl_mapping = {}

    for subcategory, probability in subcategories.items():
        # Look up CRL code for this subcategory
        crl_code = crl_lookup.get(subcategory)

        if crl_code and crl_code != "CRL-999999":
            # Valid CRL code found
            crl_mapping[crl_code] = probability
            logger.info(f"Mapped '{subcategory}' -> {crl_code} (prob: {probability})")
        elif crl_code == "CRL-999999":
            # Null CRL code - skip or map to UNASSIGNED
            logger.info(f"Skipping '{subcategory}' with null CRL code (prob: {probability})")
            crl_mapping["UNASSIGNED"] = crl_mapping.get("UNASSIGNED", 0) + probability
        else:
            # Unknown subcategory
            logger.warning(f"Unknown subcategory '{subcategory}' - mapping to UNASSIGNED (prob: {probability})")
            crl_mapping["UNASSIGNED"] = crl_mapping.get("UNASSIGNED", 0) + probability

    return crl_mapping


def lambda_handler(event, context):
    """
    CRL (Complaint Report Labeling) Mapping

    Maps subcategories to official CRL codes using a JSON lookup table.

    Expected input from Step Function (Parallel State results):
    [
        {
            "complaint_id": "CAS-00001",
            "narrative": "...",
            "level": {"1": 0.11, "2": 0.81, "3": 0.01}
        },
        {
            "complaint_id": "CAS-00001",
            "narrative": "...",
            "subcategory": {
                "Dose confirmation": 0.949,
                "Needle not fully extended": 0.029,
                "Injection incomplete - Autoinjector/Syringe": 0.019
            }
        }
    ]

    Returns:
    {
        "complaint_id": "CAS-00001",
        "narrative": "...",
        "level": {...},
        "subcategory": {...},
        "crl_value": {
            "CRL-000100": 0.949,
            "CRL-000108": 0.029,
            "CRL-000102": 0.019
        }
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
        subcategories = event.get('subcategory', {})

        if not complaint_id:
            raise ValueError("Missing required field: complaint_id")

        if not subcategories:
            logger.warning(f"No subcategories found for complaint {complaint_id}")
            crl_value = None
        else:
            logger.info(f"Processing CRL mapping for complaint {complaint_id}")
            logger.info(f"Subcategories to map: {subcategories}")

            # Perform CRL mapping
            crl_value = map_subcategories_to_crl(subcategories)
            logger.info(f"CRL mapping result: {crl_value}")

        # Build output
        output = {
            **event,  # Keep all existing fields
            'crl_value': crl_value
        }

        logger.info(f"✅ CRL mapping completed for {complaint_id}")

        return output

    except Exception as e:
        logger.error(f"❌ Error in CRL mapping: {str(e)}")

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
