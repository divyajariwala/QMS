import React from "react";
import { Box, Button, Paper, Stack, Typography } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import styles from "./executiveSummary.module.scss";
import { ExecutiveSummaryItem } from "./mockdata";

export interface ExecutiveSummaryProps {
  title?: string;
  items: ExecutiveSummaryItem[];
  onBack: () => void;
  onPrimaryAction?: () => void;
  primaryActionLabel?: string;
}

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  title = "AI Generated Executive Summary",
  items,
  onBack,
  onPrimaryAction,
  primaryActionLabel = "Save and Send",
}) => {
  return (
    <Paper variant="outlined" className={styles.summaryRoot}>
      <Box className={styles.headerRow}>
        <Stack direction="row" spacing={1} alignItems="center">
          <Button
            variant="text"
            startIcon={<ArrowBackIcon />}
            onClick={onBack}
            className={styles.backBtn}
          >
          </Button>
          <Typography variant="h6" className={styles.title}>
            {title}
          </Typography>
        </Stack>
      </Box>

      {/* Content */}
      <Box className={styles.contentBox}>
        {items?.length ? (
          items.map((item, idx) => (
            <Box key={`${item.label}-${idx}`} className={styles.section}>
              <Typography variant="subtitle2" className={styles.sectionLabel}>
                {item.label}
              </Typography>
              <Typography
                variant="body1"
                className={styles.sectionText}
                whiteSpace="pre-line"
              >
                {item.content}
              </Typography>
            </Box>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            No summary available.
          </Typography>
        )}
      </Box>

      {/* Footer actions */}
      <Box className={styles.footerRow}>
        <Stack direction="row" spacing={1} justifyContent="flex-end">
          {onPrimaryAction && (
            <Button
              variant="contained"
              color="primary"
              onClick={onPrimaryAction}
            >
              {primaryActionLabel}
            </Button>
          )}
        </Stack>
      </Box>
    </Paper>
  );
};

export default ExecutiveSummary;

