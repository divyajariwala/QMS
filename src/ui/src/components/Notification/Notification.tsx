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
  position: "top" | "bottom";
}

const Notification: React.FC<NotificationProps> = ({
  open,
  message = "Approved and Sent to QMS",
  duration = 4000,
  onClose,
  position
}) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={onClose}
      anchorOrigin={{ vertical: position, horizontal: "center" }}
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