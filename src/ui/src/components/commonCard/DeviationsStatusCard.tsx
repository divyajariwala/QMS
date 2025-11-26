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
         page="deviations"
        title="Total Deviations"
        cardValue="15,340"
        legend={[
          { colorClass: "dotPending", label: "Pending", value: "10,000" },
          { colorClass: "dotProcessed", label: "Processed", value: "4,000" },
          { colorClass: "dotOverdue", label: "Overdue", value: "1,340" },
        ]}
      />
      <StatusCard
        iconSrc={DeviationsIcon}
        page="deviations"
        iconAlt="RCA"
        title="Total Deviations"
        cardValue="27,340"
        legend={[
          { colorClass: "dotPending", label: "RCA Pending", value: 14000 },
          { colorClass: "dotProcessed", label: "RCA Done", value: 13340 },
          { colorClass: "dotOverdue", label: "Grading Pending", value: 13340 },
        ]}
      />

      <StatusCard  page="deviations" iconSrc={CycleIcon} iconAlt="Cycle Time" title="Cycle Time (Avg)" cardValue="2 Days"
        legend={[{ label: "Avg Time", value: "2 days" }]} />
    </div>
  );
};

export default DeviationsStatusCard;