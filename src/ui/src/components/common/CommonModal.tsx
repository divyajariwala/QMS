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
import CloseIcon from "@mui/icons-material/Close";
import styles from "./CommonModal.module.scss";

interface ModalAction {
  label: string;
  onClick: () => void;
  variant?: "text" | "outlined" | "contained";
  color?: "primary" | "secondary" | "error";
  disabled?: boolean;
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
            <Typography>{title}</Typography>

            {showCloseIcon && (
              <IconButton
                className={styles.closeIcon}
                onClick={onClose}
                size="small"
              >
                <CloseIcon />
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
            <Button
              key={index}
              variant={action.variant || "contained"}
              color={action.color || "primary"}
              disabled={action.disabled}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          ))}
        </DialogActions>
      )}
    </Dialog>
  );
};

export default CommonModal;
