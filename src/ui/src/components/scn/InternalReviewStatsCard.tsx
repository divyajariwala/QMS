import React from "react";
import styles from "./InternalReviewStatsCard.module.scss";

export interface DashboardLegendItem {
  color: string;
  label: string;
  value: number | string;
}

export interface InternalReviewStatsCardProps {
  title: string;
  value?: number | string;
  chartComponent: React.ReactNode;
  legendItems?: DashboardLegendItem[];
  icon?: React.ReactNode;
  onLegendItemClick?: (item: DashboardLegendItem) => void;
}

const InternalReviewStatsCard: React.FC<InternalReviewStatsCardProps> = ({
  title,
  value,
  chartComponent,
  legendItems,
  icon,
  onLegendItemClick,
}) => {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div>
          <h3>{title}</h3>
          {value !== undefined && (
            <div className={styles.cardValue}>{value}</div>
          )}
        </div>
        <div className={styles.iconContainer}>{icon}</div>
      </div>

      <div className={styles.cardBody}>
        <div className={styles.chartContainer}>{chartComponent}</div>

        {legendItems && legendItems.length > 0 && (
          <div className={styles.legendContainer}>
            {legendItems.map((item, index) => (
              <div
                key={index}
                className={styles.legendItem}
                onClick={() => onLegendItemClick?.(item)}
                style={{ cursor: onLegendItemClick ? "pointer" : "default" }}
              >
                <div className={styles.legendDotGroup}>
                  <div
                    className={styles.dot}
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <div className={styles.legendLabel}>{item.label}</div>
                </div>
                <div className={styles.legendValue}>{item.value}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default InternalReviewStatsCard;
