import React from 'react';
import styles from './ComplaintHeaderCard.module.scss';
import CheckIcon from '@mui/icons-material/Check';
import { Paper, Box, Stack, Grid } from '@mui/material';
import ComplaintsDueDateChip from './ComplaintsDueDateChip';
import { ComplaintHeaderCardProps } from 'src/types';
import { getDueStatus } from 'src/helpers';

const ComplaintHeaderCard: React.FC<ComplaintHeaderCardProps> = ({
  complaintData,
  onApproveAndSend,
  caseStatus,
  isApproved
}) => {
  const {
    status,
    caseId,
    overdueDays,
    primaryReporter,
    patientName,
    physicianName,
    drug,
    lotNumber,
    doseAmount,
    expirationDate,
    partNumber,
    receipt_date
  } = complaintData || {};

  return (
    <Paper className={styles.paper}>
      <Box className={styles.flexContainer}>
        <Box className={styles.leftSide}>
          <Stack spacing={0.5} className={styles.stackCustom}>
            {caseStatus === 'processed' ? (
              isApproved ? (
                <Box className={styles.statusTextGreen}>PROCESSED AND SENT TO QMS</Box>
              ) : (
                <Box className={styles.statusText}>{caseStatus.toUpperCase()}</Box>
              )
            ) : caseStatus === 'pending' ? (
              <Box className={styles.statusText}>IN REVIEW</Box>
            ) : (
              <Box className={styles.statusText}>{caseStatus?.toUpperCase()}</Box>
            )}
            <Stack direction="row" spacing={2} alignItems="center" flexWrap="nowrap" className={styles.topRowInner}>
              <Box className={styles.caseIdText}>{caseId}</Box>
              <ComplaintsDueDateChip
                type={receipt_date && getDueStatus(receipt_date).type}
                label={receipt_date && getDueStatus(receipt_date).label}
              />
              <Box className={styles.flexGrow} />
              {(caseStatus !== 'processed') && <button type="button" className={styles.approveSendButton} onClick={onApproveAndSend}>
                <CheckIcon />
                Approve and Send
              </button>}
            </Stack>
          </Stack>

          <Grid container spacing={1} className={styles.infoGridContainer} alignItems="flex-start">
            {/* Left block */}
            <Grid item xs={6} sm={3}>
              <Box className={styles.labelText}>Primary Reporter</Box>
              <Box className={styles.primaryReporterName}>{primaryReporter?.name}</Box>
              <Box className={styles.valueText}>{primaryReporter?.address}</Box>
            </Grid>

            {/* Right block with fields */}
            <Grid item xs={12} sm={8}>
              <Grid container spacing={2}>
                <Grid item xs={8} sm={3}>
                  <Box className={styles.labelText}>Patient Name</Box>
                  <Box className={styles.valueText}>{patientName}</Box>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Box className={styles.labelText}>Physician</Box>
                  <Box className={styles.valueText}>{physicianName}</Box>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Box className={styles.labelText}>Drug</Box>
                  <Box className={styles.valueText}>{drug}</Box>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Box className={styles.labelText}>Lot #</Box>
                  <Box className={styles.valueText}>{lotNumber}</Box>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Box className={`${styles.labelText} ${styles.mt2}`}>Dose Amount</Box>
                  <Box className={styles.valueText}>{doseAmount}</Box>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Box className={`${styles.labelText} ${styles.mt2}`}>Expiration Date</Box>
                  <Box className={styles.valueText}>{expirationDate}</Box>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Box className={`${styles.labelText} ${styles.mt2}`}>Part Number</Box>
                  <Box className={styles.valueText}>{partNumber}</Box>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Paper>
  );
};

export default ComplaintHeaderCard;