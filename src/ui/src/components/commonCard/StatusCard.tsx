import React from "react";
import { StatusCardProps } from "src/types";
import styles from "./StatusCards.module.scss";
import LegendItem from "./LegendItem";

const StatusCard: React.FC<StatusCardProps> = ({ iconSrc, iconAlt, title, cardValue, legend, page }) => {
  return (
    <div className={styles.card}>
      <div className={styles.cardInfo}>
        <div className={styles.cardHeader}>
          <img src={iconSrc} className={styles.icon} alt={iconAlt} />
          <div>
            <h3>{title}</h3>
            <div className={styles.cardValue}>{cardValue}</div>
          </div>
        </div>
      </div>

      {legend && (      
          <div className={page === "complaints" ? styles.legendColumnComplaints : styles.legendColumnDeviations}>
            {legend.map(({ colorClass, label, value }) => (
              <LegendItem key={label} colorClass={colorClass} label={label} value={value}/>
            ))}
        </div>
      )}
    </div>
  );
};

export default StatusCard;