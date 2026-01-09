import React from "react";
import styles from "./DeviationsHeaderCard.module.scss";

import { Paper, Box, Stack, Typography } from "@mui/material";
import { getDueStatus } from "src/helpers";
import DeviationsDueDateChip from "./DeviationsDueDateChip";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import { formatDateMMM_D_YYYY } from "src/utils";

type DeviationData = {
  deviationData: {
    deviation_id: string;
    created_date: string;
    rca_approved: boolean;
    grading_approved: boolean;
  };
};

const GradingHeaderCard: React.FC<DeviationData> = ({
  deviationData,
}) => {
  const { deviation_id, created_date, rca_approved, grading_approved } =
    deviationData;
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
            </Stack>
          </Stack>
        </Box>
      </Box>
    </Paper>
  );
};

export default GradingHeaderCard;
