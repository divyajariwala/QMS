# Add Investigation Summary API

## Description
Manually add or update investigation summaries for deviation records when the automated extraction process doesn't generate one.

## Endpoint
`POST /addInvestigationSummary`

## Request

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "deviationId": "DV-10001",
  "summary": "Investigation revealed that the deviation was caused by equipment malfunction during the manufacturing process. Immediate corrective actions were taken to replace the faulty equipment and retrain operators on proper handling procedures."
}
```

### Parameters
- `deviationId` (string, required): Unique deviation identifier (format: DV-XXXXX)
- `summary` (string, required): Investigation summary text to be added

## Response

### Success Response (200)
```json
{
  "message": "Investigation summary updated successfully"
}
```

### Error Responses

#### 500 - Internal Server Error
```json
{
  "error": "Database error: {error_details}"
}
```

**Common Error Scenarios:**
- Missing required fields (deviationId or summary)
- Database connection failure
- Invalid deviation ID (record not found)
- Database update failure

## Database Operation

### Table: `deviations`
**Updated Field:** `investigation_summary`

```sql
UPDATE deviations 
SET investigation_summary = %s
WHERE deviation_id = %s
```

## Notes
- Updates the investigation_summary field in the deviations table
- Used when automated extraction doesn't generate a summary
- Validates presence of required fields before update
- Uses parameterized queries to prevent SQL injection
- Connection string cached for performance
- Typical response time: < 500ms
