import React from "react";
import styles from "./StatusCards.module.scss";

interface LegendItemProps {
  colorClass: "dotPending" | "dotProcessed" | "dotOverdue" | undefined;
  label: string;
  value: string | number;
}

const LegendItem: React.FC<LegendItemProps> = ({ colorClass, label, value }) => {
  return (
    <div className={styles.legendItem}>
      <span className={styles.dotWithText}>
        <span className={colorClass && `${styles.dot} ${styles[colorClass]}`} />
        <span>{label}</span>
      </span>
      <span className={styles.legendValue}>{value}</span>
    </div>
  );
};

export default LegendItem;