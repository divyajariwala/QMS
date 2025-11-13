import React from "react";
import styles from "./StatusCards.module.scss";

import StatusCard from "./StatusCard";
import DeviationsIcon from "../../assets/icons/deviationsCard.svg";
import CycleIcon from "../../assets/icons/cycleTime.svg";

const DeviationsStatusCard: React.FC = () => {
  return (
    <div className={styles.cardsContainer}>
      <StatusCard
        iconSrc={DeviationsIcon}
        iconAlt="RCA"
        title="Total Deviations"
        cardValue="27,340"
        legend={[
          { colorClass: "dotPending", label: "RCA", value: 14000 },
          { colorClass: "dotOverdue", label: "Grading", value: 13340 },
        ]}
      />

      <StatusCard
        iconSrc={DeviationsIcon}
        iconAlt="RCA"
        title="Total RCA"
        cardValue="14,000"
        legend={[
          { colorClass: "dotPending", label: "Pending", value: "7,000" },
          { colorClass: "dotProcessed", label: "Processed", value: "3,000" },
          { colorClass: "dotOverdue", label: "Overdue", value: "4,000" },
        ]}
      />

      <StatusCard iconSrc={CycleIcon} iconAlt="Cycle Time" title="Cycle Time (Avg)" cardValue="2 Days"
        legend={[{ label: "Avg Time", value: "2 days" }]} />
    </div>
  );
};

export default DeviationsStatusCard;