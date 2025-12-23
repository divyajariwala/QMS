# Update RCA API Usage Guide

## Overview

The Update RCA endpoint allows updating an existing RCA (Root Cause Analysis) record in the database. This endpoint performs a full update of all RCA fields for a specific record identified by its `rca_id`.

**Purpose:** Update existing RCA record  
**Method:** PUT (full update)  
**Dependencies:** PostgreSQL Aurora, AWS Secrets Manager

---

## Endpoint

### PUT - Update RCA
Update an existing RCA analysis in the database.

**Endpoint:** `/updateRCA`  
**Method:** `PUT`  
**Authentication:** As configured in API Gateway  
**Content-Type:** `application/json`

---

## Request Format

```json
{
  "rca_id": 123,
  "deviation_id": "DV-00001",
  "issues": "Updated: Cleaning validation for APS tanks was not completed before use.",
  "issues_category": "Procedure issue",
  "major_root_cause_category": "Equipment/Software Issues",
  "major_root_cause_category_validated": "Equipment/Software Issues",
  "near_root_cause": "Updated: Lack of clear procedure to hold all tanks pending cleaning validation.",
  "near_root_cause_category": "Procedure/Instruction Issue",
  "root_cause": "Updated: Established cleaning validation procedures were not consistently followed.",
  "root_cause_category": "Procedure Not Used",
  "updated_by": "user@example.com"
}
```

---

## Request Parameters

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `rca_id` | integer | ID of the RCA record to update (must be > 0) |
| `deviation_id` | string | Deviation identifier (non-empty) |
| `issues` | string | Issues text (non-empty) |
| `issues_category` | string | Selected issues category from dropdown |
| `major_root_cause_category` | string | Major root cause category text (non-empty) |
| `near_root_cause` | string | Near root cause text (non-empty) |
| `near_root_cause_category` | string | Selected near root cause category from dropdown |
| `root_cause` | string | Root cause text (non-empty) |
| `root_cause_category` | string | Selected root cause category from dropdown |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `major_root_cause_category_validated` | string | Uses `major_root_cause_category` | Validated major category from taxonomy |
| `updated_by` | string | "system" | User email who updated the RCA |

---

## Response Structure

### Success Response (200)

```json
{
  "success": true,
  "message": "RCA updated successfully",
  "data": {
    "rca_id": 123,
    "deviation_id": "DV-00001",
    "created_at": "2025-12-22T10:30:00.000000+00:00",
    "updated_at": "2025-12-23T15:45:00.000000+00:00",
    "updated_by": "user@example.com"
  },
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

### Error Response - Missing Fields (400)

```json
{
  "success": false,
  "message": "Missing required fields: rca_id, issues",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

### Error Response - Invalid rca_id (400)

```json
{
  "success": false,
  "message": "rca_id must be a positive integer",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

### Error Response - Invalid Data (400)

```json
{
  "success": false,
  "message": "issues must be a non-empty string",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

### Error Response - Not Found (404)

```json
{
  "success": false,
  "message": "RCA with ID 123 not found",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

### Error Response - Method Not Allowed (405)

```json
{
  "success": false,
  "message": "Method not allowed. Use PUT.",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

### Error Response - Internal Server Error (500)

```json
{
  "success": false,
  "message": "Internal server error",
  "data": {
    "details": "Database connection timeout"
  },
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

---

## cURL Examples

### Update RCA

```bash
curl -X PUT https://api.example.com/updateRCA \
  -H "Content-Type: application/json" \
  -d '{
    "rca_id": 123,
    "deviation_id": "DV-00001",
    "issues": "Updated: Cleaning validation for APS tanks was not completed before use.",
    "issues_category": "Procedure issue",
    "major_root_cause_category": "Equipment/Software Issues",
    "major_root_cause_category_validated": "Equipment/Software Issues",
    "near_root_cause": "Updated: Lack of clear procedure to hold all tanks pending cleaning validation.",
    "near_root_cause_category": "Procedure/Instruction Issue",
    "root_cause": "Updated: Established cleaning validation procedures were not consistently followed.",
    "root_cause_category": "Procedure Not Used",
    "updated_by": "user@example.com"
  }'
```

### With Pretty Print

```bash
curl -X PUT https://api.example.com/updateRCA \
  -H "Content-Type: application/json" \
  -d @updated_rca.json | jq .
```

---

## JavaScript/Fetch Examples

### Update RCA

```javascript
const updateRCA = async (rcaData) => {
  try {
    const response = await fetch('/api/updateRCA', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(rcaData)
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('RCA updated:', result.data);
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Failed to update RCA:', error);
    throw error;
  }
};

// Usage
const rcaData = {
  rca_id: 123,
  deviation_id: 'DV-00001',
  issues: 'Updated: Cleaning validation for APS tanks was not completed before use.',
  issues_category: 'Procedure issue',
  major_root_cause_category: 'Equipment/Software Issues',
  major_root_cause_category_validated: 'Equipment/Software Issues',
  near_root_cause: 'Updated: Lack of clear procedure to hold all tanks pending cleaning validation.',
  near_root_cause_category: 'Procedure/Instruction Issue',
  root_cause: 'Updated: Established cleaning validation procedures were not consistently followed.',
  root_cause_category: 'Procedure Not Used',
  updated_by: 'user@example.com'
};

updateRCA(rcaData)
  .then(result => {
    console.log('Updated at:', result.updated_at);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### With Error Handling

```javascript
const updateRCAWithErrorHandling = async (rcaData) => {
  try {
    const response = await fetch('/api/updateRCA', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(rcaData)
    });
    
    const result = await response.json();
    
    if (!result.success) {
      // Handle specific error cases
      if (response.status === 404) {
        console.error('RCA not found:', result.message);
        // Show "RCA not found" message to user
      } else if (response.status === 400) {
        console.error('Validation error:', result.message);
        // Show validation error to user
      } else {
        console.error('Server error:', result.message);
        // Show generic error to user
      }
      throw new Error(result.message);
    }
    
    return result.data;
    
  } catch (error) {
    console.error('Failed to update RCA:', error);
    throw error;
  }
};
```

---

## React Hook Example

```javascript
import { useState } from 'react';

function useUpdateRCA() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateRCA = async (rcaData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/updateRCA', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(rcaData)
      });
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message);
      }
      
      return result.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateRCA, loading, error };
}

// Usage in component
function RCAEditForm({ rca }) {
  const { updateRCA, loading, error } = useUpdateRCA();
  const [formData, setFormData] = useState(rca);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const result = await updateRCA({
        ...formData,
        updated_by: 'user@example.com'
      });
      
      console.log('RCA updated:', result);
      // Show success message
      // Optionally redirect or refresh data
    } catch (err) {
      console.error('Failed to update RCA:', err);
      // Error is already in state, will be displayed
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Issues:</label>
        <textarea
          value={formData.issues}
          onChange={(e) => handleChange('issues', e.target.value)}
        />
      </div>
      
      <div>
        <label>Issues Category:</label>
        <select
          value={formData.issues_category}
          onChange={(e) => handleChange('issues_category', e.target.value)}
        >
          {/* Category options */}
        </select>
      </div>
      
      {/* More fields... */}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Updating...' : 'Update RCA'}
      </button>
      
      {error && <div className="error">{error}</div>}
    </form>
  );
}
```

---

## Complete RCA Workflow

This endpoint is part of the complete RCA workflow:

```
1. GET /getRCACategories
   └─> Load category options for dropdowns (once, cached)

2. POST /generateRCA
   └─> Generate RCA text using AI
   └─> Returns generated text + auto-selected categories

3. POST /submitRCA
   └─> Save new RCA(s) to database
   └─> Returns rca_id(s)

4. GET /rca?deviation_id=XXX (future)
   └─> Retrieve saved RCAs for viewing/editing
   └─> Returns list of RCAs with rca_id

5. PUT /updateRCA  ← THIS ENDPOINT
   └─> Update existing RCA
   └─> Requires rca_id from step 3 or 4
```

---

## Workflow Example

```javascript
// Complete workflow: Generate → Save → Edit → Update
const completeRCAWorkflow = async (investigationSummary, deviationId) => {
  try {
    // 1. Load categories (once, on page load)
    const categoriesResponse = await fetch('/api/getRCACategories');
    const categories = await categoriesResponse.json();
    
    // 2. Generate RCA
    const rcaResponse = await fetch('/api/generateRCA', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        investigation_summary: investigationSummary,
        deviation_id: deviationId
      })
    });
    const generatedRCA = await rcaResponse.json();
    
    // 3. Save to database
    const saveResponse = await fetch('/api/submitRCA', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...generatedRCA.data,
        created_by: 'user@example.com'
      })
    });
    const saved = await saveResponse.json();
    const rcaId = saved.data.rca_id;
    
    console.log('RCA saved with ID:', rcaId);
    
    // 4. User edits the RCA in UI
    // ... user makes changes ...
    
    // 5. Update the RCA
    const updateResponse = await fetch('/api/updateRCA', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rca_id: rcaId,
        deviation_id: deviationId,
        issues: editedIssues,
        issues_category: selectedIssuesCategory,
        major_root_cause_category: editedMajorCategory,
        major_root_cause_category_validated: selectedMajorCategory,
        near_root_cause: editedNearCause,
        near_root_cause_category: selectedNearCategory,
        root_cause: editedRootCause,
        root_cause_category: selectedRootCategory,
        updated_by: 'user@example.com'
      })
    });
    const updated = await updateResponse.json();
    
    console.log('RCA updated at:', updated.data.updated_at);
    
  } catch (error) {
    console.error('RCA workflow error:', error);
  }
};
```

---

## Database Behavior

### Update Logic

1. **Check Existence:** Verifies RCA with given `rca_id` exists
2. **If Not Found:** Returns 404 error
3. **If Found:** Updates all fields
4. **Timestamps:**
   - `created_at` is NOT modified (preserves original)
   - `updated_at` is set to current timestamp
5. **Returns:** Updated record metadata

**Important:** This is a full update (PUT), not a partial update (PATCH). All fields must be provided.

---

## Validation Rules

### Field Validation

The endpoint validates:
- ✅ All required fields are present
- ✅ `rca_id` is a positive integer
- ✅ Text fields are non-empty strings
- ✅ `deviation_id` is provided
- ✅ Category fields are provided

### Error Messages

Validation errors are clear and specific:
- `"rca_id must be a positive integer"`
- `"issues must be a non-empty string"`
- `"Missing required fields: rca_id, issues"`
- `"RCA with ID 123 not found"`

---

## Performance

### Response Times

| Scenario | Cold Start | Warm Start |
|----------|------------|------------|
| Update RCA | ~500-800ms | ~200-300ms |

### Recommendations

- ✅ Validate data on frontend before sending
- ✅ Show loading state during update
- ✅ Handle 404 errors gracefully
- ✅ Implement retry logic for 500 errors

---

## Error Handling

### Common Errors

| Status Code | Message | Cause | Solution |
|-------------|---------|-------|----------|
| 400 | Missing required fields: rca_id | Missing rca_id | Include rca_id in request |
| 400 | rca_id must be a positive integer | Invalid rca_id | Provide integer > 0 |
| 400 | issues must be a non-empty string | Empty string | Provide non-empty text |
| 404 | RCA with ID 123 not found | RCA doesn't exist | Verify rca_id is correct |
| 405 | Method not allowed. Use PUT. | Wrong HTTP method | Use PUT method only |
| 500 | Internal server error | Database error | Check CloudWatch logs |

### Error Handling Example

```javascript
const updateRCAWithRetry = async (rcaData, maxRetries = 3) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch('/api/updateRCA', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rcaData)
      });
      
      const result = await response.json();
      
      if (!result.success) {
        // Don't retry on 4xx errors (client errors)
        if (response.status >= 400 && response.status < 500) {
          throw new Error(result.message);
        }
        
        // Retry on 5xx errors (server errors)
        if (attempt < maxRetries) {
          console.log(`Attempt ${attempt} failed, retrying...`);
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
          continue;
        }
        
        throw new Error(result.message);
      }
      
      return result.data;
      
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
    }
  }
};
```

---

## Testing

### Test Event - Update RCA (Lambda Console)

```json
{
  "httpMethod": "PUT",
  "body": "{\"rca_id\":123,\"deviation_id\":\"DV-00001\",\"issues\":\"Updated issues\",\"issues_category\":\"Test Category\",\"major_root_cause_category\":\"Test Major\",\"near_root_cause\":\"Test Near\",\"near_root_cause_category\":\"Test Near Cat\",\"root_cause\":\"Test Root\",\"root_cause_category\":\"Test Root Cat\",\"updated_by\":\"test@example.com\"}"
}
```

### Test OPTIONS (CORS Preflight)

```json
{
  "httpMethod": "OPTIONS"
}
```

---

## Best Practices

1. **Always Include rca_id:** Required to identify which RCA to update
2. **Validate Before Sending:** Check all fields on frontend
3. **Handle 404 Errors:** RCA might have been deleted
4. **Show Loading State:** Updates can take 200-500ms
5. **Confirm Before Update:** Ask user to confirm changes
6. **Track Changes:** Log who updated and when
7. **Retry on 500 Errors:** Implement retry logic for server errors
8. **Use updated_by:** Always include user email for audit trail

---

## Security

### Database Credentials

- Stored in AWS Secrets Manager
- Retrieved at runtime
- Never logged or exposed
- Rotated automatically

### SQL Injection Protection

- Uses parameterized queries
- All inputs are sanitized
- psycopg handles escaping

### CORS

- Configured for specific origins
- Preflight requests supported
- Credentials can be included

---

## Monitoring

### CloudWatch Metrics

- **Invocations:** Number of RCA updates
- **Duration:** Time to update in database
- **Errors:** Failed updates (404, 500)
- **Throttles:** Rate limiting events

### CloudWatch Logs

**Success:**
```
Updating RCA ID: 123
✅ Updated RCA in database: ID=123
✅ RCA update completed successfully for ID 123
```

**Not Found:**
```
❌ Validation error: RCA with ID 123 not found
```

**Error:**
```
❌ Error updating RCA in database: connection timeout
```

---

## Related Endpoints

### POST /submitRCA
Save new RCA to database.

**Purpose:** Create new RCA records  
**Documentation:** See `src/app/submit_rca/API_USAGE.md`

**Example:**
```javascript
const response = await fetch('/api/submitRCA', {
  method: 'POST',
  body: JSON.stringify(rcaData)
});
```

### POST /generateRCA
Generate RCA text using AI.

**Purpose:** AI-powered RCA generation  
**Documentation:** See `src/app/generate_rca/API_USAGE.md`

**Example:**
```javascript
const response = await fetch('/api/generateRCA', {
  method: 'POST',
  body: JSON.stringify({ investigation_summary, deviation_id })
});
```

### GET /getRCACategories
Load category options for dropdowns.

**Purpose:** Get all available RCA categories  
**Documentation:** See `src/app/get_rca_categories/API_USAGE.md`

**Example:**
```javascript
const response = await fetch('/api/getRCACategories');
```

---

## Support

For issues or questions:
- Check CloudWatch logs for detailed error messages
- Verify database connectivity and credentials
- Ensure rca_id exists in database
- Review validation error messages
- Check VPC configuration if database connection fails

---

## Related Documentation

- `README.md` - Complete endpoint documentation
- `lambda_function.py` - Implementation code
- `../submit_rca/API_USAGE.md` - Submit RCA endpoint
- `../generate_rca/API_USAGE.md` - Generate RCA endpoint
- `../get_rca_categories/API_USAGE.md` - Get categories endpoint
