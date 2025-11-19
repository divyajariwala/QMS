import React from 'react';
import { Box, CircularProgress, Paper, Typography, Slide } from '@mui/material';
import styles from './ProcessingNotification.module.scss';

interface ProcessingNotificationProps {
  loading: boolean;
}

const ProcessingNotification: React.FC<ProcessingNotificationProps> = ({ loading }) => {
  return (
    <Slide direction="down" in={loading} mountOnEnter unmountOnExit>
      <Paper elevation={3} className={styles.notificationPaper}>
        <CircularProgress size={24} />
        <Typography variant="body1" fontWeight={500}>
          Processing the text
        </Typography>
      </Paper>
    </Slide>
  );
};

export default ProcessingNotification;