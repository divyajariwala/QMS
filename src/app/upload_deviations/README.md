# Upload Deviations API

## Description
Uploads deviation PDF files to S3 and queues them for processing. Creates deviation records in the database and triggers text extraction workflow.

## Endpoint
`POST /uploadDeviations`

## Request

### Headers
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
```

### Body
Multipart form data with PDF file field

### Supported File Types
- PDF (`.pdf`) only

### File Size Limit
10 MB maximum (API Gateway limit)

## Response

### Success Response (200)
```json
{
  "success": true,
  "message": "PDF file uploaded and queued for processing successfully",
  "data": {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "deviation_id": "DV-00001",
    "filename": "deviation_report.pdf",
    "file_size": 1048576,
    "s3_key": "deviations/20240115/550e8400-e29b-41d4-a716-446655440000_deviation_report.pdf",
    "status": "processing",
    "message_id": "abc123-def456"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Responses

#### 400 - Invalid File Type
```json
{
  "success": false,
  "message": "Only PDF files are allowed",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 400 - File Too Large
```json
{
  "success": false,
  "message": "File too large. Maximum size: 10MB",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 400 - Empty File
```json
{
  "success": false,
  "message": "File is empty",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 500 - Queue Not Found
```json
{
  "success": false,
  "message": "Queue qms-dev-process-deviations not found",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Workflow
1. Validates file is PDF format
2. Uploads file to S3 bucket at `deviations/YYYYMMDD/{file_id}_{filename}`
3. Creates record in `deviation_files` table
4. Creates deviation record in `deviations` table with auto-generated ID (DV-XXXXX)
5. Sends message to SQS queue for processing
6. Returns deviation details

## Notes
- Deviation ID is auto-generated in format `DV-XXXXX`
- Files are stored in S3 with path: `deviations/YYYYMMDD/{file_id}_{filename}`
- File metadata includes original filename, upload timestamp, and file size
- Deviation is automatically queued for text extraction
- Initial deviation status is set to "Pending"
- User information is extracted from event context
