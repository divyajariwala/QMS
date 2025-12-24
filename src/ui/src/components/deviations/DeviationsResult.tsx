import React from "react";
import { Box, Button, Radio, Skeleton } from "@mui/material";
import { useNavigate } from "react-router-dom";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import ComplaintsDueDateChip from "../../components/complaint/ComplaintsDueDateChip";
import Calendar from "../../assets/icons/calendar.svg";
import styles from "./DeviationsResult.module.scss";
import { getDueStatus } from "src/helpers";
import { DeviationProps } from "src/types";
import { formatDateMMM_D_YYYY } from "src/utils";

const DeviationsResult: React.FC<DeviationProps> = ({ deviation, loading }) => {
  const navigate = useNavigate();
  const headerStatusRaw = (deviation?.status ?? "").toString().trim();
  const headerStatusUpper = headerStatusRaw.toUpperCase();
  const { deviation_id, created_date, deviation_description } = deviation;
  const progress = !deviation.rca_approved
    ? 0
    : !deviation.grading_approved
    ? 50
    : 100;

  const rcaStatus = deviation?.rca_approved;
  const gradingStatus = deviation?.grading_approved;
  const dueInfo = getDueStatus(created_date);

  const onStartRca = () => {
    if (!loading) {
      navigate(`/deviations/${deviation_id}`);
    }
  };
  const onStartGrading = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div className={styles.complaintsCardContainer}>
      <div className={styles.headerRow}>
        <Box>
          {headerStatusRaw === "pending" ? (
            <Box className={styles.statusText}>IN REVIEW</Box>
          ) : (
            <Box className={styles.statusText}>{headerStatusUpper}</Box>
          )}
          <div className={styles.container}>
            <span className={styles.caseNumberText}>{deviation_id}</span>
            {loading && (
              <span className={styles.processText}>
                Deviation is being processed...
              </span>
            )}
            <div className={styles.dateGroup}>
              <img src={Calendar} className={styles.dateIcon} />
              <span className={styles.label}>Received Date: </span>
              <span className={styles.date}>
                {formatDateMMM_D_YYYY(created_date)}
              </span>
            </div>
          </div>
        </Box>
        <ComplaintsDueDateChip type={dueInfo.type} label={dueInfo.label} />
      </div>
      {loading ? (
        <Skeleton variant="rectangular" width={500} height={24} />
      ) : (
        <div className={styles.infoRow}>{deviation_description}</div>
      )}
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
            <Radio size="small" checked={rcaStatus} />
            <span className={styles.stepLabel}>Root Cause Analysis</span>
          </div>
          {rcaStatus ? (
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
            <Radio size="small" checked={rcaStatus && gradingStatus} />
            <span className={styles.stepLabel}>Grading</span>
          </div>
          {rcaStatus ? (
            <>
              {gradingStatus ? (
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
                  className={styles.startGradingButton}
                  startIcon={<PlayCircleOutlineIcon />}
                  onClick={onStartGrading}
                >
                  Start Grading
                </Button>
              )}
            </>
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
