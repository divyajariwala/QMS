import React from "react";
import { Box, LinearProgress, Button, Radio } from "@mui/material";
import { useNavigate } from "react-router-dom";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import ComplaintsDueDateChip from "../../components/complaint/ComplaintsDueDateChip";
import Calendar from "../../assets/icons/calendar.svg";
import styles from "./DeviationsResult.module.scss";
import { getDueStatus } from "src/helpers";
import { DeviationProps } from "src/types";

const DeviationsResult: React.FC<DeviationProps> = ({ deviation }) => {
  const navigate = useNavigate();
  const headerStatusRaw = (deviation?.status ?? "").toString().trim();
  const headerStatusUpper = headerStatusRaw.toUpperCase();
  const caseNumber = deviation?.["Case Number"];
  const receivedDate = deviation?.["Recieved Date"];
  const dueDate = deviation?.["Due Date"];
  const progress = deviation?.progress ? deviation.progress : 0;
  const rcaStatusUpper = (deviation?.rcaStatus ?? "")
    .toString()
    .trim()
    .toUpperCase();
  const gradingStatusUpper = (deviation?.gradingStatus ?? "")
    .toString()
    .trim()
    .toUpperCase();
  const isInReview = headerStatusUpper === "IN-REVIEW";
  const gradingPendingHeader = /GRADING/.test(headerStatusUpper) && !isInReview;
  const showGradingPendingView =
    !isInReview &&
    (gradingPendingHeader ||
      gradingStatusUpper === "PENDING" ||
      headerStatusUpper.includes("GRADING PENDING"));
  const dueInfo = getDueStatus(dueDate);
  const onStartRca = (e: React.MouseEvent) => {
    e.stopPropagation();
    console.log("Start RCA for", caseNumber);
    navigate(`/deviations/${caseNumber}`);
  };
  const onStartGrading = (e: React.MouseEvent) => {
    e.stopPropagation();
    console.log("Start Grading for", caseNumber);
  };

  return (
    <div className={styles.complaintsCardContainer}>
      <div className={styles.headerRow}>
        <Box>
          <div className={styles.container}>
            <span className={styles.idText}>{headerStatusUpper}</span>
          </div>
          <div className={styles.container}>
            <span className={styles.caseNumberText}>{caseNumber}</span>

            <div className={styles.dateGroup}>
              <img src={Calendar} className={styles.dateIcon} />
              <span className={styles.label}>Received Date: </span>
              <span className={styles.date}>{receivedDate}</span>
            </div>
          </div>
        </Box>
        <ComplaintsDueDateChip type={dueInfo.type} label={dueInfo.label} />
      </div>
      <div className={styles.infoRow}>Deviation description</div>
      <div className={styles.progressSection}>
        <div className={styles.progressHeader}>
          <span className={styles.progressLabel}>Overall Progress</span>
          <span className={styles.progressPercent}>{`${Math.round(
            progress
          )}%`}</span>
        </div>
        <div className={styles.progressBarBackground}>
          <div
            className={styles.progressBarFill}
            style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
          />
        </div>
      </div>
      <div className={styles.stepsRow}>
        <div className={styles.stepColumn}>
          <div className={styles.stepHeader}>
            <Radio size="small" checked={rcaStatusUpper === "COMPLETED"} />
            <span className={styles.stepLabel}>Root Cause Analysis</span>
          </div>
          {showGradingPendingView && rcaStatusUpper === "COMPLETED" ? (
            <div className={styles.completedPill}>
              <CheckCircleOutlineIcon
                fontSize="small"
                className={styles.completedIcon}
              />
              <span>Completed</span>
            </div>
          ) : (
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
        <div className={styles.stepColumn}>
          <div className={styles.stepHeader}>
            <Radio size="small" checked={gradingStatusUpper === "COMPLETED"} />
            <span className={styles.stepLabel}>Grading</span>
          </div>
          {showGradingPendingView ? (
            <Button
              variant="outlined"
              className={styles.startGradingButton}
              startIcon={<PlayCircleOutlineIcon />}
              onClick={onStartGrading}
            >
              Start Grading
            </Button>
          ) : (
            <div className={styles.waitingPill}>
              <span>Waiting for RCA</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DeviationsResult;
