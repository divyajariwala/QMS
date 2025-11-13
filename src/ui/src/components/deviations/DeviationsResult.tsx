import React from "react";
import { Box, Typography, LinearProgress, Button, Radio, IconButton } from "@mui/material";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import Calendar from "../../assets/icons/calendar.svg";
import ComplaintsDueDateChip from "../../components/complaint/ComplaintsDueDateChip";
import styles from "./DeviationsResult.module.scss";
import { DeviationProps, Status } from "src/types";
import { getDueStatus } from "src/helpers";

const formatDateShort = (value?: string | Date | null) => {
  if (!value) return "-";
  const d = typeof value === "string" ? new Date(value) : value;
  if (isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, { month: "short", day: "2-digit", year: "numeric" });
};

const DeviationsResult: React.FC<DeviationProps> = ({ deviation }) => {
  const headerStatusRaw = (deviation?.status || "").toString();
  const headerStatus = headerStatusRaw.trim();
  const headerStatusUpper = headerStatus.toUpperCase();

  const caseNumber = deviation?.caseNumber || deviation?.["Case Number"] || deviation?.id || "DV-12345";
  const receivedDate = deviation?.receivedDate || deviation?.["Received Date"] || deviation?.["Recieved Date"];
  const dueDate = deviation?.dueDate || deviation?.["Due Date"];
  const progress = typeof deviation?.progress === "number" ? deviation.progress : 0;
  const rcaStatus = deviation?.rcaStatus as Status | undefined;
  const gradingStatus = deviation?.gradingStatus as Status | undefined;

  // Decide which layout: in-review layout vs grading-pending layout
  const isInReview = headerStatusUpper === "IN-REVIEW";
  // grading pending if header contains "GRADING" and not in-review OR gradingStatus indicates pending
  const gradingPendingHeader = /GRADING/.test(headerStatusUpper) && !isInReview;
  const gradingPendingComputed = gradingPendingHeader || gradingStatus === ("PENDING" as Status) || headerStatusUpper.includes("GRADING PENDING");
  const showGradingPendingView = !isInReview && gradingPendingComputed;

  const dueStatus = getDueStatus(dueDate || null);

  const onStartRca = (e: React.MouseEvent) => {
    e.stopPropagation();
    console.log("Start RCA for", caseNumber);
  };
  const onStartGrading = (e: React.MouseEvent) => {
    e.stopPropagation();
    console.log("Start Grading for", caseNumber);
  };

  return (
    <div className={styles.card} role="article" aria-label={`Deviation ${caseNumber}`}>
      <div className={styles.headerRow}>
        <div className={styles.headerLeft}>
          <div className={styles.headerTop}>
            <Typography className={styles.status} component="span">
              {headerStatus || "IN-REVIEW"}
            </Typography>

            <Typography className={styles.caseNumber} component="a" tabIndex={0}>
              {caseNumber}
            </Typography>

            <div className={styles.receivedDate}>
              <img src={Calendar} className={styles.dateIcon} alt="Received" />
              <span className={styles.receivedLabel}>Received Date:</span>
              <span className={styles.receivedValue}>{formatDateShort(receivedDate)}</span>
            </div>
          </div>

          <Typography className={styles.description} component="p">
            {deviation?.description || "Deviation description"}
          </Typography>
        </div>

        <div className={styles.headerRight}>
          <ComplaintsDueDateChip type={dueStatus.type} label={dueStatus.label} />
        </div>
      </div>

      <div className={styles.progressSection}>
        <div className={styles.progressHeader}>
          <span className={styles.progressLabel}>Overall Progress</span>
          <span className={styles.progressPercent}>{`${Math.round(progress)}%`}</span>
        </div>
        {/* use dark progress styling for grading-pending to match screenshot */}
        <LinearProgress
          variant="determinate"
          value={Math.max(0, Math.min(100, progress))}
          className={`${styles.progressBar} ${showGradingPendingView ? styles.progressBarDark : ""}`}
        />
      </div>

      <div className={styles.stepsRow}>
        {/* Left column (RCA) */}
        <div className={styles.stepColumn}>
          <div className={styles.stepHeader}>
            <Radio size="small" checked={rcaStatus === "COMPLETED"} />
            <span className={styles.stepLabel}>Root Cause Analysis</span>
          </div>

          {showGradingPendingView && rcaStatus === "COMPLETED" ? (
            // Completed pill (green) under the left step
            <div className={styles.completedPill}>
              <CheckCircleOutlineIcon fontSize="small" className={styles.completedIcon} />
              <span>Completed</span>
            </div>
          ) : (
            // In-review default Start RCA button
            <Button
              variant="outlined"
              color="primary"
              startIcon={<PlayCircleOutlineIcon />}
              className={styles.startButton}
              onClick={onStartRca}
            >
              Start RCA
            </Button>
          )}
        </div>

        {/* Right column (Grading) */}
        <div className={styles.stepColumn}>
          <div className={styles.stepHeader}>
            <Radio size="small" checked={gradingStatus === "COMPLETED"} />
            <span className={styles.stepLabel}>Grading</span>
          </div>

          {showGradingPendingView ? (
            // Show purple outlined Start Grading button
            <Button
              variant="outlined"
              className={styles.startGradingButton}
              startIcon={<PlayCircleOutlineIcon />}
              onClick={onStartGrading}
            >
              Start Grading
            </Button>
          ) : (
            // In-review: show waiting pill
            <div className={styles.waitingPill}>
              <span>Waiting for RCA</span>
              <KeyboardArrowRightIcon fontSize="small" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DeviationsResult;