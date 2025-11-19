import React from "react";
import { useNavigate } from "react-router-dom";
import { Box, Stack } from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import ComplaintsDueDateChip from "./ComplaintsDueDateChip";
import { getDueStatus } from "src/helpers";
import {formatDateMMM_D_YYYY} from "src/utils"

import CriticalityIcon from "../../assets/icons/criticality.svg";
import ReportTypeIcon from "../../assets/icons/reportType.svg";
import CategoryIcon from "../../assets/icons/category.svg";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import ProductComplaintIcon from "../../assets/icons/productComplaint.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";

import styles from "./ComplaintsResult.module.scss";
import { InfoChipProps, InfoItemProps, ComplaintProps } from "src/types";

const InfoItem = ({
  label,
  iconSrc,
  iconAlt,
  value,
}: InfoItemProps) => (
  <div className={styles.stackColumn}>
    <Box className={styles.infoItemLabel}>{label}</Box>
    <div className={styles.iconValueRow}>
      <img src={iconSrc} alt={iconAlt} className={styles.infoItemIcon} />
      {typeof value === "string" ? (
        <Box className={styles.infoItemValue}>{value}</Box>
      ) : (
        value
      )}
    </div>
  </div>
);

const Chip = ({
  iconSrc,
  iconAlt,
  label,
  className,
}: InfoChipProps) => (
  <div className={className}>
    <Stack direction="row" gap={0.5}>
      <img src={iconSrc} alt={iconAlt} />
      <Box
        className={styles.infoItemLabel}
      >
        {label}
      </Box>
    </Stack>
  </div>
);

const ComplaintsResult: React.FC<ComplaintProps> = ({ complaint, selected }) => {
  const navigate = useNavigate();

  const handleSeeDetailsClick = () => {
    navigate(`/complaints/${complaint.case_id}`);
  };

  const infoItems = [
    {
      label: "Criticality",
      iconSrc: CriticalityIcon,
      iconAlt: "Criticality",
      value: complaint.criticality,
    },
    {
      label: "Report Type",
      iconSrc: ReportTypeIcon,
      iconAlt: "Report Type",
      value: complaint.report_type,
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
      value: formatDateMMM_D_YYYY(complaint.receipt_date),
    },
  ];

  return (
    <div className={styles.complaintsCardContainer}>
      <div className={styles.headerRow}>
        <Box>
          <Box className={styles.statusText}>{selected === 'pending' ? "IN REVIEW" : selected.toUpperCase()}</Box>
          <Box className={styles.caseNumberText}>{complaint.case_id}</Box>
        </Box>
        <ComplaintsDueDateChip
          type={getDueStatus(complaint.receipt_date).type}
          label={getDueStatus(complaint.receipt_date).label}
        />
      </div>

      <div className={styles.infoRow}>
        {infoItems.map(({ label, iconSrc, iconAlt, value }) => (
          <InfoItem key={label} label={label} iconSrc={iconSrc} iconAlt={iconAlt} value={value} />
        ))}

        <div className={styles.infoItemColumn}>
          <Box className={styles.infoItemLabel}>Case Type</Box>
          <div className={styles.caseTypeRow}>
            {complaint.case_type.includes("Product Complaint") && (
              <Chip
                iconSrc={ProductComplaintIcon}
                iconAlt="Product Complaint"
                label="Product Complaint"
                className={styles.productComplaintsChip}
              />
            )}
            {complaint.case_type.includes("Adverse Event") && (
              <Chip
                iconSrc={AdverseEventIcon}
                iconAlt="Adverse Event"
                label="Adverse Event"
                className={styles.adverseEventChip}
              />
            )}
            {(!complaint.case_type.includes("Product Complaint") && !complaint.case_type.includes("Adverse Event")) && <Box className={styles.infoItemValue}>NA</Box>}
          </div>
        </div>
      </div>

      <div className={styles.bottomRow} onClick={handleSeeDetailsClick}>
        <Box className={styles.shortDescription}>Short Description</Box>
        <div className={styles.seeDetailsRow}>
          <Box className={styles.seeDetailsText}>See Details</Box>
          <KeyboardArrowRightIcon style={{ cursor: "pointer" }} />
        </div>
      </div>
    </div>
  );
};

export default ComplaintsResult;