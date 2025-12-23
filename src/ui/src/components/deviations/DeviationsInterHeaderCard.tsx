import React from "react";
import styles from "./DeviationsInterHeaderCard.module.scss";

import { Paper, Box, Stack, Typography } from "@mui/material";
import { getDueStatus } from "src/helpers";
import DeviationsDueDateChip from "./DeviationsDueDateChip";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import { formatDateMMM_D_YYYY } from "src/utils";

type DeviationData = {
  deviationData: {
    deviation_id: string;
    created_date: string;
    status: string;
  };
};

const DeviationInterHeaderCard: React.FC<DeviationData> = ({
  deviationData,
}) => {
  const { deviation_id, created_date, status } = deviationData;
  return (
    <Paper className={styles.paper}>
      <Box className={styles.flexContainer}>
        <Box className={styles.leftSide}>
          <Stack spacing={0.5} className={styles.stackCustom}>
            {status === "pending" ? (
              <Box className={styles.statusText}>IN REVIEW</Box>
            ) : (
              <Box className={styles.statusText}>{status?.toUpperCase()}</Box>
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
                  <Typography
                    component="p"
                    className={styles.infoItem__valueText}
                  >
                    {formatDateMMM_D_YYYY(created_date)}
                  </Typography>
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

export default DeviationInterHeaderCard;
