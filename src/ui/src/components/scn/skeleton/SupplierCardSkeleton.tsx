import React from "react";
import { Box, Stack, Skeleton } from "@mui/material";

const SupplierCardSkeleton: React.FC = () => {
  return (
    <>
      <Box
        sx={{
          p: 2,
          border: "1px solid #E5E7EB",
          borderRadius: "10px",
          background: "#fff",
        }}
      >
        <Stack direction="row" justifyContent="space-between" mb={1.5}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Skeleton variant="rounded" width={90} height={22} />
            <Skeleton variant="text" width={110} height={22} />
          </Stack>
          <Skeleton variant="rounded" width={70} height={22} />
        </Stack>
        <Stack direction="row" spacing={4} mb={0.5}>
          {[120, 100, 140, 130].map((w, i) => (
            <Box key={i}>
              <Skeleton variant="text" width={80} height={14} />
              <Skeleton variant="text" width={w} height={18} />
            </Box>
          ))}
        </Stack>
        <Skeleton variant="text" width="70%" height={14} sx={{ mt: 1 }} />
      </Box>
    </>
  );
};

export default SupplierCardSkeleton;
