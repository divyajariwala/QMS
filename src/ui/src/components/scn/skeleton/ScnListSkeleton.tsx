import React from "react";
import { Box, Skeleton, Stack } from "@mui/material";
import styles from "../SCNInternalReview.module.scss";

const ScnListSkeleton: React.FC<{ count?: number }> = ({ count = 6 }) => {
  return (
    <Stack className={styles.queueList} gap={2}>
      {Array.from({ length: count }).map((_, i) => (
        <Box key={i} className={styles.queueCard}>
          <Skeleton width={80} height={16} />
          <Stack direction="row" justifyContent="space-between">
            <Skeleton width={160} height={24} />
            <Skeleton width={60} height={22} />
          </Stack>
          <Skeleton width="70%" height={20} />
          <Skeleton width="100%" height={6} />
          <Skeleton width="60%" height={16} />
        </Box>
      ))}
    </Stack>
  );
};

export default ScnListSkeleton;
