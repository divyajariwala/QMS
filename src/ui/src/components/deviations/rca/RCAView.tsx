import React, { useState, useMemo } from "react";
import { Box, Stack, Typography, Button } from "@mui/material";
import RCACategory from "../../../assets/icons/rcaCategory.svg";

import { RcaRecord } from "./RCATypes";
import styles from "./RootCauseAnalysis.module.scss";

const CHAR_LIMIT = 100;

const RcaView: React.FC<{ rca: RcaRecord }> = ({ rca }) => {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const toggleExpand = (idx: number) => {
    setExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const truncateAtWord = (text: string, limit: number) => {
    if (text.length <= limit) return text;
    const cut = text.slice(0, limit);
    const lastSpace = cut.lastIndexOf(" ");
    const safeCut = lastSpace > 0 ? cut.slice(0, lastSpace) : cut;
    return `${safeCut}…`;
  };

  return (
    <Box className={styles.maxRcaHeight}>
      <div className={styles.rcaTimeline}>
        {rca.sections.map((s, idx) => {
          const hasExplanation = !!s.explanation;
          const needsToggle =
            hasExplanation && s.explanation!.length > CHAR_LIMIT;

          const displayText = useMemo(() => {
            if (!hasExplanation) return "";
            if (expanded[idx] || !needsToggle) return s.explanation!;
            return truncateAtWord(s.explanation!, CHAR_LIMIT);
          }, [hasExplanation, needsToggle, expanded[idx], s.explanation]);

          return (
            <Stack
              key={idx}
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
                  <Typography
                    variant="subtitle1"
                    className={styles.rcaSubTitle}
                  >
                    {s.value}
                  </Typography>
                </Stack>
                {hasExplanation && (
                  <Box className={styles.rcaExplanation}>
                    <Typography
                      variant="subtitle2"
                      className={styles.rcaExplanationTitle}
                    >
                      Explanation
                    </Typography>
                    <Typography
                      variant="body2"
                      className={styles.rcaExplanationBody}
                      id={`rca-explanation-${idx}`}
                      aria-live="polite"
                    >
                      {displayText}
                    </Typography>

                    {needsToggle && (
                      <Box className={styles.rcaToggleContainer}>
                        <Button
                          size="small"
                          variant="text"
                          className={styles.rcaToggleBtn}
                          onClick={() => toggleExpand(idx)}
                          aria-expanded={!!expanded[idx]}
                          aria-controls={`rca-explanation-${idx}`}
                        >
                          {expanded[idx] ? "See Less" : "See More"}
                        </Button>
                      </Box>
                    )}
                  </Box>
                )}
              </Stack>
            </Stack>
          );
        })}
      </div>
    </Box>
  );
};

export default RcaView;
