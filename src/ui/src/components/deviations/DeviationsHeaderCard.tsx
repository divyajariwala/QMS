import React from "react";
import styles from "./DeviationsInterHeaderCard.module.scss";

import { Paper, Box, Stack, Typography } from "@mui/material";
import { DeviationInterHeaderCardProps } from "src/types";
import { getDueStatus } from "src/helpers";
import DeviationsDueDateChip from "./DeviationsDueDateChip";
import ReceiptDateIcon from "../../assets/icons/receiptDate.svg";
import { formatDateMMM_D_YYYY } from "src/utils";
import CheckIcon from "@mui/icons-material/Check";

const DeviationHeaderCard: React.FC<DeviationInterHeaderCardProps> = ({
  caseStatus,
  createdAt,
  deviationId,
}) => {
  return (
    <Paper className={styles.paper}>
      <Box className={styles.flexContainer}>
        <Box className={styles.leftSide}>
          <Stack spacing={0.5} className={styles.stackCustom}>
            {caseStatus === "pending" ? (
              <Box className={styles.statusText}>IN REVIEW</Box>
            ) : (
              <Box className={styles.statusText}>
                {caseStatus?.toUpperCase()}
              </Box>
            )}
            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
              flexWrap="nowrap"
              className={styles.topRowInner}
            >
              <Box className={styles.caseIdText}>{deviationId}</Box>
              <div className={styles.infoItem}>
                <div className={styles.infoItem__valueRow}>
                  <img src={ReceiptDateIcon} alt={"date"} />
                  {typeof createdAt === "string" ? (
                    <Typography
                      component="p"
                      className={styles.infoItem__valueText}
                    >
                      {formatDateMMM_D_YYYY(createdAt)}
                    </Typography>
                  ) : (
                    createdAt
                  )}
                </div>
              </div>
              <DeviationsDueDateChip
                type={createdAt && getDueStatus(createdAt).type}
                label={createdAt && getDueStatus(createdAt).label}
              />
              {(caseStatus === "pending" || caseStatus === "overdue") && (
                <button type="button" className={styles.approveSendButton}>
                  <CheckIcon />
                  Submit
                </button>
              )}
            </Stack>
          </Stack>
        </Box>
      </Box>
    </Paper>
  );
};

export default DeviationHeaderCard;
