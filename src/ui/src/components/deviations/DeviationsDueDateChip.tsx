import React from "react";
import { Stack, Box } from "@mui/material";
import OverdueIcon from "../../assets/icons/overdue.svg";
import DueTodayIcon from "../../assets/icons/dueToday.svg";
import DueTomorrowIcon from "../../assets/icons/dueTomorrow.svg";
import DueIcon from "../../assets/icons/due.svg";
import { ModuleDueDateChipProps, DueDateChipProps } from "src/types";
import styles from "./DeviationsDueDateChip.module.scss";

const DueDateChip = ({
  iconSrc,
  iconAlt,
  label,
  className,
}: DueDateChipProps) => (
  <Stack
    direction="row"
    alignItems={"center"}
    gap={0.5}
    className={`${styles.dueDateChip} ${className ?? ""}`}
  >
    <img src={iconSrc} alt={iconAlt} className={styles.dueDateChip__icon} />
    <Box className={styles.dueDateChip__label}>{label}</Box>
  </Stack>
);

const DeviationsDueDateChip: React.FC<ModuleDueDateChipProps> = ({
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

export default DeviationsDueDateChip;
