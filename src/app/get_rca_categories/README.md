# Get RCA Categories Lambda Function

## Overview

This Lambda function provides a GET endpoint that returns the complete RCA (Root Cause Analysis) category taxonomy for use by the frontend UI. It exposes the structured category data from `rca-edit-data.json` without the verbose `definition` and `number` fields to optimize payload size.

## Endpoint

**Method:** `GET`  
**Path:** `/rca-categories`  
**Authentication:** None (or as configured in API Gateway)

## Response Structure

```json
{
  "success": true,
  "message": "RCA categories retrieved successfully",
  "data": {
    "Factors": [
      {
        "factor_name": "Equipment/Software Issues",
        "ProblemCategories": [
          {
            "name": "Process/Manufacturing Equipment Issue"
          },
          {
            "name": "Software Issue"
          },
          {
            "name": "Material/Product Issue"
          },
          {
            "name": "Utility/Support Equipment Issue"
          },
          {
            "name": "Other Equipment Issue"
          }
        ]
      },
      {
        "factor_name": "Personnel Issues",
        "ProblemCategories": [
          {
            "name": "Company Personnel Issue"
          },
          {
            "name": "Contract Personnel Issue"
          },
          {
            "name": "Third-Party Personnel Issue"
          }
        ]
      },
      {
        "factor_name": "Other Issues",
        "ProblemCategories": [
          {
            "name": "Natural Phenomena"
          },
          {
            "name": "External Events"
          },
          {
            "name": "External Sabotage and Other Criminal Activity"
          },
          {
            "name": "Cause Cannot be Determined"
          }
        ]
      }
    ],
    "MajorRootCauseCategories": [
      {
        "description": "Design Issue",
        "properties": {
          "details": [
            {
              "NearRootCauses": "Design Input Issue",
              "rootcauses": [
                {
                  "name": "Design Scope Issue"
                },
                {
                  "name": "Design Input Data Issue"
                },
                {
                  "name": "Uncertain"
                },
                {
                  "name": "Not Applicable"
                }
              ]
            },
            {
              "NearRootCauses": "Design Output Issue",
              "rootcauses": [
                {
                  "name": "Design Output Incorrect"
                },
                {
                  "name": "Design Output Unclear or Inconsistent"
                },
                {
                  "name": "Uncertain"
                },
                {
                  "name": "Not Applicable"
                }
              ]
            }
          ]
        }
      }
    ]
  },
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

## Usage Examples

### cURL

```bash
curl -X GET https://api.example.com/rca-categories
```

### JavaScript/Fetch

```javascript
const response = await fetch('https://api.example.com/rca-categories');
const data = await response.json();

if (data.success) {
  const categories = data.data;
  console.log('Factors:', categories.Factors);
  console.log('Major Categories:', categories.MajorRootCauseCategories);
}
```

### React Hook

```javascript
import { useState, useEffect } from 'react';

function useRCACategories() {
  const [categories, setCategories] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/rca-categories')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setCategories(data.data);
        } else {
          setError(data.message);
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { categories, loading, error };
}

// Usage in component
function RCAForm() {
  const { categories, loading, error } = useRCACategories();

  if (loading) return <div>Loading categories...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <select>
        {categories.Factors.map(factor => (
          <optgroup key={factor.factor_name} label={factor.factor_name}>
            {factor.ProblemCategories.map(cat => (
              <option key={cat.name} value={cat.name}>
                {cat.name}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
}
```

## Data Structure

### Factors

**Purpose:** Problem categories grouped by factor type (used for "Issues" dropdown)

**Structure:**
- 3 Factors: Equipment/Software, Personnel, Other
- 12 total Problem Categories

### Major Root Cause Categories

**Purpose:** Hierarchical category structure for Major → Near → Root cause selection

**Structure:**
- 14 Major Root Cause Categories
- Each has multiple Near Root Causes (details)
- Each Near Root Cause has multiple Root Causes

## Benefits

### 1. Reduced Payload Size
- Excludes verbose `definition` fields (500+ characters each)
- Excludes `number` fields (not needed by UI)
- ~70-80% smaller than full data

### 2. Optimized for Frontend
- Clean, minimal structure
- Easy to parse and use in dropdowns
- Supports hierarchical filtering

### 3. Cacheable
- Static data that changes infrequently
- Can be cached on frontend
- Reduces API calls

### 4. Single Source of Truth
- All category data from `rca-edit-data.json`
- Consistent with backend RCA generation
- Easy to maintain

## Deployment

### Files Required

```
get_rca_categories/
├── lambda_function.py
├── utils.py
├── __init__.py
├── rca-edit-data.json  ← IMPORTANT: Must be included
└── requirements.txt
```

### Lambda Configuration

**Runtime:** Python 3.11+  
**Memory:** 128 MB (minimal requirements)  
**Timeout:** 10 seconds  
**Environment Variables:** None required

### API Gateway Configuration

**Method:** GET  
**Path:** `/rca-categories`  
**CORS:** Enabled  
**Authorization:** As needed

## Error Handling

### 404 - File Not Found
```json
{
  "success": false,
  "message": "Failed to load RCA categories",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

### 405 - Method Not Allowed
```json
{
  "success": false,
  "message": "Method not allowed. Use GET.",
  "data": {},
  "timestamp": "2025-12-22T10:30:00.000000+00:00"
}
```

### 500 - Internal Server Error
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

## Testing

### Local Testing

```bash
# Navigate to function directory
cd src/app/get_rca_categories

# Test with Python
python -c "
from lambda_function import lambda_handler
import json

event = {'httpMethod': 'GET'}
result = lambda_handler(event, None)
print(json.dumps(json.loads(result['body']), indent=2))
"
```

### Integration Testing

```bash
# Test deployed endpoint
curl -X GET https://api.example.com/rca-categories | jq .
```

## Monitoring

### CloudWatch Metrics

- **Invocations:** Number of API calls
- **Duration:** Response time (should be <100ms)
- **Errors:** Failed requests
- **Throttles:** Rate limiting events

### CloudWatch Logs

Key log messages:
- `Loading RCA categories from: <path>`
- `✅ Successfully loaded X Factors and Y Major Categories`
- `✅ Returning X Factors, Y Problem Categories, Z Major Categories`
- `❌ Error loading RCA categories: <error>`

## Performance

**Expected Response Time:** 50-100ms  
**Payload Size:** ~50-100KB (depending on category count)  
**Cold Start:** ~200-300ms  
**Warm Start:** ~50ms

## Caching Strategy

### Frontend Caching

```javascript
// Cache categories in localStorage
const CACHE_KEY = 'rca_categories';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

async function getCachedCategories() {
  const cached = localStorage.getItem(CACHE_KEY);
  
  if (cached) {
    const { data, timestamp } = JSON.parse(cached);
    const age = Date.now() - timestamp;
    
    if (age < CACHE_DURATION) {
      return data;
    }
  }
  
  // Fetch fresh data
  const response = await fetch('/api/rca-categories');
  const result = await response.json();
  
  if (result.success) {
    localStorage.setItem(CACHE_KEY, JSON.stringify({
      data: result.data,
      timestamp: Date.now()
    }));
    
    return result.data;
  }
  
  return null;
}
```

### API Gateway Caching

Enable caching in API Gateway:
- **TTL:** 3600 seconds (1 hour)
- **Cache Key:** None (static endpoint)
- **Encrypted:** Yes

## Maintenance

### Updating Categories

1. Update `rca-edit-data.json` with new categories
2. Deploy updated Lambda function
3. Clear frontend cache if needed
4. Test endpoint returns new categories

### Version Control

Categories are versioned through:
- Git commits to `rca-edit-data.json`
- Lambda function version/alias
- API Gateway stage

## Related Documentation

- `../generate_rca/README.md` - RCA generation endpoint
- `../generate_rca/FRONTEND_USAGE_EXAMPLE.md` - Frontend integration examples
- `../generate_rca/CATEGORY_OPTIONS_UPDATE.md` - Category structure details
