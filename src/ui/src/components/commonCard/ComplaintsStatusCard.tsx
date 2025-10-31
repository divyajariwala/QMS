import React from "react";
import styles from "./StatusCards.module.scss";

import StatusCard from "./StatusCard";
import DeviationsIcon from "../../assets/icons/deviationsCard.svg";
import CycleIcon from "../../assets/icons/cycleTime.svg";

const ComplaintsStatusCard: React.FC = () => {
  return (
    <div className={styles.cardsContainer}>
      <StatusCard
        iconSrc={DeviationsIcon}
        iconAlt="RCA"
        title="Total Complaints"
        cardValue="27,340"
        legend={[
          { colorClass: "dotPending", label: "Pending", value: "14,000" },
          { colorClass: "dotProcessed", label: "Processed", value: "7,123" },
          { colorClass: "dotOverdue", label: "Overdue", value: "2,000" },
        ]}
      />

      <StatusCard iconSrc={CycleIcon} iconAlt="Cycle Time" title="Cycle Time (Avg)" cardValue="2 Days" legend={[
        { label: "Best Time", value: "6hrs" },
        { label: "Avg Time", value: "2 days" },
        { label: "Longest Time", value: "7 days" },
      ]} />
    </div>
  );
};

export default ComplaintsStatusCard;