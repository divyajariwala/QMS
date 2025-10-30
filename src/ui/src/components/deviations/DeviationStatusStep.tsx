import React from "react";
import { Typography, Stack, Box } from "@mui/material";

import stepActive from "../../assets/icons/stepActive.svg";
import stepCompleted from "../../assets/icons/stepCompleted.svg";
import stepIncomplete from "../../assets/icons/stepIncomplete.svg";
import { Status, StatusStepProps, StatusStepsProps, ConnectorProps } from "src/types";

import styles from "./DeviationStatusStep.module.scss";

const statusStyles: Record<
  Status,
  { icon: string; color: string }
> = {
  completed: {
    icon: stepCompleted,
    color: "#4CAF50",
  },
  active: {
    icon: stepActive,
    color: "#1976D2",
  },
  inactive: {
    icon: stepIncomplete,
    color: "#BDBDBD",
  },
};

const Connector = ({ active }: ConnectorProps) => {
  const connectorClassName = `${styles.connector} ${
    active ? styles.active : ""
  }`;

  return <Box className={connectorClassName} />;
};

const iconClassNames: Record<Status, string> = {
  completed: styles.iconCompleted,
  active: styles.iconActive,
  inactive: styles.iconInactive,
};

const StatusStep = ({ label, status }: StatusStepProps) => {
  const { icon } = statusStyles[status];

  return (
    <Stack
      className={styles.statusStep}
      direction="row"
      spacing={0.5}
      alignItems="center"
    >
      <img src={icon} alt={`${label} icon`} className={iconClassNames[status]} />
      <Typography variant="body2" className={styles.label}>
        {label}
      </Typography>
    </Stack>
  );
};

const DeviationStatusStep = ({ rcaStatus, gradingStatus }: StatusStepsProps) => {
  const connectorActive =
    (rcaStatus === "completed" && gradingStatus !== "inactive") ||
    (rcaStatus === "active" && gradingStatus !== "inactive");

  return (
    <Stack
      className={styles.deviationStatusStep}
      direction="row"
      alignItems="center"
    >
      <StatusStep label="RCA" status={rcaStatus} />
      <Connector active={connectorActive} />
      <StatusStep label="Grading" status={gradingStatus} />
    </Stack>
  );
};

export default DeviationStatusStep;