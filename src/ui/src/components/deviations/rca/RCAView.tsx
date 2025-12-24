import React from "react";
import { Box, Stack, Typography } from "@mui/material";
import RCACategory from "../../../assets/icons/rcaCategory.svg";

import { RcaRecord } from "./RCATypes";
import styles from "./RootCauseAnalysis.module.scss";

const RcaView: React.FC<{ rca: RcaRecord }> = ({ rca }) => (
  <Box className={styles.maxRcaHeight}>
    <div className={styles.rcaTimeline}>
      {rca.sections.map((s) => (
        <Stack
          direction="row"
          alignItems="flex-start"
          className={styles.rcaSection}
        >
          <img
            src={RCACategory}
            alt="RCA Category Icon"
            className={styles.rcaMarker}
          />
          <Stack direction="column" className={styles.rcaSubSection}>
            <Typography variant="h6" className={styles.rcaSectionTitle}>
              {s.title}
            </Typography>
            <Stack
              direction="row"
              alignItems="center"
              justifyContent="space-between"
              sx={{ width: "100%" }}
            >
              <Typography variant="subtitle1" className={styles.rcaSubTitle}>
                {s.value}
              </Typography>
            </Stack>
            {s.explanation && (
              <Box className={styles.rcaExplanation}>
                <Typography
                  variant="subtitle2"
                  className={styles.rcaExplanationTitle}
                >
                  Explanation
                </Typography>
                <Typography variant="body2">{s.explanation}</Typography>
              </Box>
            )}
          </Stack>
        </Stack>
      ))}
    </div>
  </Box>
);

export default RcaView;
