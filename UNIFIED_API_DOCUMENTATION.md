# QMS AI - Unified API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Base Configuration](#base-configuration)
3. [Complaints APIs](#complaints-apis)
4. [Deviations APIs](#deviations-apis)
5. [Authentication](#authentication)
6. [Workflow and Audit Logging](#workflow-and-audit-logging)
7. [Error Handling](#error-handling)
8. [Design Considerations](#design-considerations)

---

## Overview

The QMS AI system provides REST APIs for managing product complaints and deviations. All APIs are deployed via AWS API Gateway with Lambda backend integration.

**Base URL:** `https://{api-gateway-id}.execute-api.us-east-1.amazonaws.com/dev`

**Environment:** dev  
**Region:** us-east-1  
**Project:** QMS AI

---

## Base Configuration

### Common Headers
```
Content-Type: application/json
Access-Control-Allow-Origin: *
```

### Response Format
All APIs return standardized JSON responses:
```json
{
  "success": true|false,
  "message": "Description",
  "data": {},
  "timestamp": "ISO-8601 timestamp"
}
```

---

## Complaints APIs

### 1. Create Complaint

**Endpoint:** `POST /createComplaint`

**Description:** Creates a new complaint with narrative text and queues it for processing.

**Request Body:**
```json
{
  "narrative": "Patient John Doe experienced adverse reaction to Drug XYZ lot ABC123."
}
```

**Parameters:**
- `narrative` (string, required): Detailed complaint description

**Success Response (200):**
```json
{
  "success": true,
  "message": "Complaint created and queued for processing",
  "data": {
    "complaint": {
      "complaint_id": "CAS-00001",
      "narrative": "Patient John Doe experienced...",
      "status": "Pending",
      "created_at": "2024-01-15T10:30:00.000Z"
    },
    "message_id": "abc123-def456-ghi789"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses:**
- 400: Missing narrative
- 500: Internal server error

**Design Considerations:**
- Auto-generates complaint ID (CAS-XXXXX format)
- Automatically queues for text extraction via SQS
- Initial status set to "Pending"
- **Workflow Logging:** Logs COMPLAINT_CREATED step with narrative_length, created_by, complaint_id, status

---

### 2. Upload Complaints

**Endpoint:** `POST /uploadComplaints`

**Description:** Uploads complaint files (PDF, CSV, XLSX) to S3 and processes them.

**Request:**
- Content-Type: `multipart/form-data`
- File field with supported formats

**Supported File Types:**
- PDF (.pdf) - Single complaint per file
- CSV (.csv) - Multiple complaints with "narrative" column
- Excel (.xlsx, .xls) - Multiple complaints with "narrative" column

**File Size Limit:** 50 MB

**Success Response - PDF (200):**
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

**Success Response - CSV/Excel (200):**
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

**CSV/Excel Format:**
Required column: `narrative`

Example CSV:
```csv
complaint_id,narrative
COMP-001,"Patient experienced nausea after taking medication"
COMP-002,"Device malfunction during injection"
```

**Error Responses:**
- 400: Invalid file format
- 400: File too large
- 400: Missing narrative column

**Design Considerations:**
- Files stored in S3: `uploads/YYYYMMDD/{file_id}_{filename}`
- PDF creates one complaint record
- CSV/Excel creates multiple records (one per row)
- Empty narratives skipped
- All complaints auto-queued for extraction
- **Workflow Logging:** Logs FILE_UPLOADED step with filename, size, type, uploaded_by, s3_key, file_id

---

### 3. Get Complaints

**Endpoint:** `GET /getComplaints`

**Description:** Retrieves complaints data with three modes: list all, get single, or get adverse events.

**Query Parameters:**

**Mode 1 - Get All Complaints:**
- `page` (integer, optional): Page number (default: 1)
- `status` (string, optional): Filter by status (pending, processed, overdue)
- `search` (string, optional): Search by complaint ID

**Mode 2 - Get Single Complaint:**
- `complaint_id` (string): Specific complaint ID

**Mode 3 - Get Adverse Events:**
- `adverse_events` (boolean): Set to true
- `page` (integer, optional): Page number

**Success Response - All Complaints (200):**
```json
{
  "caseStats": {
    "total_complaints": 150,
    "pending": 45,
    "processed": 100,
    "overdue": 5,
    "avg_cycle_time": 3
  },
  "caseStatus": {
    "pending": [...],
    "processed": [...],
    "overdue": [...]
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 150,
    "items_per_page": 15,
    "has_next": true,
    "has_previous": false
  },
  "complaints": [
    {
      "case_id": "CAS-00001",
      "criticality": "High",
      "report_type": "Initial",
      "receipt_date": "2024-01-15",
      "case_type": ["Product Complaint"],
      "status": "pending",
      "text_extracted": true,
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

**Success Response - Single Complaint (200):**
```json
{
  "case_id": "CAS-00001",
  "receipt_date": "2024-01-15",
  "created_at": "2024-01-15T10:30:00.000Z",
  "criticality": "High",
  "report_type": "Initial",
  "ai_summary": "Patient experienced adverse reaction...",
  "case_type": ["Product Complaint"],
  "narrative": "Full narrative text...",
  "primary_reporter": {
    "name": "Dr. John Smith",
    "address": "123 Medical Center Dr"
  },
  "patient_name": "Jane Doe",
  "physician_name": "Dr. John Smith",
  "product_details": {
    "drug": "Drug XYZ",
    "lot_no": "ABC123",
    "dosage": "10mg",
    "expiration_date": "2025-12-31",
    "part_number": "PART-001"
  },
  "caseStatus": "pending",
  "text_extracted": true,
  "complaintClassified": true,
  "category_details": [
    {
      "id": "1",
      "label": "Dose confirmation",
      "level": "2",
      "crl": "Dose confirmation",
      "priority": "Low",
      "unit": 5,
      "percentage": 94.92
    }
  ],
  "crl_list": ["Dose confirmation", "Device malfunction", "NA"],
  "label_list": ["Dose confirmation", "Device malfunction", "Needle bent"]
}
```

**Error Responses:**
- 404: Complaint not found
- 500: Internal server error

**Design Considerations:**
- Pagination: 15 items per page
- Search ignores status filter
- Overdue: 5+ days old pending complaints
- Statistics refreshed on each request
- Category details only for classified complaints

---

### 4. Classify Complaints

**Endpoint:** `POST /classifyComplaints`

**Description:** Triggers classification workflow via Step Functions.

**Request Body:**
```json
{
  "complaint_id": "CAS-00001"
}
```

**Parameters:**
- `complaint_id` (string, required): Complaint ID (format: CAS-XXXXX)

**Success Response (200):**
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

**Error Responses:**
- 400: Missing complaint_id
- 404: Complaint not found
- 500: Internal server error

**Workflow:**
1. Validates complaint_id
2. Retrieves narrative from database
3. Starts Step Functions execution
4. Step Functions orchestrates:
   - Level calculation
   - Subcategory classification
   - CRL code assignment
   - Priority determination

**Design Considerations:**
- Asynchronous processing
- Execution name: `classify-{complaint_id}-{timestamp}`
- Results stored in `inference_results` table
- Complaint must have narrative field
- **Workflow Logging:** Logs CLASSIFICATION_STARTED step with narrative_length, triggered_by, execution_arn

---

### 5. Approve Complaints

**Endpoint:** `POST /approveComplaints`

**Description:** Approves a complaint, updating status from Pending/Overdue to Processed.

**Request Body:**
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
    }
  ]
}
```

**Parameters:**
- `case_id` (string, required): Complaint ID
- `caseStatus` (string, required): Current status (pending/overdue)
- `categoryDetails` (array, required): Approved classifications

**Success Response (200):**
```json
{
  "success": true,
  "message": "Complaint CAS-00001 approved successfully",
  "data": {
    "case_id": "CAS-00001",
    "category_details": [...],
    "caseStatus": "processed",
    "approved_at": "2024-01-15T10:30:00.000Z",
    "approved_by": "user@example.com"
  }
}
```

**Error Responses:**
- 400: Missing case_id
- 400: Invalid status
- 404: Complaint not found
- 500: Internal server error

**Workflow:**
1. Validates case_id and status
2. Checks complaint exists and is Pending/Overdue
3. Creates record in `processed_complaints` table
4. Updates status to "Processed"
5. Recalculates average cycle time
6. **Logs workflow and audit trail**

**Design Considerations:**
- Only Pending/Overdue can be approved
- Category details stored as JSONB
- Approval timestamp in UTC
- User info from Cognito/headers
- Status cannot be reverted
- **Workflow Logging:** Logs COMPLAINT_APPROVED step with previous_status, category_count, approved_by, category_details
- **Audit Logging:** Logs status field change (Pending/Overdue → Processed) with old_value, new_value, changed_by

---

### 6. Modify Extracted Text

**Endpoint:** `POST /modifyExtractedDetails`

**Description:** Updates extracted complaint details after text extraction.

**Request Body:**
```json
{
  "caseId": "CAS-00001",
  "primaryReporter": {
    "name": "Dr. John Smith",
    "address": "123 Medical Center Dr, City, State 12345"
  },
  "patientName": "Jane Doe",
  "physicianName": "Dr. John Smith",
  "drug": "Drug XYZ",
  "lotNumber": "ABC123",
  "doseAmount": "10mg",
  "expirationDate": "2025-12-31",
  "partNumber": "PART-001"
}
```

**Parameters:**
- `caseId` (string, required): Complaint ID
- All other fields optional

**Success Response (200):**
```json
{
  "message": "Record updated successfully"
}
```

**Error Response (500):**
```json
{
  "error": "Database error: <details>"
}
```

**Design Considerations:**
- All fields optional except caseId
- Updates `complaints` table directly
- Date format: YYYY-MM-DD
- Empty strings allowed
- **Workflow Logging:** Logs DETAILS_MODIFIED step with fields_count, modified_by, fields_modified list
- **Audit Logging:** Logs each changed field individually (9 fields tracked: primary_reporter, primary_reporter_address, patient_name, physician, drug, lot_no, dosage, expiration_date, part_number)

---

## Deviations APIs

### 7. Upload Deviations

**Endpoint:** `POST /uploadDeviations`

**Description:** Uploads deviation PDF files to S3 and queues for processing.

**Request:**
- Content-Type: `multipart/form-data`
- PDF file only

**File Size Limit:** 10 MB

**Success Response (200):**
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

**Error Responses:**
- 400: Invalid file type (PDF only)
- 400: File too large
- 400: Empty file
- 500: Queue not found

**Workflow:**
1. Validates PDF format
2. Uploads to S3: `deviations/YYYYMMDD/{file_id}_{filename}`
3. Creates record in `deviation_files` table
4. Creates deviation in `deviations` table (DV-XXXXX)
5. Sends to SQS for processing

**Design Considerations:**
- Auto-generated deviation ID (DV-XXXXX)
- Initial status: "Pending"
- User info from event context
- Automatic text extraction queuing

---

### 8. Get Deviations

**Endpoint:** `GET /getDeviation`

**Description:** Retrieves deviation data with filtering and pagination.

**Query Parameters:**
- `deviation_id` (string): Get specific deviation
- `status` (string): Filter by status (Pending, Processed, Overdue)
- `page` (integer): Page number (default: 1)
- `search` (string): Search by deviation ID

**Success Response - All Deviations (200):**
```json
{
  "caseStats": {
    "total_deviations": 150,
    "pending": 45,
    "processed": 100,
    "overdue": 5,
    "avg_cycle_time": 3,
    "rca_pending": 20,
    "rca_done": 80,
    "grading_pending": 15
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 150,
    "items_per_page": 15,
    "has_next": true,
    "has_previous": false
  },
  "deviations": [
    {
      "case_id": "DV-00001",
      "receipt_date": "2024-01-15T10:30:00.000Z",
      "deviation_description": "Equipment malfunction",
      "status": "pending",
      "grading_approved": false,
      "rca_approved": false,
      "grading_completed": false
    }
  ]
}
```

**Success Response - Single Deviation (200):**
```json
{
  "case_id": "DV-00001",
  "receipt_date": "2024-01-15T10:30:00.000Z",
  "deviation_description": "Equipment malfunction",
  "status": "pending",
  "grading_approved": false,
  "rca_approved": false,
  "grading_completed": false
}
```

**Error Responses:**
- 404: Deviation not found
- 500: Internal server error

**Design Considerations:**
- Pagination: 15 items per page
- Statistics auto-refreshed
- Search across all statuses
- Excludes pure adverse events

---

### 9. Add Investigation Summary

**Endpoint:** `POST /addInvestigationSummary`

**Description:** Manually add/update investigation summaries for deviations.

**Request Body:**
```json
{
  "deviationId": "DV-10001",
  "summary": "Investigation revealed equipment malfunction during manufacturing process."
}
```

**Parameters:**
- `deviationId` (string, required): Deviation ID (DV-XXXXX)
- `summary` (string, required): Investigation summary text

**Success Response (200):**
```json
{
  "message": "Investigation summary updated successfully"
}
```

**Error Response (500):**
```json
{
  "error": "Database error: {details}"
}
```

**Design Considerations:**
- Updates `deviations.investigation_summary` field
- Used when automated extraction fails
- Parameterized queries prevent SQL injection
- Response time: < 500ms

---

### 10. Generate RCA

**Endpoint:** `POST /generateRCA` or `GET /generateRCA`

**Description:** Generates or retrieves Root Cause Analysis for deviations using AWS Bedrock.

#### POST - Generate New RCA

**Request Body:**
```json
{
  "deviation_id": "DV-00001",
  "investigation_summary": "During manufacturing on January 10, 2024, batch Product XYZ (Lot ABC123) had contamination. Investigation revealed sterilization equipment failed to reach 121°C, only reaching 115°C due to faulty temperature sensor not calibrated in 18 months.",
  "created_by": "user@example.com"
}
```

**Parameters:**
- `deviation_id` (string, optional): Deviation ID for reference
- `investigation_summary` (string, required): Detailed investigation text
- `created_by` (string, optional): User email (defaults to 'system')

**Success Response (200):**
```json
{
  "success": true,
  "message": "RCA generated successfully",
  "data": {
    "deviation_id": "DV-00001",
    "issues": "Primary issue was contamination in Product XYZ Lot ABC123. Sterilization equipment failed to achieve required 121°C, only reaching 115°C, compromising sterility assurance.",
    "major_root_cause_category": "Equipment/Instrumentation",
    "near_root_cause": "Temperature sensor was faulty and not calibrated within required timeframe. Sensor exceeded 12-month calibration interval by 6 months.",
    "root_cause": "Fundamental root cause was failure of preventive maintenance system to ensure timely calibration. Organization lacked effective calibration tracking and alert system."
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### GET - Retrieve Existing RCA

**Query Parameters:**
- `deviation_id` (string, required): Deviation ID

**Success Response (200):**
```json
{
  "success": true,
  "message": "RCA retrieved successfully",
  "data": {
    "rca_id": 1,
    "deviation_id": "DV-00001",
    "issues": "...",
    "major_root_cause_category": "Equipment/Instrumentation",
    "near_root_cause": "...",
    "root_cause": "...",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z",
    "created_by": "system"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses:**
- 400: Missing investigation_summary
- 400: Invalid type
- 400: Empty summary
- 404: No RCA found (GET only)
- 500: Internal server error

**RCA Sections:**
1. **Issues**: Specific problems found in investigation
2. **Major Root Cause Category**: High-level classification (Equipment, Human Error, Process, Materials, Environment, Management System)
3. **Near Root Cause**: Immediate/proximate cause
4. **Root Cause**: Fundamental systemic cause

**Design Considerations:**
- Uses AWS Bedrock Claude Haiku model
- 4 separate AI calls for each section
- Processing time: 10-30 seconds
- Maximum tokens: 2048 per section
- Temperature: 0 (deterministic)
- POST updates existing RCA (ON CONFLICT DO UPDATE)
- GET retrieves saved RCA

---

## Authentication

### 11. Auth Callback

**Endpoint:** `POST /authCallback`

**Description:** Handles authentication callback from identity provider.

**Request Body:**
```json
{
  "code": "authorization_code",
  "state": "state_parameter"
}
```

**Design Considerations:**
- Integrates with Cognito
- Exchanges authorization code for tokens
- Returns user session information

---

## Workflow and Audit Logging

### Overview
Comprehensive workflow and audit logging implemented for complaints process compliance tracking.

### Workflow Logging
All complaint workflow steps are logged to `workflow_logs` table:

| Step | Lambda Function | Workflow Step | Data Captured |
|------|----------------|---------------|---------------|
| 1. Create | create_complaint | COMPLAINT_CREATED | narrative_length, created_by, complaint_id, status |
| 2. Upload | upload_complaints | FILE_UPLOADED | filename, size, type, uploaded_by, s3_key, file_id |
| 3. Extract | extract_and_process_complaints | TEXT_EXTRACTED | source (pdf/narrative), extracted_fields, text_length |
| 4. Classify | classify_complaints | CLASSIFICATION_STARTED | narrative_length, triggered_by, execution_arn |
| 5. Modify | modify_extracted_text | DETAILS_MODIFIED | fields_count, modified_by, fields_modified list |
| 6. Approve | approve_complaints | COMPLAINT_APPROVED | previous_status, category_count, approved_by, category_details |

### Audit Logging
Field-level changes are logged to `unified_audit` table:

**Tracked Changes:**
- Status changes (Pending → Processed, Pending → Overdue)
- All 9 extracted detail fields when modified
- Each change includes: entity_type, entity_id, changed_field, old_value, new_value, changed_by, timestamp

### Database Tables

**workflow_logs:**
```sql
log_id (WFL-XXXXX), complaint_id, step, start_date, end_date, input (JSONB), output (JSONB)
```

**unified_audit:**
```sql
audit_id (AUD-XXXXX), entity_type, entity_id, changed_field, old_value, new_value, changed_by, timestamp
```

### Query Examples

**Get Workflow for Complaint:**
```sql
SELECT * FROM workflow_logs 
WHERE complaint_id = 'CAS-00001' 
ORDER BY start_date;
```

**Get Audit Trail for Complaint:**
```sql
SELECT * FROM unified_audit 
WHERE entity_type = 'Complaint' AND entity_id = 'CAS-00001' 
ORDER BY timestamp;
```

### Compliance Benefits
1. **Complete Traceability:** Every action tracked with who, what, when
2. **Field-Level Auditing:** All modifications logged with old/new values
3. **User Attribution:** Every change linked to user (from Cognito)
4. **Immutable Records:** Audit logs cannot be modified
5. **Regulatory Ready:** Meets FDA 21 CFR Part 11 requirements

### Implementation Status
- ✅ **Complaints:** Fully implemented (6 workflow steps, field-level audit)
- ⏳ **Deviations:** Not yet implemented

---

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "message": "Detailed error description",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (validation errors)
- **404**: Resource Not Found
- **500**: Internal Server Error

### Common Error Scenarios
1. **Missing Required Fields**: 400 with field name
2. **Invalid File Format**: 400 with allowed formats
3. **File Size Exceeded**: 400 with size limit
4. **Resource Not Found**: 404 with resource identifier
5. **Database Errors**: 500 with error details
6. **Queue Errors**: 500 with queue name

---

## Design Considerations

### Architecture Patterns

#### 1. Asynchronous Processing
- File uploads trigger SQS messages
- Step Functions orchestrate complex workflows
- Lambda processes messages in batches

#### 2. Database Design
- PostgreSQL Aurora Serverless (2-16 ACU)
- Connection pooling via secrets manager
- JSONB for flexible schema (category_details)
- Stored procedures for statistics

#### 3. File Storage
- S3 bucket structure:
  - `uploads/YYYYMMDD/{file_id}_{filename}` - Complaints
  - `deviations/YYYYMMDD/{file_id}_{filename}` - Deviations
- UUID-based file IDs
- Original filename preservation

#### 4. AI/ML Integration
- AWS Bedrock for text extraction and RCA generation
- SageMaker endpoints for classification models
- Model IDs configurable via environment variables

### Performance Optimizations

#### 1. Pagination
- 15 items per page (configurable)
- Offset-based pagination
- Total count queries optimized

#### 2. Caching
- Database connection string cached
- Secrets cached in Lambda execution context

#### 3. Batch Processing
- SQS batch size: 10 messages
- Max batch window: 5 seconds
- Max concurrency: 10

### Security Best Practices

#### 1. Database Security
- Secrets Manager for credentials
- Parameterized queries (SQL injection prevention)
- VPC-isolated Aurora cluster

#### 2. API Security
- CORS enabled
- API Gateway throttling
- Lambda execution roles with least privilege

#### 3. File Upload Security
- File type validation
- Size limits enforced
- Virus scanning (recommended)

### Scalability Considerations

#### 1. Lambda Configuration
- Memory: 512MB - 3GB (varies by function)
- Timeout: 900s for processing functions
- Reserved concurrency for critical functions

#### 2. Database Scaling
- Aurora Serverless auto-scales (2-16 ACU)
- Read replicas for reporting queries
- Connection pooling

#### 3. Queue Management
- Dead letter queues for failed messages
- Visibility timeout: 900s
- Max receive count: 3

### Monitoring & Observability

#### 1. CloudWatch Logs
- All Lambda functions log to CloudWatch
- Structured logging with JSON
- Error tracking with stack traces

#### 2. Metrics
- API Gateway metrics (latency, errors)
- Lambda metrics (invocations, duration, errors)
- SQS metrics (messages, age)

#### 3. Alarms
- High error rates
- Queue depth thresholds
- Database connection failures

### Data Flow

#### Complaint Processing Flow
1. Upload → S3 → SQS → Extract Lambda → Database
2. Database → Classify API → Step Functions → ML Models → Database
3. Database → Approve API → Processed Table → Statistics Update

#### Deviation Processing Flow
1. Upload → S3 → SQS → Extract Lambda → Database
2. Database → Add Summary API → Database
3. Database → Generate RCA API → Bedrock → Database

### Best Practices

#### 1. API Usage
- Use pagination for list endpoints
- Implement retry logic with exponential backoff
- Cache frequently accessed data
- Use search for specific records

#### 2. File Uploads
- Validate files client-side before upload
- Show progress indicators for large files
- Handle upload failures gracefully
- Provide clear error messages

#### 3. Asynchronous Operations
- Poll for completion status
- Implement timeout handling
- Provide user feedback during processing
- Store execution ARNs for tracking

#### 4. Error Handling
- Log all errors with context
- Return user-friendly error messages
- Implement circuit breakers for external services
- Monitor error rates and patterns

---

## API Summary Table

| Endpoint | Method | Purpose | Async |
|----------|--------|---------|-------|
| /createComplaint | POST | Create complaint from narrative | Yes (SQS) |
| /uploadComplaints | POST | Upload complaint files | Yes (SQS) |
| /getComplaints | GET | Retrieve complaints | No |
| /classifyComplaints | POST | Trigger classification | Yes (Step Functions) |
| /approveComplaints | POST | Approve complaint | No |
| /modifyExtractedDetails | POST | Update extracted data | No |
| /uploadDeviations | POST | Upload deviation PDFs | Yes (SQS) |
| /getDeviation | GET | Retrieve deviations | No |
| /addInvestigationSummary | POST | Add investigation summary | No |
| /generateRCA | POST/GET | Generate/retrieve RCA | No (but slow) |
| /authCallback | POST | Authentication callback | No |

---

## Environment Variables Reference

### Common Variables
- `env`: Environment name (dev/qa/prod)
- `aws_region`: AWS region (us-east-1)
- `db_secret_base_name`: Database secret name
- `db_region`: Database region

### Function-Specific Variables
- `sqs_queue_base_name`: SQS queue name prefix
- `step_function_base_name`: Step Functions name prefix
- `model_id`: Bedrock model ARN
- `llm_model_id`: LLM model identifier
- `level_endpoint`: SageMaker endpoint for level classification
- `subcategory_endpoint`: SageMaker endpoint for subcategory

---

## Database Schema Reference

### Key Tables
- `complaints`: Main complaints table
- `processed_complaints`: Approved complaints
- `inference_results`: Classification results
- `case_stats`: Statistics cache
- `files`: File metadata
- `deviations`: Main deviations table
- `deviation_files`: Deviation file metadata
- `adverse_events`: Adverse events (replica of complaints)
- `workflow_logs`: Workflow step execution logs (WFL-XXXXX)
- `unified_audit`: Audit trail for field changes (AUD-XXXXX)
- `label_list`: Available classification labels

### Key Fields
- Auto-generated IDs: CAS-XXXXX (complaints), DV-XXXXX (deviations), AUD-XXXXX (audit), WFL-XXXXX (workflow)
- Status values: Pending, Processed, Overdue
- JSONB fields: category_details, product_details, levels, subcategories, crl_codes, workflow input/output
- Timestamps: created_at, updated_at (UTC)

### Workflow and Audit Logging
See [Workflow and Audit Logging](#workflow-and-audit-logging) section for complete details on:
- Workflow step tracking
- Field-level audit trails
- Compliance and traceability features

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**Maintained By:** QMS AI Team
