# Approve Complaints API

## Description
Approves a complaint by updating its status from Pending/Overdue to Processed. Stores the approved category details and updates case statistics.

## Endpoint
`POST /approveComplaints`

## Request

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "case_id": "CAS-00001",
  "caseStatus": "pending",
  "categoryDetails": [
    {
      "id": "1",
      "label": "Dose confirmation",
      "level": "2",
      "crl": "CRL-000100",
      "priority": "Low",
      "unit": 5,
      "percentage": 94.92
    },
    {
      "id": "2",
      "label": "Needle not fully extended",
      "level": "2",
      "crl": "CRL-000108",
      "priority": "Low",
      "unit": 2,
      "percentage": 2.88
    }
  ]
}
```

### Parameters
- `case_id` (string, required): Complaint ID to approve
- `caseStatus` (string, required): Current status (must be "pending" or "overdue")
- `categoryDetails` (array, required): Array of approved category classifications

### Category Details Object
- `id` (string): Category identifier
- `label` (string): Category label/name
- `level` (string): Classification level
- `crl` (string): CRL code
- `priority` (string): Priority level (Low/Medium/High)
- `unit` (integer): Number of units
- `percentage` (number): Confidence percentage

## Response

### Success Response (200)
```json
{
  "success": true,
  "message": "Complaint CAS-00001 approved successfully",
  "data": {
    "case_id": "CAS-00001",
    "category_details": [
      {
        "id": "1",
        "label": "Dose confirmation",
        "level": "2",
        "crl": "CRL-000100",
        "priority": "Low",
        "unit": 5,
        "percentage": 94.92
      }
    ],
    "caseStatus": "processed",
    "approved_at": "2024-01-15T10:30:00.000Z",
    "approved_by": "user@example.com"
  }
}
```

### Error Responses

#### 400 - Missing Case ID
```json
{
  "success": false,
  "error": "case_id is required",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 400 - Invalid Status
```json
{
  "success": false,
  "error": "Invalid status. Can only approve complaints with pending or overdue status. Current status: processed",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 404 - Complaint Not Found
```json
{
  "success": false,
  "error": "Complaint with case_id 'CAS-00001' not found or not in Pending/Overdue status",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 500 - Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error: <error details>",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Workflow
1. Validates case_id and current status
2. Checks complaint exists and is in Pending/Overdue status
3. Creates record in `processed_complaints` table
4. Updates complaint status to "Processed"
5. Recalculates average cycle time statistics
6. Returns approved complaint details

## Notes
- Only complaints with status "Pending" or "Overdue" can be approved
- Approved category details are stored as JSONB in database
- Average cycle time is automatically recalculated after approval
- User information is extracted from event context (Cognito/headers)
- Approval timestamp is recorded in UTC
- Once approved, complaint status cannot be reverted
