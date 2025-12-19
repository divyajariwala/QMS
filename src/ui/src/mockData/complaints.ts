import CriticalityIcon from "../../src/assets/icons/criticality.svg";
import ReportTypeIcon from "../../src/assets/icons/reportType.svg";
import CategoryIcon from "../../src/assets/icons/category.svg";
import ReceiptDateIcon from "../../src/assets/icons/receiptDate.svg";
import { StatusTabItem } from "src/types";

export const statuses: StatusTabItem[] = [
  { label: "In Review", count: 14000 },
  { label: "Overdue", count: 2000 },
  { label: "Processed", count: 7123 },
];

export const complaintsData = [
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 02 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Adverse Event"],
    "Due Date": "Oct 09 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint", "Adverse Event"],
    "Due Date": "Oct 10 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 11 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Adverse Event"],
    "Due Date": "Oct 12 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint", "Adverse Event"],
    "Due Date": "Oct 13 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 14 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Adverse Event"],
    "Due Date": "Oct 15 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint", "Adverse Event"],
    "Due Date": "Oct 16 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 17 2025",
  },
];


export const complaintCategories = [
  {
    id: "1",
    label: 'Broken Needle',
    level: 1,
    crl: 'Needle was chipped',
    priority: 'High',
    unit: 1,
    percentage: 85,
    color: "#43a047",
    bgColor: '#F0FAF0'
  },
  {
    id: "2",
    label: 'Bent Needle',
    level: 1,
    crl: 'Needle was chipped',
    priority: 'High',
    unit: 1,
    percentage: 65,
    color: "#f57c00",
    bgColor: '#FFF8EB'
  },
  {
    id: "3",
    label: 'Injection incomplete',
    level: 1,
    crl: 'Needle was chipped',
    priority: 'High',
    unit: 1,
    percentage: 45,
    color: "#e53935",
    bgColor: '#FFF8EB'
  },
];

export const infoItems = [
  {
    label: "Criticality",
    iconSrc: CriticalityIcon,
    iconAlt: "Criticality",
    value: 'NA',
  },
  {
    label: "Report Type",
    iconSrc: ReportTypeIcon,
    iconAlt: "Report Type",
    value: 'NA',
  },
  {
    label: "Category",
    iconSrc: CategoryIcon,
    iconAlt: "Category",
    value: 'NA',
  },
  {
    label: "Receipt Date",
    iconSrc: ReceiptDateIcon,
    iconAlt: "Receipt Date",
    value: 'Aug 04 2023',
  },
];

export const complaintHeaderData = {
  status: "IN-REVIEW",
  caseId: "CAS-12345",
  overdueDays: 5,
  primaryReporter: { name: "Cornelius Greenfelder", location: "United States, New York" },
  patientName: "John Doe",
  physicianName: "Dr. Mallory Abernathy",
  drug: "Levothyroxine",
  lotNumber: "1242",
  doseAmount: "120mg",
  expirationDate: "Aug 04 2023",
  partNumber: "#",
};

export const caseStatsMock = {
  "total_complaints": 7,
  "pending": 5,
  "processed": 1,
  "overdue": 1,
  "avg_cycle_time": 24,
  "best_time": 7,
  "longest_time": 72
}


export const MockComplaintsApiResponse = {
  caseStats: {
    total_complaints: 9,
    pending: 3,
    processed: 4,
    overdue: 2,
    // times measured in days
    avg_cycle_time: 5.6,
    best_time: 1,
    longest_time: 23,
  },

  caseStatus: {
    overdue: [
      {
        case_id: "CASE-0008",
        criticality: "High",
        report_type: "Service",
        receipt_date: "2025-08-20T09:00:00Z",
        case_type: ["ae", "pc"],
      },
      {
        case_id: "CASE-0009",
        criticality: "Medium",
        report_type: "Product",
        receipt_date: "2025-09-01T10:30:00Z",
        case_type: [],
      },
    ],
    pending: [
      {
        case_id: "CASE-0001",
        criticality: "High",
        report_type: "Product",
        receipt_date: "2025-10-28T09:12:00Z",
        case_type: ["AE", "PC"],
      },
      {
        case_id: "CASE-0005",
        criticality: "Medium",
        report_type: "Service",
        receipt_date: "2025-11-01T14:30:00Z",
        case_type: ["AE", "PC"],
      },
      {
        case_id: "CASE-0007",
        criticality: "Low",
        report_type: "Consumer",
        receipt_date: "2025-11-05T08:00:00Z",
        case_type: ["AE", "PC"],
      },
    ],

    processed: [
      {
        case_id: "CASE-0002",
        criticality: "Critical",
        report_type: "Product",
        receipt_date: "2025-09-20T12:00:00Z",
        case_type: ["AE", "PC"],
      },
      {
        case_id: "CASE-0003",
        criticality: "Medium",
        report_type: "Service",
        receipt_date: "2025-10-05T16:45:00Z",
        case_type: ["AE", "PC"],
      },
      {
        case_id: "CASE-0004",
        criticality: "Low",
        report_type: "Consumer",
        receipt_date: "2025-10-15T11:10:00Z",
        case_type: ["AE", "PC"],
      },
      {
        case_id: "CASE-0006",
        criticality: "High",
        report_type: "Product",
        receipt_date: "2025-10-25T07:25:00Z",
        case_type: ["AE", "PC"],
      },
    ],
  },
};

export const MockComplaintDetailApiResponse = {
  case_id: "CASE-00123",
  receipt_date: "2025-11-10T10:30:00Z",
  criticality: "High",
  report_type: "Product",
  ai_summary:
    "Patient reported acute onset of muscle pain and weakness within 48 hours of starting the medication. No hospitalization required. Symptoms improved after discontinuation.",
  case_type: ["AE", "PC"],
  narrative:
    "The patient, a 58-year-old male, started the medication as prescribed. Within two days he experienced progressive myalgia and proximal muscle weakness, making routine activities difficult. No prior history of similar symptoms. He stopped the drug on advice of his physician and symptoms began to abate within 72 hours. No other concomitant medication changes were reported. Follow-up planned in one week.",
  primary_reporter: {
    name: "Acme Pharmaceuticals Pharmacovigilance Team",
    address: "123 Pharma St, Suite 400, MedCity, Country",
  },
  patient_name: "John Doe",
  physician_name: "Dr. Emily Carter",
  product_details: {
    drug_name: "Simvastatin",
    dosage: "10 mg tablet",
    lot_no: "LT202511",
    expiration_date: "2026-04-30",
  },
  caseStatus: "Pending",
  category_details: [
    {
      id: "CAT-001",
      label: "Adverse Event",
      level: 1,
      crl: "CRL-A1",
      priority: "High",
      unit: 1,
      percentage: 45.0,
    },
    {
      id: "CAT-002",
      label: "Product Complaint",
      level: 2,
      crl: "CRL-P2",
      priority: "Medium",
      unit: 2,
      percentage: 35.0,
    },
    {
      id: "CAT-003",
      label: "Packaging",
      level: 3,
      crl: "CRL-PKG",
      priority: "Low",
      unit: 1,
      percentage: 20.0,
    },
  ],
};