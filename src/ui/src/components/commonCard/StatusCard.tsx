import React from "react";
import styles from "./StatusCards.module.scss";
import LegendItem from "./LegendItem";

interface LegendData {
  colorClass?: "dotPending" | "dotProcessed" | "dotOverdue";
  label: string;
  value: string | number;
}

interface StatusCardProps {
  iconSrc: string;
  iconAlt: string;
  title: string;
  cardValue: string | number;
  legend?: LegendData[];
}

const StatusCard: React.FC<StatusCardProps> = ({ iconSrc, iconAlt, title, cardValue, legend }) => {
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
        <div className={styles.cardLegend}>
          <div className={styles.legendColumn}>
            {legend.map(({ colorClass, label, value }) => (
              <LegendItem key={label} colorClass={colorClass} label={label} value={value} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusCard;