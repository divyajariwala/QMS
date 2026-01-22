import React from "react";
import styles from "./DeviationsHeaderCard.module.scss";

import { Paper, Box, Stack, Typography } from "@mui/material";
import { getDueStatus } from "src/helpers";
import DeviationsDueDateChip from "./DeviationsDueDateChip";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import LeftArrow from "../../assets/icons/leftArrow.svg"; // ✅ NEW
import { formatDateMMM_D_YYYY } from "src/utils";

type GradingHeaderCardProps = {
  deviationData: {
    deviation_id: string;
    created_date: string;
    rca_approved: boolean;
    grading_completed: boolean;
  };
  status?: "pending" | "in_review" | "processed";
  onBack?: () => void;
};

const GradingHeaderCard: React.FC<GradingHeaderCardProps> = ({
  deviationData,
  status = "pending",
  onBack,
}) => {
  const { deviation_id, created_date } = deviationData;

  const renderStatus = () => {
    switch (status) {
      case "processed":
        return <Box className={styles.statusTextGreen}>PROCESSED</Box>;
      case "in_review":
        return <Box className={styles.statusText}>IN REVIEW</Box>;
      case "pending":
      default:
        return <Box className={styles.statusGrad}>GRADING PENDING</Box>;
    }
  };

  return (
    <Paper className={styles.paper}>
      <Box className={styles.flexContainer}>
        <Box className={styles.leftSide}>
          <Stack spacing={0.5} className={styles.stackCustom}>
            {renderStatus()}
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
              {status !== "processed" && (
                <DeviationsDueDateChip
                  type={created_date && getDueStatus(created_date).type}
                  label={created_date && getDueStatus(created_date).label}
                />
              )}
              {status === "processed" && onBack && (
                <button
                  type="button"
                  className={styles.addBtn}
                  onClick={onBack}
                >
                  <img src={LeftArrow} alt="back" />
                  Back
                </button>
              )}
            </Stack>
          </Stack>
        </Box>
      </Box>
    </Paper>
  );
};

export default GradingHeaderCard;
