# Generate RCA API Usage Guide

## Overview

The Generate RCA endpoint uses AI (AWS Bedrock Claude) to automatically generate Root Cause Analysis based on an investigation summary. This endpoint focuses exclusively on AI-powered generation and returns the generated text with auto-selected categories.

**Important:** This endpoint does NOT save to database. Use the separate `/submit-rca` endpoint to save the generated RCA.

---

## Endpoint

### POST - Generate RCA
Generate a new Root Cause Analysis using AI.

**Endpoint:** `/generate-rca`  
**Method:** `POST`  
**Purpose:** AI-powered RCA generation only (no database operations)

#### Request Body
```json
{
  "investigation_summary": "Analyst S. Juyal generated duplicate results for the osmolality assay...",
  "deviation_id": "DV-12345"  // Optional, for reference only
}
```

**Required Fields:**
- `investigation_summary` (string, non-empty): The investigation summary text to analyze

**Optional Fields:**
- `deviation_id` (string): Deviation identifier for reference (not saved by this endpoint)

#### Response (Success - 200)
```json
{
  "success": true,
  "message": "RCA generated successfully",
  "data": {
    "deviation_id": "DV-12345",
    "issues": "The analyst generated duplicate results without proper authorization and failed to follow established laboratory protocols...",
    "issues_category": "Company Personnel Issue",
    "major_root_cause_category": "Personnel Issues",
    "near_root_cause": "The analyst failed to follow the correct procedure for handling test samples and did not obtain supervisor approval before repeating the assay...",
    "near_root_cause_category": "Procedure Issue",
    "root_cause": "Inadequate training and enforcement of laboratory protocols, specifically STM-QCS-0800 General Laboratory Practices, which resulted in unauthorized duplicate testing...",
    "root_cause_category": "Procedure Not Followed"
  },
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

**Response Fields:**
- `issues`: Generated issues text
- `issues_category`: Auto-selected category for issues
- `major_root_cause_category`: Generated major root cause category text
- `near_root_cause`: Generated near root cause text
- `near_root_cause_category`: Auto-selected category for near root cause
- `root_cause`: Generated root cause text
- `root_cause_category`: Auto-selected category for root cause

#### Response (Error - 400)
```json
{
  "success": false,
  "message": "investigation_summary is required",
  "data": {},
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

#### Response (Error - 405)
```json
{
  "success": false,
  "message": "Method not allowed. Use POST.",
  "data": {},
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

#### Response (Error - 500)
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {
    "details": "Error calling Bedrock: timeout"
  },
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

---

## Complete RCA Workflow

This endpoint is part of a multi-step workflow:

```
1. GET /rca-categories
   └─> Load category options for dropdowns (one-time or cached)

2. POST /generate-rca  ← THIS ENDPOINT
   └─> Generate RCA text using AI
   └─> Returns generated text + auto-selected categories

3. User reviews/edits in UI
   └─> Can modify text
   └─> Can change categories using dropdowns

4. POST /submit-rca
   └─> Save final RCA to database
   └─> Returns rca_id

5. GET /rca (future)
   └─> Retrieve saved RCA from database
```

---

## cURL Examples

### Generate New RCA
```bash
curl -X POST https://api.example.com/generate-rca \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_summary": "Analyst S. Juyal generated duplicate results for the osmolality assay (method STM-QCS-0010, version 17.0, Osmolality Determination), when testing the 12-month timepoint for the 5°C storage condition for stability protocol STAB720.CD01.DP. QC Sample Management provided the following samples for testing to be completed over the weekend: LIMS ID S-241021-00676, LIMS ID S-241127-00392 - designated for Appearance assay. SJ performed the osmolality assay using S-241127-00392; however, osmolality was in fact to be executed using the alternative sample, S-241127-00392. Upon identifying the error, the analyst proceeded to repeat the assay using the assigned LIMS sample, thereby producing duplicate results. STM-QCS-0800, General Laboratory Practices, dictates that no duplicate testing shall be done without justification to invalidate the original results and that an analyst may not proceed to repeat an assay without supervisor approval. In this case, JS did not follow the procedure.",
    "deviation_id": "DV-12345"
  }'
```

### Response Example
```bash
{
  "success": true,
  "message": "RCA generated successfully",
  "data": {
    "deviation_id": "DV-12345",
    "issues": "The investigation revealed that Analyst S. Juyal...",
    "issues_category": "Company Personnel Issue",
    "major_root_cause_category": "Personnel Issues",
    "near_root_cause": "The analyst failed to follow...",
    "near_root_cause_category": "Procedure Issue",
    "root_cause": "Inadequate training and enforcement...",
    "root_cause_category": "Procedure Not Followed"
  }
}
```

---

## JavaScript/Fetch Examples

### Generate RCA
```javascript
const generateRCA = async (investigationSummary, deviationId = null) => {
  try {
    const response = await fetch('/api/generate-rca', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        investigation_summary: investigationSummary,
        deviation_id: deviationId  // Optional
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('RCA generated:', result.data);
      return result.data;
    } else {
      console.error('Error:', result.message);
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Failed to generate RCA:', error);
    throw error;
  }
};

// Usage
const investigationSummary = "Analyst S. Juyal generated duplicate results...";
const deviationId = "DV-12345";

generateRCA(investigationSummary, deviationId)
  .then(rca => {
    console.log('Generated RCA:', rca);
    // Display in UI for user review/editing
  })
  .catch(error => console.error('Error:', error));
```

### Complete Workflow Example
```javascript
// 1. Load categories (once, on page load)
const loadCategories = async () => {
  const response = await fetch('/api/rca-categories');
  const result = await response.json();
  return result.data;
};

// 2. Generate RCA
const generateRCA = async (investigationSummary, deviationId) => {
  const response = await fetch('/api/generate-rca', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      investigation_summary: investigationSummary,
      deviation_id: deviationId
    })
  });
  
  const result = await response.json();
  return result.data;
};

// 3. Save RCA (after user review/edit)
const saveRCA = async (rcaData) => {
  const response = await fetch('/api/submit-rca', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      deviation_id: rcaData.deviation_id,
      issues: rcaData.issues,
      issues_category: rcaData.issues_category,
      major_root_cause_category: rcaData.major_root_cause_category,
      near_root_cause: rcaData.near_root_cause,
      near_root_cause_category: rcaData.near_root_cause_category,
      root_cause: rcaData.root_cause,
      root_cause_category: rcaData.root_cause_category,
      created_by: 'user@example.com'
    })
  });
  
  const result = await response.json();
  return result.data;
};

// Complete flow
async function handleRCAGeneration() {
  try {
    // Load categories for dropdowns
    const categories = await loadCategories();
    
    // Generate RCA
    const generatedRCA = await generateRCA(
      investigationSummary,
      'DV-12345'
    );
    
    // Display in UI for user to review/edit
    displayRCAForm(generatedRCA, categories);
    
    // User reviews, edits, and clicks "Save"
    // Then call saveRCA with edited data
    
  } catch (error) {
    console.error('Error in RCA workflow:', error);
  }
}
```

---

## React Hook Example

```javascript
import { useState } from 'react';

function useGenerateRCA() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rcaData, setRcaData] = useState(null);

  const generateRCA = async (investigationSummary, deviationId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate-rca', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          investigation_summary: investigationSummary,
          deviation_id: deviationId
        })
      });
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message);
      }
      
      setRcaData(result.data);
      return result.data;
      
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { generateRCA, loading, error, rcaData };
}

// Usage in component
function RCAGenerator() {
  const { generateRCA, loading, error, rcaData } = useGenerateRCA();
  const [investigationSummary, setInvestigationSummary] = useState('');

  const handleGenerate = async () => {
    try {
      await generateRCA(investigationSummary, 'DV-12345');
      // RCA data is now in rcaData state
    } catch (err) {
      console.error('Failed to generate RCA:', err);
    }
  };

  return (
    <div>
      <textarea
        value={investigationSummary}
        onChange={(e) => setInvestigationSummary(e.target.value)}
        placeholder="Enter investigation summary..."
      />
      
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate RCA'}
      </button>
      
      {error && <div className="error">{error}</div>}
      
      {rcaData && (
        <div className="rca-result">
          <h3>Generated RCA</h3>
          <div>
            <label>Issues:</label>
            <p>{rcaData.issues}</p>
            <span>Category: {rcaData.issues_category}</span>
          </div>
          {/* Display other sections */}
        </div>
      )}
    </div>
  );
}
```

---

## Error Handling

### Common Errors

| Status Code | Message | Cause | Solution |
|-------------|---------|-------|----------|
| 400 | investigation_summary is required | Missing required field | Include investigation_summary in request body |
| 400 | investigation_summary must be a string | Wrong data type | Ensure investigation_summary is a string |
| 400 | investigation_summary cannot be empty | Empty string provided | Provide non-empty investigation summary |
| 405 | Method not allowed. Use POST. | Wrong HTTP method | Use POST method only |
| 500 | Error calling Bedrock | AI service error | Check Bedrock service status and permissions |
| 500 | Error loading prompt file | Missing prompt files | Ensure all prompt files are in deployment package |
| 500 | Internal server error | Various | Check CloudWatch logs for details |

---

## AI Generation Process

The endpoint makes 5 sequential AI calls to AWS Bedrock:

1. **Generate Issues** - Analyzes investigation summary to identify issues
2. **Generate Major Root Cause Category** - Determines high-level category
3. **Generate Near Root Cause** - Identifies intermediate cause
4. **Generate Root Cause** - Determines fundamental root cause
5. **Categorize RCA** - Auto-selects specific categories from taxonomy

**Total Processing Time:** ~10-20 seconds (depending on AI response times)

---

## Testing

### Test Event (Lambda Console)
```json
{
  "httpMethod": "POST",
  "body": "{\"investigation_summary\":\"Analyst S. Juyal generated duplicate results for the osmolality assay (method STM-QCS-0010, version 17.0, Osmolality Determination), when testing the 12-month timepoint for the 5°C storage condition for stability protocol STAB720.CD01.DP. QC Sample Management provided the following samples for testing to be completed over the weekend: LIMS ID S-241021-00676, LIMS ID S-241127-00392 - designated for Appearance assay. SJ performed the osmolality assay using S-241127-00392; however, osmolality was in fact to be executed using the alternative sample, S-241127-00392. Upon identifying the error, the analyst proceeded to repeat the assay using the assigned LIMS sample, thereby producing duplicate results. STM-QCS-0800, General Laboratory Practices, dictates that no duplicate testing shall be done without justification to invalidate the original results and that an analyst may not proceed to repeat an assay without supervisor approval. In this case, JS did not follow the procedure.\",\"deviation_id\":\"DV-12345\"}"
}
```

### Test with Minimal Data
```json
{
  "httpMethod": "POST",
  "body": "{\"investigation_summary\":\"Equipment malfunction caused production delay.\"}"
}
```

### Test OPTIONS (CORS Preflight)
```json
{
  "httpMethod": "OPTIONS"
}
```

---

## Performance

**Expected Response Times:**
- Cold Start: ~15-25 seconds (includes Lambda initialization + AI calls)
- Warm Start: ~10-15 seconds (AI calls only)

**Payload Sizes:**
- Request: ~1-5 KB (investigation summary)
- Response: ~5-10 KB (generated RCA text)

---

## Related Endpoints

### GET /rca-categories
Load category options for dropdowns.

**Purpose:** Get all available RCA categories for UI dropdowns  
**Documentation:** See `src/app/get_rca_categories/README.md`

**Example:**
```javascript
const response = await fetch('/api/rca-categories');
const categories = await response.json();
// Use categories.data.Factors and categories.data.MajorRootCauseCategories
```

### POST /submit-rca
Save generated RCA to database.

**Purpose:** Persist RCA after user review/editing  
**Documentation:** See `src/app/submit_rca/README.md`

**Example:**
```javascript
const response = await fetch('/api/submit-rca', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    deviation_id: 'DV-12345',
    issues: editedIssues,
    issues_category: selectedIssuesCategory,
    major_root_cause_category: editedMajorCategory,
    near_root_cause: editedNearCause,
    near_root_cause_category: selectedNearCategory,
    root_cause: editedRootCause,
    root_cause_category: selectedRootCategory,
    created_by: 'user@example.com'
  })
});
```

---

## Migration Notes

### Breaking Changes from Previous Version

⚠️ **This endpoint no longer:**
- Saves to database (use `/submit-rca` instead)
- Returns `rca_id` (get from `/submit-rca` response)
- Returns `category_options` (use `/rca-categories` instead)
- Supports GET method (will be separate `/rca` endpoint)

⚠️ **Response structure changed:**
- Removed: `rca_id`, `category_options`, `created_at`, `updated_at`, `created_by`
- Kept: All generated text fields and auto-selected categories

### Migration Path

**Old Code:**
```javascript
// Single call did everything
const response = await fetch('/api/generateRCA', {
  method: 'POST',
  body: JSON.stringify({ investigation_summary, deviation_id })
});
// Response included rca_id and category_options
```

**New Code:**
```javascript
// 1. Load categories separately
const categories = await fetch('/api/rca-categories').then(r => r.json());

// 2. Generate RCA
const rca = await fetch('/api/generate-rca', {
  method: 'POST',
  body: JSON.stringify({ investigation_summary, deviation_id })
}).then(r => r.json());

// 3. User reviews/edits

// 4. Save to database
const saved = await fetch('/api/submit-rca', {
  method: 'POST',
  body: JSON.stringify({ ...editedRCA, created_by: user.email })
}).then(r => r.json());
// Response includes rca_id
```

---

## Best Practices

1. **Cache Categories:** Load `/rca-categories` once and cache in frontend
2. **Show Loading State:** AI generation takes 10-20 seconds
3. **Allow Editing:** Let users review and edit before saving
4. **Validate Input:** Ensure investigation_summary is non-empty
5. **Handle Errors:** Show user-friendly error messages
6. **Save Separately:** Call `/submit-rca` only after user confirms
7. **Timeout Handling:** Set appropriate timeout (30+ seconds)

---

## Support

For issues or questions:
- Check CloudWatch logs for detailed error messages
- Verify Bedrock permissions and model access
- Ensure all prompt files are in deployment package
- Review `REFACTOR_SUMMARY.md` for architecture details
