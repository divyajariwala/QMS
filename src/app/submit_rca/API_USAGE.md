# Submit RCA API Usage Guide

## Overview

The Submit RCA endpoint saves or updates Root Cause Analysis data in the PostgreSQL database. This endpoint handles persistence of RCA analysis results after user review and editing.

**Key Features:** 
- Supports both single RCA submission and batch submission of multiple RCAs in a single request
- Automatically updates the deviations table to mark RCA as generated and approved

**Purpose:** Persist RCA data to database and update deviation status  
**Transaction Safety:** All RCAs in a batch are saved atomically (all succeed or all fail)  
**Dependencies:** PostgreSQL Aurora, AWS Secrets Manager

**Database Updates:**
1. Inserts RCA(s) into `rca_analysis` table
2. Updates `deviations` table:
   - Sets `rca_generated = true`
   - Sets `rca_approved = true`
   - Sets `rca_approved_date = CURRENT_TIMESTAMP`

---

## Endpoint

### POST - Submit RCA
Save or update RCA analysis in the database.

**Endpoint:** `/submitRCA`  
**Method:** `POST`  
**Authentication:** As configured in API Gateway  
**Content-Type:** `application/json`

---

## Request Formats

### Single RCA (Backward Compatible)

```json
{
  "deviation_id": "DV-00001",
  "issues": "Cleaning validation for APS tanks was not completed before use.",
  "issues_category": "Procedure issue",
  "major_root_cause_category": "Equipment/Software Issues",
  "major_root_cause_category_validated": "Equipment/Software Issues",
  "near_root_cause": "Lack of clear procedure to hold all tanks pending cleaning validation.",
  "near_root_cause_category": "Procedure/Instruction Issue",
  "root_cause": "Established cleaning validation procedures were not consistently followed.",
  "root_cause_category": "Procedure Not Used",
  "created_by": "user@example.com"
}
```

### Batch RCAs (Multiple)

```json
[
  {
    "deviation_id": "DV-00001",
    "issues": "Cleaning validation for APS tanks was not completed before use.",
    "issues_category": "Procedure issue",
    "major_root_cause_category": "Equipment/Software Issues",
    "major_root_cause_category_validated": "Equipment/Software Issues",
    "near_root_cause": "Lack of clear procedure to hold all tanks pending cleaning validation.",
    "near_root_cause_category": "Procedure/Instruction Issue",
    "root_cause": "Established cleaning validation procedures were not consistently followed.",
    "root_cause_category": "Procedure Not Used"
  },
  {
    "deviation_id": "DV-00001",
    "issues": "Tanks 41 and 55 were used in production before validation approval.",
    "issues_category": "Procedure issue",
    "major_root_cause_category": "Equipment/Software Issues",
    "major_root_cause_category_validated": "Equipment/Software Issues",
    "near_root_cause": "Validation status was not properly communicated to operations.",
    "near_root_cause_category": "Procedure/Instruction Issue",
    "root_cause": "Failure to enforce tank HOLD status across all equipment.",
    "root_cause_category": "Procedure Not Used"
  },
  {
    "deviation_id": "DV-00001",
    "issues": "Inconsistent handling of cleaning validation across multiple tanks.",
    "issues_category": "Procedure issue",
    "major_root_cause_category": "Equipment/Software Issues",
    "major_root_cause_category_validated": "Equipment/Software Issues",
    "near_root_cause": "No standardized control for validation completion before reuse.",
    "near_root_cause_category": "Procedure/Instruction Issue",
    "root_cause": "Quality procedures existed but were not fully applied.",
    "root_cause_category": "Procedure Not Used"
  }
]
```

---

## Request Parameters

### Required Fields (Each RCA)

| Field | Type | Description |
|-------|------|-------------|
| `deviation_id` | string | Unique deviation identifier |
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
| `created_by` | string | "system" | User email who submitted the RCA |

**Note:** For batch requests, `created_by` is taken from the first item in the array.

---

## Response Structure

### Success Response - Single RCA (200)

```json
{
  "success": true,
  "message": "RCA saved successfully",
  "data": {
    "rca_id": 123,
    "deviation_id": "DV-00001",
    "created_at": "2025-12-23T10:30:00.000000+00:00",
    "updated_at": "2025-12-23T10:30:00.000000+00:00",
    "created_by": "user@example.com",
    "deviations_updated": ["DV-00001"]
  },
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
}
```

**Response Fields:**
- `rca_id`: ID of the saved RCA in rca_analysis table
- `deviation_id`: Deviation identifier
- `created_at`: Timestamp when RCA was created
- `updated_at`: Timestamp when RCA was last updated
- `created_by`: User who submitted the RCA
- `deviations_updated`: Array of deviation IDs that were updated in deviations table
```

### Success Response - Batch (200)

```json
{
  "success": true,
  "message": "3 RCAs saved successfully",
  "data": {
    "saved_count": 3,
    "rcas": [
      {
        "rca_id": 123,
        "deviation_id": "DV-00001",
        "created_at": "2025-12-23T10:30:00.000000+00:00",
        "updated_at": "2025-12-23T10:30:00.000000+00:00"
      },
      {
        "rca_id": 124,
        "deviation_id": "DV-00001",
        "created_at": "2025-12-23T10:30:01.000000+00:00",
        "updated_at": "2025-12-23T10:30:01.000000+00:00"
      },
      {
        "rca_id": 125,
        "deviation_id": "DV-00001",
        "created_at": "2025-12-23T10:30:02.000000+00:00",
        "updated_at": "2025-12-23T10:30:02.000000+00:00"
      }
    ],
    "created_by": "user@example.com",
    "deviations_updated": ["DV-00001"]
  },
  "timestamp": "2025-12-23T10:30:02.000000+00:00"
}
```

**Response Fields:**
- `saved_count`: Number of RCAs saved
- `rcas`: Array of saved RCA objects with IDs and timestamps
- `created_by`: User who submitted the RCAs
- `deviations_updated`: Array of unique deviation IDs that were updated in deviations table

**Note:** If multiple RCAs have the same `deviation_id`, that deviation is only updated once.
```

### Error Response - Empty Array (400)

```json
{
  "success": false,
  "message": "Request body cannot be an empty array",
  "data": {},
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
}
```

### Error Response - Missing Fields (400)

```json
{
  "success": false,
  "message": "Missing required fields: issues, root_cause",
  "data": {},
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
}
```

### Error Response - Batch Missing Fields (400)

```json
{
  "success": false,
  "message": "Item at index 1 missing required fields: issues, root_cause",
  "data": {},
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
}
```

### Error Response - Invalid Data (400)

```json
{
  "success": false,
  "message": "issues must be a non-empty string",
  "data": {},
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
}
```

### Error Response - Batch Invalid Data (400)

```json
{
  "success": false,
  "message": "Item at index 2: issues must be a non-empty string",
  "data": {},
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
}
```

### Error Response - Method Not Allowed (405)

```json
{
  "success": false,
  "message": "Method not allowed. Use POST.",
  "data": {},
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
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
  "timestamp": "2025-12-23T10:30:00.000000+00:00"
}
```

---

## cURL Examples

### Submit Single RCA

```bash
curl -X POST https://api.example.com/submitRCA \
  -H "Content-Type: application/json" \
  -d '{
    "deviation_id": "DV-00001",
    "issues": "Cleaning validation for APS tanks was not completed before use.",
    "issues_category": "Procedure issue",
    "major_root_cause_category": "Equipment/Software Issues",
    "major_root_cause_category_validated": "Equipment/Software Issues",
    "near_root_cause": "Lack of clear procedure to hold all tanks pending cleaning validation.",
    "near_root_cause_category": "Procedure/Instruction Issue",
    "root_cause": "Established cleaning validation procedures were not consistently followed.",
    "root_cause_category": "Procedure Not Used",
    "created_by": "user@example.com"
  }'
```

### Submit Batch RCAs

```bash
curl -X POST https://api.example.com/submitRCA \
  -H "Content-Type: application/json" \
  -d '[
    {
      "deviation_id": "DV-00001",
      "issues": "Cleaning validation for APS tanks was not completed before use.",
      "issues_category": "Procedure issue",
      "major_root_cause_category": "Equipment/Software Issues",
      "major_root_cause_category_validated": "Equipment/Software Issues",
      "near_root_cause": "Lack of clear procedure to hold all tanks pending cleaning validation.",
      "near_root_cause_category": "Procedure/Instruction Issue",
      "root_cause": "Established cleaning validation procedures were not consistently followed.",
      "root_cause_category": "Procedure Not Used"
    },
    {
      "deviation_id": "DV-00001",
      "issues": "Tanks 41 and 55 were used in production before validation approval.",
      "issues_category": "Procedure issue",
      "major_root_cause_category": "Equipment/Software Issues",
      "major_root_cause_category_validated": "Equipment/Software Issues",
      "near_root_cause": "Validation status was not properly communicated to operations.",
      "near_root_cause_category": "Procedure/Instruction Issue",
      "root_cause": "Failure to enforce tank HOLD status across all equipment.",
      "root_cause_category": "Procedure Not Used"
    }
  ]'
```

### With Pretty Print

```bash
curl -X POST https://api.example.com/submitRCA \
  -H "Content-Type: application/json" \
  -d @rca_data.json | jq .
```

---

## JavaScript/Fetch Examples

### Submit Single RCA

```javascript
const submitRCA = async (rcaData) => {
  try {
    const response = await fetch('/api/submitRCA', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(rcaData)
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('RCA saved:', result.data);
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Failed to submit RCA:', error);
    throw error;
  }
};

// Usage
const rcaData = {
  deviation_id: 'DV-00001',
  issues: 'Cleaning validation for APS tanks was not completed before use.',
  issues_category: 'Procedure issue',
  major_root_cause_category: 'Equipment/Software Issues',
  major_root_cause_category_validated: 'Equipment/Software Issues',
  near_root_cause: 'Lack of clear procedure to hold all tanks pending cleaning validation.',
  near_root_cause_category: 'Procedure/Instruction Issue',
  root_cause: 'Established cleaning validation procedures were not consistently followed.',
  root_cause_category: 'Procedure Not Used',
  created_by: 'user@example.com'
};

submitRCA(rcaData)
  .then(result => {
    console.log('Saved with ID:', result.rca_id);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Submit Batch RCAs

```javascript
const submitRCABatch = async (rcaList) => {
  try {
    const response = await fetch('/api/submitRCA', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(rcaList)
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log(`${result.data.saved_count} RCAs saved:`, result.data.rcas);
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Failed to submit RCA batch:', error);
    throw error;
  }
};

// Usage
const rcaList = [
  {
    deviation_id: 'DV-00001',
    issues: 'Cleaning validation for APS tanks was not completed before use.',
    issues_category: 'Procedure issue',
    major_root_cause_category: 'Equipment/Software Issues',
    major_root_cause_category_validated: 'Equipment/Software Issues',
    near_root_cause: 'Lack of clear procedure to hold all tanks pending cleaning validation.',
    near_root_cause_category: 'Procedure/Instruction Issue',
    root_cause: 'Established cleaning validation procedures were not consistently followed.',
    root_cause_category: 'Procedure Not Used'
  },
  {
    deviation_id: 'DV-00001',
    issues: 'Tanks 41 and 55 were used in production before validation approval.',
    issues_category: 'Procedure issue',
    major_root_cause_category: 'Equipment/Software Issues',
    major_root_cause_category_validated: 'Equipment/Software Issues',
    near_root_cause: 'Validation status was not properly communicated to operations.',
    near_root_cause_category: 'Procedure/Instruction Issue',
    root_cause: 'Failure to enforce tank HOLD status across all equipment.',
    root_cause_category: 'Procedure Not Used'
  }
];

submitRCABatch(rcaList)
  .then(result => {
    console.log(`Batch saved: ${result.saved_count} RCAs`);
    result.rcas.forEach((rca, idx) => {
      console.log(`  ${idx + 1}. ID: ${rca.rca_id}, Deviation: ${rca.deviation_id}`);
    });
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

---

## React Hook Example

```javascript
import { useState } from 'react';

function useSubmitRCA() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submitRCA = async (rcaData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/submitRCA', {
        method: 'POST',
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

  return { submitRCA, loading, error };
}

// Usage in component - Single RCA
function RCAForm({ rcaData }) {
  const { submitRCA, loading, error } = useSubmitRCA();

  const handleSubmit = async () => {
    try {
      const result = await submitRCA(rcaData);
      console.log('RCA saved with ID:', result.rca_id);
      // Show success message
    } catch (err) {
      console.error('Failed to save RCA:', err);
      // Show error message
    }
  };

  return (
    <div>
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Saving...' : 'Submit RCA'}
      </button>
      {error && <div className="error">{error}</div>}
    </div>
  );
}

// Usage in component - Batch RCAs
function RCABatchForm({ rcaList }) {
  const { submitRCA, loading, error } = useSubmitRCA();

  const handleBatchSubmit = async () => {
    try {
      const result = await submitRCA(rcaList);
      console.log(`${result.saved_count} RCAs saved`);
      // Show success message
    } catch (err) {
      console.error('Failed to save RCA batch:', err);
      // Show error message
    }
  };

  return (
    <div>
      <button onClick={handleBatchSubmit} disabled={loading}>
        {loading ? 'Saving...' : `Submit ${rcaList.length} RCAs`}
      </button>
      {error && <div className="error">{error}</div>}
    </div>
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

3. User reviews and edits RCA in UI
   └─> Can modify text fields
   └─> Can change categories using dropdowns
   └─> Can add/remove multiple root causes

4. POST /submitRCA  ← THIS ENDPOINT
   └─> Save final RCA(s) to database
   └─> Returns rca_id(s)

5. GET /rca (future)
   └─> Retrieve saved RCA for viewing/editing
```

---

## Workflow Example

```javascript
// Complete workflow from generation to save
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
    
    // 3. Display in UI for user review/editing
    displayRCAForm(generatedRCA.data, categories.data);
    
    // 4. User edits and adds multiple root causes
    const editedRCAs = [
      {
        deviation_id: deviationId,
        issues: editedIssues1,
        issues_category: selectedIssuesCategory1,
        major_root_cause_category: editedMajorCategory1,
        major_root_cause_category_validated: selectedMajorCategory1,
        near_root_cause: editedNearCause1,
        near_root_cause_category: selectedNearCategory1,
        root_cause: editedRootCause1,
        root_cause_category: selectedRootCategory1,
        created_by: user.email
      },
      {
        deviation_id: deviationId,
        issues: editedIssues2,
        issues_category: selectedIssuesCategory2,
        major_root_cause_category: editedMajorCategory2,
        major_root_cause_category_validated: selectedMajorCategory2,
        near_root_cause: editedNearCause2,
        near_root_cause_category: selectedNearCategory2,
        root_cause: editedRootCause2,
        root_cause_category: selectedRootCategory2,
        created_by: user.email
      }
    ];
    
    // 5. Save to database
    const saveResponse = await fetch('/api/submitRCA', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editedRCAs)
    });
    const saved = await saveResponse.json();
    
    console.log(`${saved.data.saved_count} RCAs saved successfully`);
    
  } catch (error) {
    console.error('RCA workflow error:', error);
  }
};
```

---

## Database Behavior

### Tables Updated

**1. rca_analysis Table:**
- Inserts new RCA record(s)
- Allows multiple RCAs per deviation_id
- Sets created_at and updated_at timestamps
- Stores all RCA fields

**2. deviations Table:**
- Updates existing deviation record
- Sets `rca_generated = true`
- Sets `rca_approved = true`
- Sets `rca_approved_date = CURRENT_TIMESTAMP`
- Only updates once per unique deviation_id (even if multiple RCAs)

### Transaction Safety

All database operations are performed in a single transaction:
- ✅ All RCA inserts succeed together
- ✅ All deviation updates succeed together
- ✅ All fail together (rollback)
- ✅ No partial saves

### Example Database State

**Before Submit:**
```sql
-- deviations table
deviation_id | rca_generated | rca_approved | rca_approved_date
DV-00001     | false         | false        | NULL

-- rca_analysis table
(empty)
```

**After Submit (3 RCAs for DV-00001):**
```sql
-- deviations table
deviation_id | rca_generated | rca_approved | rca_approved_date
DV-00001     | true          | true         | 2025-12-23 10:30:00

-- rca_analysis table
id  | deviation_id | issues                    | created_at
123 | DV-00001     | Cleaning validation...    | 2025-12-23 10:30:00
124 | DV-00001     | Tanks 41 and 55...        | 2025-12-23 10:30:01
125 | DV-00001     | Inconsistent handling...  | 2025-12-23 10:30:02
```

---

## Validation Rules

### Field Validation

The endpoint validates:
- ✅ All required fields are present
- ✅ Text fields are non-empty strings
- ✅ `deviation_id` is provided
- ✅ Category fields are provided
- ✅ Array is not empty (for batch requests)
- ✅ Each item in array is an object (for batch requests)

### Error Messages

Validation errors are clear and specific:
- Single RCA: `"issues must be a non-empty string"`
- Batch RCA: `"Item at index 2: issues must be a non-empty string"`

---

## Performance

### Response Times

| Request Type | Cold Start | Warm Start |
|--------------|------------|------------|
| Single RCA | ~500-800ms | ~200-300ms |
| Batch (3 RCAs) | ~600-900ms | ~300-500ms |
| Batch (10 RCAs) | ~800-1200ms | ~500-800ms |

### Recommendations

- ✅ Keep batch size under 50 RCAs for optimal performance
- ✅ Use batch submission when saving multiple RCAs for same deviation
- ✅ Single submission is fine for one-off saves

---

## Error Handling

### Common Errors

| Status Code | Message | Cause | Solution |
|-------------|---------|-------|----------|
| 400 | Request body cannot be an empty array | Empty array sent | Send at least one RCA |
| 400 | Missing required fields: issues | Missing required field | Include all required fields |
| 400 | Item at index 1 missing required fields | Batch item missing field | Check all items in batch |
| 400 | issues must be a non-empty string | Empty or non-string value | Provide non-empty string |
| 405 | Method not allowed. Use POST. | Wrong HTTP method | Use POST method only |
| 500 | Internal server error | Database or server error | Check CloudWatch logs |

### Error Handling Example

```javascript
const submitRCAWithErrorHandling = async (rcaData) => {
  try {
    const response = await fetch('/api/submitRCA', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rcaData)
    });
    
    const result = await response.json();
    
    if (!result.success) {
      // Handle specific error cases
      if (response.status === 400) {
        console.error('Validation error:', result.message);
        // Show validation error to user
      } else if (response.status === 500) {
        console.error('Server error:', result.message);
        // Show generic error to user
      }
      throw new Error(result.message);
    }
    
    return result.data;
    
  } catch (error) {
    console.error('Failed to submit RCA:', error);
    throw error;
  }
};
```

---

## Testing

### Test Event - Single RCA (Lambda Console)

```json
{
  "httpMethod": "POST",
  "body": "{\"deviation_id\":\"DV-TEST-001\",\"issues\":\"Test issue\",\"issues_category\":\"Test Category\",\"major_root_cause_category\":\"Test Major\",\"near_root_cause\":\"Test Near\",\"near_root_cause_category\":\"Test Near Cat\",\"root_cause\":\"Test Root\",\"root_cause_category\":\"Test Root Cat\",\"created_by\":\"test@example.com\"}"
}
```

### Test Event - Batch RCAs (Lambda Console)

```json
{
  "httpMethod": "POST",
  "body": "[{\"deviation_id\":\"DV-TEST-001\",\"issues\":\"Test issue 1\",\"issues_category\":\"Test Category\",\"major_root_cause_category\":\"Test Major\",\"near_root_cause\":\"Test Near\",\"near_root_cause_category\":\"Test Near Cat\",\"root_cause\":\"Test Root\",\"root_cause_category\":\"Test Root Cat\"},{\"deviation_id\":\"DV-TEST-002\",\"issues\":\"Test issue 2\",\"issues_category\":\"Test Category\",\"major_root_cause_category\":\"Test Major\",\"near_root_cause\":\"Test Near\",\"near_root_cause_category\":\"Test Near Cat\",\"root_cause\":\"Test Root\",\"root_cause_category\":\"Test Root Cat\"}]"
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

1. **Use Batch for Multiple RCAs:** When saving multiple root causes for the same deviation, use batch submission
2. **Validate Before Submitting:** Validate data on frontend before sending to reduce errors
3. **Handle Errors Gracefully:** Show user-friendly error messages
4. **Include created_by:** Always include user email for audit trail
5. **Use Validated Categories:** Prefer `major_root_cause_category_validated` over `major_root_cause_category`
6. **Check Response:** Always check `success` field in response
7. **Retry on 500 Errors:** Implement retry logic for server errors
8. **Keep Batch Size Reasonable:** Don't exceed 50 RCAs per batch

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

- **Invocations:** Number of RCA submissions
- **Duration:** Time to save to database
- **Errors:** Failed submissions
- **Throttles:** Rate limiting events

### CloudWatch Logs

**Single RCA:**
```
Processing single RCA
Submitting single RCA for deviation: DV-00001
✅ Saved RCA 1/1: ID=123, deviation=DV-00001
Updating deviations table for deviation: DV-00001
✅ Updated deviation DV-00001: rca_generated=true, rca_approved=true, rca_approved_date=2025-12-23 10:30:00
✅ Single RCA submission completed successfully
```

**Batch RCAs:**
```
Processing batch of 3 RCAs
Saving batch of 3 RCAs
✅ Saved RCA 1/3: ID=123, deviation=DV-00001
✅ Saved RCA 2/3: ID=124, deviation=DV-00001
✅ Saved RCA 3/3: ID=125, deviation=DV-00001
Updating deviations table for deviation: DV-00001
✅ Updated deviation DV-00001: rca_generated=true, rca_approved=true, rca_approved_date=2025-12-23 10:30:00
✅ Successfully saved batch of 3 RCAs and updated 1 deviation(s)
✅ Batch RCA submission completed successfully: 3 RCAs saved
```

---

## Related Endpoints

### GET /getRCACategories
Load category options for dropdowns.

**Purpose:** Get all available RCA categories for UI dropdowns  
**Documentation:** See `src/app/get_rca_categories/API_USAGE.md`

**Example:**
```javascript
const response = await fetch('/api/getRCACategories');
const categories = await response.json();
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
const rca = await response.json();
```

---

## Support

For issues or questions:
- Check CloudWatch logs for detailed error messages
- Verify database connectivity and credentials
- Ensure all required fields are provided
- Review validation error messages
- Check VPC configuration if database connection fails

---

## Related Documentation

- `README.md` - Complete endpoint documentation
- `BATCH_SUPPORT_SUMMARY.md` - Batch feature details
- `lambda_function.py` - Implementation code
- `../generate_rca/API_USAGE.md` - RCA generation endpoint
- `../get_rca_categories/API_USAGE.md` - Category retrieval endpoint
