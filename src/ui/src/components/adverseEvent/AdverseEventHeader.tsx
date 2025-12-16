import React from 'react';
import styles from './AdverseEventHeader.module.scss';
import { Paper, Box, Stack, Grid } from '@mui/material';
import { AdverseEventHeaderProps } from 'src/types';

const AdverseEventHeader: React.FC<AdverseEventHeaderProps> = ({
  complaintData
}) => {
  const {
    caseId,
    primaryReporter,
    patientName,
    physicianName,
    drug,
    lotNumber,
    doseAmount,
    expirationDate,
    partNumber
  } = complaintData || {};

  return (
    <Paper className={styles.paper}>
      <Box className={styles.flexContainer}>
        <Box className={styles.leftSide}>
          <Stack spacing={0.5} className={styles.stackCustom}>
            <Stack direction="row" spacing={2} alignItems="center" flexWrap="nowrap" className={styles.topRowInner}>
              <Box className={styles.caseIdText}>{caseId}</Box>
              <Box className={styles.flexGrow} />
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

export default AdverseEventHeader;