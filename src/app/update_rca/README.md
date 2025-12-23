# Update RCA Lambda Function

## Overview

This Lambda function provides a PUT endpoint that updates an existing RCA (Root Cause Analysis) record in the PostgreSQL database. It allows users to modify all fields of a previously saved RCA.

**Method:** `PUT`  
**Path:** `/updateRCA`  
**Authentication:** As configured in API Gateway

---

## Request Body

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

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `rca_id` | integer | ID of the RCA record to update (must be positive) |
| `deviation_id` | string | Deviation identifier (non-empty) |
| `issues` | string | Issues text (non-empty) |
| `issues_category` | string | Selected issues category |
| `major_root_cause_category` | string | Major root cause category text (non-empty) |
| `near_root_cause` | string | Near root cause text (non-empty) |
| `near_root_cause_category` | string | Selected near root cause category |
| `root_cause` | string | Root cause text (non-empty) |
| `root_cause_category` | string | Selected root cause category |

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

### Error Responses

#### 400 - Bad Request (Missing Fields)
```json
{
  "success": false,
  "message": "Missing required fields: rca_id, issues",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

#### 400 - Bad Request (Invalid rca_id)
```json
{
  "success": false,
  "message": "rca_id must be a positive integer",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

#### 404 - Not Found
```json
{
  "success": false,
  "message": "RCA with ID 123 not found",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

#### 405 - Method Not Allowed
```json
{
  "success": false,
  "message": "Method not allowed. Use PUT.",
  "data": {},
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

#### 500 - Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {
    "details": "Error message here"
  },
  "timestamp": "2025-12-23T15:45:00.000000+00:00"
}
```

---

## Database Behavior

### Update Logic

The function performs a standard UPDATE operation:

1. **Check if RCA exists:** Queries database for the given `rca_id`
2. **If not found:** Returns 404 error
3. **If found:** Updates all fields and sets `updated_at` to current timestamp
4. **Returns:** Updated record metadata

**Important Notes:**
- `created_at` is NOT modified (preserves original creation time)
- `updated_at` is automatically set to current timestamp
- `created_by` is replaced with `updated_by` value
- All fields are replaced (full update, not partial)

---

## Usage Examples

### cURL

```bash
curl -X PUT https://api.example.com/updateRCA \
  -H "Content-Type: application/json" \
  -d '{
    "rca_id": 123,
    "deviation_id": "DV-00001",
    "issues": "Updated issues text...",
    "issues_category": "Procedure issue",
    "major_root_cause_category": "Equipment/Software Issues",
    "major_root_cause_category_validated": "Equipment/Software Issues",
    "near_root_cause": "Updated near root cause text...",
    "near_root_cause_category": "Procedure/Instruction Issue",
    "root_cause": "Updated root cause text...",
    "root_cause_category": "Procedure Not Used",
    "updated_by": "user@example.com"
  }'
```

### JavaScript/Fetch

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
  issues: 'Updated issues text...',
  issues_category: 'Procedure issue',
  major_root_cause_category: 'Equipment/Software Issues',
  major_root_cause_category_validated: 'Equipment/Software Issues',
  near_root_cause: 'Updated near root cause text...',
  near_root_cause_category: 'Procedure/Instruction Issue',
  root_cause: 'Updated root cause text...',
  root_cause_category: 'Procedure Not Used',
  updated_by: 'user@example.com'
};

updateRCA(rcaData)
  .then(result => console.log('Updated:', result))
  .catch(error => console.error('Error:', error));
```

### React Hook

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

  const handleSubmit = async () => {
    try {
      const result = await updateRCA(formData);
      console.log('RCA updated:', result);
      // Show success message
    } catch (err) {
      console.error('Failed to update RCA:', err);
      // Show error message
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={loading}>
        {loading ? 'Updating...' : 'Update RCA'}
      </button>
      {error && <div className="error">{error}</div>}
    </form>
  );
}
```

---

## Workflow Integration

This endpoint is part of the complete RCA workflow:

```
1. GET /getRCACategories
   └─> Load category options for dropdowns

2. POST /generateRCA
   └─> Generate RCA text using AI

3. POST /submitRCA
   └─> Save new RCA to database
   └─> Returns rca_id

4. GET /rca?deviation_id=XXX (future)
   └─> Retrieve saved RCAs for viewing

5. PUT /updateRCA  ← THIS ENDPOINT
   └─> Update existing RCA
   └─> Requires rca_id
```

---

## Validation

### Field Validation

The function validates:
- ✅ All required fields are present
- ✅ `rca_id` is a positive integer
- ✅ Text fields are non-empty strings
- ✅ `deviation_id` is provided
- ✅ Category fields are provided

### Database Validation

The database enforces:
- ✅ RCA with given `rca_id` must exist
- ✅ Required fields are NOT NULL
- ✅ Timestamps are automatically managed

---

## Error Handling

### Common Errors

| Status Code | Message | Cause | Solution |
|-------------|---------|-------|----------|
| 400 | Missing required fields: rca_id | Missing rca_id | Include rca_id in request |
| 400 | rca_id must be a positive integer | Invalid rca_id type | Provide integer > 0 |
| 400 | issues must be a non-empty string | Empty or non-string value | Provide non-empty string |
| 404 | RCA with ID 123 not found | RCA doesn't exist | Verify rca_id is correct |
| 405 | Method not allowed. Use PUT. | Wrong HTTP method | Use PUT method only |
| 500 | Internal server error | Database or server error | Check CloudWatch logs |

---

## Deployment

### Files Required

```
update_rca/
├── lambda_function.py
├── utils.py
├── secrets_util.py
├── __init__.py
└── requirements.txt
```

### Lambda Configuration

**Runtime:** Python 3.11+  
**Memory:** 256 MB  
**Timeout:** 30 seconds  
**Handler:** `lambda_function.lambda_handler`

**Environment Variables:**
- `env` - Environment name (dev, staging, prod)
- `aws_region` - AWS region (default: us-east-1)
- `db_secret_base_name` - Base name for DB secret (default: aurora-postgres-master)

**IAM Permissions Required:**
- `secretsmanager:GetSecretValue` - To retrieve database credentials
- VPC access if database is in VPC

### API Gateway Configuration

**Method:** PUT  
**Path:** `/updateRCA`  
**CORS:** Enabled  
**Authorization:** As needed

---

## Performance

**Expected Response Time:** 200-500ms  
**Database Operation:** Single UPDATE  
**Cold Start:** ~500-800ms  
**Warm Start:** ~200ms

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
- **Errors:** Failed updates
- **Throttles:** Rate limiting events

### CloudWatch Logs

**Success:**
```
Updating RCA ID: 123
✅ Updated RCA in database: ID=123
✅ RCA update completed successfully for ID 123
```

**Error:**
```
❌ Validation error: RCA with ID 123 not found
❌ Error updating RCA in database: connection timeout
```

---

## Testing

### Test Event (Lambda Console)

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

## Troubleshooting

### Common Issues

**Issue:** "RCA with ID 123 not found"
- **Solution:** Verify the RCA exists in database with that ID

**Issue:** "Missing required fields"
- **Solution:** Ensure all required fields are in request body

**Issue:** "Database connection timeout"
- **Solution:** Check VPC configuration and security groups

**Issue:** "rca_id must be a positive integer"
- **Solution:** Ensure rca_id is a number, not a string

---

## Related Documentation

- `../submit_rca/README.md` - RCA submission endpoint
- `../generate_rca/README.md` - RCA generation endpoint
- `../get_rca_categories/README.md` - Category retrieval endpoint
