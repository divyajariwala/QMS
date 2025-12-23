import React from "react";
import styles from "./StatusCards.module.scss";

import StatusCard from "./StatusCard";
import DeviationsIcon from "../../assets/icons/deviationsCard.svg";
import CycleIcon from "../../assets/icons/cycleTime.svg";
import { deviationStatsProps } from "src/types";
import { formatDays } from "src/helpers";

const DeviationsStatusCard: React.FC<deviationStatsProps> = ({
  deviationStats,
}) => {
  const {
    total_deviations,
    pending,
    processed,
    overdue,
    avg_cycle_time,
    rca_pending,
    rca_done,
    grading_pending,
    grading_done,
    workflow_progress,
  } = deviationStats || {};
  return (
    <div className={styles.cardsContainer}>
      <StatusCard
        iconSrc={DeviationsIcon}
        iconAlt="RCA"
        page="deviations"
        title="Total Deviations"
        cardValue={total_deviations}
        legend={[
          {
            colorClass: "dotPending",
            label: "Pending",
            value: pending as number,
          },
          {
            colorClass: "dotProcessed",
            label: "Processed",
            value: processed as number,
          },
          {
            colorClass: "dotOverdue",
            label: "Overdue",
            value: overdue as number,
          },
        ]}
      />
      <StatusCard
        iconSrc={DeviationsIcon}
        page="deviations"
        iconAlt="RCA"
        title="Workflow Progress"
        cardValue={workflow_progress}
        legend={[
          {
            colorClass: "dotPending",
            label: "RCA Pending",
            value: rca_pending as number,
          },
          {
            colorClass: "dotProcessed",
            label: "RCA Done",
            value: rca_done as number,
          },
          {
            colorClass: "dotPending",
            label: "Grading Pending",
            value: grading_pending as number,
          },
          {
            colorClass: "dotProcessed",
            label: "Grading Done",
            value: grading_done as number,
          },
        ]}
      />

      <StatusCard
        page="deviations"
        iconSrc={CycleIcon}
        iconAlt="Cycle Time"
        title="Cycle Time (Avg)"
        cardValue={formatDays(avg_cycle_time)}
        legend={[{ label: "Avg Time", value: formatDays(avg_cycle_time) }]}
      />
    </div>
  );
};

export default DeviationsStatusCard;
