import React from "react";
import Snackbar from "@mui/material/Snackbar";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import Typography from "@mui/material/Typography";
import styles from "./Notification.module.scss";

interface NotificationProps {
  open: boolean;
  message?: string;
  duration?: number;  // Duration in milliseconds
  onClose: () => void;
}

const Notification: React.FC<NotificationProps> = ({
  open,
  message = "Approved and Sent to QMS",
  duration = 4000,
  onClose,
}) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={onClose}
      anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      message={
        <span className={styles.notificationContent}>
          <CheckCircleIcon className={styles.icon} />
          <Typography component="span">{message}</Typography>
        </span>
      }
      ContentProps={{
        classes: {
          root: styles.notificationContent,
        },
      }}
    />
  );
};

export default Notification;