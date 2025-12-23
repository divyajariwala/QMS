# Submit RCA Lambda Function

## Overview

This Lambda function provides a POST endpoint that saves or updates RCA (Root Cause Analysis) data in the PostgreSQL database. It handles the persistence of RCA analysis results submitted by users through the frontend UI.

**New Feature:** Supports batch submission - can save multiple RCAs in a single request.

## Endpoint

**Method:** `POST`  
**Path:** `/submitRCA`  
**Authentication:** As configured in API Gateway

## Request Body

### Single RCA (Backward Compatible)

```json
{
  "deviation_id": "DV-00001",
  "issues": "The investigation revealed multiple issues with the manufacturing process...",
  "issues_category": "Process/Manufacturing Equipment Issue",
  "major_root_cause_category": "Design Issue",
  "major_root_cause_category_validated": "Design Issue",
  "near_root_cause": "The near root cause was identified as inadequate design input...",
  "near_root_cause_category": "Design Input Issue",
  "root_cause": "The fundamental root cause was the failure to consider all design inputs...",
  "root_cause_category": "Design Scope Issue",
  "created_by": "user@example.com"
}
```

### Multiple RCAs (Batch)

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

### Required Fields (Each RCA Object)

| Field | Type | Description |
|-------|------|-------------|
| `deviation_id` | string | Unique deviation identifier |
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
| `created_by` | string | "system" | User who submitted the RCA |

**Note:** For batch requests, `created_by` is taken from the first item in the array.

## Response Structure

### Success Response - Single RCA (200)

```json
{
  "success": true,
  "message": "RCA saved successfully",
  "data": {
    "rca_id": 123,
    "deviation_id": "DV-00001",
    "created_at": "2025-12-22T10:30:00.000000+00:00",
    "updated_at": "2025-12-22T10:30:00.000000+00:00",
    "created_by": "user@example.com"
  },
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
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
        "created_at": "2025-12-22T10:30:00.000000+00:00",
        "updated_at": "2025-12-22T10:30:00.000000+00:00"
      },
      {
        "rca_id": 124,
        "deviation_id": "DV-00001",
        "created_at": "2025-12-22T10:30:01.000000+00:00",
        "updated_at": "2025-12-22T10:30:01.000000+00:00"
      },
      {
        "rca_id": 125,
        "deviation_id": "DV-00001",
        "created_at": "2025-12-22T10:30:02.000000+00:00",
        "updated_at": "2025-12-22T10:30:02.000000+00:00"
      }
    ],
    "created_by": "user@example.com"
  },
  "timestamp": "2025-12-22T10:30:02.000000+00:00"
}
```

### Error Responses

#### 400 - Bad Request (Empty Array)
```json
{
  "success": false,
  "message": "Request body cannot be an empty array",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

#### 400 - Bad Request (Missing Fields)
```json
{
  "success": false,
  "message": "Missing required fields: issues, root_cause",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

#### 400 - Bad Request (Batch - Missing Fields)
```json
{
  "success": false,
  "message": "Item at index 1 missing required fields: issues, root_cause",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

#### 400 - Bad Request (Invalid Data)
```json
{
  "success": false,
  "message": "issues must be a non-empty string",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

#### 400 - Bad Request (Batch - Invalid Data)
```json
{
  "success": false,
  "message": "Item at index 2: issues must be a non-empty string",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

#### 405 - Method Not Allowed
```json
{
  "success": false,
  "message": "Method not allowed. Use POST.",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
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
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

## Database Schema

The function saves data to the `rca_analysis` table:

```sql
CREATE TABLE rca_analysis (
    id SERIAL PRIMARY KEY,
    deviation_id VARCHAR(50) UNIQUE NOT NULL,
    issues TEXT NOT NULL,
    issues_category VARCHAR(255),
    major_root_cause_category TEXT NOT NULL,
    major_root_cause_category_explanation TEXT,
    near_root_cause TEXT NOT NULL,
    near_root_cause_category VARCHAR(255),
    root_cause TEXT NOT NULL,
    root_cause_category VARCHAR(255),
    created_by VARCHAR(255) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Upsert Behavior

The function uses `INSERT ... ON CONFLICT` to handle both new records and updates:

- **New Record:** If `deviation_id` doesn't exist, creates new RCA record
- **Update:** If `deviation_id` exists, updates all fields and sets `updated_at` to current timestamp

## Usage Examples

### cURL - Single RCA

```bash
curl -X POST https://api.example.com/submitRCA \
  -H "Content-Type: application/json" \
  -d '{
    "deviation_id": "DV-00001",
    "issues": "Issues text...",
    "issues_category": "Process/Manufacturing Equipment Issue",
    "major_root_cause_category": "Design Issue",
    "major_root_cause_category_validated": "Design Issue",
    "near_root_cause": "Near root cause text...",
    "near_root_cause_category": "Design Input Issue",
    "root_cause": "Root cause text...",
    "root_cause_category": "Design Scope Issue",
    "created_by": "user@example.com"
  }'
```

### cURL - Batch RCAs

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

### JavaScript/Fetch - Single RCA

```javascript
const submitRCA = async (rcaData) => {
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
};

// Usage
const rcaData = {
  deviation_id: 'DV-00001',
  issues: 'Issues text...',
  issues_category: 'Process/Manufacturing Equipment Issue',
  major_root_cause_category: 'Design Issue',
  major_root_cause_category_validated: 'Design Issue',
  near_root_cause: 'Near root cause text...',
  near_root_cause_category: 'Design Input Issue',
  root_cause: 'Root cause text...',
  root_cause_category: 'Design Scope Issue',
  created_by: 'user@example.com'
};

submitRCA(rcaData)
  .then(result => console.log('Saved:', result))
  .catch(error => console.error('Error:', error));
```

### JavaScript/Fetch - Batch RCAs

```javascript
const submitRCABatch = async (rcaList) => {
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
  .then(result => console.log('Batch saved:', result))
  .catch(error => console.error('Error:', error));
```

### React Hook

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

// Usage in component
function RCAForm() {
  const { submitRCA, loading, error } = useSubmitRCA();

  const handleSubmit = async (formData) => {
    try {
      const result = await submitRCA(formData);
      console.log('RCA saved with ID:', result.rca_id);
      // Show success message
    } catch (err) {
      console.error('Failed to save RCA:', err);
      // Show error message
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={loading}>
        {loading ? 'Saving...' : 'Submit RCA'}
      </button>
      {error && <div className="error">{error}</div>}
    </form>
  );
}
```

## Deployment

### Files Required

```
submit_rca/
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

**Method:** POST  
**Path:** `/submitRCA`  
**CORS:** Enabled  
**Authorization:** As needed  
**Request Validation:** Enabled (recommended)

## Workflow Integration

This endpoint is part of the RCA workflow:

```
1. GET /rca-categories
   └─> Frontend loads category options

2. POST /generate-rca
   └─> Backend generates RCA text using AI

3. User reviews and edits RCA
   └─> Can change categories using dropdowns

4. POST /submitRCA  ← THIS ENDPOINT
   └─> Saves final RCA to database

5. GET /generate-rca?deviation_id=XXX
   └─> Retrieves saved RCA for viewing
```

## Validation

### Field Validation

The function validates:
- ✅ All required fields are present
- ✅ Text fields are non-empty strings
- ✅ `deviation_id` is provided
- ✅ Category fields are provided

### Database Constraints

The database enforces:
- ✅ `deviation_id` is unique
- ✅ Required fields are NOT NULL
- ✅ Timestamps are automatically managed

## Error Handling

### Database Errors

If database save fails:
- Error is logged to CloudWatch
- 500 error returned to client
- Transaction is rolled back
- No partial data is saved

### Validation Errors

If validation fails:
- 400 error returned immediately
- No database operation attempted
- Clear error message provided

## Monitoring

### CloudWatch Metrics

- **Invocations:** Number of RCA submissions
- **Duration:** Time to save to database
- **Errors:** Failed submissions
- **Throttles:** Rate limiting events

### CloudWatch Logs

Key log messages:
```
Environment: dev, Region: us-east-1
Submitting RCA for deviation: DV-00001
✅ Saved RCA to database: ID=123
✅ RCA submission completed successfully for DV-00001
```

Error messages:
```
❌ Validation error: Missing required fields: issues
❌ Error saving RCA to database: connection timeout
```

## Performance

**Expected Response Time:** 200-500ms  
**Database Operation:** Single INSERT/UPDATE  
**Cold Start:** ~500-800ms  
**Warm Start:** ~200ms

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

## Testing

### Unit Tests

```python
# Test successful save
def test_save_rca():
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'deviation_id': 'DV-TEST-001',
            'issues': 'Test issues',
            'issues_category': 'Test Category',
            'major_root_cause_category': 'Test Major',
            'near_root_cause': 'Test Near',
            'near_root_cause_category': 'Test Near Cat',
            'root_cause': 'Test Root',
            'root_cause_category': 'Test Root Cat',
            'created_by': 'test@example.com'
        })
    }
    
    result = lambda_handler(event, None)
    assert result['statusCode'] == 200
```

### Integration Tests

```bash
# Test with real database
curl -X POST https://api-dev.example.com/submitRCA \
  -H "Content-Type: application/json" \
  -d @test_rca.json
```

## Troubleshooting

### Common Issues

**Issue:** "DB_SECRET_NAME not configured"
- **Solution:** Set environment variables correctly

**Issue:** "Missing required fields"
- **Solution:** Ensure all required fields are in request body

**Issue:** "Database connection timeout"
- **Solution:** Check VPC configuration and security groups

**Issue:** "Duplicate key violation"
- **Solution:** This shouldn't happen due to ON CONFLICT, check database state

## Related Documentation

- `../generate_rca/README.md` - RCA generation endpoint
- `../get_rca_categories/README.md` - Category retrieval endpoint
- `schema.sql` - Database schema definition
