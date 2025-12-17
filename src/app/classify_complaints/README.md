# Classify Complaints API

## Description
Triggers the classification workflow for a complaint by starting a Step Functions execution. Retrieves the complaint narrative from the database and initiates the classification process.

## Endpoint
`POST /classifyComplaints`

## Request

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "complaint_id": "CAS-00001"
}
```

### Parameters
- `complaint_id` (string, required): The complaint ID to classify (format: CAS-XXXXX)

## Response

### Success Response (200)
```json
{
  "success": true,
  "message": "Classification started successfully",
  "data": {
    "complaint_id": "CAS-00001",
    "execution_arn": "arn:aws:states:us-east-1:123456789012:execution:qms-dev-classify-complaints:classify-CAS-00001-20240115-103000",
    "status": "started"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Responses

#### 400 - Missing Complaint ID
```json
{
  "success": false,
  "message": "Missing complaint_id",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 404 - Complaint Not Found
```json
{
  "success": false,
  "message": "Complaint CAS-00001 not found",
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

## Workflow
1. Validates complaint_id is provided
2. Retrieves narrative from database
3. Starts Step Functions state machine execution
4. Step Functions orchestrates:
   - Level calculation
   - Subcategory classification
   - CRL code assignment
   - Priority determination

## Notes
- Complaint must exist in the database
- Complaint must have a narrative field
- Step Functions execution name format: `classify-{complaint_id}-{timestamp}`
- Classification results are stored in the `inference_results` table
- This API only triggers the workflow; actual classification is asynchronous
