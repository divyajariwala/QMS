# Get RCA Categories API Usage Guide

## Overview

The Get RCA Categories endpoint provides the complete RCA (Root Cause Analysis) category taxonomy for populating dropdown menus in the UI. This endpoint returns a structured hierarchy of categories without verbose fields, optimized for frontend consumption.

**Purpose:** Load category options for RCA form dropdowns  
**Caching:** Highly cacheable - data changes infrequently  
**Dependencies:** None (reads from static JSON file)

---

## Endpoint

### GET - Get RCA Categories
Retrieve the complete RCA category taxonomy.

**Endpoint:** `/getRCACategories`  
**Method:** `GET`  
**Authentication:** As configured in API Gateway  
**Parameters:** None required

---

## Response Structure

### Success Response (200)

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
      },
      {
        "description": "Equipment Reliability Program Issue",
        "properties": {
          "details": [
            {
              "NearRootCauses": "Equipment Reliability Program Design Issue",
              "rootcauses": [
                {
                  "name": "Critical Equipment Not Identified"
                },
                {
                  "name": "No or Inappropriate Maintenance Selected"
                }
              ]
            }
          ]
        }
      }
    ]
  },
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

### Statistics

**Response includes:**
- 3 Factors (Equipment/Software, Personnel, Other)
- 12 Problem Categories (for Issues dropdown)
- 14 Major Root Cause Categories
- 68 Near Root Causes
- 100+ Root Causes

**Payload Size:** ~16 KB (91% smaller than full data with definitions)

---

## Data Structure

### Factors (Problem Categories)

Used for the **Issues** section dropdown.

```json
{
  "factor_name": "Equipment/Software Issues",
  "ProblemCategories": [
    { "name": "Process/Manufacturing Equipment Issue" },
    { "name": "Software Issue" },
    ...
  ]
}
```

**Purpose:** Group problem categories by factor type  
**Usage:** Flatten all ProblemCategories for Issues dropdown

### Major Root Cause Categories

Used for hierarchical dropdowns: **Major → Near → Root**

```json
{
  "description": "Design Issue",
  "properties": {
    "details": [
      {
        "NearRootCauses": "Design Input Issue",
        "rootcauses": [
          { "name": "Design Scope Issue" },
          { "name": "Design Input Data Issue" }
        ]
      }
    ]
  }
}
```

**Purpose:** Hierarchical category structure  
**Usage:** 
- Major categories for Major Root Cause dropdown
- Near causes filtered by selected major category
- Root causes filtered by selected near cause

---

## cURL Examples

### Basic Request

```bash
curl -X GET https://api.example.com/getRCACategories
```

### With Pretty Print

```bash
curl -X GET https://api.example.com/getRCACategories | jq .
```

### Save to File

```bash
curl -X GET https://api.example.com/getRCACategories -o categories.json
```

---

## JavaScript/Fetch Examples

### Basic Fetch

```javascript
const loadCategories = async () => {
  try {
    const response = await fetch('/api/getRCACategories');
    const result = await response.json();
    
    if (result.success) {
      console.log('Categories loaded:', result.data);
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Failed to load categories:', error);
    throw error;
  }
};

// Usage
const categories = await loadCategories();
console.log('Factors:', categories.Factors);
console.log('Major Categories:', categories.MajorRootCauseCategories);
```

### With Caching (localStorage)

```javascript
const CACHE_KEY = 'rca_categories';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

const getCachedCategories = async () => {
  // Check cache first
  const cached = localStorage.getItem(CACHE_KEY);
  
  if (cached) {
    const { data, timestamp } = JSON.parse(cached);
    const age = Date.now() - timestamp;
    
    if (age < CACHE_DURATION) {
      console.log('Using cached categories');
      return data;
    }
  }
  
  // Fetch fresh data
  console.log('Fetching fresh categories');
  const response = await fetch('/api/getRCACategories');
  const result = await response.json();
  
  if (result.success) {
    // Cache the data
    localStorage.setItem(CACHE_KEY, JSON.stringify({
      data: result.data,
      timestamp: Date.now()
    }));
    
    return result.data;
  }
  
  throw new Error(result.message);
};

// Usage
const categories = await getCachedCategories();
```

### Extract Dropdown Options

```javascript
const loadCategories = async () => {
  const response = await fetch('/api/getRCACategories');
  const result = await response.json();
  const categories = result.data;
  
  // Extract Issues categories (flatten all problem categories)
  const issuesCategories = [];
  categories.Factors.forEach(factor => {
    factor.ProblemCategories.forEach(cat => {
      issuesCategories.push(cat.name);
    });
  });
  
  // Extract Major categories
  const majorCategories = categories.MajorRootCauseCategories.map(
    cat => cat.description
  );
  
  return {
    issuesCategories,
    majorCategories,
    fullData: categories
  };
};

// Usage
const { issuesCategories, majorCategories, fullData } = await loadCategories();
```

---

## React Hook Example

```javascript
import { useState, useEffect } from 'react';

function useRCACategories() {
  const [categories, setCategories] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await fetch('/api/getRCACategories');
        const result = await response.json();
        
        if (result.success) {
          setCategories(result.data);
        } else {
          setError(result.message);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadCategories();
  }, []);

  return { categories, loading, error };
}

// Usage in component
function RCAForm() {
  const { categories, loading, error } = useRCACategories();

  if (loading) return <div>Loading categories...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!categories) return null;

  return (
    <div>
      {/* Issues Dropdown */}
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

      {/* Major Category Dropdown */}
      <select>
        {categories.MajorRootCauseCategories.map(cat => (
          <option key={cat.description} value={cat.description}>
            {cat.description}
          </option>
        ))}
      </select>
    </div>
  );
}
```

---

## Hierarchical Dropdown Implementation

### Get Near Causes by Major Category

```javascript
const getNearCauseOptions = (categories, majorCategory) => {
  // Find the major category object
  const majorCat = categories.MajorRootCauseCategories.find(
    cat => cat.description === majorCategory
  );
  
  if (!majorCat) return [];
  
  // Extract near root causes
  return majorCat.properties.details.map(detail => detail.NearRootCauses);
};

// Usage
const nearCauses = getNearCauseOptions(categories, 'Design Issue');
// Returns: ["Design Input Issue", "Design Output Issue", ...]
```

### Get Root Causes by Near Cause

```javascript
const getRootCauseOptions = (categories, majorCategory, nearCause) => {
  // Find the major category
  const majorCat = categories.MajorRootCauseCategories.find(
    cat => cat.description === majorCategory
  );
  
  if (!majorCat) return [];
  
  // Find the near cause detail
  const nearCauseDetail = majorCat.properties.details.find(
    detail => detail.NearRootCauses === nearCause
  );
  
  if (!nearCauseDetail) return [];
  
  // Return root cause names
  return nearCauseDetail.rootcauses.map(rc => rc.name);
};

// Usage
const rootCauses = getRootCauseOptions(
  categories,
  'Design Issue',
  'Design Input Issue'
);
// Returns: ["Design Scope Issue", "Design Input Data Issue", ...]
```

### Complete Dropdown Component

```javascript
function RCADropdowns({ categories, rcaData, onChange }) {
  const [selectedMajor, setSelectedMajor] = useState(rcaData.major_root_cause_category_validated);
  const [selectedNear, setSelectedNear] = useState(rcaData.near_root_cause_category);

  // Get filtered options
  const nearCauseOptions = getNearCauseOptions(categories, selectedMajor);
  const rootCauseOptions = getRootCauseOptions(categories, selectedMajor, selectedNear);

  return (
    <div>
      {/* Issues Dropdown */}
      <select 
        value={rcaData.issues_category}
        onChange={(e) => onChange('issues_category', e.target.value)}
      >
        {categories.Factors.flatMap(factor =>
          factor.ProblemCategories.map(cat => (
            <option key={cat.name} value={cat.name}>
              {cat.name}
            </option>
          ))
        )}
      </select>

      {/* Major Category Dropdown */}
      <select 
        value={selectedMajor}
        onChange={(e) => {
          setSelectedMajor(e.target.value);
          onChange('major_root_cause_category_validated', e.target.value);
        }}
      >
        {categories.MajorRootCauseCategories.map(cat => (
          <option key={cat.description} value={cat.description}>
            {cat.description}
          </option>
        ))}
      </select>

      {/* Near Cause Dropdown (filtered by major) */}
      <select 
        value={selectedNear}
        onChange={(e) => {
          setSelectedNear(e.target.value);
          onChange('near_root_cause_category', e.target.value);
        }}
      >
        {nearCauseOptions.map(cause => (
          <option key={cause} value={cause}>
            {cause}
          </option>
        ))}
      </select>

      {/* Root Cause Dropdown (filtered by near) */}
      <select 
        value={rcaData.root_cause_category}
        onChange={(e) => onChange('root_cause_category', e.target.value)}
      >
        {rootCauseOptions.map(cause => (
          <option key={cause} value={cause}>
            {cause}
          </option>
        ))}
      </select>
    </div>
  );
}
```

---

## Error Handling

### Error Responses

#### 405 - Method Not Allowed
```json
{
  "success": false,
  "message": "Method not allowed. Use GET.",
  "data": {},
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

#### 500 - Internal Server Error
```json
{
  "success": false,
  "message": "Failed to load RCA categories",
  "data": {},
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

### Error Handling Example

```javascript
const loadCategories = async () => {
  try {
    const response = await fetch('/api/getRCACategories');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.message);
    }
    
    return result.data;
    
  } catch (error) {
    console.error('Failed to load categories:', error);
    
    // Fallback to empty structure
    return {
      Factors: [],
      MajorRootCauseCategories: []
    };
  }
};
```

---

## Performance

### Response Times

- **Cold Start:** ~200-300ms (Lambda initialization)
- **Warm Start:** ~50ms (file read only)
- **Cached (API Gateway):** ~10-20ms

### Payload Size

- **Full data (with definitions):** ~180 KB
- **Optimized response:** ~16 KB
- **Reduction:** 91%

### Optimization Tips

1. **Cache on Frontend:** Store in localStorage/sessionStorage
2. **Cache Duration:** 24 hours (data rarely changes)
3. **API Gateway Caching:** Enable with 1-hour TTL
4. **CloudFront:** Add CDN layer for global distribution

---

## Caching Strategy

### Frontend Caching

```javascript
class CategoryCache {
  static CACHE_KEY = 'rca_categories';
  static CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

  static async get() {
    const cached = localStorage.getItem(this.CACHE_KEY);
    
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      
      if (Date.now() - timestamp < this.CACHE_DURATION) {
        return data;
      }
    }
    
    return null;
  }

  static set(data) {
    localStorage.setItem(this.CACHE_KEY, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
  }

  static clear() {
    localStorage.removeItem(this.CACHE_KEY);
  }
}

// Usage
const categories = await CategoryCache.get() || await fetchCategories();
CategoryCache.set(categories);
```

### API Gateway Caching

Enable caching in API Gateway:
- **Cache TTL:** 3600 seconds (1 hour)
- **Cache Key:** None (static endpoint)
- **Encrypted:** Yes

### CloudFront Caching

Add CloudFront distribution:
- **TTL:** 86400 seconds (24 hours)
- **Query String:** Ignore
- **Cookies:** Ignore

---

## Testing

### Test with cURL

```bash
# Basic test
curl -X GET https://api.example.com/getRCACategories

# Test response time
curl -w "\nTime: %{time_total}s\n" -X GET https://api.example.com/getRCACategories

# Test with invalid method
curl -X POST https://api.example.com/getRCACategories
```

### Test Event (Lambda Console)

```json
{
  "httpMethod": "GET"
}
```

### Test OPTIONS (CORS)

```json
{
  "httpMethod": "OPTIONS"
}
```

---

## Integration with Other Endpoints

### Complete RCA Workflow

```javascript
// 1. Load categories (once, on page load)
const categories = await fetch('/api/getRCACategories')
  .then(r => r.json())
  .then(r => r.data);

// 2. Generate RCA
const rca = await fetch('/api/generateRCA', {
  method: 'POST',
  body: JSON.stringify({ investigation_summary, deviation_id })
}).then(r => r.json()).then(r => r.data);

// 3. Display with dropdowns populated from categories
displayRCAForm(rca, categories);

// 4. User reviews/edits

// 5. Save to database
await fetch('/api/submit-rca', {
  method: 'POST',
  body: JSON.stringify(editedRCA)
});
```

---

## TypeScript Types

```typescript
interface CategoryResponse {
  success: boolean;
  message: string;
  data: CategoryData;
  timestamp: string;
}

interface CategoryData {
  Factors: Factor[];
  MajorRootCauseCategories: MajorRootCauseCategory[];
}

interface Factor {
  factor_name: string;
  ProblemCategories: ProblemCategory[];
}

interface ProblemCategory {
  name: string;
}

interface MajorRootCauseCategory {
  description: string;
  properties: {
    details: NearRootCauseDetail[];
  };
}

interface NearRootCauseDetail {
  NearRootCauses: string;
  rootcauses: RootCause[];
}

interface RootCause {
  name: string;
}
```

---

## Best Practices

1. **Load Once:** Fetch categories once on app initialization
2. **Cache Aggressively:** Data changes infrequently
3. **Handle Errors:** Provide fallback empty structure
4. **Validate Data:** Check structure before using
5. **Filter Hierarchically:** Use validated major category for filtering
6. **Refresh Periodically:** Clear cache daily or on app update
7. **Monitor Performance:** Track load times and cache hit rates

---

## Common Use Cases

### Populate All Dropdowns

```javascript
const categories = await fetch('/api/getRCACategories').then(r => r.json());

// Issues dropdown
const issuesOptions = categories.data.Factors.flatMap(
  f => f.ProblemCategories.map(c => c.name)
);

// Major category dropdown
const majorOptions = categories.data.MajorRootCauseCategories.map(
  c => c.description
);
```

### Filter by Selection

```javascript
// When user selects major category
const onMajorCategoryChange = (selectedMajor) => {
  const majorCat = categories.MajorRootCauseCategories.find(
    c => c.description === selectedMajor
  );
  
  const nearOptions = majorCat.properties.details.map(
    d => d.NearRootCauses
  );
  
  setNearCauseOptions(nearOptions);
};
```

### Validate Selection

```javascript
const isValidCategory = (categories, major, near, root) => {
  const majorCat = categories.MajorRootCauseCategories.find(
    c => c.description === major
  );
  
  if (!majorCat) return false;
  
  const nearDetail = majorCat.properties.details.find(
    d => d.NearRootCauses === near
  );
  
  if (!nearDetail) return false;
  
  return nearDetail.rootcauses.some(rc => rc.name === root);
};
```

---

## Support

For issues or questions:
- Check CloudWatch logs for errors
- Verify `rca-edit-data.json` is in deployment package
- Ensure proper CORS configuration
- Review response structure matches expected format

---

## Related Documentation

- `README.md` - Complete endpoint documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `../generate_rca/API_USAGE.md` - RCA generation endpoint
- `../submit_rca/README.md` - RCA submission endpoint
