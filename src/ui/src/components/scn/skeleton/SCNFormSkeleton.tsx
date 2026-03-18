import React from "react";
import { Box, Stack, Skeleton } from "@mui/material";

const FieldSkeleton = ({ fullWidth = false }: { fullWidth?: boolean }) => (
  <Box sx={{ flex: 1 }}>
    <Skeleton width={120} height={18} />
    <Skeleton
      variant="rectangular"
      height={40}
      sx={{ mt: 1, borderRadius: 1 }}
      width={fullWidth ? "100%" : undefined}
    />
  </Box>
);

const TextAreaSkeleton = () => (
  <Box>
    <Skeleton width={180} height={18} />
    <Skeleton
      variant="rectangular"
      height={100}
      sx={{ mt: 1, borderRadius: 1 }}
    />
  </Box>
);

const SectionTitleSkeleton = () => (
  <Skeleton width={200} height={28} />
);

const DividerSkeleton = () => (
  <Skeleton height={1} width="100%" sx={{ my: 2 }} />
);

const SCNFormSkeleton: React.FC = () => {
  return (
    <Box
      sx={{
        background: "#fff",
        border: "1px solid #e3e3e3",
        borderRadius: 2,
        p: 3,
        display: "flex",
        flexDirection: "column",
        gap: 3,
      }}
    >
      {/* SCN Identification */}
      <Box>
        <Stack direction="row" justifyContent="space-between">
          <SectionTitleSkeleton />
          <Skeleton width={80} height={32} />
        </Stack>

        <Stack direction="row" spacing={4} mt={2}>
          <FieldSkeleton />
          <FieldSkeleton />
        </Stack>

        <Stack direction="row" spacing={4} mt={3}>
          <FieldSkeleton />
          <FieldSkeleton />
        </Stack>
      </Box>

      {/* Current State */}
      <Box>
        <SectionTitleSkeleton />
        <TextAreaSkeleton />
      </Box>

      {/* Proposed State */}
      <TextAreaSkeleton />

      {/* Justification */}
      <TextAreaSkeleton />

      {/* Radio / Impact Section */}
      <Box>
        <Stack direction="row" spacing={4}>
          <Box sx={{ flex: 1 }}>
            <Skeleton width={160} height={18} />
            <Stack direction="row" spacing={2} mt={1}>
              <Skeleton width={60} height={24} />
              <Skeleton width={60} height={24} />
            </Stack>
          </Box>

          <Box sx={{ flex: 1 }}>
            <Skeleton width={200} height={18} />
            <Stack direction="row" spacing={2} mt={1}>
              <Skeleton width={100} height={24} />
              <Skeleton width={100} height={24} />
            </Stack>
          </Box>
        </Stack>

        <Stack direction="row" spacing={4} mt={3}>
          <Box sx={{ flex: 1 }}>
            <Skeleton width={120} height={18} />
            <Stack direction="row" spacing={2} mt={1}>
              <Skeleton width={60} height={24} />
              <Skeleton width={80} height={24} />
              <Skeleton width={60} height={24} />
            </Stack>
          </Box>

          <FieldSkeleton />
        </Stack>

        <Stack direction="row" spacing={4} mt={3}>
          <FieldSkeleton />
          <Box sx={{ flex: 1 }} />
        </Stack>
      </Box>

      <DividerSkeleton />

      {/* Change Timing */}
      <Box>
        <SectionTitleSkeleton />
        <Stack direction="row" spacing={4} mt={2}>
          <FieldSkeleton />
          <FieldSkeleton />
        </Stack>
      </Box>

      <DividerSkeleton />

      {/* Materials */}
      <Box>
        <SectionTitleSkeleton />
        <FieldSkeleton fullWidth />
      </Box>

      {/* Attachments */}
      <Box>
        <SectionTitleSkeleton />
        <Skeleton
          variant="rectangular"
          height={200}
          sx={{ borderRadius: 1, mt: 2 }}
        />

        <Box mt={3}>
          <Skeleton width={120} height={18} />
          <Stack spacing={2} mt={2}>
            {[1, 2].map((i) => (
              <Skeleton
                key={i}
                variant="rectangular"
                height={64}
                sx={{ borderRadius: 1 }}
              />
            ))}
          </Stack>
        </Box>
      </Box>
    </Box>
  );
};

export default SCNFormSkeleton;
