import React, { useState } from 'react';
import { Box, Grid } from '@mui/material';
import CriticalityIcon from "../../assets/icons/criticality.svg";
import ReportTypeIcon from "../../assets/icons/reportType.svg";
import CategoryIcon from "../../assets/icons/category.svg";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import ProductComplaintIcon from "../../assets/icons/productComplaint.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";
import { orange, red, green } from '@mui/material/colors';
import ComplaintHeaderCard from './ComplaintHeaderCard';
import ComplaintBreadcrumbs from './ComplaintBreadcrumbs';
import ComplaintSecondaryInfo from './ComplaintSecondaryInfo';
import ComplaintAISummary from './ComplaintAISummary';
import ComplaintNarrative from './ComplaintNarrative';
import ComplaintCategory from './ComplaintCategory';
import styles from "./ComplaintsResult.module.scss";

const infoItems = [
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

const complaintCategories: ComplaintCategoryItem[] = [
  {
    id: "1",
    label: 'Broken Needle',
    level: 1,
    crl: 'Needle was chipped',
    priority: 'High',
    unit: 1,
    percentage: 85,
    color: green[600],
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
    color: orange[700],
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
    color: red[600],
    bgColor: '#FFF8EB'
  },
];

interface ComplaintCategoryItem {
  id: string;           // new unique id
  label: string;
  level: number;
  crl: string;
  priority: string;
  unit: number;
  percentage: number;
  color: string;
  bgColor: string;
}

const ComplaintsDetails: React.FC = () => {
  const [complaints, setComplaints] = useState<ComplaintCategoryItem[]>(complaintCategories);

  return (
    <Box sx={{ minHeight: '100vh' }}>

      {/* Breadcrumbs */}
      <ComplaintBreadcrumbs caseId="CAS-12345" />

      {/* Complaint Header Card */}
      <ComplaintHeaderCard
        status="IN-REVIEW"
        caseId="CAS-12345"
        overdueDays={5}
        primaryReporter={{ name: "Cornelius Greenfelder", location: "United States, New York" }}
        patientName="John Doe"
        physicianName="Dr. Mallory Abernathy"
        drug="Levothyroxine"
        lotNumber="1242"
        doseAmount="120mg"
        expirationDate="Aug 04 2023"
        partNumber="#"
        onApproveAndSend={() => {
          // handle approve and send action here
          console.log('Approve and Send clicked!');
        }}
      />
      {/* Secondary Info Card */}
      <ComplaintSecondaryInfo
        infoItems={infoItems}
        productComplaintIconSrc={ProductComplaintIcon}
        adverseEventIconSrc={AdverseEventIcon}
        productComplaintsChipClassName={styles.productComplaintsChip}
        adverseEventChipClassName={styles.adverseEventChip}
      />

      {/* AI Summary */}
      <ComplaintAISummary />

      {/* Narrative and Complaint Category section side by side */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Narrative */}
        <Grid item xs={12} md={4.9}>
          <ComplaintNarrative />
        </Grid>

        {/* Complaint Category */}
        <Grid item xs={12} md={7.1}>
          <ComplaintCategory
            complaintCategories={complaints}
            onSave={(updatedItem) => {
              setComplaints((prev) =>
                prev.map((item) =>
                  item.id === updatedItem.id ? { ...item, ...updatedItem } : item
                )
              );
            }}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComplaintsDetails;