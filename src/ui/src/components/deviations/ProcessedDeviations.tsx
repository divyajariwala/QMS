import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Box,
  Grid,
  Paper,
  Typography,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  IconButton,
  Collapse,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./ProcessedDeviations.module.scss";
import { fetchDeviationDetailById } from "src/services/deviations";
import { DeviationDetail } from "src/types";
import Notification from "@components/Notification/Notification";
import GradingHeaderCard from "./GradingHeaderCard";
import Spinner from "@components/common/Spinner/Spinner";

type GradingUiStatus = "pending" | "in_review" | "processed";
type ExpandedState = Record<number, boolean>;

interface RCAItem {
  problem_category: string;
  major_root_cause_category: string;
  near_root_cause_category: string;
  root_cause_category: string;
}

const ProcessedDeviation: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<"success" | "error">("success");
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [deviationData, setDeviationData] = useState<DeviationDetail | null>(
    null
  );
  const [uiStatus] = useState<GradingUiStatus>("processed");
  const [rcaItems, setRcaItems] = useState<RCAItem[]>([]);
  const [gradingData, setGradingData] = useState<any[]>([]);
  const [executiveSummary, setExecutiveSummary] = useState<any[]>([]);
  const [expanded, setExpanded] = React.useState<ExpandedState>({});

  const { deviationId } = useParams<{ deviationId: string | undefined }>();

  const toggle = (idx: number) =>
    setExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }));

  const handleShowNotification = () => setOpen(true);
  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") return;
    setOpen(false);
  };

  const items = [
    { label: "Home", to: "/" },
    { label: "Deviations", to: "/deviations" },
    { label: deviationId?.toString() ?? "" },
  ];

  useEffect(() => {
    async function init() {
      setLoading(true);
      try {
        const data = await fetchDeviationDetailById(deviationId);
        setDeviationData(data);
        setRcaItems(data.rcaData || []);
        setGradingData(data.gradingData || []);
        setExecutiveSummary(data.executiveSummary || []);
        const expandedMap = Object.fromEntries(
          (data.rcaData || []).map((_: any, idx: number) => [idx, true])
        );
        setExpanded(expandedMap);
      } catch (err: any) {
        setType("error");
        setMessage("Failed to get deviation details");
        handleShowNotification();
        console.log(err.message || "Failed to get details");
      } finally {
        setLoading(false);
      }
    }
    if (deviationId) init();
  }, [deviationId]);

  const trimSafe = (val: string) =>
    typeof val === "string" ? val.trim() : val;

  if (loading) return <Spinner />;

  return (
    <Box>
      <CommonBreadcrumbs items={items} />
      {deviationData && (
        <GradingHeaderCard deviationData={deviationData} status={uiStatus} />
      )}
      <Box className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <Paper variant="outlined" className={styles.rootPaper}>
            <Typography
              variant="h6"
              className={styles.mainTitle}
              marginBottom={2}
            >
              Deviation results
            </Typography>

            {/* === RCA (Accordion) === */}
            <Accordion defaultExpanded className={styles.boxRca}>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="rca-content"
                id="rca-header"
                sx={{
                  "& .MuiAccordionSummary-content.Mui-expanded": {
                    margin: "12px 0",
                  },

                  "&.MuiAccordionSummary-root.Mui-expanded": {
                    minHeight: "fit-content",
                  },

                  position: "relative",
                  "&.Mui-expanded::after": {
                    content: '""',
                    position: "absolute",
                    left: 0,
                    right: 0,
                    bottom: 0,
                    height: "1px",
                    backgroundColor: (theme) => theme.palette.divider,
                  },
                }}
              >
                <Typography variant="h6" className={styles.title}>
                  RCA
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ padding: "16px" }}>
                {rcaItems.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No data to display
                  </Typography>
                ) : (
                  <TableContainer component={Paper} elevation={2}>
                    <Table aria-label="RCA expandable table" size="small">
                      <TableBody>
                        {rcaItems.map((row, idx) => {
                          const isOpen = !!expanded[idx];
                          const rcaLabel = `RCA ${idx + 1}`;

                          return (
                            <React.Fragment key={idx}>
                              <TableRow hover>
                                <TableCell width={56}>
                                  <IconButton
                                    aria-label={isOpen ? "Collapse" : "Expand"}
                                    size="small"
                                    onClick={() => toggle(idx)}
                                  >
                                    {isOpen ? (
                                      <KeyboardArrowUp />
                                    ) : (
                                      <KeyboardArrowDown />
                                    )}
                                  </IconButton>
                                </TableCell>
                                <TableCell component="th" scope="row">
                                  <Typography fontWeight={600}>
                                    {rcaLabel}
                                  </Typography>
                                </TableCell>
                                {/* Spacer cells so the expand icon is visually aligned */}
                                <TableCell colSpan={4} />
                              </TableRow>

                              {/* Detail row with four columns */}
                              <TableRow>
                                <TableCell
                                  style={{ paddingBottom: 0, paddingTop: 0 }}
                                  colSpan={6}
                                >
                                  <Collapse
                                    in={isOpen}
                                    timeout="auto"
                                    unmountOnExit
                                  >
                                    <Box sx={{ margin: 2 }}>
                                      <Box
                                        sx={{
                                          border: "1px solid",
                                          borderColor: "divider",
                                          borderRadius: "5px",
                                          overflow: "hidden",
                                        }}
                                      >
                                        <Table
                                          size="small"
                                          aria-label={`${rcaLabel} details`}
                                          sx={{
                                            "& th": { fontWeight: 600 },
                                            borderCollapse: "separate",
                                            borderSpacing: 0,
                                          }}
                                        >
                                          <TableHead>
                                            <TableRow>
                                              <TableCell>
                                                Problem Category
                                              </TableCell>
                                              <TableCell>
                                                Major Root Cause
                                              </TableCell>
                                              <TableCell>
                                                Near Root Cause
                                              </TableCell>
                                              <TableCell>Root Cause</TableCell>
                                            </TableRow>
                                          </TableHead>
                                          <TableBody>
                                            <TableRow hover>
                                              <TableCell>
                                                {trimSafe(row.problem_category)}
                                              </TableCell>
                                              <TableCell>
                                                {trimSafe(
                                                  row.major_root_cause_category
                                                )}
                                              </TableCell>
                                              <TableCell>
                                                {trimSafe(
                                                  row.near_root_cause_category
                                                )}
                                              </TableCell>
                                              <TableCell>
                                                {trimSafe(
                                                  row.root_cause_category
                                                )}
                                              </TableCell>
                                            </TableRow>
                                          </TableBody>
                                        </Table>
                                      </Box>
                                    </Box>
                                  </Collapse>
                                </TableCell>
                              </TableRow>
                            </React.Fragment>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </AccordionDetails>
            </Accordion>

            {/* === Grading (Accordion) === */}
            <Accordion defaultExpanded className={styles.boxGrading}>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="grading-content"
                id="grading-header"
                sx={{
                  "& .MuiAccordionSummary-content.Mui-expanded": {
                    margin: "12px 0",
                  },

                  "&.MuiAccordionSummary-root.Mui-expanded": {
                    minHeight: "fit-content",
                  },
                  position: "relative",
                  "&.Mui-expanded::after": {
                    content: '""',
                    position: "absolute",
                    left: 0,
                    right: 0,
                    bottom: 0,
                    height: "1px",
                    backgroundColor: (theme) => theme.palette.divider,
                  },
                }}
              >
                <Typography variant="h6" className={styles.title}>
                  Grading
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ padding: "16px" }}>
                {gradingData.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No data to display
                  </Typography>
                ) : (
                  gradingData.map((item, idx) => {
                    const isPositive = item.score >= 6;
                    const isNegative = item.score > 0 && item.score <= 5;
                    const isHtml =
                      typeof item.text === "string" &&
                      /<\/?[a-z][\s\S]*>/i.test(item.text);

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
                                {item.section_label}
                              </Typography>
                            </Box>
                            <Box className={styles.textField}>
                              {isHtml ? (
                                <div
                                  dangerouslySetInnerHTML={{
                                    __html: item.text,
                                  }}
                                />
                              ) : (
                                item.text || "N/A"
                              )}
                            </Box>
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
                              {item.improvement_suggestion ? (
                                <Typography
                                  variant="body2"
                                  className={styles.suggestionText}
                                >
                                  {item.improvement_suggestion}
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
                  })
                )}
              </AccordionDetails>
            </Accordion>

            {/* === Executive Summary (Accordion) === */}
            <Accordion defaultExpanded className={styles.boxSummary}>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="executive-summary-content"
                id="executive-summary-header"
                sx={{
                  "& .MuiAccordionSummary-content.Mui-expanded": {
                    margin: "12px 0",
                  },

                  "&.MuiAccordionSummary-root.Mui-expanded": {
                    minHeight: "fit-content",
                  },
                  position: "relative",
                  "&.Mui-expanded::after": {
                    content: '""',
                    position: "absolute",
                    left: 0,
                    right: 0,
                    bottom: 0,
                    height: "1px",
                    backgroundColor: (theme) => theme.palette.divider,
                  },
                }}
              >
                <Typography variant="h6" className={styles.title}>
                  Executive Summary
                </Typography>
              </AccordionSummary>

              <AccordionDetails sx={{ padding: "16px" }}>
                {executiveSummary.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No data to display
                  </Typography>
                ) : (
                  executiveSummary.map((item, idx) => {
                    const content = item?.content ?? "";
                    const isHtml =
                      typeof content === "string" &&
                      /<\/?[a-z][\s\S]*>/i.test(content);

                    return (
                      <Box
                        key={`${item.label}-${idx}`}
                        className={styles.section}
                      >
                        <Typography
                          variant="subtitle2"
                          className={styles.sectionLabel}
                        >
                          {item.label}
                        </Typography>

                        {isHtml ? (
                          <div
                            className={styles.summaryContemt}
                            dangerouslySetInnerHTML={{ __html: content }}
                          />
                        ) : (
                          <p className={styles.summaryContemt}>{content}</p>
                        )}
                      </Box>
                    );
                  })
                )}
              </AccordionDetails>
            </Accordion>
          </Paper>
        </Grid>
      </Box>

      <Notification
        open={open}
        onClose={handleCloseNotification}
        position="top"
        type={type}
        message={message}
      />
    </Box>
  );
};

export default ProcessedDeviation;
