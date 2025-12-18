# Generate RCA API Usage Guide

## Endpoints

### POST - Generate RCA
Generate a new Root Cause Analysis for a deviation.

**Endpoint:** `/generateRCA`  
**Method:** `POST`

#### Request Body
```json
{
  "deviation_id": "DV-12345",
  "investigation_summary": "Analyst S. Juyal generated duplicate results for the osmolality assay...",
  "created_by": "john.doe@company.com"  // Optional, defaults to 'system'
}
```

#### Response (Success - 200)
```json
{
  "success": true,
  "message": "RCA generated and saved successfully",
  "data": {
    "rca_id": 1,
    "deviation_id": "DV-12345",
    "issues": "The analyst generated duplicate results without proper authorization...",
    "major_root_cause_category": "Company personnel issue",
    "near_root_cause": "The analyst failed to follow the correct procedure...",
    "root_cause": "Inadequate training and enforcement of laboratory protocols..."
  },
  "timestamp": "2025-12-18T16:00:00.000Z"
}
```

#### Response (Error - 400)
```json
{
  "success": false,
  "message": "investigation_summary is required",
  "data": {},
  "timestamp": "2025-12-18T16:00:00.000Z"
}
```

#### Response (Partial Success - 500)
If RCA is generated but database save fails:
```json
{
  "success": false,
  "message": "RCA generated but failed to save to database",
  "data": {
    "deviation_id": "DV-12345",
    "issues": "...",
    "major_root_cause_category": "...",
    "near_root_cause": "...",
    "root_cause": "...",
    "error": "Database connection error details"
  },
  "timestamp": "2025-12-18T16:00:00.000Z"
}
```

---

### GET - Retrieve Existing RCA
Retrieve an existing Root Cause Analysis for a deviation.

**Endpoint:** `/generateRCA?deviation_id=DV-12345`  
**Method:** `GET`

#### Query Parameters
- `deviation_id` (required): The deviation ID to retrieve RCA for

#### Response (Success - 200)
```json
{
  "success": true,
  "message": "RCA retrieved successfully",
  "data": {
    "rca_id": 1,
    "deviation_id": "DV-12345",
    "issues": "The analyst generated duplicate results...",
    "major_root_cause_category": "Company personnel issue",
    "near_root_cause": "The analyst failed to follow...",
    "root_cause": "Inadequate training and enforcement...",
    "created_at": "2025-12-18T16:00:00.000Z",
    "updated_at": "2025-12-18T16:00:00.000Z",
    "created_by": "system"
  },
  "timestamp": "2025-12-18T16:00:00.000Z"
}
```

#### Response (Not Found - 404)
```json
{
  "success": false,
  "message": "No RCA found for deviation: DV-12345",
  "data": {},
  "timestamp": "2025-12-18T16:00:00.000Z"
}
```

---

## cURL Examples

### Generate New RCA
```bash
curl -X POST https://api.example.com/generateRCA \
  -H "Content-Type: application/json" \
  -d '{
    "deviation_id": "DV-12345",
    "investigation_summary": "Analyst S. Juyal generated duplicate results for the osmolality assay (method STM-QCS-0010, version 17.0, Osmolality Determination), when testing the 12-month timepoint for the 5°C storage condition for stability protocol STAB720.CD01.DP.",
    "created_by": "john.doe@company.com"
  }'
```

### Retrieve Existing RCA
```bash
curl -X GET "https://api.example.com/generateRCA?deviation_id=DV-12345"
```

---

## JavaScript/Fetch Examples

### Generate New RCA
```javascript
const generateRCA = async (deviationId, investigationSummary) => {
  try {
    const response = await fetch('https://api.example.com/generateRCA', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        deviation_id: deviationId,
        investigation_summary: investigationSummary,
        created_by: 'user@example.com'
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('RCA generated:', data.data);
      return data.data;
    } else {
      console.error('Error:', data.message);
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('Failed to generate RCA:', error);
    throw error;
  }
};

// Usage
generateRCA('DV-12345', 'Investigation summary text...')
  .then(rca => console.log('Success:', rca))
  .catch(error => console.error('Error:', error));
```

### Retrieve Existing RCA
```javascript
const getRCA = async (deviationId) => {
  try {
    const response = await fetch(
      `https://api.example.com/generateRCA?deviation_id=${deviationId}`
    );
    
    const data = await response.json();
    
    if (data.success) {
      console.log('RCA retrieved:', data.data);
      return data.data;
    } else {
      console.error('Error:', data.message);
      return null;
    }
  } catch (error) {
    console.error('Failed to retrieve RCA:', error);
    throw error;
  }
};

// Usage
getRCA('DV-12345')
  .then(rca => {
    if (rca) {
      console.log('Found RCA:', rca);
    } else {
      console.log('No RCA found');
    }
  })
  .catch(error => console.error('Error:', error));
```

---

## Workflow Integration

### Typical Flow
1. User views a deviation (DV-12345)
2. User clicks "Generate RCA" button
3. Frontend calls POST `/generateRCA` with investigation summary
4. Lambda generates RCA using AI (4 separate calls to Bedrock)
5. Lambda saves RCA to database
6. Frontend receives and displays the generated RCA
7. Later, when user returns to the deviation, frontend calls GET `/generateRCA?deviation_id=DV-12345` to retrieve existing RCA

### Update Existing RCA
To update an existing RCA, simply call POST again with the same `deviation_id`. The database will update the existing record (using ON CONFLICT DO UPDATE).

---

## Error Handling

### Common Errors

| Status Code | Message | Cause | Solution |
|-------------|---------|-------|----------|
| 400 | investigation_summary is required | Missing required field | Include investigation_summary in request body |
| 400 | investigation_summary must be a string | Wrong data type | Ensure investigation_summary is a string |
| 400 | deviation_id query parameter is required | Missing query param (GET) | Include deviation_id in query string |
| 404 | No RCA found for deviation | RCA doesn't exist | Generate new RCA using POST |
| 500 | RCA generated but failed to save | Database error | Check database connectivity and credentials |
| 500 | Internal server error | Various | Check CloudWatch logs for details |

---

## Testing

### Test Event (POST)
```json
{
  "httpMethod": "POST",
  "body": "{\"deviation_id\":\"DV-12345\",\"investigation_summary\":\"Analyst S. Juyal generated duplicate results for the osmolality assay (method STM-QCS-0010, version 17.0, Osmolality Determination), when testing the 12-month timepoint for the 5°C storage condition for stability protocol STAB720.CD01.DP. QC Sample Management provided the following samples for testing to be completed over the weekend: LIMS ID S-241021-00676, LIMS ID S-241127-00392 - designated for Appearance assay. SJ performed the osmolality assay using S-241127-00392; however, osmolality was in fact to be executed using the alternative sample, S-241127-00392. Upon identifying the error, the analyst proceeded to repeat the assay using the assigned LIMS sample, thereby producing duplicate results. STM-QCS-0800, General Laboratory Practices, dictates that no duplicate testing shall be done without justification to invalidate the original results and that an analyst may not proceed to repeat an assay without supervisor approval. In this case, JS did not follow the procedure.\",\"created_by\":\"test@example.com\"}"
}
```

### Test Event (GET)
```json
{
  "httpMethod": "GET",
  "queryStringParameters": {
    "deviation_id": "DV-12345"
  }
}
```
