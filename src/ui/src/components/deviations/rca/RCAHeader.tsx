import React from "react";
import {
  Box,
  IconButton,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import EditIcon from "../../../assets/icons/pencil.svg";
import DeleteIcon from "../../../assets/icons/delete.svg";
import CloseIcon from "../../../assets/icons/closeCross.svg";
import CheckIcon from "../../../assets/icons/greenTick.svg";
import RestoreIcon from "@mui/icons-material/Restore";

import styles from "./RootCauseAnalysis.module.scss";

interface RcaHeaderProps {
  currentTitle: string;
  isEditing?: boolean;
  onEdit: () => void;
  onDelete: () => void;
  onCancelEdit: () => void;
  onSave: () => void;
  onReset: () => void;
  showReset?: boolean;
}

const RcaHeader: React.FC<RcaHeaderProps> = ({
  currentTitle,
  isEditing = false,
  onEdit,
  onDelete,
  onCancelEdit,
  onSave,
  onReset,
  showReset,
}) => {
  return (
    <Paper elevation={0} className={styles.rcaHeaderBox}>
      <Box className={styles.rcaHeaderInner}>
        <Typography variant="subtitle1" className={styles.rcaHeaderTitle}>
          {currentTitle}
        </Typography>

        {!isEditing && (
          <Stack direction="row" spacing={1}>
            <IconButton
              aria-label="edit"
              onClick={onEdit}
              className={styles.actionButton}
            >
              <img src={EditIcon} alt="Edit Icon" />
            </IconButton>
            <IconButton
              aria-label="delete"
              onClick={onDelete}
              className={styles.actionButton}
            >
              <img src={DeleteIcon} alt="Delete Icon" />
            </IconButton>
            {showReset && (
              <IconButton
                aria-label="restore"
                onClick={onReset}
                className={styles.actionButton}
              >
                <RestoreIcon />
              </IconButton>
            )}
          </Stack>
        )}

        {isEditing && (
          <Stack direction="row" spacing={1}>
            <IconButton
              aria-label="cancel"
              color="error"
              onClick={onCancelEdit}
              className={styles.cancelButton}
            >
              <img src={CloseIcon} alt="Cancel" />
            </IconButton>
            <IconButton
              aria-label="save"
              color="success"
              onClick={onSave}
              className={styles.confirmButton}
            >
              <img src={CheckIcon} alt="Confirm" />
            </IconButton>
          </Stack>
        )}
      </Box>
    </Paper>
  );
};

export default RcaHeader;
