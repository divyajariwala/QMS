import React, { useMemo, useState } from "react";
import { Box, Button, Radio, Skeleton } from "@mui/material";
import { useNavigate } from "react-router-dom";
import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import Calendar from "../../assets/icons/calendar.svg";
import styles from "./DeviationsResult.module.scss";
import { getDueStatus } from "src/helpers";
import { DeviationProps } from "src/types";
import { formatDateMMM_D_YYYY } from "src/utils";
import DeviationsDueDateChip from "./DeviationsDueDateChip";

const DeviationsResult: React.FC<DeviationProps> = ({ deviation, loading }) => {
  const navigate = useNavigate();
  const { deviation_id, created_date, deviation_description } = deviation;
  const [descExpanded, setDescExpanded] = useState(false);
  const CHAR_LIMIT = 200;
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
      navigate(`/approveRca/${deviation_id}`);
    }
  };
  const onStartGrading = () => {
    if (!loading) {
      navigate(`/approveGrading/${deviation_id}`);
    }
  };

  const truncateAtWord = (text: string, limit: number) => {
    if (!text) return "";
    if (text.length <= limit) return text;
    const cut = text.slice(0, limit);
    const lastSpace = cut.lastIndexOf(" ");
    const safeCut = lastSpace > 0 ? cut.slice(0, lastSpace) : cut;
    return `${safeCut}…`;
  };

  const descNeedsToggle = useMemo(
    () => (deviation_description ?? "").length > CHAR_LIMIT,
    [deviation_description]
  );

  const descDisplayText = useMemo(() => {
    if (!deviation_description) return "";
    if (descExpanded || !descNeedsToggle) return deviation_description;
    return truncateAtWord(deviation_description, CHAR_LIMIT);
  }, [deviation_description, descExpanded, descNeedsToggle]);

  return (
    <div className={styles.complaintsCardContainer}>
      <div className={styles.headerRow}>
        <Box>
          {gradingStatus === true ? (
            <Box className={styles.statusTextGreen}>GRADING COMPLETED</Box>
          ) : rcaStatus === true && gradingStatus === false ? (
            <Box className={styles.statusGrad}>GRADING PENDING</Box>
          ) : (
            <Box className={styles.statusText}>IN REVIEW</Box>
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
        {deviation.status !== "processed" && (
          <DeviationsDueDateChip type={dueInfo.type} label={dueInfo.label} />
        )}
      </div>
      {loading ? (
        <Skeleton variant="rectangular" width={500} height={24} />
      ) : (
        <div className={styles.infoRow}>
          <span>
            {descDisplayText}
            {descNeedsToggle && (
              <Button
                className={styles.seeMoreBtn}
                onClick={() => setDescExpanded((v) => !v)}
              >
                {descExpanded ? " See Less" : " See More"}
              </Button>
            )}
          </span>
        </div>
      )}

      <div className={styles.progressSection}>
        <div className={styles.progressHeader}>
          <span className={styles.progressLabel}>Overall Progress</span>
          <span className={styles.progressPercent}>
            {`${Math.round(progress)}%`}
          </span>
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
