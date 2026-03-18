import React from "react";
import { Box, Stack, Skeleton } from "@mui/material";

const SCNImpactTabSkeleton: React.FC = () => {
  return (
    <>
      {/* Action buttons row */}
      <Stack direction="row" gap={1.5} justifyContent="flex-end" mb={3} mt={1}>
        <Skeleton
          variant="rectangular"
          width={160}
          height={36}
          sx={{ borderRadius: 1 }}
        />
        <Skeleton
          variant="rectangular"
          width={100}
          height={36}
          sx={{ borderRadius: 1 }}
        />
        <Skeleton
          variant="rectangular"
          width={110}
          height={36}
          sx={{ borderRadius: 1 }}
        />
      </Stack>

      {/* AI Summary card */}
      <Box
        sx={{
          border: "1px solid #e3e3e3",
          borderRadius: 2,
          p: 2.5,
          mb: 2,
        }}
      >
        {/* Header */}
        <Stack direction="row" alignItems="center" gap={1} mb={1.5}>
          <Skeleton variant="circular" width={22} height={22} />
          <Skeleton width={100} height={24} />
        </Stack>

        {/* Summary text lines */}
        <Skeleton width="100%" height={16} sx={{ mb: 0.5 }} />
        <Skeleton width="95%" height={16} sx={{ mb: 0.5 }} />
        <Skeleton width="80%" height={16} sx={{ mb: 2 }} />

        {/* Chips */}
        <Stack direction="row" gap={1.5} flexWrap="wrap">
          <Skeleton
            variant="rectangular"
            width={160}
            height={32}
            sx={{ borderRadius: 4 }}
          />
          <Skeleton
            variant="rectangular"
            width={130}
            height={32}
            sx={{ borderRadius: 4 }}
          />
          <Skeleton
            variant="rectangular"
            width={180}
            height={32}
            sx={{ borderRadius: 4 }}
          />
        </Stack>
      </Box>

      {/* SCN Predicted Output toggle */}
      <Box mt={3}>
        <Stack direction="row" alignItems="center" gap={2} mb={1}>
          <Skeleton width={160} height={18} />
          <Skeleton width={90} height={22} sx={{ borderRadius: 4 }} />
        </Stack>
        <Skeleton
          variant="rectangular"
          width={160}
          height={36}
          sx={{ borderRadius: 1 }}
        />
      </Box>

      {/* Assessment Summary */}
      <Box mt={4}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          mb={1}
        >
          <Skeleton width={180} height={26} />
          <Skeleton
            variant="rectangular"
            width={80}
            height={32}
            sx={{ borderRadius: 1 }}
          />
        </Stack>
        <Skeleton width={320} height={16} sx={{ mb: 2 }} />

        {/* Change Control Summary sub-section */}
        <Skeleton width={200} height={20} sx={{ mb: 2 }} />
        <Stack direction="row" spacing={8}>
          <Box>
            <Skeleton width={180} height={16} sx={{ mb: 1 }} />
            <Stack direction="row" spacing={3}>
              <Skeleton width={50} height={22} />
              <Skeleton width={50} height={22} />
            </Stack>
          </Box>
          <Box flex={1} maxWidth={400}>
            <Skeleton width={140} height={16} sx={{ mb: 1 }} />
            <Skeleton
              variant="rectangular"
              height={40}
              sx={{ borderRadius: 1 }}
            />
          </Box>
        </Stack>
      </Box>

      {/* SCN Summary */}
      <Box mt={4}>
        <Skeleton width={140} height={26} sx={{ mb: 2 }} />
        <Stack direction="row" spacing={8}>
          <Box flex={1}>
            <Skeleton width={100} height={16} sx={{ mb: 1 }} />
            <Skeleton
              variant="rectangular"
              height={40}
              sx={{ borderRadius: 1 }}
            />
          </Box>
          <Box flex={1}>
            <Skeleton width={150} height={16} sx={{ mb: 1 }} />
            <Stack direction="row" spacing={2} mt={0.5}>
              <Skeleton width={65} height={22} />
              <Skeleton width={85} height={22} />
              <Skeleton width={65} height={22} />
            </Stack>
          </Box>
        </Stack>
        <Box mt={3}>
          <Skeleton width={140} height={16} sx={{ mb: 1 }} />
          <Skeleton
            variant="rectangular"
            height={88}
            sx={{ borderRadius: 1 }}
          />
        </Box>
      </Box>

      {/* Assign section */}
      <Box mt={4}>
        <Skeleton width={80} height={26} sx={{ mb: 2 }} />
        <Skeleton width={120} height={16} sx={{ mb: 1.5 }} />
        <Stack direction="row" gap={1} flexWrap="wrap">
          {[100, 140, 120, 110, 80, 90].map((w, i) => (
            <Skeleton
              key={i}
              variant="rectangular"
              width={w}
              height={32}
              sx={{ borderRadius: 4 }}
            />
          ))}
        </Stack>
      </Box>
    </>
  );
};

export default SCNImpactTabSkeleton;
