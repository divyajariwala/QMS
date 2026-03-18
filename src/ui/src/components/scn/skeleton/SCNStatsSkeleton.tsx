import React from "react";
import { Box, Skeleton } from "@mui/material";
import styles from "../SCNStatsQuickLinks.module.scss";

const SCNStatsSkeleton: React.FC = () => {
  return (
    <Box className={styles.wrapper} sx={{ mt: 2, mb: 2 }}>
      {/* Stats Card Skeleton 1 */}
      <Box className={styles.statsCard}>
        <Box className={styles.statsHeader}>
          <Skeleton
            variant="rounded"
            width={53}
            height={53}
            sx={{ borderRadius: "8px" }}
          />
          <Box className={styles.totalContent} sx={{ width: "100%" }}>
            <Skeleton variant="text" width="40%" height={20} />
            <Skeleton variant="text" width="20%" height={40} />
          </Box>
        </Box>
        <Box className={styles.statsGrid}>
          <Box className={styles.statsColumn}>
            <Box className={styles.statRow}>
              <Skeleton variant="text" width="60%" height={24} />
              <Skeleton variant="text" width="10%" height={24} />
            </Box>
            <Box className={styles.statRowLast}>
              <Skeleton variant="text" width="60%" height={24} />
              <Skeleton variant="text" width="10%" height={24} />
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Stats Card Skeleton 2 */}
      <Box className={styles.statsCard}>
        <Box className={styles.statsHeader}>
          <Skeleton
            variant="rounded"
            width={53}
            height={53}
            sx={{ borderRadius: "8px" }}
          />
          <Box className={styles.totalContent} sx={{ width: "100%" }}>
            <Skeleton variant="text" width="40%" height={20} />
            <Skeleton variant="text" width="20%" height={40} />
          </Box>
        </Box>
        <Box className={styles.statsGrid}>
          <Box className={styles.statsColumn}>
            <Box className={styles.statRow}>
              <Skeleton variant="text" width="60%" height={24} />
              <Skeleton variant="text" width="10%" height={24} />
            </Box>
            <Box className={styles.statRowLast}>
              <Skeleton variant="text" width="60%" height={24} />
              <Skeleton variant="text" width="10%" height={24} />
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Quick Links Card Skeleton */}
      <Box className={styles.quickLinksCard}>
        <Skeleton variant="text" width="40%" height={32} sx={{ mb: 3 }} />
        <Box className={styles.statsColumn}>
          {[1, 2, 3].map((i) => (
            <Box
              key={i}
              className={i === 3 ? styles.statRowLast : styles.statRow}
            >
              <Skeleton variant="text" width="70%" height={24} />
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default SCNStatsSkeleton;
