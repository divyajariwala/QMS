import React from "react";
import { useNavigate } from "react-router-dom";
import { Box, Stack } from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import ComplaintsDueDateChip from "./ComplaintsDueDateChip";

import CriticalityIcon from "../../assets/icons/criticality.svg";
import ReportTypeIcon from "../../assets/icons/reportType.svg";
import CategoryIcon from "../../assets/icons/category.svg";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import ProductComplaintIcon from "../../assets/icons/productComplaint.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";

import styles from "./ComplaintsResult.module.scss";

interface ComplaintProps {
  complaint: {
    Criticality: string;
    "Report Type": string;
    Category: string;
    "Receipt Date": string;
    "Case Type": string[];
    "Due Date": string;
  };
}

const InfoItem = ({
  label,
  iconSrc,
  iconAlt,
  value,
}: {
  label: string;
  iconSrc: string;
  iconAlt: string;
  value: string | React.ReactNode;
}) => (
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
}: {
  iconSrc: string;
  iconAlt: string;
  label: string;
  className?: string;
}) => (
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

const getDueStatus = (
  dateStr: string
): {
  type: "Overdue" | "Today" | "Tomorrow" | "Due";
  label: string;
} => {
  const dueDate = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return {
      type: "Overdue",
      label: `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) === 1 ? "" : "s"}`,
    };
  } else if (diffDays === 0) {
    return { type: "Today", label: "Due Today" };
  } else if (diffDays === 1) {
    return { type: "Tomorrow", label: "Due Tomorrow" };
  } else {
    const formattedDate = dueDate
      .toLocaleDateString("en-US", { year: "numeric", month: "short", day: "2-digit" })
      .replace(/,/g, "");
    return { type: "Due", label: `Due on ${formattedDate}` };
  }
};

const ComplaintsResult: React.FC<ComplaintProps> = ({ complaint }) => {
  const navigate = useNavigate();

  const handleSeeDetailsClick = () => {
    navigate(`/complaints/CAS-12345`);
  };

  const infoItems = [
    {
      label: "Criticality",
      iconSrc: CriticalityIcon,
      iconAlt: "Criticality",
      value: complaint.Criticality,
    },
    {
      label: "Report Type",
      iconSrc: ReportTypeIcon,
      iconAlt: "Report Type",
      value: complaint["Report Type"],
    },
    {
      label: "Category",
      iconSrc: CategoryIcon,
      iconAlt: "Category",
      value: complaint.Category,
    },
    {
      label: "Receipt Date",
      iconSrc: ReceiptDateIcon,
      iconAlt: "Receipt Date",
      value: complaint["Receipt Date"],
    },
  ];

  return (
    <div className={styles.complaintsCardContainer}>
      <div className={styles.headerRow}>
        <Box>
          <Box className={styles.statusText}>IN-REVIEW</Box>
          <Box className={styles.caseNumberText}>CAS-12345</Box>
        </Box>
        <ComplaintsDueDateChip
          type={getDueStatus(complaint["Due Date"]).type}
          label={getDueStatus(complaint["Due Date"]).label}
        />
      </div>

      <div className={styles.infoRow}>
        {infoItems.map(({ label, iconSrc, iconAlt, value }) => (
          <InfoItem key={label} label={label} iconSrc={iconSrc} iconAlt={iconAlt} value={value} />
        ))}

        <div className={styles.infoItemColumn}>
          <Box className={styles.infoItemLabel}>Case Type</Box>
          <div className={styles.caseTypeRow}>
            {complaint["Case Type"].includes("Product Complaint") && (
              <Chip
                iconSrc={ProductComplaintIcon}
                iconAlt="Product Complaint"
                label="Product Complaint"
                className={styles.productComplaintsChip}
              />
            )}
            {complaint["Case Type"].includes("Adverse Event") && (
              <Chip
                iconSrc={AdverseEventIcon}
                iconAlt="Adverse Event"
                label="Adverse Event"
                className={styles.adverseEventChip}
              />
            )}
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