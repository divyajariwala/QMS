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
    | "supplierActionRequired"
    | "pendingReview"
    | "inReview"
    | "approved"
    | "rejected"
    | "supplierInfoRequested";

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

const getNormalizedStatus = (status: string) => {
  const s = (status || "").replace(/ /g, "_").toUpperCase();
  if (s === "SUPPLIER_ACTION_REQUIRED") return "supplierActionRequired";
  if (s === "PENDING_REVIEW") return "pendingReview";
  if (s === "IN_REVIEW") return "inReview";
  if (s === "SUPPLIER_INFO_REQUESTED") return "supplierInfoRequested";
  if (s === "APPROVED") return "approved";
  if (s === "REJECTED") return "rejected";
  return status;
};

const SCNResultCard: React.FC<SCNResultCardProps> = ({
  scn,
  onSeeDetails,
  isEditingCard,
}) => {
  const navigate = useNavigate();
  const normalizedStatus = getNormalizedStatus(scn.status);

  const handleSeeDetailsClick = () => {
    navigate(`/scn/supplier/${scn.id}`);
  };
  const getCardTopBorderClass = () => {
    switch (normalizedStatus) {
      case "supplierActionRequired":
        return styles.cardBorderYellow;
      case "pendingReview":
        return styles.cardBorderPurple;
      case "inReview":
        return styles.cardBorderGray;
      case "supplierInfoRequested":
        return styles.cardBorderYellow;
      case "approved":
        return styles.cardBorderApproved;
      case "rejected":
        return styles.cardBorderRejected;
      default:
        return "";
    }
  };

  const getStatusClass = () => {
    switch (normalizedStatus) {
      case "supplierActionRequired":
        return styles.statusYellow;
      case "pendingReview":
        return styles.statusPurple;
      case "inReview":
        return styles.statusGray;
      case "supplierInfoRequested":
        return styles.statusYellow;
      case "approved":
        return styles.statusApproved;
      case "rejected":
        return styles.statusRejected;
      default:
        return "";
    }
  };

  // Returns a human-friendly label for the status badge
  const getStatusLabel = () => {
    switch (normalizedStatus) {
      case "supplierActionRequired":
        return "Supplier Action Required";
      case "pendingReview":
        return "Pending Review";
      case "inReview":
        return "In Review";
      case "supplierInfoRequested":
        return "Supplier Info Requested";
      case "approved":
        return "Approved";
      case "rejected":
        return "Rejected";
      default:
        return scn.status;
    }
  };

  const getClassificationClass = () => {
    switch (scn.changeClassification.toUpperCase()) {
      case "MINOR":
        return styles.statusLow;
      case "MODERATE":
        return styles.statusMedium;
      case "MAJOR":
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
      className={
        !isEditingCard
          ? `${styles.card} ${getCardTopBorderClass()}`
          : `${styles.detailsPageCard} ${getCardTopBorderClass()}`
      }
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
            <span className={styles.dateInfoValue}>{scn.notificationDate}</span>
          </Box>
        </Box>
        <Box className={styles.infoItem}>
          <span className={styles.infoLabel}>Planned Implementation Date</span>
          <Box className={styles.dateValue}>
            <img src={CalendarIcon} alt="Calendar" />
            <span className={styles.dateInfoValue}>
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
        <Box paddingTop={3}>
          <p className={`${styles.summaryText} ${styles.mobileSummary}`}>
            {scn.changeTitleSummary}
          </p>
        </Box>
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
            <p className={`${styles.summaryText} ${styles.desktopSummary}`}>
              {scn.changeTitleSummary}
            </p>
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
