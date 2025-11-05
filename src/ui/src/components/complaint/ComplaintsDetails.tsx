import React, { useState, useEffect } from 'react';
import { useParams } from "react-router-dom";
import { Box, Grid } from '@mui/material';
import ProductComplaintIcon from "../../assets/icons/productComplaint.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";
import ComplaintHeaderCard from './ComplaintHeaderCard';
import ComplaintSecondaryInfo from './ComplaintSecondaryInfo';
import ComplaintAISummary from './ComplaintAISummary';
import ComplaintNarrative from './ComplaintNarrative';
import ComplaintCategory from './ComplaintCategory';
import { ComplaintDetail } from 'src/types';
import CommonBreadcrumbs from '@components/commonBreadCrumbs/CommonBreadcrumbs';
import CriticalityIcon from "../../assets/icons/criticality.svg";
import ReportTypeIcon from "../../assets/icons/reportType.svg";
import CategoryIcon from "../../assets/icons/category.svg";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import { formatDateMMM_D_YYYY } from 'src/utils';
import { calculateOverdueDays } from 'src/helpers';
import { fetchComplaintDetailById, postApproveComplaint } from 'src/services/api.service';
import Notification from '@components/Notification/Notification';
import styles from "./ComplaintsResult.module.scss";

const ComplaintsDetails: React.FC = () => {
  const [open, setOpen] = useState(false);
  //const [complaints, setComplaints] = useState<ComplaintCategoryItem[]>(complaintCategories);
  const [complaintDetails, setComplaintDetails] = useState<ComplaintDetail | null>(null);
  const [isApproved, setIsApproved] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const { complaintId } = useParams<{ complaintId: string | undefined }>();
  const complaintHeaderData = {
    status: complaintDetails?.caseStatus,
    caseId: complaintDetails?.case_id,
    overdueDays: calculateOverdueDays(complaintDetails?.receipt_date as string),
    primaryReporter: complaintDetails?.primary_reporter,
    patientName: complaintDetails?.patient_name,
    physicianName: complaintDetails?.physician_name,
    drug: complaintDetails?.product_details?.drug_name,
    lotNumber: complaintDetails?.product_details?.lot_no,
    doseAmount: complaintDetails?.product_details?.dosage,
    expirationDate: '',
    partNumber: '',
    receipt_date: complaintDetails?.receipt_date
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (complaintDetails) {
        const res = await postApproveComplaint(complaintDetails);
        setComplaintDetails(res?.data);
        setIsApproved(true);
        handleShowNotification();
      }

    } catch (err: any) {
      console.log(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleShowNotification = () => {
    setOpen(true);
  };

  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string,
  ) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const items = [
    { label: 'Home', to: '/' },
    { label: 'Complaints', to: '/complaints' },
    { label: complaintDetails?.case_id.toString() },
  ];

  const infoItems = [
    {
      label: "Criticality",
      iconSrc: CriticalityIcon,
      iconAlt: "Criticality",
      value: complaintDetails?.criticality,
    },
    {
      label: "Report Type",
      iconSrc: ReportTypeIcon,
      iconAlt: "Report Type",
      value: complaintDetails?.report_type,
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
      value: formatDateMMM_D_YYYY(complaintDetails?.receipt_date as string),
    },
  ];

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const data = await fetchComplaintDetailById(complaintId);
        setComplaintDetails(data);
      } catch (err: any) {
        console.log(err.message || "Failed to load complaint details.");
      } finally {
        setLoading(false);
      }
    }
    if (complaintId) fetchData();
  }, [complaintId]);
  console.log(complaintDetails)
  if (loading) return <p>Loading details...</p>;
  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />
      <ComplaintHeaderCard
        complaintData={complaintHeaderData}
        onApproveAndSend={handleSubmit}
        caseStatus={complaintDetails?.caseStatus}
        isApproved={isApproved}
      />
      <ComplaintSecondaryInfo
        infoItems={infoItems}
        productComplaintIconSrc={ProductComplaintIcon}
        adverseEventIconSrc={AdverseEventIcon}
        productComplaintsChipClassName={styles.productComplaintsChip}
        adverseEventChipClassName={styles.adverseEventChip}
        caseType={complaintDetails?.case_type as string[]}
      />
      <ComplaintAISummary ai_summary={complaintDetails?.ai_summary as string} />
      <Grid container spacing={3} className={styles.gridWithMarginTop}>
        <Grid item xs={12} md={4.9}>
          <ComplaintNarrative narrative={complaintDetails?.narrative as string} />
        </Grid>
        <Grid item xs={12} md={7.1}>
          <ComplaintCategory
            complaintCategories={complaintDetails?.category_details || []}
            setComplaintCategories={(newCategoryDetails) => {
              setComplaintDetails((prev) => {
                if (!prev) return prev;
                // Force deep clone
                const clonedPrev = JSON.parse(JSON.stringify(prev));
                clonedPrev.category_details = newCategoryDetails;
                console.log("Setting complaintDetails with cloned data:", clonedPrev);
                return clonedPrev;
              });
            }}

          />
        </Grid>
      </Grid>
      <Notification open={open} onClose={handleCloseNotification} />
    </Box>
  );
};

export default ComplaintsDetails;