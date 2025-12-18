# RCA Analysis - Database Structure

## Table: `rca_analysis`

Complete structure for storing Root Cause Analysis data with categories for UI dropdowns.

---

## Schema

```sql
CREATE TABLE rca_analysis (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Foreign Key
    deviation_id VARCHAR(50) NOT NULL UNIQUE,
    
    -- Issues Section (Problem Category)
    issues TEXT,                      -- AI-generated text description
    issues_category VARCHAR(100),     -- Dropdown category (e.g., "Company personnel issue")
    
    -- Major Root Cause Category Section
    major_root_cause_category VARCHAR(100),              -- AI-generated category
    major_root_cause_category_explanation TEXT,          -- Same as major_root_cause_category
    
    -- Near Root Cause Section
    near_root_cause TEXT,                    -- AI-generated text description
    near_root_cause_category VARCHAR(100),   -- Dropdown category (e.g., "Procedure Issue")
    
    -- Root Cause Section
    root_cause TEXT,                    -- AI-generated text description
    root_cause_category VARCHAR(100),   -- Dropdown category (e.g., "Procedure Not Followed")
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    
    -- Constraints
    CONSTRAINT fk_deviation FOREIGN KEY (deviation_id) 
        REFERENCES deviations(deviation_id) ON DELETE CASCADE
);
```

---

## Field Mapping to UI

### Issues Section
| Database Field | UI Component | Example Value |
|---------------|--------------|---------------|
| `issues` | Text area (read-only/editable) | "The analyst generated duplicate results..." |
| `issues_category` | **Dropdown (blue)** | "Company personnel issue" |

### Major Root Cause Category Section
| Database Field | UI Component | Example Value |
|---------------|--------------|---------------|
| `major_root_cause_category` | Text display | "Personnel Issues" |
| `major_root_cause_category_explanation` | Hidden (same as above) | "Personnel Issues" |

### Near Root Cause Section
| Database Field | UI Component | Example Value |
|---------------|--------------|---------------|
| `near_root_cause` | Text area (read-only/editable) | "The analyst failed to follow..." |
| `near_root_cause_category` | **Dropdown (blue)** | "Procedure Issue" |

### Root Cause Section
| Database Field | UI Component | Example Value |
|---------------|--------------|---------------|
| `root_cause` | Text area (read-only/editable) | "Procedure Not Followed due to..." |
| `root_cause_category` | **Dropdown (blue)** | "Procedure Not Followed" |

---

## Complete Example Record

```sql
INSERT INTO rca_analysis (
    deviation_id,
    issues,
    issues_category,
    major_root_cause_category,
    major_root_cause_category_explanation,
    near_root_cause,
    near_root_cause_category,
    root_cause,
    root_cause_category,
    created_by
) VALUES (
    'DV-12345',
    
    -- Issues
    'The analyst generated duplicate test results by performing the osmolality assay twice - once with the wrong sample (S-241127-00392) and once with the correct sample. The second test was conducted without obtaining required supervisor approval as mandated by STM-QCS-0800 General Laboratory Practices.',
    'Company personnel issue',
    
    -- Major Category
    'Personnel Issues',
    'Personnel Issues',
    
    -- Near Root Cause
    'This is a Procedure Issue within Personnel Issues. The analyst failed to follow the established procedure outlined in STM-QCS-0800 General Laboratory Practices, which explicitly requires supervisor approval before repeating any assay. The immediate cause was the analyst''s decision to proceed with repeat testing without obtaining the required authorization.',
    'Procedure Issue',
    
    -- Root Cause
    'The fundamental root cause is Procedure Not Followed combined with Oversight/Inspection Issue. The analyst was aware of the procedure requiring supervisor approval but chose not to follow it. Additionally, there was inadequate supervisory oversight to catch this deviation in real-time. The systemic issue is a lack of enforcement mechanisms and real-time monitoring to ensure critical procedures are followed, particularly for actions that could compromise data integrity.',
    'Procedure Not Followed',
    
    -- Metadata
    'system'
);
```

---

## Query Examples

### Get RCA with all fields
```sql
SELECT 
    id,
    deviation_id,
    issues,
    issues_category,
    major_root_cause_category,
    near_root_cause,
    near_root_cause_category,
    root_cause,
    root_cause_category,
    created_at,
    updated_at,
    created_by
FROM rca_analysis
WHERE deviation_id = 'DV-12345';
```

### Get RCAs by Issues Category
```sql
SELECT 
    deviation_id,
    issues_category,
    major_root_cause_category,
    created_at
FROM rca_analysis
WHERE issues_category = 'Company personnel issue'
ORDER BY created_at DESC;
```

### Get RCAs by Root Cause Category
```sql
SELECT 
    deviation_id,
    root_cause_category,
    near_root_cause_category,
    major_root_cause_category,
    created_at
FROM rca_analysis
WHERE root_cause_category = 'Procedure Not Followed'
ORDER BY created_at DESC;
```

### Category Distribution Report
```sql
SELECT 
    issues_category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM rca_analysis
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY issues_category
ORDER BY count DESC;
```

### Trending by Major Category
```sql
SELECT 
    major_root_cause_category,
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) as count
FROM rca_analysis
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY major_root_cause_category, week
ORDER BY week DESC, count DESC;
```

### Find Inconsistencies (Near Cause doesn't match Major)
```sql
SELECT 
    deviation_id,
    major_root_cause_category,
    near_root_cause_category
FROM rca_analysis
WHERE 
    (major_root_cause_category = 'Personnel Issues' 
     AND near_root_cause_category NOT IN (
         'Procedure Issue', 
         'Training/Guidance Issue', 
         'Human Factors Issue',
         'Tech/Craftsman Issue',
         'Supervision Issue',
         'No Communication or Not Timely',
         'Company Issue',
         'Third Party/Personnel Issue'
     ))
    OR
    (major_root_cause_category = 'Equipment/Software Issues'
     AND near_root_cause_category NOT IN (
         'Design Issue',
         'Equipment Reliability Issue',
         'Procedure/Instruction Issue',
         'Materials/Parts Issue',
         'Software Issue',
         'Utility/Support Equipment Issue',
         'Other Equipment Issue'
     ));
```

---

## Indexes

```sql
-- Primary lookup
CREATE INDEX idx_rca_deviation_id ON rca_analysis(deviation_id);

-- Category filtering
CREATE INDEX idx_rca_major_category ON rca_analysis(major_root_cause_category);
CREATE INDEX idx_rca_issues_category ON rca_analysis(issues_category);
CREATE INDEX idx_rca_near_cause_category ON rca_analysis(near_root_cause_category);
CREATE INDEX idx_rca_root_cause_category ON rca_analysis(root_cause_category);

-- Date filtering
CREATE INDEX idx_rca_created_at ON rca_analysis(created_at);
```

---

## Dropdown Values Reference

### Issues Category Options
```
- Company personnel issue
- Procedure issue
- Training issue
- Equipment issue
- Process/manufacturing equipment issue
- System/software issue
- Documentation issue
- Quality control issue
- Communication issue
- Supervision issue
- External factors
- Other
```

### Major Root Cause Category Options
```
- Equipment/Software Issues
- Personnel Issues
- Other Issues
```

### Near Root Cause Category Options (Personnel Issues)
```
- Procedure Issue
- Training/Guidance Issue
- Human Factors Issue
- Tech/Craftsman Issue
- Supervision Issue
- No Communication or Not Timely
- Company Issue
- Third Party/Personnel Issue
```

### Near Root Cause Category Options (Equipment/Software Issues)
```
- Design Issue
- Equipment Reliability Issue
- Procedure/Instruction Issue
- Materials/Parts Issue
- Software Issue
- Utility/Support Equipment Issue
- Other Equipment Issue
```

### Root Cause Category Options (Examples for Procedure Issue)
```
- Procedure Not Performed Correctly
- Procedure Not Used
- Procedure Not Followed
- Change Control Issue
- Procedure Inadequate
- Procedure Not Available
- Procedure Difficult to Use
```

---

## Migration Path

### If table doesn't exist
Run: `schema.sql`

### If table exists without category columns
Run: `migration_add_categories.sql`

### Verify migration
```sql
SELECT 
    column_name, 
    data_type, 
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'rca_analysis'
ORDER BY ordinal_position;
```

Expected output should include:
- `issues_category`
- `near_root_cause_category`
- `root_cause_category`

---

## Data Validation

### Check for NULL categories
```sql
SELECT 
    deviation_id,
    CASE WHEN issues_category IS NULL THEN 'Missing' ELSE 'OK' END as issues_cat,
    CASE WHEN near_root_cause_category IS NULL THEN 'Missing' ELSE 'OK' END as near_cat,
    CASE WHEN root_cause_category IS NULL THEN 'Missing' ELSE 'OK' END as root_cat
FROM rca_analysis
WHERE issues_category IS NULL 
   OR near_root_cause_category IS NULL 
   OR root_cause_category IS NULL;
```

### Check for invalid categories
```sql
-- Check if categories are from valid ABS taxonomy
SELECT 
    deviation_id,
    issues_category
FROM rca_analysis
WHERE issues_category NOT IN (
    'Company personnel issue',
    'Procedure issue',
    'Training issue',
    'Equipment issue',
    'Process/manufacturing equipment issue',
    'System/software issue',
    'Documentation issue',
    'Quality control issue',
    'Communication issue',
    'Supervision issue',
    'External factors',
    'Other'
);
```

---

## Backup & Restore

### Backup RCA data
```bash
pg_dump -h hostname -U username -d database_name -t rca_analysis > rca_backup.sql
```

### Restore RCA data
```bash
psql -h hostname -U username -d database_name < rca_backup.sql
```

---

## Performance Considerations

### Table Size Estimates
- Average row size: ~2-3 KB (with text fields)
- 1,000 RCAs: ~2-3 MB
- 10,000 RCAs: ~20-30 MB
- 100,000 RCAs: ~200-300 MB

### Query Performance
- Indexed queries (by deviation_id): < 1ms
- Category filtering: < 10ms (with indexes)
- Aggregation queries: < 100ms (for 10K records)

### Optimization Tips
1. Use indexes on frequently queried columns
2. Archive old RCAs (> 2 years) to separate table
3. Use materialized views for complex reports
4. Partition by date if table grows > 1M records

---

## Integration with Frontend

### API Response Format
```json
{
  "rca_id": 1,
  "deviation_id": "DV-12345",
  "issues": "text...",
  "issues_category": "Company personnel issue",
  "major_root_cause_category": "Personnel Issues",
  "near_root_cause": "text...",
  "near_root_cause_category": "Procedure Issue",
  "root_cause": "text...",
  "root_cause_category": "Procedure Not Followed",
  "created_at": "2025-12-18T16:00:00Z",
  "updated_at": "2025-12-18T16:00:00Z",
  "created_by": "system"
}
```

### Frontend Dropdown Population
```jsx
// Load category from database
<select value={rca.issues_category}>
  <option value="Company personnel issue">Company personnel issue</option>
  <option value="Procedure issue">Procedure issue</option>
  ...
</select>
```

---

## Conclusion

The database structure is designed to:
- ✅ Store both AI-generated text and user-selectable categories
- ✅ Support the UI prototype with dropdown values
- ✅ Enable trending and analytics by category
- ✅ Maintain data integrity with foreign keys
- ✅ Provide fast queries with proper indexes
- ✅ Allow for easy updates and versioning

All fields are properly indexed and documented for optimal performance and maintainability.
