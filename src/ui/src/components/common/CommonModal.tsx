import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Box,
  Typography,
  Button,
} from "@mui/material";
import CloseIcon from "../../assets/icons/CloseVector.svg";
import styles from "./CommonModal.module.scss";
import AppButton from "./AppButton";

interface ModalAction {
  label: string;
  onClick: () => void;
  variant?:
    | "primary"
    | "secondary"
    | "outlined"
    | "danger"
    | "success"
    | "ghost";
  color?: string;
  disabled?: boolean;
  classes?: string;
}

interface CommonModalProps {
  open: boolean;
  title?: string;
  onClose: () => void;
  children: React.ReactNode;

  actions?: ModalAction[];

  showCloseIcon?: boolean;
  width?: number | string;
  maxWidth?: number | string;
  hideDivider?: boolean;
}

const CommonModal: React.FC<CommonModalProps> = ({
  open,
  title,
  onClose,
  children,
  actions,
  showCloseIcon = true,
  width = 600,
  maxWidth = "90vw",
  hideDivider = false,
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width,
          maxWidth,
          borderRadius: "10px",
        },
      }}
    >
      {title && (
        <>
          <DialogTitle className={styles.dialogTitle}>
            <span>{title}</span>
            {showCloseIcon && (
              <IconButton
                className={styles.closeIcon}
                onClick={onClose}
                size="small"
              >
                <img src={CloseIcon} alt="X" />
              </IconButton>
            )}
          </DialogTitle>

          {!hideDivider && <Box className={styles.divider} />}
        </>
      )}

      <DialogContent className={styles.content}>{children}</DialogContent>

      {actions && actions.length > 0 && (
        <DialogActions className={styles.actions}>
          {actions.map((action, index) => (
            <AppButton
              key={index}
              variant={action.variant || "primary"}
              disabled={action.disabled}
              onClick={action.onClick}
              className={action.classes}
            >
              {action.label}
            </AppButton>
          ))}
        </DialogActions>
      )}
    </Dialog>
  );
};

export default CommonModal;
