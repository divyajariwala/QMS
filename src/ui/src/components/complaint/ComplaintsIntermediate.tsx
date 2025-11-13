import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import { Box, Grid } from '@mui/material';
import ProductComplaintIcon from "../../assets/icons/productComplaint.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";
import ArrowRight from "../../assets/icons/arrowRight.svg";
import ComplaintInterHeaderCard from './ComplaintInterHeaderCard';
import ComplaintSecondaryInfo from './ComplaintSecondaryInfo';
import ComplaintNarrative from './ComplaintNarrative';
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
import { MockComplaintDetailApiResponse } from 'src/mockData/mockData';
import ModifyDetails from '../../components/modifyDetails/ModifyDetails';
import styles from "./ComplaintsResult.module.scss";

const ComplaintsIntermediate: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [openModifyDetails, setOpenModifyDetails] = useState(false);
  const [complaintDetails, setComplaintDetails] = useState<ComplaintDetail | null>(null);
  const [headerData, setHeaderData] = useState<any>(null); // holds editable header fields
  const [isApproved, setIsApproved] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const { complaintId } = useParams<{ complaintId: string | undefined }>();
  const navigate = useNavigate();

  // Load complaint details
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        //const data = await fetchComplaintDetailById(complaintId);
        const data = MockComplaintDetailApiResponse;
        setComplaintDetails(data);
      } catch (err: any) {
        console.log(err.message || "Failed to load complaint details.");
      } finally {
        setLoading(false);
      }
    }
    if (complaintId) fetchData();
  }, [complaintId]);

  // Initialize headerData from complaintDetails whenever complaintDetails changes
  useEffect(() => {
    if (!complaintDetails) return;
    setHeaderData({
      status: complaintDetails?.caseStatus ?? '',
      caseId: complaintDetails?.case_id ?? '',
      overdueDays: calculateOverdueDays(complaintDetails?.receipt_date as string),
      primaryReporter: complaintDetails?.primary_reporter ?? '',
      patientName: complaintDetails?.patient_name ?? '',
      physicianName: complaintDetails?.physician_name ?? '',
      drug: complaintDetails?.product_details?.drug_name ?? '',
      lotNumber: complaintDetails?.product_details?.lot_no ?? '',
      doseAmount: complaintDetails?.product_details?.dosage ?? '',
      expirationDate: complaintDetails?.product_details?.expiration_date ?? '',
      partNumber: '',
      receipt_date: complaintDetails?.receipt_date ?? ''
    });
  }, [complaintDetails]);

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

  const handleShowNotification = () => setOpen(true);

  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string,
  ) => {
    if (reason === "clickaway") return;
    setOpen(false);
  };

  const items = [
    { label: 'Home', to: '/' },
    { label: 'Complaints', to: '/complaints' },
    { label: complaintDetails?.case_id?.toString() ?? '' },
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

  const handleClassify = () => {
    navigate(`/approveComplaints/${complaintDetails?.case_id}`);
  };

  // New: handle modify details submit. `data` shape should match ModifyDetails onSubmit payload.
  const handleModifySubmit = (data: any) => {
    // Update complaintDetails (so child components that depend on complaintDetails reflect changes)
    setComplaintDetails(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        primary_reporter: data.primaryReporter ?? prev.primary_reporter,
        patient_name: data.patientName ?? prev.patient_name,
        physician_name: data.physicianName ?? prev.physician_name,
        // update product_details while preserving other product fields
        product_details: {
          ...(prev.product_details ?? {}),
          drug_name: data.product ?? prev.product_details?.drug_name,
          lot_no: data.lotNumber ?? prev.product_details?.lot_no,
          dosage: data.doseAmount ?? prev.product_details?.dosage,
        },
        receipt_date: data.reportDate ?? prev.receipt_date,
      };
    });

    // Update headerData shown in the header card
    setHeaderData((prev: any) => ({
      ...(prev ?? {}),
      primaryReporter: data.primaryReporter ?? prev?.primaryReporter,
      patientName: data.patientName ?? prev?.patientName,
      physicianName: data.physicianName ?? prev?.physicianName,
      drug: data.product ?? prev?.drug,
      lotNumber: data.lotNumber ?? prev?.lotNumber,
      doseAmount: data.doseAmount ?? prev?.doseAmount,
      receipt_date: data.reportDate ?? prev?.receipt_date,
    }));

    // Close modify dialog
    setOpenModifyDetails(false);
  };

  if (loading) return <p>Loading details...</p>;

  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />
      <ComplaintInterHeaderCard
        complaintData={headerData}
        caseStatus={complaintDetails?.caseStatus}
        setOpenModifyDetails={setOpenModifyDetails}
      />
      <ComplaintSecondaryInfo
        infoItems={infoItems}
        productComplaintIconSrc={ProductComplaintIcon}
        adverseEventIconSrc={AdverseEventIcon}
        productComplaintsChipClassName={styles.productComplaintsChip}
        adverseEventChipClassName={styles.adverseEventChip}
        caseType={complaintDetails?.case_type as string[]}
      />
      <Grid container spacing={3} className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <ComplaintNarrative narrative={complaintDetails?.narrative as string} />
        </Grid>
        <Grid item xs={12} md={7.1}>
          <div className={styles.cardBox}>
            <div className={styles.cardTitle}>Complaint Category</div>
            <div className={styles.cardSubtitle}>Please review and modify.</div>
            <div className={styles.emptyCategory}>
              <p className={styles.emptyCategoryText}>There is no complaint category created.</p>
              <button className={styles.classifyBtn} onClick={handleClassify}>
                Classify Complaint <img src={ArrowRight} alt="" />
              </button>
            </div>
          </div>
        </Grid>
      </Grid>

      <Notification open={open} onClose={handleCloseNotification} />

      <ModifyDetails
        onSubmit={handleModifySubmit}
        initialValues={headerData}
        open={openModifyDetails}
        onClose={() => setOpenModifyDetails(false)}
      />
    </Box>
  );
};

export default ComplaintsIntermediate;