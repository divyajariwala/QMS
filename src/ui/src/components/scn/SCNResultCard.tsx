import React from "react";
import { useNavigate } from "react-router-dom";
import { Box, Stack } from "@mui/material";
import styles from "./SCNResultCard.module.scss";
import CalendarIcon from "../../assets/icons/calendarLight.svg";
import AdverseEvents from "../../assets/icons/adverseEvent.svg";
import ProductComplaints from "../../assets/icons/productComplaint.svg";
import OverdueIcon from "../../assets/icons/overdue.svg";
import RightIcon from "../../assets/icons/rightDark.svg";

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
  changeTitle?: string;
}

interface SCNResultCardProps {
  scn: SCNItem;
  onSeeDetails?: (id: string) => void;
  isEditingCard?: boolean;
}

const SCNResultCard: React.FC<SCNResultCardProps> = ({
  scn,
  onSeeDetails,
  isEditingCard,
}) => {
  const navigate = useNavigate();

  const handleSeeDetailsClick = () => {
    navigate(`/scn/supplier/${scn.id}`);
  };
  const getStatusClass = () => {
    switch (scn.status) {
      case "SUPPLIER ACTION REQUIRED":
        return styles.statusRed;
      case "PENDING REVIEW":
        return styles.statusBlue;
      case "IN REVIEW":
        return styles.statusOrange;
      default:
        return "";
    }
  };

  const getClassificationClass = () => {
    switch (scn.changeClassification) {
      case "Low":
        return styles.statusLow;
      case "Medium":
        return styles.statusMedium;
      case "High":
        return styles.statusHigh;
      default:
        return "";
    }
  };

  const getChangeTypeConfig = () => {
    if (scn.changeType === "Adverse Event") {
      return {
        className: styles.changeTypeOrange,
        icon: AdverseEvents,
      };
    }

    return {
      className: styles.changeTypeBlue,
      icon: ProductComplaints,
    };
  };

  const changeTypeConfig = getChangeTypeConfig();

  return (
    <Box className={styles.card} onClick={handleSeeDetailsClick}>
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
          <h3
            className={
              isEditingCard ? styles.scnNumberEditing : styles.scnNumber
            }
          >
            {scn.scnNumber}
          </h3>
        </Box>
        {scn.overdueDays && (
          <Box className={styles.overdueTag}>
            <img src={OverdueIcon} alt="Overdue" />
            <span>Overdue by {scn.overdueDays} days</span>
          </Box>
        )}
      </Stack>
      {/* Info Row */}
      <Box className={styles.infoRow}>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Change Classification</span>
          <span
            className={`${styles.classificationStatus} ${getClassificationClass()}`}
          >
            {scn.changeClassification}
          </span>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Supplier ref</span>
          <span className={styles.infoValue}>{scn.supplierRef}</span>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Notification Date Date</span>
          <Box className={styles.dateValue}>
            <img src={CalendarIcon} alt="Calendar" />
            <span className={styles.infoValue}>{scn.notificationDate}</span>
          </Box>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Planned Implementation Date</span>
          <Box className={styles.dateValue}>
            <img src={CalendarIcon} alt="Calendar" />
            <span className={styles.infoValue}>
              {scn.plannedImplementationDate}
            </span>
          </Box>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Change Type</span>
          <Box
            className={`${styles.changeTypeTag} ${changeTypeConfig.className}`}
          >
            <img src={changeTypeConfig.icon} alt={scn.changeType} />
            <span>{scn.changeType}</span>
          </Box>
        </Box>
        {!isEditingCard && (
          <Box className={styles.infoItem}>
            <span className={styles.infoLabel}>Change Title</span>
            <span className={styles.infoValue}>{scn.changeTitle}</span>
          </Box>
        )}
      </Box>
      {/* Summary Row */}
      {!isEditingCard && (
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
              handleSeeDetailsClick();
            }}
          >
            See details
            <img src={RightIcon} alt=">" />
          </a>
        </Stack>
      )}
    </Box>
  );
};

export default SCNResultCard;
