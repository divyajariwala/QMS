import React from "react";
import { Box, Divider, Paper, Stack, Typography } from "@mui/material";
import LeftArrow from "../../../assets/icons/leftArrow.svg";
import AISummary from "../../../assets/icons/aiSummary.svg";

import styles from "./executiveSummary.module.scss";
import { ExecutiveSummaryItem } from "./mockdata";

export interface ExecutiveSummaryProps {
  items: ExecutiveSummaryItem[];
  onBack: () => void;
  onPrimaryAction?: () => void;
}

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  items,
  onBack,
  onPrimaryAction,
}) => {
  return (
    <Paper variant="outlined" className={styles.summaryRoot}>
      <Box className={styles.headerRow}>
        <Stack direction="row" spacing={1} alignItems="center">
          <img
            src={LeftArrow}
            alt={"left arrow"}
            onClick={onBack}
            className={styles.backIcon}
          />
          <Typography variant="h6" className={styles.title}>
            <img src={AISummary} alt={"left arrow"} />
            AI Generated Executive Summary
          </Typography>
        </Stack>
      </Box>
      <Divider className={styles.headerDivider} />

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
      <Divider className={styles.headerDivider} />

      {/* Footer actions */}
      <Box>
        <Stack direction="row" spacing={1} className={styles.footerRow}>
          {onPrimaryAction && (
            <button className={styles.classifyBtn} onClick={onPrimaryAction}>
              Save and Send to QMS
            </button>
          )}
        </Stack>
      </Box>
    </Paper>
  );
};

export default ExecutiveSummary;
