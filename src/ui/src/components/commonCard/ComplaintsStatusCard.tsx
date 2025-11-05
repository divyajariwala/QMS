import React from "react";
import styles from "./StatusCards.module.scss";

import StatusCard from "./StatusCard";
import { formatHoursToDays } from "src/helpers"
import { complaintStatsProps } from "src/types";
import DeviationsIcon from "../../assets/icons/deviationsCard.svg";
import CycleIcon from "../../assets/icons/cycleTime.svg";

const ComplaintsStatusCard: React.FC<complaintStatsProps> = ({ complaintStats }) => {
  const { total_complaints, pending, processed, overdue, avg_cycle_time,
    best_time, longest_time } = complaintStats || {}
  return (
    <div className={styles.cardsContainer}>
      <StatusCard
        iconSrc={DeviationsIcon}
        iconAlt="RCA"
        title="Total Complaints"
        cardValue={total_complaints}
        legend={[
          { colorClass: "dotPending", label: "Pending", value: pending as number },
          { colorClass: "dotProcessed", label: "Processed", value: processed as number },
          { colorClass: "dotOverdue", label: "Overdue", value: overdue as number },
        ]}
      />

      <StatusCard iconSrc={CycleIcon} iconAlt="Cycle Time" title="Cycle Time (Avg)" cardValue={formatHoursToDays(avg_cycle_time)} legend={[
        { label: "Best Time", value: formatHoursToDays(best_time) },
        { label: "Avg Time", value: formatHoursToDays(avg_cycle_time) },
        { label: "Longest Time", value: formatHoursToDays(longest_time) },
      ]} />
    </div>
  );
};

export default ComplaintsStatusCard;