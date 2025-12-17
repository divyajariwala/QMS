# Upload Complaints API

## Description
Uploads complaint files (PDF, CSV, XLSX) to S3 and processes them. PDF files are queued for text extraction, while CSV/Excel files are parsed and each row is queued as a separate complaint.

## Endpoint
`POST /uploadComplaints`

## Request

### Headers
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
```

### Body
Multipart form data with file field

### Supported File Types
- PDF (`.pdf`) - Single complaint per file
- CSV (`.csv`) - Multiple complaints with "narrative" column
- Excel (`.xlsx`, `.xls`) - Multiple complaints with "narrative" column

### File Size Limit
50 MB maximum

## Response

### Success Response - PDF Upload (200)
```json
{
  "success": true,
  "message": "PDF file uploaded and queued for processing successfully",
  "data": {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "complaint_id": "CAS-00001",
    "filename": "complaint_document.pdf",
    "file_size": 1048576,
    "s3_key": "uploads/20240115/550e8400-e29b-41d4-a716-446655440000_complaint_document.pdf",
    "status": "processing",
    "message_id": "abc123-def456"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Success Response - CSV/Excel Upload (200)
```json
{
  "success": true,
  "message": "CSV file processed and 10 complaints queued successfully",
  "data": {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "complaints.csv",
    "file_size": 2048576,
    "s3_key": "uploads/20240115/550e8400-e29b-41d4-a716-446655440000_complaints.csv",
    "complaints_processed": 10,
    "complaint_message_ids": ["msg1", "msg2", "..."]
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Responses

#### 400 - Invalid File Format
```json
{
  "success": false,
  "message": "Invalid file format. Allowed: .csv, .xlsx, .pdf, .xls",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 400 - File Too Large
```json
{
  "success": false,
  "message": "File too large. Maximum size: 50MB",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 400 - Missing Narrative Column
```json
{
  "success": false,
  "message": "File must have a column named \"narrative\"",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## CSV/Excel File Format

### Required Column
- `narrative` - Complaint description text

### Example CSV
```csv
complaint_id,narrative
COMP-001,"Patient experienced nausea after taking medication"
COMP-002,"Device malfunction during injection"
```

### Example Excel
| complaint_id | narrative |
|--------------|-----------|
| COMP-001 | Patient experienced nausea after taking medication |
| COMP-002 | Device malfunction during injection |

## Notes
- Files are stored in S3 with path: `uploads/YYYYMMDD/{file_id}_{filename}`
- PDF files create one complaint record
- CSV/Excel files create multiple complaint records (one per row)
- Empty narratives are skipped in CSV/Excel processing
- All complaints are queued for automatic text extraction and classification
- File metadata is stored in the `files` table
- Complaint records are created in the `complaints` table
