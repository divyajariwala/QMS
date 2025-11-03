import React from "react";
import styles from "./StatusTabs.module.scss";

type StatusTabItem = {
  label: string;
  count?: number;
};

type Props = {
  pending?: number;
  processed?: number;
  overdue?: number;
  activeIndex: number;
  setActiveIndex: (val: number) => void;
};

const StatusTabs: React.FC<Props> = ({
  pending,
  processed,
  overdue,
  activeIndex,
  setActiveIndex,
}) => {
  const statuses: StatusTabItem[] = [
    { label: "In Review", count: pending },
    { label: "Overdue", count: overdue },
    { label: "Processed", count: processed },
  ];

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