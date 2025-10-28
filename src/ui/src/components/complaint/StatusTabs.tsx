import React, { useState } from "react";
import styles from "./StatusTabs.module.scss";

interface Status {
  label: string;
  count: number;
  description: React.ReactNode;
}

const statuses: Status[] = [
  { label: "In Review", count: 14000, description: "Details for In Review." },
  { label: "Overdue", count: 2000, description: "Details for Overdue." },
  { label: "Processed", count: 7123, description: "Details for Processed." },
];

const StatusTabs: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <div className={styles.tabsContainer}>
      <div className={styles.tabs}>
        {statuses.map(({ label, count }, index) => {
          const isActive = index === activeIndex;
          return (
            <div
              key={label}
              role="tab"
              aria-selected={isActive}
              tabIndex={isActive ? 0 : -1}
              className={styles.tab}
              onClick={() => setActiveIndex(index)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  setActiveIndex(index);
                }
              }}
            >
              <div className={`${styles.tabContent} ${isActive ? styles.active : ""}`}>
                <span className={styles.label}>{label}</span>
                <span className={isActive ? styles.countActive : styles.count}>
                  {count.toLocaleString()}
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