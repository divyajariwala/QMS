import React from "react";
import { Box, Stack } from "@mui/material";
import styles from "./SCNResultCard.module.scss";

interface SCNItem {
  id: string;
  status: "SUPPLIER ACTION REQUIRED" | "PENDING REVIEW" | "IN REVIEW";
  scnNumber: string;
  changeClassification: string;
  supplierRef: string;
  notificationDate: string;
  plannedImplementationDate: string;
  changeType: "Adverse Event" | "Product Complaint";
  changeTitleSummary: string;
  overdueDays?: number;
}

interface SCNResultCardProps {
  scn: SCNItem;
  onSeeDetails: (id: string) => void;
}

// Calendar Icon Component
const CalendarIcon = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4.5 1V2.5M9.5 1V2.5M1.75 5.5H12.25M2.5 2.5H11.5C11.9142 2.5 12.25 2.83579 12.25 3.25V11.5C12.25 11.9142 11.9142 12.25 11.5 12.25H2.5C2.08579 12.25 1.75 11.9142 1.75 11.5V3.25C1.75 2.83579 2.08579 2.5 2.5 2.5Z" stroke="#9CA3AF" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

// Clock/Alarm Icon Component
const ClockIcon = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="7" cy="7" r="5.5" stroke="#F97316" strokeWidth="1.2"/>
    <path d="M7 4V7L9 8.5" stroke="#F97316" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

// Document Icon Component
const DocumentIcon = ({ color }: { color: string }) => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M7 1H3C2.44772 1 2 1.44772 2 2V10C2 10.5523 2.44772 11 3 11H9C9.55228 11 10 10.5523 10 10V4L7 1Z" stroke={color} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M7 1V4H10" stroke={color} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

// External Link Icon
const ExternalLinkIcon = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 6 .5V9.5C9 9.76522 8.89464 10.0196 8.70711 10.2071C8.51957 10.3946 8.26522 10.5 8 10.5H2.5C2.23478 10.5 1.98043 10.3946 1.79289 10.2071C1.60536 10.0196 1.5 9.76522 1.5 9.5V4C1.5 3.73478 1.60536 3.48043 1.79289 3.29289C1.98043 3.10536 2.23478 3 2.5 3H5.5" stroke="#2563EB" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M7.5 1.5H10.5V4.5" stroke="#2563EB" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M5 7L10.5 1.5" stroke="#2563EB" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const SCNResultCard: React.FC<SCNResultCardProps> = ({ scn, onSeeDetails }) => {
  const getStatusClass = () => {
    switch (scn.status) {
      case "SUPPLIER ACTION REQUIRED":
        return styles.statusRed;
      case "PENDING REVIEW":
        return styles.statusOrange;
      case "IN REVIEW":
        return styles.statusBlue;
      default:
        return "";
    }
  };

  const getBorderClass = () => {
    switch (scn.status) {
      case "SUPPLIER ACTION REQUIRED":
        return styles.borderRed;
      case "PENDING REVIEW":
        return styles.borderOrange;
      case "IN REVIEW":
        return styles.borderBlue;
      default:
        return "";
    }
  };

  const getChangeTypeConfig = () => {
    if (scn.changeType === "Adverse Event") {
      return { className: styles.changeTypeOrange, color: "#EA580C" };
    }
    return { className: styles.changeTypeBlue, color: "#2563EB" };
  };

  const changeTypeConfig = getChangeTypeConfig();

  return (
    <Box className={`${styles.card} ${getBorderClass()}`}>
      {/* Header Row */}
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="flex-start"
        className={styles.headerRow}
      >
        <Box>
          <span className={`${styles.status} ${getStatusClass()}`}>
            {scn.status}
          </span>
          <h3 className={styles.scnNumber}>{scn.scnNumber}</h3>
        </Box>
        {scn.overdueDays && (
          <Box className={styles.overdueTag}>
            <ClockIcon />
            <span>Overdue by {scn.overdueDays} days</span>
          </Box>
        )}
      </Stack>

      {/* Info Row */}
      <Box className={styles.infoRow}>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Change Classification</span>
          <span className={styles.infoValue}>{scn.changeClassification}</span>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Supplier ref</span>
          <span className={styles.infoValue}>{scn.supplierRef}</span>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Notification Date Date</span>
          <Box className={styles.dateValue}>
            <CalendarIcon />
            <span>{scn.notificationDate}</span>
          </Box>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Planned Implementation Date</span>
          <Box className={styles.dateValue}>
            <CalendarIcon />
            <span>{scn.plannedImplementationDate}</span>
          </Box>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Change Type</span>
          <Box className={`${styles.changeTypeTag} ${changeTypeConfig.className}`}>
            <DocumentIcon color={changeTypeConfig.color} />
            <span>{scn.changeType}</span>
          </Box>
        </Box>
      </Box>

      {/* Summary Row */}
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="flex-end"
        className={styles.summaryRow}
      >
        <Box className={styles.summarySection}>
          {/* <Box className={styles.summaryHeader}>
            <span className={styles.summaryLabel}>Change Title / Summary</span>
            <a href="#" className={styles.editLink}>
              Edit <ExternalLinkIcon />
            </a>
          </Box> */}
          <p className={styles.summaryText}>{scn.changeTitleSummary}</p>
        </Box>
        <a
          href="#"
          className={styles.seeDetailsLink}
          onClick={(e) => {
            e.preventDefault();
            onSeeDetails(scn.id);
          }}
        >
          See details <span className={styles.arrowIcon}>›</span>
        </a>
      </Stack>
    </Box>
  );
};

export default SCNResultCard;