import React from "react";
import { useNavigate } from "react-router-dom"; 
import { Box, Stack, Typography } from "@mui/material";
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

const labelTypographySx = {
  fontFamily: "Inter",
  fontWeight: 500,
  fontSize: "14px",
  lineHeight: "20px",
  letterSpacing: "-0.1px",
  color: "#5F6D7E",
};

const valueTypographySx = {
  fontFamily: "Inter",
  fontWeight: 600,
  fontSize: "16px",
  lineHeight: "22px",
  letterSpacing: "-0.1px",
  color: "#272D37",
};

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
  <Stack direction="column" gap={0.75}>
    <Typography variant="subtitle1" sx={labelTypographySx}>
      {label}
    </Typography>
    <Stack direction="row" gap={0.5} alignItems="center">
      <img src={iconSrc} alt={iconAlt} />
      {typeof value === "string" ? (
        <Typography variant="body1" sx={valueTypographySx}>
          {value}
        </Typography>
      ) : (
        value
      )}
    </Stack>
  </Stack>
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
  <Stack direction="row" gap={0.5} className={className}>
    <img src={iconSrc} alt={iconAlt} />
    <Typography
      variant="subtitle1"
      sx={{
        fontFamily: "Inter",
        fontWeight: 500,
        fontSize: "14px",
        lineHeight: "20px",
        letterSpacing: "-0.1px",
      }}
    >
      {label}
    </Typography>
  </Stack>
);

const getDueStatus = (
  dateStr: string
): {
  type: "Overdue" | "Today" | "Tomorrow" | "Due";
  label: string;
} => {
  const dueDate = new Date(dateStr);

  // Get "today" at midnight (to ignore time differences)
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Get tomorrow's date at midnight
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  // Get the difference in time (milliseconds)
  const diffTime = dueDate.getTime() - today.getTime();

  // Calculate difference in full days between dueDate and today
  // Positive means dueDate after today, negative means before today
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return {
      type: "Overdue",
      label: `Overdue by ${Math.abs(diffDays)} day${
        Math.abs(diffDays) === 1 ? "" : "s"
      }`,
    };
  } else if (diffDays === 0) {
    return {
      type: "Today",
      label: "Due Today",
    };
  } else if (diffDays === 1) {
    return {
      type: "Tomorrow",
      label: "Due Tomorrow",
    };
  } else {
    const formattedDate = dueDate
      .toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "2-digit",
      })
      .replace(/,/g, "");

    return {
      type: "Due",
      label: `Due on ${formattedDate}`,
    };
  }
};

const ComplaintsResult: React.FC<ComplaintProps> = ({ complaint }) => {
  const navigate = useNavigate();
  const handleSeeDetailsClick = () => {
    navigate(`/productComplaints/CAS-12345`);
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
    <Stack
      direction={"column"}
      alignItems={"flex-start"}
      justifyContent={"flex-start"}
      gap={1.5}
      mt={2.5}
      className={styles.complaintsCardContainer}
    >
      <Stack
        width={"100%"}
        direction={"row"}
        alignItems={"flex-start"}
        justifyContent={"space-between"}
      >
        <Box>
          <Typography
            variant="subtitle1"
            sx={{
              fontFamily: "Inter",
              fontWeight: 600,
              fontSize: "12px",
              lineHeight: "24px",
              letterSpacing: "-0.1px",
              textTransform: "uppercase",
              color: "#3B3B3B",
            }}
          >
            IN-REVIEW
          </Typography>
          <Typography
            variant="body1"
            sx={{
              fontFamily: "Inter",
              fontWeight: 600,
              fontSize: "16px",
              lineHeight: "24px",
              letterSpacing: "-0.1px",
              textTransform: "uppercase",
              color: "#0089EB",
            }}
          >
            CAS-12345
          </Typography>
        </Box>
        <ComplaintsDueDateChip
          type={getDueStatus(complaint["Due Date"]).type}
          label={getDueStatus(complaint["Due Date"]).label}
        />
      </Stack>
      <Stack direction={"row"} gap={8}>
        {infoItems.map(({ label, iconSrc, iconAlt, value }) => (
          <InfoItem
            key={label}
            label={label}
            iconSrc={iconSrc}
            iconAlt={iconAlt}
            value={value}
          />
        ))}
        <Stack direction={"column"} gap={0.75}>
          <Typography variant="subtitle1" sx={labelTypographySx}>
            Case Type
          </Typography>
          <Stack direction={"row"} gap={0.5}>
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
          </Stack>
        </Stack>
      </Stack>
      <Stack
        width={"100%"}
        direction={"row"}
        alignItems={"center"}
        justifyContent={"space-between"}
        onClick={handleSeeDetailsClick}
      >
        <Typography
          variant="caption"
          sx={{
            fontFamily: "Inter",
            fontWeight: 400,
            fontSize: "14px",
            lineHeight: "20px",
            letterSpacing: "-0.1px",
            color: "#5F6D7E",
          }}
        >
          Short Description
        </Typography>
        <Stack
          direction={"row"}
          alignItems={"center"}
          justifyContent={"space-between"}
        >
          <Typography
            variant="caption"
            sx={{
              fontFamily: "Inter",
              fontWeight: 600,
              fontSize: "14px",
              lineHeight: "20px",
              color: "#437EF7",
              cursor: 'pointer'
            }}
          >
            See Details
          </Typography>
          <KeyboardArrowRightIcon />
        </Stack>
      </Stack>
    </Stack>
  );
};

export default ComplaintsResult;
