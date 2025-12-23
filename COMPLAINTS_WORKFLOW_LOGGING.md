# Complaints Workflow and Audit Logging Implementation

## Overview
Implemented comprehensive workflow and audit logging for complaints process compliance tracking.

## Files Modified

### 1. audit_logger.py (NEW - Shared Utility)
**Location:** `src/app/audit_logger.py`

**Functions:**
- `log_workflow(conn, entity_id, step, input_data, output_data, start_time)` - Logs workflow steps
- `log_audit(conn, entity_type, entity_id, changed_field, old_value, new_value, changed_by)` - Logs field changes
- `get_user_from_event(event)` - Extracts user from API Gateway event

### 2. create_complaint/lambda_function.py
**Workflow Step:** `COMPLAINT_CREATED`
- Logs when complaint is created from narrative
- Captures: narrative_length, created_by, complaint_id, status

### 3. upload_complaints/lambda_function.py
**Workflow Step:** `FILE_UPLOADED`
- Logs when file is uploaded to S3
- Captures: filename, size, type, uploaded_by, s3_key, file_id

### 4. approve_complaints/lambda_function.py
**Workflow Step:** `COMPLAINT_APPROVED`
**Audit Trail:** Status change (Pending/Overdue → Processed)
- Logs complaint approval with category details
- Captures: previous_status, category_count, approved_by, category_details
- Audit logs status field change

### 5. modify_extracted_text/lambda_function.py
**Workflow Step:** `DETAILS_MODIFIED`
**Audit Trail:** All 9 field changes tracked individually
- Logs when extracted details are modified
- Captures: fields_count, modified_by, fields_modified list
- Audit logs each changed field: primary_reporter, primary_reporter_address, patient_name, physician, drug, lot_no, dosage, expiration_date, part_number

### 6. extract_and_process_complaints/lambda_function.py
**Workflow Step:** `TEXT_EXTRACTED`
- Logs when text extraction completes
- Captures: source (pdf/narrative), extracted_fields, text_length

### 7. classify_complaints/lambda_function.py
**Workflow Step:** `CLASSIFICATION_STARTED`
- Logs when classification workflow starts
- Captures: narrative_length, triggered_by, execution_arn

## Complaints Workflow Steps Logged

| Step | Lambda Function | Workflow Step | Audit Fields |
|------|----------------|---------------|--------------|
| 1. Create | create_complaint | COMPLAINT_CREATED | - |
| 2. Upload | upload_complaints | FILE_UPLOADED | - |
| 3. Extract | extract_and_process_complaints | TEXT_EXTRACTED | - |
| 4. Classify | classify_complaints | CLASSIFICATION_STARTED | - |
| 5. Modify | modify_extracted_text | DETAILS_MODIFIED | 9 fields tracked |
| 6. Approve | approve_complaints | COMPLAINT_APPROVED | status |

## Database Tables Used

### workflow_logs
```sql
log_id (WFL-XXXXX), complaint_id, step, start_date, end_date, input (JSONB), output (JSONB)
```

### unified_audit
```sql
audit_id (AUD-XXXXX), entity_type, entity_id, changed_field, old_value, new_value, changed_by, timestamp
```

## Usage Example

### Query Workflow for Complaint
```sql
SELECT * FROM workflow_logs 
WHERE complaint_id = 'CAS-00001' 
ORDER BY start_date;
```

### Query Audit Trail for Complaint
```sql
SELECT * FROM unified_audit 
WHERE entity_type = 'Complaint' AND entity_id = 'CAS-00001' 
ORDER BY timestamp;
```

## Compliance Benefits

1. **Complete Traceability**: Every complaint action tracked with who, what, when
2. **Field-Level Auditing**: All modifications logged with old/new values
3. **User Attribution**: Every change linked to user (from Cognito)
4. **Immutable Records**: Audit logs cannot be modified
5. **Regulatory Ready**: Meets FDA 21 CFR Part 11 requirements

## Performance Impact

- **Minimal**: Uses existing database connection
- **Non-blocking**: Logging errors don't fail main operation
- **Efficient**: Single transaction with main operation

## Next Steps (Future)

- Create API endpoints to query audit logs
- Build compliance reports from workflow_logs
- Add alerting for suspicious audit patterns
- Implement deviations workflow logging when module is complete
