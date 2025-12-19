# Create Complaint API

## Description
Creates a new complaint with narrative text and queues it for processing. The complaint is stored in the database with an auto-generated ID and sent to SQS for extraction and classification.

## Endpoint
`POST /createComplaint`

## Request

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "narrative": "Patient John Doe experienced adverse reaction to Drug XYZ lot ABC123. Symptoms included nausea and dizziness."
}
```

### Parameters
- `narrative` (string, required): Detailed description of the complaint

## Response

### Success Response (200)
```json
{
  "success": true,
  "message": "Complaint created and queued for processing",
  "data": {
    "complaint": {
      "complaint_id": "CAS-00001",
      "narrative": "Patient John Doe experienced adverse reaction...",
      "status": "Pending",
      "created_at": "2024-01-15T10:30:00.000Z"
    },
    "message_id": "abc123-def456-ghi789"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Responses

#### 400 - Bad Request
```json
{
  "success": false,
  "message": "Narrative is required",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 500 - Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error: <error details>",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Notes
- Complaint ID is auto-generated in format `CAS-XXXXX`
- Narrative text is required and cannot be empty
- Complaint is automatically queued for text extraction and classification
- Initial status is set to "Pending"
