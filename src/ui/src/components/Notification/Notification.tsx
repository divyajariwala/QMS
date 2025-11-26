import React from "react";
import Snackbar from "@mui/material/Snackbar";
import SnackbarContent from "@mui/material/SnackbarContent";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import Typography from "@mui/material/Typography";
import clsx from "clsx";
import styles from "./Notification.module.scss";

interface NotificationProps {
  open: boolean;
  message?: string;
  duration?: number;
  onClose: () => void;
  position: "top" | "bottom";
  type?: "success" | "error";
}

const Notification: React.FC<NotificationProps> = ({
  open,
  message = "Approved and Sent to QMS",
  duration = 4000,
  onClose,
  position,
  type = "success",
}) => {
  const Icon = type === "success" ? CheckCircleIcon : ErrorIcon;

  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={onClose}
      anchorOrigin={{ vertical: position, horizontal: "center" }}
    >
      <SnackbarContent
        className={clsx(styles.notificationContent, {
          [styles.success]: type === "success",
          [styles.error]: type === "error",
        })}
        message={
          <span className={styles.messageWrapper}>
            <Icon className={styles.icon} />
            <Typography component="span">{message}</Typography>
          </span>
        }
      />
    </Snackbar>
  );
};

export default Notification;