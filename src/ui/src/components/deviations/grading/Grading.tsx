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
  SectionDataRes,
  SectionData,
  SuggestionData,
  ExecSummaryPayload,
  ExecutiveSummaryItem,
} from "./GradingTypes";

import ExecutiveSummary from "./ExecutiveSummary";
import {
  fetchExecutiveSummary,
  fetchGradingData,
  fetchGradingSuggestions,
  submitGrading,
} from "src/services/deviations";

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
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [summaryItems, setSummaryItems] = useState<ExecutiveSummaryItem[]>([]);
  const [submitted, setSubmitted] = useState(false);
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
  const notify = (
    message: string,
    severity: "success" | "info" | "error" = "info"
  ) => {
    setSnack({ open: true, message, severity });
  };

  useEffect(() => {
    (async () => {
      setLoadingSections(true);
      try {
        const { data }: SectionDataRes = await fetchGradingData(deviationId);
        setSections(data);
        setValues(data.map((s) => s.content ?? ""));
      } catch (err) {
        notify("Failed to load sections", "error");
      } finally {
        setLoadingSections(false);
      }
    })();
  }, [deviationId]);

  const isCompose = mode === "compose";
  const isGrading = mode === "grading";

  const handleStartGrading = async () => {
    setMode("grading");
    setLoadingSuggestions(true);
    onEnterReview?.();
    try {
      const suggs = await fetchGradingSuggestions({
        deviation_id: deviationId,
      });
      setSuggestions(suggs.data);
    } catch (err) {
      notify("Failed to start grading", "error");
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const regenerateSuggestions = async () => {
    setLoadingSuggestions(true);
    try {
      const suggs = await fetchGradingSuggestions({
        deviation_id: deviationId,
        existing_results: suggestions,
      });
      setSuggestions(suggs.data);
      notify("Improvement suggestions updated", "success");
    } catch (err) {
      notify("Failed to fetch improvement suggestions", "error");
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleGenerateSummary = async () => {
    setSummaryItems([]);
    setSummaryOpen(true);
    try {
      const apiPayload = {
        deviation_id: deviationId,
      };
      const items = await fetchExecutiveSummary(apiPayload);
      setSummaryItems(items.data);
      notify("Executive summary generated.", "success");
    } catch {
      notify("Failed to generate executive summary", "error");
    }
  };

  const handleBackFromSummary = () => {
    setSummaryOpen(false);
  };

  const handleSaveAndSubmit = async (payload: ExecSummaryPayload) => {
    try {
      const apiPayload = {
        deviation_id: deviationId,
        sections: payload,
      };
      await submitGrading(apiPayload);
      notify("Summary sent to QMS.", "success");
      setSubmitted(true);
      onProcessed?.();
    } catch (err) {
      notify("Failed to send to QMS.", "error");
    }
  };

  return (
    <Paper variant="outlined" className={styles.rootPaper}>
      {summaryOpen ? (
        <ExecutiveSummary
          items={summaryItems}
          onBack={handleBackFromSummary}
          onSaveAndSubmit={!submitted ? handleSaveAndSubmit : undefined}
          disabled={submitted}
          tinymceScriptSrc={import.meta.env.VITE_TINYMCE_CDN}
          onNotify={notify}
        />
      ) : (
        <>
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
                  disabled={loadingSections || !deviationId}
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
                    disabled={loadingSuggestions}
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
                        <Paper
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
                                {suggestion.improvement_suggestion}
                              </Typography>
                            ) : (
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
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
        </>
      )}

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
