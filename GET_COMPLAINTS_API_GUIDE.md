# Get Complaints API - Usage Guide

## Base URL
```
GET /getComplaints
```

## Overview
The Get Complaints API provides access to complaint data with support for filtering, pagination, and search functionality. It serves both the Complaints page and Adverse Events page with different data filtering rules.

---

## Endpoints

### 1. Get All Complaints (Complaints Page)
Retrieves all product complaints and mixed cases (product complaint + adverse event). **Excludes pure adverse events.**

**Request:**
```http
GET /getComplaints
```

**Response:**
```json
{
  "caseStats": {
    "total_complaints": 100,
    "pending": 45,
    "processed": 50,
    "overdue": 5,
    "avg_cycle_time": 24
  },
  "caseStatus": {
    "pending": [
      {
        "case_id": "CAS-00100",
        "criticality": "High",
        "report_type": "Spontaneous",
        "receipt_date": "2023-01-15",
        "case_type": ["Product Complaint"],
        "text_extracted": true,
        "created_at": "2023-01-15T10:00:00"
      }
    ],
    "processed": [...],
    "overdue": [...]
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 7,
    "total_items": 100,
    "items_per_page": 15,
    "has_next": true,
    "has_previous": false
  },
  "complaints": [...]
}
```

---

### 2. Get All Complaints with Pagination
Retrieve complaints with page number.

**Request:**
```http
GET /getComplaints?page=2
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)

**Response:** Same structure as endpoint 1, with `current_page: 2`

---

### 3. Get Complaints by Status Filter
Filter complaints by status (pending, processed, or overdue).

**Request:**
```http
GET /getComplaints?status=pending
```

**Query Parameters:**
- `status` (string): One of `pending`, `processed`, or `overdue`

**Response:**
```json
{
  "caseStats": {
    "total_complaints": 100,
    "pending": 45,
    "processed": 50,
    "overdue": 5,
    "avg_cycle_time": 24
  },
  "caseStatus": {
    "pending": [
      {
        "case_id": "CAS-00100",
        "criticality": "High",
        "report_type": "Spontaneous",
        "receipt_date": "2023-01-15",
        "case_type": ["Product Complaint"],
        "text_extracted": true,
        "created_at": "2023-01-15T10:00:00"
      }
    ],
    "processed": [],
    "overdue": []
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_items": 45,
    "items_per_page": 15,
    "has_next": true,
    "has_previous": false
  },
  "complaints": [...]
}
```

---

### 4. Search Complaints (Complaints Page)
Search for complaints by partial or full complaint ID. **Excludes pure adverse events.**

**Request:**
```http
GET /getComplaints?search=348
```

**Query Parameters:**
- `search` (string): Partial or full complaint ID

**Response:**
```json
{
  "caseStats": {
    "total_complaints": 100,
    "pending": 45,
    "processed": 50,
    "overdue": 5,
    "avg_cycle_time": 24
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
      "case_id": "CAS-00348",
      "criticality": "High",
      "report_type": "Spontaneous",
      "receipt_date": "2023-03-15",
      "case_type": ["Product Complaint"],
      "status": "pending",
      "text_extracted": true,
      "created_at": "2023-03-15T10:00:00"
    },
    {
      "case_id": "CAS-01348",
      "criticality": "Medium",
      "report_type": "Study",
      "receipt_date": "2023-04-20",
      "case_type": ["Product Complaint", "Adverse Event"],
      "status": "processed",
      "text_extracted": true,
      "created_at": "2023-04-20T11:00:00"
    }
  ]
}
```

**Note:** Search results include:
- Pure product complaints
- Mixed cases (product complaint + adverse event)
- **Excludes** pure adverse events

---

### 5. Get Single Complaint Details
Retrieve detailed information for a specific complaint.

**Request:**
```http
GET /getComplaints?complaint_id=CAS-00348
```

**Query Parameters:**
- `complaint_id` (string): Complaint ID

**Response:**
```json
{
  "case_id": "CAS-00348",
  "receipt_date": "2023-03-15",
  "created_at": "2023-03-15T10:00:00",
  "criticality": "High",
  "report_type": "Spontaneous",
  "ai_summary": "Patient experienced discomfort after injection...",
  "case_type": ["Product Complaint"],
  "narrative": "Full complaint narrative text...",
  "primary_reporter": {
    "name": "John Doe",
    "address": "123 Main St"
  },
  "patient_name": "Jane Patient",
  "physician_name": "Dr. Smith",
  "product_details": {
    "drug": "Sertraline",
    "lot_no": "LOT-HH225",
    "dosage": "5 mg",
    "expiration_date": "2027-01-04",
    "part_number": "P-657298"
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
  "crl_list": ["Dose confirmation", "Needle issue", "NA"],
  "label_list": ["Dose confirmation", "Needle issue"]
}
```

---

### 6. Get Adverse Events (Adverse Events Page)
Retrieve all adverse events including pure adverse events and mixed cases. **Excludes pure product complaints.**

**Request:**
```http
GET /getComplaints?adverse_events=true
```

**Query Parameters:**
- `adverse_events` (string): Must be `"true"`

**Response:**
```json
{
  "pagination": {
    "current_page": 1,
    "total_pages": 2,
    "total_items": 25,
    "items_per_page": 15,
    "has_next": true,
    "has_previous": false
  },
  "adverse_events": [
    {
      "case_id": "CAS-00818",
      "criticality": "Minor",
      "report_type": "Spontaneous",
      "receipt_date": "2020-02-05",
      "case_type": ["Adverse Event"],
      "status": "pending",
      "text_extracted": true,
      "created_at": "2025-12-11T11:17:43"
    },
    {
      "case_id": "CAS-00816",
      "criticality": "Medium",
      "report_type": "Spontaneous",
      "receipt_date": "2020-02-05",
      "case_type": ["Product Complaint", "Adverse Event"],
      "status": "processed",
      "text_extracted": true,
      "created_at": "2025-12-11T09:01:38"
    }
  ]
}
```

---

### 7. Get Adverse Events with Pagination
Retrieve adverse events with page number.

**Request:**
```http
GET /getComplaints?adverse_events=true&page=2
```

**Query Parameters:**
- `adverse_events` (string): Must be `"true"`
- `page` (integer): Page number (default: 1)

**Response:** Same structure as endpoint 6, with `current_page: 2`

---

### 8. Search Adverse Events (Adverse Events Page)
Search for adverse events by partial or full complaint ID. **Includes pure adverse events and mixed cases only.**

**Request:**
```http
GET /getComplaints?adverse_events=true&search=818
```

**Query Parameters:**
- `adverse_events` (string): Must be `"true"`
- `search` (string): Partial or full complaint ID

**Response:**
```json
{
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 2,
    "items_per_page": 15,
    "has_next": false,
    "has_previous": false
  },
  "adverse_events": [
    {
      "case_id": "CAS-00818",
      "criticality": "Minor",
      "report_type": "Spontaneous",
      "receipt_date": "2020-02-05",
      "case_type": ["Adverse Event"],
      "status": "pending",
      "text_extracted": true,
      "created_at": "2025-12-11T11:17:43"
    },
    {
      "case_id": "CAS-01818",
      "criticality": "Major",
      "report_type": "Study",
      "receipt_date": "2020-03-10",
      "case_type": ["Adverse Event", "Product Complaint"],
      "status": "processed",
      "text_extracted": true,
      "created_at": "2025-12-12T14:22:15"
    }
  ]
}
```

**Note:** Search results include:
- Pure adverse events
- Mixed cases (adverse event + product complaint)
- **Excludes** pure product complaints

---

## Data Filtering Rules

### Complaints Page (Default)
- **Includes:** Product complaints, Mixed cases (product complaint + adverse event)
- **Excludes:** Pure adverse events

### Adverse Events Page (`adverse_events=true`)
- **Includes:** Pure adverse events, Mixed cases (adverse event + product complaint)
- **Excludes:** Pure product complaints

---

## Error Responses

### 404 - Complaint Not Found
```json
{
  "success": false,
  "error": "Complaint not found"
}
```

### 500 - Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

---

## Field Descriptions

### caseStats
- `total_complaints`: Total number of complaints across all statuses
- `pending`: Number of pending complaints
- `processed`: Number of processed complaints
- `overdue`: Number of overdue complaints
- `avg_cycle_time`: Average processing time in hours

### Complaint Object
- `case_id`: Unique complaint identifier
- `criticality`: Severity level (High, Medium, Low, Minor, Major, Critical)
- `report_type`: Type of report (Spontaneous, Study, Literature)
- `receipt_date`: Date complaint was received
- `case_type`: Array of case types (Product Complaint, Adverse Event)
- `status`: Current status (pending, processed, overdue)
- `text_extracted`: Whether text extraction is complete
- `created_at`: Timestamp when complaint was created

### Category Details (Classification Results)
- `id`: Category identifier
- `label`: Subcategory name
- `level`: Classification level (0, 1, 2)
- `crl`: CRL code or subcategory name
- `priority`: Priority level (Low, Medium, High)
- `unit`: Unit value
- `percentage`: Confidence score (0-100)

---

## Usage Examples

### JavaScript/Fetch
```javascript
// Get all complaints
fetch('/getComplaints')
  .then(response => response.json())
  .then(data => console.log(data));

// Search complaints
fetch('/getComplaints?search=348')
  .then(response => response.json())
  .then(data => console.log(data.search_results));

// Get adverse events
fetch('/getComplaints?adverse_events=true&page=1')
  .then(response => response.json())
  .then(data => console.log(data.adverse_events));

// Get single complaint
fetch('/getComplaints?complaint_id=CAS-00348')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python/Requests
```python
import requests

# Get all complaints with status filter
response = requests.get('/getComplaints?status=pending&page=1')
data = response.json()

# Search adverse events
response = requests.get('/getComplaints?adverse_events=true&search=818')
data = response.json()

# Get single complaint details
response = requests.get('/getComplaints?complaint_id=CAS-00348')
complaint = response.json()
```

### cURL
```bash
# Get all complaints
curl -X GET "/getComplaints"

# Search complaints (Complaints page)
curl -X GET "/getComplaints?search=348"

# Get adverse events with search
curl -X GET "/getComplaints?adverse_events=true&search=818"

# Get single complaint
curl -X GET "/getComplaints?complaint_id=CAS-00348"

# Get complaints by status with pagination
curl -X GET "/getComplaints?status=pending&page=2"
```

---

## Notes

1. **Pagination:** Default page size is 15 items per page
2. **Search:** Case-insensitive partial matching on complaint_id
3. **Status Filter:** Only applies to complaints page, not search results
4. **Classification:** `complaintClassified` indicates if AI classification is complete
5. **CRL Mapping:** `crl` field equals subcategory name, or "NA" for unassigned
6. **Mixed Cases:** Appear in both Complaints and Adverse Events pages
