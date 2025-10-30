import React from "react";
import { Stack, Typography } from "@mui/material";
import OverdueIcon from "../../assets/icons/overdue.svg";
import DueTodayIcon from "../../assets/icons/dueToday.svg";
import DueTomorrowIcon from "../../assets/icons/dueTomorrow.svg";
import DueIcon from "../../assets/icons/due.svg";
import styles from "./ComplaintsDueDateChip.module.scss";

interface ComplaintsDueDateChipProps {
  type: "Overdue" | "Today" | "Tomorrow" | "Due";
  label: string;
}

const DueDateChip = ({
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
  <Stack direction="row" alignItems={"center"} gap={0.5} className={className}>
    <img
      src={iconSrc}
      alt={iconAlt}
      style={{ width: "12px", height: "12px" }}
    />
    <Typography
      variant="subtitle1"
      sx={{
        fontFamily: "Inter",
        fontWeight: 500,
        fontSize: "13px",
        lineHeight: "18px",
        letterSpacing: "-0.1px",
      }}
    >
      {label}
    </Typography>
  </Stack>
);

const ComplaintsDueDateChip: React.FC<ComplaintsDueDateChipProps> = ({
  type,
  label,
}) => {
  switch (type) {
    case "Overdue":
      return (
        <DueDateChip
          iconSrc={OverdueIcon}
          iconAlt="Overdue"
          label={label}
          className={styles.overdueChip}
        />
      );
    case "Today":
      return (
        <DueDateChip
          iconSrc={DueTodayIcon}
          iconAlt="Due Today"
          label={label}
          className={styles.dueTodayChip}
        />
      );
    case "Tomorrow":
      return (
        <DueDateChip
          iconSrc={DueTomorrowIcon}
          iconAlt="Due Tomorrow"
          label={label}
          className={styles.dueTomorrowChip}
        />
      );
    case "Due":
      return (
        <DueDateChip
          iconSrc={DueIcon}
          iconAlt="Due"
          label={label}
          className={styles.dueChip}
        />
      );
    default:
      return (
        <DueDateChip
          iconSrc={DueIcon}
          iconAlt="Due"
          label={label}
          className={styles.dueChip}
        />
      );
  }
};

export default ComplaintsDueDateChip;
