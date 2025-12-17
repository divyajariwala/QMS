# Get Complaints API

## Description
Retrieves complaints data from the database. Supports three modes: list all complaints, get single complaint details, or get adverse events only.

## Endpoint
`GET /getComplaints`

## Request Modes

### 1. Get All Complaints
`GET /getComplaints?page=1&status=pending&search=CAS-001`

### 2. Get Single Complaint
`GET /getComplaints?complaint_id=CAS-00001`

### 3. Get Adverse Events
`GET /getComplaints?adverse_events=true&page=1`

## Query Parameters

### Common Parameters
- `page` (integer, optional): Page number for pagination (default: 1)
- `search` (string, optional): Search by complaint ID

### Mode-Specific Parameters
- `complaint_id` (string): Get specific complaint details
- `status` (string): Filter by status (pending, processed, overdue)
- `adverse_events` (boolean): Get adverse events only (true/false)

## Response

### Get All Complaints (200)
```json
{
  "caseStats": {
    "total_complaints": 150,
    "pending": 45,
    "processed": 100,
    "overdue": 5,
    "avg_cycle_time": 3
  },
  "caseStatus": {
    "pending": [
      {
        "case_id": "CAS-00001",
        "criticality": "High",
        "report_type": "Initial",
        "receipt_date": "2024-01-15",
        "case_type": ["Product Complaint"],
        "text_extracted": true,
        "created_at": "2024-01-15T10:30:00.000Z"
      }
    ],
    "processed": [],
    "overdue": []
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 150,
    "items_per_page": 15,
    "has_next": true,
    "has_previous": false
  },
  "complaints": [
    {
      "case_id": "CAS-00001",
      "criticality": "High",
      "report_type": "Initial",
      "receipt_date": "2024-01-15",
      "case_type": ["Product Complaint"],
      "status": "pending",
      "text_extracted": true,
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

### Get Single Complaint (200)
```json
{
  "case_id": "CAS-00001",
  "receipt_date": "2024-01-15",
  "created_at": "2024-01-15T10:30:00.000Z",
  "criticality": "High",
  "report_type": "Initial",
  "ai_summary": "Patient experienced adverse reaction...",
  "case_type": ["Product Complaint"],
  "narrative": "Full narrative text...",
  "primary_reporter": {
    "name": "Dr. John Smith",
    "address": "123 Medical Center Dr"
  },
  "patient_name": "Jane Doe",
  "physician_name": "Dr. John Smith",
  "product_details": {
    "drug": "Drug XYZ",
    "lot_no": "ABC123",
    "dosage": "10mg",
    "expiration_date": "2025-12-31",
    "part_number": "PART-001"
  },
  "caseStatus": "pending",
  "text_extracted": true,
  "complaintClassified": true,
  "category_details": [
    {
      "id": "1",
      "label": "Dose confirmation",
      "level": "2",
      "crl": "Dose confirmation",
      "priority": "Low",
      "unit": 5,
      "percentage": 94.92
    }
  ],
  "crl_list": ["Dose confirmation", "Device malfunction", "NA"],
  "label_list": ["Dose confirmation", "Device malfunction", "Needle bent"]
}
```

### Get Adverse Events (200)
```json
{
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 75,
    "items_per_page": 15,
    "has_next": true,
    "has_previous": false
  },
  "adverse_events": [
    {
      "case_id": "CAS-00001",
      "criticality": "High",
      "report_type": "Initial",
      "receipt_date": "2024-01-15",
      "case_type": ["Adverse Event"],
      "status": "pending",
      "text_extracted": true,
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

### Search Results (200)
```json
{
  "caseStats": {
    "total_complaints": 150,
    "pending": 45,
    "processed": 100,
    "overdue": 5,
    "avg_cycle_time": 3
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 2,
    "items_per_page": 15,
    "has_next": false,
    "has_previous": false
  },
  "search_results": [
    {
      "case_id": "CAS-00123",
      "criticality": "High",
      "report_type": "Initial",
      "receipt_date": "2024-01-15",
      "case_type": ["Product Complaint"],
      "status": "pending",
      "text_extracted": true,
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

### Error Responses

#### 404 - Complaint Not Found
```json
{
  "success": false,
  "error": "Complaint not found"
}
```

#### 500 - Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "<error details>"
}
```

## Notes
- Pagination returns 15 items per page
- Search ignores status filter and searches across all statuses
- Adverse events mode returns both pure adverse events and mixed cases
- Category details are only available for classified complaints
- CRL and label lists are dynamically updated from database
- Overdue complaints are automatically updated (5+ days old pending complaints)
- Statistics are refreshed on each request
