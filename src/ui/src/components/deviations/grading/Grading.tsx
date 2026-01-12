import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Box,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  Typography,
  Snackbar,
  Alert,
  Divider,
} from "@mui/material";

import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import GradingIcon from "../../../assets/icons/grading.svg";
import RegenerateIcon from "../../../assets/icons/refresh.svg";
import ArrowRight from "../../../assets/icons/arrowRight.svg";

import styles from "./grading.module.scss";
import {
  fetchImprovementSuggestionsMock,
  fetchExecutiveSummaryMock,
  SectionData,
  SuggestionData,
  ExecutiveSummaryItem,
} from "./mockdata";

import ExecutiveSummary from "./ExecutiveSummary";
import { fetchGradingData } from "src/services/deviations";

type Mode = "compose" | "grading";

interface GradingProps {
  onEnterReview?: () => void;
  onProcessed?: () => void;
}

const Grading: React.FC<GradingProps> = ({ onEnterReview, onProcessed }) => {
  const [mode, setMode] = useState<Mode>("compose");
  const [sections, setSections] = useState<SectionData[]>([]);
  const [values, setValues] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<SuggestionData[]>([]);
  const [loadingSections, setLoadingSections] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const { deviationId } = useParams<{ deviationId: string | undefined }>();

  const [snack, setSnack] = useState<{
    open: boolean;
    message: string;
    severity?: "success" | "info" | "error";
  }>({
    open: false,
    message: "",
    severity: "info",
  });

  const [summaryOpen, setSummaryOpen] = useState(false);
  const [summaryItems, setSummaryItems] = useState<ExecutiveSummaryItem[]>([]);
  const [submitted, setSubmitted] = useState(false);
  type ExecSummaryPayload = { label: string; content: string }[];

  useEffect(() => {
    (async () => {
      setLoadingSections(true);
      try {
        const {data} = await fetchGradingData(deviationId);
        setSections(data);
        setValues(data.map((s) => s.content ?? ""));
      } catch (err) {
        setSnack({
          open: true,
          message: "Failed to load sections",
          severity: "error",
        });
      } finally {
        setLoadingSections(false);
      }
    })();
  }, []);

  const isCompose = mode === "compose";
  const isGrading = mode === "grading";

  const handleStartGrading = async () => {
    setMode("grading");
    await regenerateSuggestions();
  };

  const regenerateSuggestions = async () => {
    setLoadingSuggestions(true);
    try {
      const suggs = await fetchImprovementSuggestionsMock(values);
      setSuggestions(suggs);
      setSnack({
        open: true,
        message: "Improvement suggestions updated",
        severity: "success",
      });
    } catch (err) {
      setSnack({
        open: true,
        message: "Failed to fetch improvement suggestions",
        severity: "error",
      });
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleGenerateSummary = async () => {
    try {
      const items = await fetchExecutiveSummaryMock(values);
      setSummaryItems(items);
      setSummaryOpen(true);
      onEnterReview?.();
    } catch {
      setSnack({
        open: true,
        message: "Failed to generate executive summary",
        severity: "error",
      });
    }
  };

  const handleBackFromSummary = () => {
    setSummaryOpen(false);
  };

  const handleExecutiveSummaryPrimaryAction = (payload: ExecSummaryPayload) => {
    console.log("Executive Summary (HTML):", JSON.stringify(payload, null, 2));
    setSnack({
      open: true,
      message: "Summary sent successfully.",
      severity: "success",
    });
    setSubmitted(true);
    onProcessed?.();
  };

  if (summaryOpen) {
    return (
      <ExecutiveSummary
        items={summaryItems}
        onBack={handleBackFromSummary}
        onPrimaryAction={
          !submitted ? handleExecutiveSummaryPrimaryAction : undefined
        }
        disabled={submitted}
      />
    );
  }

  return (
    <Paper variant="outlined" className={styles.rootPaper}>
      <Box className={styles.headerRow}>
        <Typography variant="h6" className={styles.title}>
          Grading
        </Typography>
        <Stack direction="row" spacing={1} className={styles.actionBtnBox}>
          {isCompose && (
            <button
              type="button"
              className={styles.gradingBtn}
              onClick={handleStartGrading}
            >
              Start Grading
              <img src={GradingIcon} alt={"start grading"} />
            </button>
          )}

          {isGrading && (
            <>
              <button
                type="button"
                className={styles.regenerateBtn}
                onClick={regenerateSuggestions}
                disabled={loadingSuggestions}
              >
                Regenerate
                <img src={RegenerateIcon} alt={"regenerate"} />
              </button>
              <button
                className={styles.classifyBtn}
                onClick={handleGenerateSummary}
                disabled={submitted}
              >
                Generate Executive Summary
                <img src={ArrowRight} alt="generate summary" />
              </button>
            </>
          )}
        </Stack>
      </Box>

      <Divider className={styles.headerDivider} />
      <Box className={styles.contentPad}>
        {loadingSections ? (
          <Box className={styles.loaderBox}>
            <CircularProgress size={24} />
            <Typography variant="body2" sx={{ ml: 1 }}>
              Loading sections…
            </Typography>
          </Box>
        ) : (
          <Box>
            {sections.map((section, idx) => {
              const val = values[idx] ?? "";
              if (isCompose) {
                return (
                  <Paper
                    key={`section-${idx}`}
                    variant="outlined"
                    className={styles.sectionPaper}
                  >
                    <Box className={styles.labelRow}>
                      <Typography
                        variant="subtitle1"
                        className={styles.sectionLabel}
                      >
                        {section.label}
                      </Typography>
                    </Box>
                    <Box className={styles.textField}>{val || "N/A"}</Box>
                  </Paper>
                );
              }

              const suggestion = suggestions[idx];
              const score = suggestion?.score;
              const hasScore = typeof score === "number";
              const isPositive = hasScore && (score as number) >= 6;
              const isNegative = hasScore && (score as number) <= 5;

              return (
                <Grid
                  key={`section-${idx}`}
                  container
                  spacing={2}
                  className={styles.sectionRow}
                >
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" className={styles.sectionPaper}>
                      <Box className={styles.labelRow}>
                        <Typography
                          variant="subtitle1"
                          className={styles.sectionLabel}
                        >
                          {section.label}
                        </Typography>
                      </Box>
                      <Box className={styles.textField}>{val || "N/A"}</Box>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Paper
                      variant="outlined"
                      className={styles.suggestionsPaper}
                    >
                      <Box className={styles.suggestionLabelRow}>
                        <Typography
                          variant="subtitle1"
                          className={styles.sectionLabel}
                        >
                          Improvement Suggestion
                        </Typography>

                        {isPositive ? (
                          <ThumbUpAltOutlinedIcon
                            fontSize="small"
                            className={styles.thumbsUp}
                          />
                        ) : isNegative ? (
                          <ThumbDownAltOutlinedIcon
                            fontSize="small"
                            className={styles.thumbsDown}
                          />
                        ) : (
                          <ThumbUpAltOutlinedIcon
                            fontSize="small"
                            style={{ opacity: 0.4 }}
                          />
                        )}
                      </Box>

                      <Box className={styles.suggestionBody}>
                        {loadingSuggestions ? (
                          <Box className={styles.loaderInline}>
                            <CircularProgress size={18} />
                            <Typography variant="body2" sx={{ ml: 1 }}>
                              Updating…
                            </Typography>
                          </Box>
                        ) : suggestion ? (
                          <Typography
                            variant="body2"
                            className={styles.suggestionText}
                          >
                            {suggestion.text}
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            No suggestion available for this section yet.
                          </Typography>
                        )}
                      </Box>
                    </Paper>
                  </Grid>
                </Grid>
              );
            })}
          </Box>
        )}
      </Box>

      <Snackbar
        open={snack.open}
        autoHideDuration={2500}
        onClose={() => setSnack((s) => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          severity={snack.severity ?? "info"}
          onClose={() => setSnack((s) => ({ ...s, open: false }))}
        >
          {snack.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default Grading;
