# Generate RCA API Usage Guide

## Overview

The Generate RCA endpoint uses AI (AWS Bedrock Claude) to automatically generate Root Cause Analysis based on an investigation summary. This endpoint focuses exclusively on AI-powered generation and returns the generated text with auto-selected categories.

**Important:** This endpoint does NOT save to database. Use the separate `/submitRCA` endpoint to save the generated RCA.

---

## Endpoint

### POST - Generate RCA
Generate a new Root Cause Analysis using AI.

**Endpoint:** `/generateRCA`  
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

**Important:** The response `data` field is ALWAYS an array, even if only one RCA is generated. This supports scenarios where multiple distinct root causes exist for a single deviation (e.g., RCA1, RCA2 tabs in UI).

**Single RCA Response:**
```json
{
  "success": true,
  "message": "1 RCA(s) generated successfully",
  "data": [
    {
      "deviation_id": "DV-12345",
      "issues": "The analyst generated duplicate results without proper authorization and failed to follow established laboratory protocols...",
      "issues_category": "Company Personnel Issue",
      "major_root_cause_category": "Personnel Issues",
      "major_root_cause_category_validated": "Detailed explanation of why this falls under Personnel Issues category. The analyst's actions demonstrate a lack of adherence to established protocols...",
      "near_root_cause": "The analyst failed to follow the correct procedure for handling test samples and did not obtain supervisor approval before repeating the assay...",
      "near_root_cause_category": "Procedure Issue",
      "root_cause": "Inadequate training and enforcement of laboratory protocols, specifically STM-QCS-0800 General Laboratory Practices, which resulted in unauthorized duplicate testing...",
      "root_cause_category": "Procedure Not Followed"
    }
  ],
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

**Multiple RCAs Response:**
```json
{
  "success": true,
  "message": "3 RCA(s) generated successfully",
  "data": [
    {
      "deviation_id": "DV-00001",
      "issues": "Cleaning validation for APS tanks was not completed before use.",
      "issues_category": "Procedure issue",
      "major_root_cause_category": "Equipment/Software Issues",
      "major_root_cause_category_validated": "This issue stems from equipment management and validation procedures not being properly followed...",
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
      "major_root_cause_category_validated": "Equipment release procedures failed to prevent unauthorized use of unvalidated tanks...",
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
      "major_root_cause_category_validated": "Systemic gaps in equipment validation tracking and control systems...",
      "near_root_cause": "No standardized control for validation completion before reuse.",
      "near_root_cause_category": "Procedure/Instruction Issue",
      "root_cause": "Quality procedures existed but were not fully applied.",
      "root_cause_category": "Procedure Not Used"
    }
  ],
  "timestamp": "2025-12-22T16:00:00.000000+00:00"
}
```

**Response Fields (per RCA in array):**
- `issues`: Generated issues text describing the specific causal factor
- `issues_category`: Auto-selected category for issues
- `major_root_cause_category`: Short category name (e.g., "Personnel Issues", "Equipment/Software Issues")
- `major_root_cause_category_validated`: Long AI-generated explanation text about why this category applies
- `near_root_cause`: Generated near root cause text
- `near_root_cause_category`: Auto-selected category for near root cause
- `root_cause`: Generated root cause text
- `root_cause_category`: Auto-selected category for root cause

**Field Structure Note:**
- All `_category` fields contain short category names
- `major_root_cause_category_validated` contains the long explanation text
- Non-category fields contain detailed AI-generated descriptions

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
1. GET /getRCACategories
   └─> Load category options for dropdowns (one-time or cached)

2. POST /generateRCA  ← THIS ENDPOINT
   └─> Generate RCA text using AI
   └─> Returns generated text + auto-selected categories

3. User reviews/edits in UI
   └─> Can modify text
   └─> Can change categories using dropdowns

4. POST /submitRCA
   └─> Save final RCA to database
   └─> Returns rca_id

5. GET /rca (future)
   └─> Retrieve saved RCA from database
```

---

## cURL Examples

### Generate New RCA
```bash
curl -X POST https://api.example.com/generateRCA \
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
  "message": "1 RCA(s) generated successfully",
  "data": [
    {
      "deviation_id": "DV-12345",
      "issues": "The investigation revealed that Analyst S. Juyal...",
      "issues_category": "Company Personnel Issue",
      "major_root_cause_category": "Personnel Issues",
      "major_root_cause_category_validated": "This issue is categorized under Personnel Issues because it involves an analyst's failure to follow established protocols...",
      "near_root_cause": "The analyst failed to follow...",
      "near_root_cause_category": "Procedure Issue",
      "root_cause": "Inadequate training and enforcement...",
      "root_cause_category": "Procedure Not Followed"
    }
  ]
}
```

---

## JavaScript/Fetch Examples

### Generate RCA
```javascript
const generateRCA = async (investigationSummary, deviationId = null) => {
  try {
    const response = await fetch('/api/generateRCA', {
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
      console.log(`Generated ${result.data.length} RCA(s):`, result.data);
      return result.data;  // Always an array
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
  .then(rcas => {
    console.log(`Generated ${rcas.length} RCA(s)`);
    
    // Handle single or multiple RCAs
    if (rcas.length === 1) {
      console.log('Single RCA:', rcas[0]);
      // Display single RCA in UI
    } else {
      console.log('Multiple RCAs:', rcas);
      // Display tabs: RCA1, RCA2, etc.
      rcas.forEach((rca, index) => {
        console.log(`RCA ${index + 1}:`, rca);
      });
    }
  })
  .catch(error => console.error('Error:', error));
```

### Complete Workflow Example
```javascript
// 1. Load categories (once, on page load)
const loadCategories = async () => {
  const response = await fetch('/api/getRCACategories');
  const result = await response.json();
  return result.data;
};

// 2. Generate RCA (returns array)
const generateRCA = async (investigationSummary, deviationId) => {
  const response = await fetch('/api/generateRCA', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      investigation_summary: investigationSummary,
      deviation_id: deviationId
    })
  });
  
  const result = await response.json();
  return result.data;  // Always an array of RCAs
};

// 3. Save RCAs (accepts single RCA or array)
const saveRCAs = async (rcaDataArray, createdBy = 'system') => {
  const response = await fetch('/api/submitRCA', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rcaDataArray)  // Can be single object or array
  });
  
  const result = await response.json();
  return result.data;
};

// Complete flow
async function handleRCAGeneration() {
  try {
    // Load categories for dropdowns
    const categories = await loadCategories();
    
    // Generate RCA(s) - returns array
    const generatedRCAs = await generateRCA(
      investigationSummary,
      'DV-12345'
    );
    
    console.log(`Generated ${generatedRCAs.length} RCA(s)`);
    
    // Display in UI for user to review/edit
    if (generatedRCAs.length === 1) {
      // Single RCA - show single form
      displayRCAForm(generatedRCAs[0], categories);
    } else {
      // Multiple RCAs - show tabs (RCA1, RCA2, etc.)
      displayRCATabs(generatedRCAs, categories);
    }
    
    // User reviews, edits, and clicks "Save All"
    // Then call saveRCAs with edited data array
    
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
  const [rcaData, setRcaData] = useState([]);  // Array of RCAs

  const generateRCA = async (investigationSummary, deviationId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generateRCA', {
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
      
      setRcaData(result.data);  // Always an array
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
  const [activeTab, setActiveTab] = useState(0);

  const handleGenerate = async () => {
    try {
      await generateRCA(investigationSummary, 'DV-12345');
      // RCA data is now in rcaData state (array)
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
      
      {rcaData.length > 0 && (
        <div className="rca-result">
          <h3>Generated {rcaData.length} RCA(s)</h3>
          
          {/* Show tabs if multiple RCAs */}
          {rcaData.length > 1 && (
            <div className="rca-tabs">
              {rcaData.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setActiveTab(index)}
                  className={activeTab === index ? 'active' : ''}
                >
                  RCA {index + 1}
                </button>
              ))}
            </div>
          )}
          
          {/* Display active RCA */}
          <div className="rca-content">
            <div>
              <label>Issues:</label>
              <p>{rcaData[activeTab].issues}</p>
              <span>Category: {rcaData[activeTab].issues_category}</span>
            </div>
            
            <div>
              <label>Major Root Cause Category:</label>
              <p>{rcaData[activeTab].major_root_cause_category}</p>
            </div>
            
            <div>
              <label>Explanation:</label>
              <p>{rcaData[activeTab].major_root_cause_category_validated}</p>
            </div>
            
            {/* Display other sections */}
          </div>
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

The endpoint uses an optimized approach to generate RCAs:

### Primary Method: Single AI Call (Preferred)
1. **Generate Multiple RCAs** - One AI call generates all RCAs as JSON array
   - Identifies all distinct root causes
   - Generates issues, major category explanation, near cause, and root cause for each
   - Returns structured JSON array

2. **Categorize Each RCA** - One AI call per RCA to assign taxonomy categories
   - Auto-selects specific categories from ABS Root Cause Map
   - Maps generated text to predefined category options

**Total Processing Time:** ~5-15 seconds for single RCA, ~10-25 seconds for multiple RCAs

### Fallback Method: Sequential Calls
If JSON parsing fails, falls back to legacy method:
1. Generate Issues
2. Generate Major Root Cause Category
3. Generate Near Root Cause
4. Generate Root Cause
5. Categorize RCA

**Fallback Processing Time:** ~15-25 seconds

### Multiple RCAs Support
The AI can identify when multiple distinct root causes exist and generate separate RCAs for each. This supports the UI requirement for RCA1, RCA2 tabs when multiple root causes are present.

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

### GET /getRCACategories
Load category options for dropdowns.

**Purpose:** Get all available RCA categories for UI dropdowns  
**Documentation:** See `src/app/get_rca_categories/README.md`

**Example:**
```javascript
const response = await fetch('/api/getRCACategories');
const categories = await response.json();
// Use categories.data.Factors and categories.data.MajorRootCauseCategories
```

### POST /submitRCA
Save generated RCA to database.

**Purpose:** Persist RCA after user review/editing  
**Documentation:** See `src/app/submit_rca/README.md`

**Example:**
```javascript
const response = await fetch('/api/submitRCA', {
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
- Saves to database (use `/submitRCA` instead)
- Returns `rca_id` (get from `/submitRCA` response)
- Returns `category_options` (use `/getRCACategories` instead)
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
// Response data was a single object
```

**New Code:**
```javascript
// 1. Load categories separately
const categories = await fetch('/api/getRCACategories').then(r => r.json());

// 2. Generate RCA(s) - returns array
const result = await fetch('/api/generateRCA', {
  method: 'POST',
  body: JSON.stringify({ investigation_summary, deviation_id })
}).then(r => r.json());

const rcas = result.data;  // ALWAYS an array

// 3. User reviews/edits (handle single or multiple RCAs)
if (rcas.length === 1) {
  // Show single form
  displaySingleRCA(rcas[0]);
} else {
  // Show tabs: RCA1, RCA2, etc.
  displayMultipleRCAs(rcas);
}

// 4. Save to database (can save array or single object)
const saved = await fetch('/api/submitRCA', {
  method: 'POST',
  body: JSON.stringify(rcas)  // Send array or single object
}).then(r => r.json());
// Response includes rca_id(s)
```

**Key Changes:**
- Response `data` is now ALWAYS an array (even for single RCA)
- Must handle `rcas.length` to determine if single or multiple
- `submitRCA` accepts both single object and array for flexibility
- `major_root_cause_category_validated` is now a long explanation text, not just category name

---

## Best Practices

1. **Cache Categories:** Load `/getRCACategories` once and cache in frontend
2. **Show Loading State:** AI generation takes 5-25 seconds depending on complexity
3. **Handle Array Response:** Response data is ALWAYS an array - check `rcas.length`
4. **Support Multiple RCAs:** Show tabs (RCA1, RCA2) when `rcas.length > 1`
5. **Allow Editing:** Let users review and edit each RCA before saving
6. **Validate Input:** Ensure investigation_summary is non-empty
7. **Handle Errors:** Show user-friendly error messages
8. **Save Separately:** Call `/submitRCA` only after user confirms (accepts array or single object)
9. **Timeout Handling:** Set appropriate timeout (30+ seconds)
10. **Field Structure:** Remember `major_root_cause_category_validated` is long text, not just category name

---

## Support

For issues or questions:
- Check CloudWatch logs for detailed error messages
- Verify Bedrock permissions and model access
- Ensure all prompt files are in deployment package
- Review `REFACTOR_SUMMARY.md` for architecture details
