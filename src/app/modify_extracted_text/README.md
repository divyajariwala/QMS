# Modify Extracted Text API

## Description
Updates extracted complaint details including reporter information, patient details, and product information after text extraction.

## Endpoint
`POST /modifyExtractedDetails`

## Request

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "caseId": "CAS-00001",
  "primaryReporter": {
    "name": "Dr. John Smith",
    "address": "123 Medical Center Dr, City, State 12345"
  },
  "patientName": "Jane Doe",
  "physicianName": "Dr. John Smith",
  "drug": "Drug XYZ",
  "lotNumber": "ABC123",
  "doseAmount": "10mg",
  "expirationDate": "2025-12-31",
  "partNumber": "PART-001"
}
```

### Parameters
- `caseId` (string, required): Complaint ID to update
- `primaryReporter` (object, required): Reporter information
  - `name` (string): Reporter's name
  - `address` (string): Reporter's address
- `patientName` (string): Patient's name
- `physicianName` (string): Physician's name
- `drug` (string): Drug/product name
- `lotNumber` (string): Lot number
- `doseAmount` (string): Dosage amount
- `expirationDate` (string): Expiration date (YYYY-MM-DD)
- `partNumber` (string): Part number

## Response

### Success Response (200)
```json
{
  "message": "Record updated successfully"
}
```

### Error Response (500)
```json
{
  "error": "Database error: <error details>"
}
```

## Notes
- All fields are optional except `caseId`
- Updates the `complaints` table directly
- Used after text extraction to correct or update extracted information
- Date format for `expirationDate` should be YYYY-MM-DD
- Empty strings are allowed for any field
