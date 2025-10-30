import CriticalityIcon from "../../src/assets/icons/criticality.svg";
import ReportTypeIcon from "../../src/assets/icons/reportType.svg";
import CategoryIcon from "../../src/assets/icons/category.svg";
import ReceiptDateIcon from "../../src/assets/icons/receiptDate.svg";
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