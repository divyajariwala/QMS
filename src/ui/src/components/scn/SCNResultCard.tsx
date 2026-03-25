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
  status:
    | "SUPPLIER ACTION REQUIRED"
    | "PENDING REVIEW"
    | "IN REVIEW"
    | "APPROVED"
    | "REJECTED"
    | "SUPPLIER INFO REQUESTED";
  scnNumber: string;
  changeClassification: string;
  supplierRef: string;
  notificationDate: string;
  plannedImplementationDate: string;
  changeType: string;
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
  const getCardTopBorderClass = () => {
    switch (scn.status) {
      case "SUPPLIER ACTION REQUIRED":
        return styles.cardBorderYellow;
      case "PENDING REVIEW":
        return styles.cardBorderPurple;
      case "IN REVIEW":
        return styles.cardBorderGray;
      case "SUPPLIER INFO REQUESTED":
        return styles.cardBorderGray;
      case "APPROVED":
        return styles.cardBorderApproved;
      case "REJECTED":
        return styles.cardBorderRejected;
      default:
        return "";
    }
  };
  const getStatusClass = () => {
    switch (scn.status) {
      case "SUPPLIER ACTION REQUIRED":
        return styles.statusYellow;
      case "PENDING REVIEW":
        return styles.statusPurple;
      case "IN REVIEW":
        return styles.statusGray;
      case "SUPPLIER INFO REQUESTED":
        return styles.statusGray;
      case "APPROVED":
        return styles.statusApproved;
      case "REJECTED":
        return styles.statusRejected;
      default:
        return "";
    }
  };

  // Returns a human-friendly label for the status badge
  const getStatusLabel = () => {
    switch (scn.status) {
      case "SUPPLIER ACTION REQUIRED":
        return "Supplier Action Required";
      case "PENDING REVIEW":
        return "Pending Review";
      case "IN REVIEW":
        return "In Review";
      case "SUPPLIER INFO REQUESTED":
        return "Supplier Info Requested";
      case "APPROVED":
        return "Approved";
      case "REJECTED":
        return "Rejected";
      default:
        return scn.status;
    }
  };

  const getClassificationClass = () => {
    switch (scn.changeClassification) {
      case "Minor":
        return styles.statusLow;
      case "Moderate":
        return styles.statusMedium;
      case "Major":
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
    <Box
      className={`${styles.card} ${getCardTopBorderClass()}`}
      onClick={handleSeeDetailsClick}
    >
      {/* Header Row */}
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="flex-start"
        className={styles.headerRow}
      >
        <Box>
          <span className={`${styles.status} ${getStatusClass()}`}>
            {getStatusLabel()}
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
          <span className={styles.infoLabel}>Notification Date</span>
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
