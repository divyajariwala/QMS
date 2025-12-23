"""
Submit RCA Lambda Function

This Lambda function handles the submission (save/update) of RCA (Root Cause Analysis)
data to the database. It accepts RCA analysis results from the frontend and persists
them to the PostgreSQL database.

Endpoint: POST /submit-rca

Request Body:
{
    "deviation_id": "DV-00001",
    "issues": "Issues text...",
    "issues_category": "Process/Manufacturing Equipment Issue",
    "major_root_cause_category": "Design Issue",
    "near_root_cause": "Near root cause text...",
    "near_root_cause_category": "Design Input Issue",
    "root_cause": "Root cause text...",
    "root_cause_category": "Design Scope Issue",
    "created_by": "user@example.com"
}

Response:
{
    "success": true,
    "message": "RCA saved successfully",
    "data": {
        "rca_id": 123,
        "deviation_id": "DV-00001",
        "created_at": "2025-12-22T10:30:00",
        "updated_at": "2025-12-22T10:30:00",
        "created_by": "user@example.com"
    }
}
"""

__version__ = "1.0.0"
