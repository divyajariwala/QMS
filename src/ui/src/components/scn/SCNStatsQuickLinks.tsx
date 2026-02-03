import React from "react";
import { Box, Stack } from "@mui/material";
import styles from "./SCNStatsQuickLinks.module.scss";
import OpenSCNsIcon from "../../assets/icons/openSCNs.svg";
import SCNsSummaryIcon from "../../assets/icons/summarySCNs.svg";

interface SCNStats {
  total: number;
  pendingReview: number;
  inReview: number;
  supplierActionRequired: number;
  openSCNs: number;
  approved: number;
  rejected: number;
}

interface SCNStatsQuickLinksProps {
  stats: SCNStats;
}

const SCNStatsQuickLinks: React.FC<SCNStatsQuickLinksProps> = ({ stats }) => {
  const quickLinks = [
    { label: "Submission templates", href: "#" },
    { label: "Notification timelines", href: "#" },
    { label: "FAQs", href: "#" },
  ];

  return (
    <Box className={styles.wrapper}>
      {/* Stats Card */}
      <Box className={styles.statsCard}>
        {/* Header: Icon + Total SCNs */}
        <Box className={styles.statsHeader}>
          <Box className={styles.iconWrapper}>
            <img src={SCNsSummaryIcon} />
          </Box>
          <Box className={styles.totalContent}>
            <span className={styles.totalLabel}>SCNs Summary</span>
            <span className={styles.totalValue}>{stats.total}</span>
          </Box>
        </Box>

        {/* Stats Grid - 2 Columns */}
        <Box className={styles.statsGrid}>
          {/* Right Column */}
          <Box className={styles.statsColumn}>
            <Box className={styles.statRow}>
              <span className={styles.statLabel}>Approved</span>
              <span className={styles.statValue}>{stats.approved}</span>
            </Box>
            <Box className={styles.statRow}>
              <span className={styles.statLabel}>Rejected</span>
              <span className={styles.statValue}>{stats.rejected}</span>
            </Box>
          </Box>
        </Box>
      </Box>
      {/* Stats Card */}
      <Box className={styles.statsCard}>
        {/* Header: Icon + Total SCNs */}
        <Box className={styles.statsHeader}>
          <Box className={styles.iconWrapper}>
            {/* <GridIcon /> */}
            {/* <img src={TotalSCNIcon} /> */}
            <img src={OpenSCNsIcon} />
          </Box>
          <Box className={styles.totalContent}>
            <span className={styles.totalLabel}>Open SCNs</span>
            <span className={styles.totalValue}>{stats.total}</span>
          </Box>
        </Box>

        {/* Stats Grid - 2 Columns */}
        <Box className={styles.statsGrid}>
          {/* Left Column */}
          <Box className={styles.statsColumn}>
            <Box className={styles.statRow}>
              <span className={`${styles.dot} ${styles.yellowDot}`} />
              <span className={styles.statLabel}>Pending Review</span>
              <span className={styles.statValue}>{stats.pendingReview}</span>
            </Box>
            <Box className={styles.statRow}>
              <span className={`${styles.dot} ${styles.greenDot}`} />
              <span className={styles.statLabel}>In Review</span>
              <span className={styles.statValue}>{stats.inReview}</span>
            </Box>
            <Box className={styles.statRowLast}>
              <span className={`${styles.dot} ${styles.redDot}`} />
              <span className={styles.statLabel}>Supplier Action Required</span>
              <span className={styles.statValue}>
                {stats.supplierActionRequired}
              </span>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Quick Links Card */}
      <Box className={styles.quickLinksCard}>
        <span className={styles.quickLinksTitle}>Quick links</span>
        <Box className={styles.statsColumn}>
          {quickLinks.map((link, index) => (
            <Box
              className={
                quickLinks.length - 1 === index
                  ? styles.statRowLast
                  : styles.statRow
              }
            >
              <a href={link.href} className={styles.quickLink}>
                {link.label}
              </a>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default SCNStatsQuickLinks;
