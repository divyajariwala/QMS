import React from "react";
import { Box, Stack } from "@mui/material";
import styles from "./SCNStatusCard.module.scss";

const GridIcon = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="3" y="3" width="7" height="7" rx="1.5" fill="#6366F1" />
    <rect x="3" y="14" width="7" height="7" rx="1.5" fill="#6366F1" />
    <rect x="14" y="3" width="7" height="7" rx="1.5" fill="#6366F1" />
    <rect x="14" y="14" width="7" height="7" rx="1.5" fill="#6366F1" />
  </svg>
);

interface SCNStats {
  total: number;
  pendingReview: number;
  inReview: number;
  supplierActionRequired: number;
  openSCNs: number;
  approved: number;
  rejected: number;
}

interface SCNStatusCardProps {
  stats: SCNStats;
}

const SCNStatusCard: React.FC<SCNStatusCardProps> = ({ stats }) => {
  return (
    <Box className={styles.statusCard}>
      <Stack direction="row" alignItems="center" gap={3}>
        {/* Total SCNs Section */}
        <Box className={styles.totalSection}>
          <Box className={styles.iconWrapper}>
            <GridIcon />
          </Box>
          <Box className={styles.totalContent}>
            <p className={styles.totalLabel}>Total SCNs</p>
            <p className={styles.totalValue}>{stats.total}</p>
          </Box>
        </Box>

        {/* Divider */}
        <Box className={styles.divider} />

        {/* Stats Grid - Two Columns */}
        <Stack direction="row" gap={6} className={styles.statsGrid}>
          {/* Left Column */}
          <Box className={styles.statsColumn}>
            <Box className={styles.statItem}>
              <span className={`${styles.dot} ${styles.blueDot}`}></span>
              <span className={styles.statLabel}>Pending Review</span>
              <span className={styles.statValue}>{stats.pendingReview}</span>
            </Box>
            <Box className={styles.statItem}>
              <span className={`${styles.dot} ${styles.orangeDot}`}></span>
              <span className={styles.statLabel}>In Review</span>
              <span className={styles.statValue}>{stats.inReview}</span>
            </Box>
            <Box className={styles.statItem}>
              <span className={`${styles.dot} ${styles.redDot}`}></span>
              <span className={styles.statLabel}>Supplier Action Required</span>
              <span className={styles.statValue}>
                {stats.supplierActionRequired}
              </span>
            </Box>
          </Box>

          {/* Right Column */}
          <Box className={styles.statsColumn}>
            <Box className={styles.statItem}>
              <span className={`${styles.dot} ${styles.yellowDot}`}></span>
              <span className={styles.statLabel}>Open SCNs</span>
              <span className={styles.statValue}>{stats.openSCNs}</span>
            </Box>
            <Box className={styles.statItem}>
              <span className={`${styles.dot} ${styles.greenDot}`}></span>
              <span className={styles.statLabel}>Approved</span>
              <span className={styles.statValue}>{stats.approved}</span>
            </Box>
            <Box className={styles.statItem}>
              <span className={`${styles.dot} ${styles.grayDot}`}></span>
              <span className={styles.statLabel}>Rejected</span>
              <span className={styles.statValue}>{stats.rejected}</span>
            </Box>
          </Box>
        </Stack>
      </Stack>
    </Box>
  );
};

export default SCNStatusCard;
