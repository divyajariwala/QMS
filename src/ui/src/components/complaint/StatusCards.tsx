import React from "react";
import styles from "./StatusCards.module.scss";
import DeviationsIcon from "../../assets/icons/deviationsCard.svg";
import CycleIcon from "../../assets/icons/cycleTime.svg";

const StatusCards: React.FC = () => {
  return (
    <div className={styles.cardsContainer}>

      {/* Card 2 */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <img src={DeviationsIcon} className={styles.icon} alt="RCA" />
          <div className={styles.headerText}>
            <h3>Total Complaints</h3>
            <div className={styles.cardValue}>14,340</div>
          </div>
        </div>
        <div className={styles.cardLegend}>
          <div className={styles.legendColumn}>
            <div className={styles.legendItem}>
              <span className={styles.dotWithText}>
                <span className={`${styles.dot} ${styles.dotPending}`} />
                <span>Pending</span>
              </span>
              <span className={styles.legendValue}>7,000</span>
            </div>

            <div className={styles.legendItem}>
              <span className={styles.dotWithText}>
                <span className={`${styles.dot} ${styles.dotProcessed}`} />
                <span>Processed</span>
              </span>
              <span className={styles.legendValue}>3,340</span>
            </div>

            <div className={styles.legendItem}>
              <span className={styles.dotWithText}>
                <span className={`${styles.dot} ${styles.dotOverdue}`} />
                <span>Overdue</span>
              </span>
              <span className={styles.legendValue}>4,000</span>
            </div>
          </div>
        </div>
      </div>

      {/* Card 3 */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <img src={CycleIcon} className={styles.icon} alt="Cycle Time" />
          <div className={styles.headerText}>
            <h3>Cycle Time (Avg)</h3>
            <div className={styles.cardValue}>2 Days</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusCards;