import React, { useState } from "react";
import { statuses } from "../../mockData/mockData"
import styles from "./StatusTabs.module.scss";

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
              tabIndex={isActive ? 0 : -1}
              className={`${styles.tab} ${isActive ? styles.active : ""}`}
              onClick={() => setActiveIndex(index)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  setActiveIndex(index);
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