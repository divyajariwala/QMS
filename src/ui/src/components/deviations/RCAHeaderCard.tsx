import React from "react";
import styles from "./DeviationsHeaderCard.module.scss";

import { Paper, Box, Stack, Typography } from "@mui/material";
import { getDueStatus } from "src/helpers";
import DeviationsDueDateChip from "./DeviationsDueDateChip";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import LeftArrow from "../../assets/icons/leftArrow.svg";
import { formatDateMMM_D_YYYY } from "src/utils";
import CheckIcon from "@mui/icons-material/Check";
import { useNavigate } from "react-router-dom";

type DeviationData = {
  deviationData: {
    deviation_id: string;
    created_date: string;
    rca_approved: boolean;
    grading_approved: boolean;
  };
  onSubmit?: () => void;
  isRcaSubmitted?: boolean;
  hasRCA?: boolean;
};

const RCAHeaderCard: React.FC<DeviationData> = ({
  deviationData,
  onSubmit,
  isRcaSubmitted,
  hasRCA = false,
}) => {
  const { deviation_id, created_date, rca_approved, grading_approved } =
    deviationData;
  const navigate = useNavigate();
  const onBack = () => {
    navigate(`/deviations`);
  };
  return (
    <Paper className={styles.paper}>
      <Box className={styles.flexContainer}>
        <Box className={styles.leftSide}>
          <Stack spacing={0.5} className={styles.stackCustom}>
            {grading_approved === true ? (
              <Box className={styles.statusTextGreen}>GRADING COMPLETED</Box>
            ) : rca_approved === true && grading_approved === false ? (
              <Box className={styles.statusGrad}>GRADING PENDING</Box>
            ) : (
              <Box className={styles.statusText}>IN REVIEW</Box>
            )}
            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
              flexWrap="nowrap"
              className={styles.topRowInner}
            >
              <Box className={styles.caseIdText}>{deviation_id}</Box>
              <div className={styles.infoItem}>
                <div className={styles.infoItem__valueRow}>
                  <img src={ReceiptDateIcon} alt={"date"} />
                  {typeof created_date === "string" ? (
                    <Typography
                      component="p"
                      className={styles.infoItem__valueText}
                    >
                      {formatDateMMM_D_YYYY(created_date)}
                    </Typography>
                  ) : (
                    created_date
                  )}
                </div>
              </div>
              <DeviationsDueDateChip
                type={created_date && getDueStatus(created_date).type}
                label={created_date && getDueStatus(created_date).label}
              />

              {hasRCA &&
                (!isRcaSubmitted ? (
                  <button
                    type="button"
                    className={styles.approveSendButton}
                    onClick={onSubmit}
                  >
                    <CheckIcon />
                    Submit
                  </button>
                ) : (
                  <button
                    type="button"
                    className={styles.addBtn}
                    onClick={onBack}
                  >
                    <img src={LeftArrow} alt={"left arrow"} />
                    Back
                  </button>
                ))}
            </Stack>
          </Stack>
        </Box>
      </Box>
    </Paper>
  );
};

export default RCAHeaderCard;
