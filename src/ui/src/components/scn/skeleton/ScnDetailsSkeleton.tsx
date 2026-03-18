import React from "react";
import { Box, Skeleton, Stack } from "@mui/material";

const ScnDetailsSkeleton = () => {
  return (
    <Box>
      <Skeleton width={120} height={20} />
      <Stack direction="row" justifyContent="space-between" mt={1}>
        <Skeleton width={200} height={28} />
        <Skeleton width={70} height={22} />
      </Stack>

      <Stack direction="row" gap={2} mt={2}>
        <Skeleton width={120} height={36} />
        <Skeleton width={140} height={36} />
        <Skeleton width={100} height={36} />
      </Stack>

      <Box mt={3}>
        <Skeleton height={18} width="80%" />
        <Skeleton height={18} width="70%" />
        <Skeleton height={18} width="60%" />
      </Box>

      <Box mt={3}>
        <Skeleton height={140} />
      </Box>
    </Box>
  );
};

export default ScnDetailsSkeleton;
