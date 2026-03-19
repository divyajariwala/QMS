import React from "react";
import { Box, Stack, LinearProgress } from "@mui/material";
import styles from "./SCNStatsQuickLinks.module.scss";
import ArrowRightIcon from "../../assets/icons/arrowRightGray.svg";
import DonutChart from "../charts/DonutChart";
import SCNsSummaryIcon from "../../assets/icons/trendingFileIconOrg.svg";
import SCNsFileIcon from "../../assets/icons/fileIconOrg.svg";
import LinkIcon from "../../assets/icons/hyperlinkIconOrg.svg";

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
      {/* Total SCNs Card */}
      <Box className={styles.statsCard}>
        <Box className={styles.statsHeader}>
          <Box className={styles.totalContent}>
            <span className={styles.totalLabel}>Reviewed SCNs</span>
            <span className={styles.totalValue}>
              {stats.approved + stats.rejected}
            </span>
          </Box>
          <Box className={styles.iconWrapper}>
            <img src={SCNsSummaryIcon} alt="Total SCNs" />
          </Box>
        </Box>

        <Box className={styles.progressSection}>
          <Box className={styles.progressRow}>
            <Box className={styles.progressLabels}>
              <span className={styles.progressLabel}>Approved</span>
              <span className={styles.progressValue}>{stats.approved}</span>
            </Box>
            <LinearProgress
              variant="determinate"
              value={stats.total ? (stats.approved / stats.total) * 100 : 0}
              className={styles.progressBar}
              classes={{
                colorPrimary: styles.progressTrack,
                bar: styles.progressFill,
              }}
            />
          </Box>
          <Box className={styles.progressRow}>
            <Box className={styles.progressLabels}>
              <span className={styles.progressLabel}>Rejected</span>
              <span className={styles.progressValue}>{stats.rejected}</span>
            </Box>
            <LinearProgress
              variant="determinate"
              className={styles.progressBar}
              classes={{
                colorPrimary: styles.progressTrack,
                bar: styles.progressFillYellow,
              }}
              value={stats.total ? (stats.rejected / stats.total) * 100 : 0}
            />
          </Box>
        </Box>
      </Box>

      {/* Open SCNs Card */}
      <Box className={styles.statsCard}>
        <Box className={styles.statsHeader}>
          <Box className={styles.totalContent}>
            <span className={styles.totalLabel}>Open SCNs</span>
            <span className={styles.totalValue}>
              {stats.openSCNs || stats.pendingReview + stats.inReview}
            </span>
          </Box>
          <Box className={styles.iconWrapper}>
            <img src={SCNsFileIcon} alt="Open SCNs" />
          </Box>
        </Box>

        <Box className={styles.statsGrid}>
          <Box className={styles.chartWrapper}>
            <DonutChart
              data={[
                { name: "Pending Review", value: stats.pendingReview },
                { name: "In Review", value: stats.inReview },
              ]}
              colors={["#eeeff1", "#ff7219"]}
              innerRadius={0}
              outerRadius={35}
            />
          </Box>
          <Box className={styles.legendColumn}>
            <Box className={styles.statRow}>
              <Stack direction="row" spacing={1} alignItems="center">
                <span className={`${styles.dot} ${styles.greyDot}`} />
                <span className={styles.statLabel}>Pending Review</span>
              </Stack>
              <span className={styles.statValue}>{stats.pendingReview}</span>
            </Box>
            <Box className={styles.statRowLast}>
              <Stack direction="row" spacing={1} alignItems="center">
                <span className={`${styles.dot} ${styles.orangeDot}`} />
                <span className={styles.statLabel}>In Review</span>
              </Stack>
              <span className={styles.statValue}>{stats.inReview}</span>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Quick Links Card */}
      <Box className={styles.statsCard}>
        <Box className={styles.statsHeader}>
          <Box className={styles.totalContent}>
            <span className={styles.totalLabel}>Quick links</span>
            <span className={styles.totalValue}>{quickLinks.length}</span>
          </Box>
          <Box className={styles.iconWrapper}>
            <img src={LinkIcon} alt="Link" />
          </Box>
        </Box>

        <Box className={styles.linksColumn}>
          {quickLinks.map((link, index) => (
            <Box
              key={index}
              className={
                quickLinks.length - 1 === index
                  ? styles.linkRowLast
                  : styles.linkRow
              }
            >
              <a href={link.href} className={styles.quickLink}>
                {link.label}
              </a>
              <img
                src={ArrowRightIcon}
                alt="Arrow Right"
                className={styles.arrowIcon}
              />
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default SCNStatsQuickLinks;
