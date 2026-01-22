import React, { useState, useEffect } from 'react';
import { useParams } from "react-router-dom";
import { Box, Grid } from '@mui/material';
import ProductComplaintIcon from "../../assets/icons/productComplaint.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";
import AdverseEventHeader from './AdverseEventHeader';
import ComplaintSecondaryInfo from '../complaint/ComplaintSecondaryInfo';
import ComplaintNarrative from '../complaint/ComplaintNarrative';
import { ComplaintDetail } from 'src/types';
import CommonBreadcrumbs from '@components/commonBreadCrumbs/CommonBreadcrumbs';
import CriticalityIcon from "../../assets/icons/criticality.svg";
import ReportTypeIcon from "../../assets/icons/reportType.svg";
import CategoryIcon from "../../assets/icons/category.svg";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import { formatDateMMM_D_YYYY } from 'src/utils';
import { calculateOverdueDays } from 'src/helpers';
import { fetchComplaintDetailById } from 'src/services/api.service';
import styles from "./AdverseEventDetails.module.scss";

const AdverseEventDetails: React.FC = () => {
  const [complaintDetails, setComplaintDetails] = useState<ComplaintDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const { complaintId } = useParams<{ complaintId: string | undefined }>();
  const complaintHeaderData = {
    status: complaintDetails?.caseStatus,
    caseId: complaintDetails?.case_id,
    overdueDays: calculateOverdueDays(complaintDetails?.receipt_date as string),
    primaryReporter: complaintDetails?.primary_reporter,
    patientName: complaintDetails?.patient_name,
    physicianName: complaintDetails?.physician_name,
    drug: complaintDetails?.product_details?.drug,
    lotNumber: complaintDetails?.product_details?.lot_no,
    doseAmount: complaintDetails?.product_details?.dosage,
    expirationDate: complaintDetails?.product_details?.expiration_date,
    partNumber: complaintDetails?.product_details?.part_number,
    receipt_date: complaintDetails?.receipt_date
  };

  async function fetchData() {
    setLoading(true);
    try {
      const data = await fetchComplaintDetailById(complaintId);
      if (data?.category_details) {
        data.category_details = data.category_details.sort((a, b) => b.percentage - a.percentage);
      }
      setComplaintDetails(data);
    } catch (err: any) {
      console.log(err.message || "Failed to load complaint details.");
    } finally {
      setLoading(false);
    }
  }

  const items = [
    { label: 'Home', to: '/' },
    { label: 'Adverse Events', to: '/adverseEvent' },
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
      value: formatDateMMM_D_YYYY(complaintDetails?.created_at as string),
    },
  ];

  useEffect(() => {
    if (complaintId) fetchData();
  }, [complaintId]);

  if (loading) return <p>Loading details...</p>;
  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />
      <AdverseEventHeader
        complaintData={complaintHeaderData}
      />
      <ComplaintSecondaryInfo
        infoItems={infoItems}
        productComplaintIconSrc={ProductComplaintIcon}
        adverseEventIconSrc={AdverseEventIcon}
        productComplaintsChipClassName={styles.productComplaintsChip}
        adverseEventChipClassName={styles.adverseEventChip}
        caseType={complaintDetails?.case_type as string[]}
      />
        <Grid item xs={12} md={12} mt={3}>
          <ComplaintNarrative narrative={complaintDetails?.narrative as string} />
        </Grid>
    </Box>
  );
};

export default AdverseEventDetails;