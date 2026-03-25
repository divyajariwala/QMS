import React from "react";
import { Box, Typography } from "@mui/material";
import CommonModal from "@components/common/CommonModal";
import styles from "./ChangeSCNOutputModal.module.scss";

interface ChangeSCNOutputModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  currentStatus: "SCN" | "NON_SCN";
  targetStatus: "SCN" | "NON_SCN";
  isSubmitting?: boolean;
}

const ChangeSCNOutputModal: React.FC<ChangeSCNOutputModalProps> = ({
  open,
  onClose,
  onConfirm,
  currentStatus,
  targetStatus,
  isSubmitting = false,
}) => {
  const currentStatusLabel = currentStatus === "SCN" ? "SCN" : "Non-SCN";
  const targetStatusLabel = targetStatus === "SCN" ? "SCN" : "Non-SCN";

  return (
    <CommonModal
      open={open}
      onClose={onClose}
      title="Change SCN Output"
      width={592}
      actions={[
        {
          label: "Cancel",
          variant: "outlined",
          onClick: onClose,
          disabled: isSubmitting,
          classes: styles.actionButton,
        },
        {
          label: "Proceed",
          variant: "primary",
          onClick: onConfirm,
          disabled: isSubmitting,
          classes: styles.proceedButton,
        },
      ]}
    >
      <Box className={styles.confirmationWrapper}>
        <Typography className={styles.confirmationText}>
          Are you sure you want to change the status from{" "}
          <strong>{currentStatusLabel}</strong> to{" "}
          <strong>{targetStatusLabel}</strong>?.
        </Typography>
      </Box>
    </CommonModal>
  );
};

export default ChangeSCNOutputModal;
