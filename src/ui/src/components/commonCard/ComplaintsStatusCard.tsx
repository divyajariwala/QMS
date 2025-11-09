import React from "react";
import styles from "./StatusCards.module.scss";
import DeviationsIcon from "../../assets/icons/container.svg";
import CycleIcon from "../../assets/icons/cycleTime.svg";
import { complaintStatsProps } from "src/types";
import { formatHoursToDays } from "src/helpers";
import DonutChart from "./DonutChart";

const ComplaintsStatusCard: React.FC<complaintStatsProps> = ({ complaintStats }) => {
  const {
    total_complaints = 0,
    pending = 0,
    processed = 0,
    overdue = 0,
    avg_cycle_time = 0,
    longest_time = 0,
  } = complaintStats || {};

  const safePercent = (v: number, total: number) => (total > 0 ? (v / total) * 100 : 0);
  const pendingPercent = safePercent(pending, total_complaints);
  const processedPercent = safePercent(processed, total_complaints);
  const overduePercent = safePercent(overdue, total_complaints);
  const cycleTimeChangePercent = 12;

  return (
    <div className={styles.cardsContainer}>
      <div className={styles.totalComplaintsCard}>
        <div className={styles.leftSectionComplaints}>
          <div className={styles.iconWrapper}>
            <img src={DeviationsIcon} alt="Total Complaints Icon" />
          </div>

          <div className={styles.totalContent}>
            <div className={styles.title}>Total Complaints</div>
            <div className={styles.totalValue}>{total_complaints.toLocaleString()}</div>

            {/* NEW flex row: progress + donut */}
            <div className={styles.metricsRow}>
              <div className={styles.progressGroup}>
                <div className={styles.progressItem}>
                  <div className={styles.labelRow}>
                    <span className={`${styles.dot} ${styles.dotPending}`} />
                    <span>Pending</span>
                    <span className={styles.value}>{pending.toLocaleString()}</span>
                    <span className={styles.progressPercent}>{pendingPercent.toFixed(0)}%</span>
                  </div>
                  <div className={styles.progressBarBackground}>
                    <div className={styles.progressBar} style={{ width: `${pendingPercent}%`, backgroundColor: "#155DFC" }} />
                  </div>
                </div>

                <div className={styles.progressItem}>
                  <div className={styles.labelRow}>
                    <span className={`${styles.dot} ${styles.dotProcessed}`} />
                    <span>Processed</span>
                    <span className={styles.value}>{processed.toLocaleString()}</span>
                    <span className={styles.progressPercent}>{processedPercent.toFixed(0)}%</span>
                  </div>
                  <div className={styles.progressBarBackground}>
                    <div className={styles.progressBar} style={{ width: `${processedPercent}%`, backgroundColor: "#00A63E" }} />
                  </div>
                </div>

                <div className={styles.progressItem}>
                  <div className={styles.labelRow}>
                    <span className={`${styles.dot} ${styles.dotOverdue}`} />
                    <span>Overdue</span>
                    <span className={styles.value}>{overdue.toLocaleString()}</span>
                    <span className={styles.progressPercent}>{overduePercent.toFixed(0)}%</span>
                  </div>
                  <div className={styles.progressBarBackground}>
                    <div className={styles.progressBar} style={{ width: `${overduePercent}%`, backgroundColor: "#E7000B" }} />
                  </div>
                </div>
              </div>
            </div>
            {/* END metricsRow */}
          </div>
        </div>
        <div className={styles.donutContainer}>
          <DonutChart
            data={[pending, processed, overdue]}
            colors={["#155DFC", "#00A63E", "#E7000B"]}
            total={total_complaints}
            width={140}
            height={140}
          />
        </div>
      </div>

      <div className={styles.cycleTimeCard}>
        <div className={styles.leftSectionCycleTime}>
          <div className={styles.iconWrapperWhite}>
            <img src={CycleIcon} alt="Cycle Time Icon" />
          </div>

          <div className={styles.cycleContent}>
            <div className={styles.titleWhite}>Cycle Time (Avg)</div>
            <div className={styles.cycleValue}>
              {formatHoursToDays(avg_cycle_time)}
              <span className={styles.cycleChange}>↑ {cycleTimeChangePercent}%</span>
            </div>

            <div className={styles.cycleDetails}>
              <div>
                <div className={styles.cycleDetailsFirst}>Avg Time</div>
                <div className={styles.cycleDetailsSecond}>{formatHoursToDays(avg_cycle_time)}</div>
              </div>
              <div>
                <div className={styles.cycleDetailsFirst}>Longest Time</div>
                <div className={styles.cycleDetailsSecond}>{formatHoursToDays(longest_time)}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComplaintsStatusCard;