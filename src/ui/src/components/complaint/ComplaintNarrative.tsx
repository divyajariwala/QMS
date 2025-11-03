import React from 'react';
import { Paper, Stack, Box } from '@mui/material';
import styles from './ComplaintNarrative.module.scss';

const ComplaintNarrative = ({narrative}: {narrative: string}) => {
  return (
    <Paper variant="outlined" className={styles.complaintNarrative}>
      <Stack direction="row" alignItems="center" spacing={1} className={styles.header}>
        <Box className={styles.title}>
          Narrative
        </Box>
      </Stack>
      <Box className={styles.body}>
        {narrative}
      </Box>
    </Paper>
  );
};

export default ComplaintNarrative;