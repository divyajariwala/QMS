import React from "react";
import { Box, Stack } from "@mui/material";
import styles from "./SCNStatsQuickLinks.module.scss";
// import TotalSCNIcon from "../../assets/icons/totalSCNIcon.svg";
import OpenSCNsIcon from "../../assets/icons/openSCNs.svg";
import SCNsSummaryIcon from "../../assets/icons/summarySCNs.svg";

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
            <Box className={styles.statRow}>
              <span className={`${styles.dot} ${styles.redDot}`} />
              <span className={styles.statLabel}>Supplier Action Required</span>
              <span className={styles.statValue}>
                {stats.supplierActionRequired}
              </span>
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

      {/* Quick Links Card */}
      <Box className={styles.quickLinksCard}>
        <span className={styles.quickLinksTitle}>Quick links</span>
        <ul className={styles.quickLinksList}>
          {quickLinks.map((link, index) => (
            <li key={index}>
              <a href={link.href} className={styles.quickLink}>
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      </Box>
    </Box>
  );
};

export default SCNStatsQuickLinks;
