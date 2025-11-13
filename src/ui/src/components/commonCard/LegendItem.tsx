import React from "react";
import { LegendItemProps } from "src/types";
import styles from "./StatusCards.module.scss";

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