import React from "react";
import styles from "./StatusTabs.module.scss";

type StatusTabItem = {
  label: string;
  key: "pending" | "processed" | "overdue";
  count?: number;
};

type Props = {
  pending?: number;
  processed?: number;
  overdue?: number;
  active: "pending" | "processed" | "overdue";
  setActive: (val: "pending" | "processed" | "overdue") => void;
  setPageNumber: (val: number) => void;
};

const StatusTabs: React.FC<Props> = ({
  pending,
  processed,
  overdue,
  active,
  setActive,
  setPageNumber,
}) => {
  const statuses: StatusTabItem[] = [
    { label: "Overdue", key: "overdue", count: overdue },
    { label: "Pending", key: "pending", count: pending },
    { label: "Processed", key: "processed", count: processed },
  ];

  return (
    <div className={styles.tabsContainer}>
      <div className={styles.tabs}>
        {statuses.map(({ label, count, key }) => {
          const isActive = key === active;
          return (
            <div
              key={label}
              role="tab"
              tabIndex={isActive ? 0 : -1}
              className={`${styles.tab} ${isActive ? styles.active : ""}`}
              onClick={() => {
                setActive(key);
                setPageNumber(1);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  setActive(key);
                }
              }}
            >
              <div className={styles.tabContent}>
                <span className={styles.label}>{label}</span>
                <span className={isActive ? styles.countActive : styles.count}>
                  {count ?? 0}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StatusTabs;
