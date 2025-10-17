import React, { useState } from 'react';
import { Box, Grid } from '@mui/material';
import ProductComplaintIcon from "../../assets/icons/productComplaint.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";
import ComplaintHeaderCard from './ComplaintHeaderCard';
import ComplaintDetailsBreadcrumbs from './ComplaintDetailsBreadcrumbs';
import ComplaintSecondaryInfo from './ComplaintSecondaryInfo';
import ComplaintAISummary from './ComplaintAISummary';
import ComplaintNarrative from './ComplaintNarrative';
import ComplaintCategory from './ComplaintCategory';
import { complaintCategories, infoItems, complaintHeaderData } from 'src/mockData/mockData';
import styles from "./ComplaintsResult.module.scss";

interface ComplaintCategoryItem {
  id: string;
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
    <Box className={styles.rootBox}>
      <ComplaintDetailsBreadcrumbs caseId={"CAS-12345"} />
      <ComplaintHeaderCard
        complaintData={complaintHeaderData}
        onApproveAndSend={() => {
          console.log('Approve and Send clicked!');
        }}
      />
      <ComplaintSecondaryInfo
        infoItems={infoItems}
        productComplaintIconSrc={ProductComplaintIcon}
        adverseEventIconSrc={AdverseEventIcon}
        productComplaintsChipClassName={styles.productComplaintsChip}
        adverseEventChipClassName={styles.adverseEventChip}
      />
      <ComplaintAISummary />
      <Grid container spacing={3} className={styles.gridWithMarginTop}>
        <Grid item xs={12} md={4.9}>
          <ComplaintNarrative />
        </Grid>
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