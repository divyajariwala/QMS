import React from "react";
import { Typography, Stack, Box } from "@mui/material";

import stepActive from "../../assets/icons/stepActive.svg";
import stepCompleted from "../../assets/icons/stepCompleted.svg";
import stepIncomplete from "../../assets/icons/stepIncomplete.svg";

import styles from "./DeviationStatusStep.module.scss";

type Status = "completed" | "active" | "inactive";

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

interface ConnectorProps {
  active: boolean;
}

const Connector = ({ active }: ConnectorProps) => {
  const connectorClassName = `${styles.connector} ${
    active ? styles.active : ""
  }`;

  return <Box className={connectorClassName} />;
};

interface StatusStepProps {
  label: string;
  status: Status;
}

const StatusStep = ({ label, status }: StatusStepProps) => {
  const { icon, color } = statusStyles[status];

  return (
    <Stack
      className={styles.statusStep}
      direction="row"
      spacing={0.5}
      alignItems="center"
    >
      <img
        src={icon}
        alt={`${label} icon`}
        style={{ filter: `drop-shadow(0 0 0 ${color})` }}
      />
      <Typography variant="body2" className={styles.label}>
        {label}
      </Typography>
    </Stack>
  );
};

interface StatusStepsProps {
  rcaStatus: Status;
  gradingStatus: Status;
}

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