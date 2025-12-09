# 3-Step Extraction Process

## Overview
The complaint extraction process has been refactored from a single-step to a 3-step chaining approach for improved accuracy and validation.

## Architecture

### Step 1: Basic Information Extraction
**Purpose**: Extract all basic complaint details and generate a comprehensive narrative summary

**Files**:
- PDF: `prompt_step1.txt` + `toolspec_step1.json`
- Narrative: `prompt_narrative_step1.txt` + `toolspec_narrative_step1.json`

**Extracts**:
- case_id
- receipt_date
- report_type
- narrative (full text)
- narrative_summary (50-150 words capturing severity, patient condition, product issues, outcome)
- primary_reporter
- patient_name
- physician_name
- product_details

**Key Point**: The narrative summary is generated with criticality, category, and case type in mind, capturing all relevant severity and classification indicators.

### Step 2: Criticality Extraction
**Purpose**: Determine criticality level from the narrative summary

**Files**:
- `prompt_narrative_step2_criticality.txt` + `toolspec_narrative_step2.json`

**Extracts**:
- criticality: Critical | Major | Minor | Medium | N/A

**Validation**: Enum constraint ensures only valid values are returned

### Step 3: Classification Extraction
**Purpose**: Determine category and case type from the narrative summary

**Files**:
- `prompt_narrative_step3_classification.txt` + `toolspec_narrative_step3.json`

**Extracts**:
- category: Array of product types (Medical Device, Pharmaceutical Drug, etc.)
- case_type: Array with Adverse Event, Product Complaint, or both

**Validation**: Enum constraints ensure only valid values are returned

## Benefits

1. **Improved Accuracy**: Each step focuses on a specific extraction task
2. **Better Validation**: Toolspecs enforce allowed values for criticality, category, and case_type
3. **Consistent Summary**: Narrative summary is generated once and reused for classification
4. **Reduced Hallucination**: Specialized prompts with clear constraints
5. **Maintainability**: Easy to update individual extraction steps

## Flow Diagram

```
Input (PDF/Narrative)
    ↓
Step 1: Extract Basic Info + Narrative Summary
    ↓
Step 2: Extract Criticality from Summary
    ↓
Step 3: Extract Category & Case Type from Summary
    ↓
Combine Results → Update Database
```

## Lambda Function Changes

The `lambda_function.py` has been updated to:
- Support step parameter in `load_tool_spec()`, `construct_pdf_prompt()`, `construct_narrative_prompt()`, and `process_with_bedrock()`
- Chain 3 Bedrock calls for both PDF and narrative processing
- Combine results from all 3 steps before database update
- Handle edge cases (empty PDFs, non-complaint documents)

## Backward Compatibility

Original prompt files (`prompt.txt`, `prompt_narrative.txt`) are marked as deprecated but kept for reference.
