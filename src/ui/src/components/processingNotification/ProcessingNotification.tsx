import React from 'react';
import { Box, CircularProgress, Paper, Slide } from '@mui/material';
import styles from './ProcessingNotification.module.scss';

interface ProcessingNotificationProps {
  loading: boolean;
}

const ProcessingNotification: React.FC<ProcessingNotificationProps> = ({ loading }) => {
  return (
    <Slide direction="down" in={loading} mountOnEnter unmountOnExit>
      <Paper elevation={3} className={styles.notificationPaper}>
        <CircularProgress size={24} />
        <Box fontWeight={500}>
          Processing the text
        </Box>
      </Paper>
    </Slide>
  );
};

export default ProcessingNotification;