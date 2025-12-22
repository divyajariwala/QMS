"""
Get RCA Categories Lambda Function

This Lambda function exposes the RCA category taxonomy from rca-edit-data.json
for use by the frontend UI. It provides all available categories for dropdown
population without the verbose definition and number fields.

Endpoint: GET /rca-categories

Response Structure:
{
    "Factors": [
        {
            "factor_name": "Equipment/Software Issues",
            "ProblemCategories": [
                {"name": "Process/Manufacturing Equipment Issue"},
                ...
            ]
        },
        ...
    ],
    "MajorRootCauseCategories": [
        {
            "description": "Design Issue",
            "properties": {
                "details": [
                    {
                        "NearRootCauses": "Design Input Issue",
                        "rootcauses": [
                            {"name": "Design Scope Issue"},
                            ...
                        ]
                    },
                    ...
                ]
            }
        },
        ...
    ]
}
"""

__version__ = "1.0.0"
