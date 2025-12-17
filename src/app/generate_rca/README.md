# Generate RCA API

## Description
Generates Root Cause Analysis (RCA) for a deviation based on its investigation summary. Uses AWS Bedrock Claude model to analyze the summary and generate four RCA sections: Issues, Major Root Cause Category, Near Root Cause, and Root Cause.

## Endpoint
`POST /generateRCA`

## Request

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "deviation_id": "DV-00001",
  "investigation_summary": "During the manufacturing process on January 10, 2024, a batch of Product XYZ (Lot ABC123) was found to have contamination. The investigation revealed that the sterilization equipment failed to reach the required temperature of 121°C, only reaching 115°C. This was due to a faulty temperature sensor that had not been calibrated in 18 months, exceeding the required 12-month calibration interval. The maintenance logs showed the sensor was last calibrated in July 2022."
}
```

### Parameters
- `deviation_id` (string, optional): Deviation ID for reference
- `investigation_summary` (string, required): Detailed investigation summary text

## Response

### Success Response (200)
```json
{
  "success": true,
  "message": "RCA generated successfully",
  "data": {
    "deviation_id": "DV-00001",
    "issues": "The primary issue identified was contamination in Product XYZ Lot ABC123 during manufacturing. The sterilization equipment failed to achieve the required temperature of 121°C, only reaching 115°C. This temperature deviation compromised the sterility assurance of the batch.",
    "major_root_cause_category": "Equipment/Instrumentation",
    "near_root_cause": "The temperature sensor in the sterilization equipment was faulty and had not been calibrated within the required timeframe. The sensor exceeded its 12-month calibration interval by 6 months, with the last calibration performed in July 2022.",
    "root_cause": "The fundamental root cause was the failure of the preventive maintenance system to ensure timely calibration of critical equipment. The organization lacked an effective calibration tracking and alert system to prevent equipment from operating beyond its calibration due date. This systemic gap in the quality management system allowed critical equipment to operate with uncalibrated sensors, leading to process failures."
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Responses

#### 400 - Missing Investigation Summary
```json
{
  "success": true,
  "message": "investigation_summary is required",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 400 - Invalid Type
```json
{
  "success": true,
  "message": "investigation_summary must be a string",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 400 - Empty Summary
```json
{
  "success": true,
  "message": "investigation_summary cannot be empty",
  "data": {},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 500 - Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {
    "details": "<error details>"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## RCA Sections

### 1. Issues
Identifies and describes all specific problems found in the investigation. Focuses on what went wrong and the immediate problems observed.

### 2. Major Root Cause Category
Classifies the root cause into a high-level category (e.g., Equipment/Instrumentation, Human Error, Process, Materials, Environment, Management System).

### 3. Near Root Cause
Describes the immediate or proximate cause that directly led to the issue. This is one level deeper than the surface problem.

### 4. Root Cause
Identifies the fundamental, systemic cause that, if addressed, would prevent the incident from recurring. Focuses on underlying organizational or process failures.

## Notes
- Uses AWS Bedrock Claude Haiku model for analysis
- Each RCA section is generated independently with specialized prompts
- Investigation summary should be detailed and comprehensive for best results
- Generated RCA is returned but NOT automatically saved to database
- Consider calling a separate update API to persist the RCA results
- Processing time depends on investigation summary length (typically 10-30 seconds)
- Maximum token limit: 2048 tokens per section
- Temperature setting: 0 (deterministic output)
