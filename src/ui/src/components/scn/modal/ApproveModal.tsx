import React, { useEffect, useState } from "react";
import CommonModal from "@components/common/CommonModal";
import { Box, CircularProgress, Typography } from "@mui/material";
import styles from "./ApproveModal.module.scss";
import { scnApproveReject } from "src/services/scn";
import { ScnApproveRejectResponse } from "src/types";

interface ApproveModalProps {
  open: boolean;
  onClose: () => void;
  onDone: (changeControlRequired: string) => void;
  defaultChangeControl?: string;
  emailId?: string;
}

const ApproveModal: React.FC<ApproveModalProps> = ({
  open,
  onClose,
  onDone,
  defaultChangeControl = "Yes",
  emailId,
}) => {
  const [changeControlRequired, setChangeControlRequired] =
    useState<string>(defaultChangeControl);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync internal state with prop when modal opens
  useEffect(() => {
    if (open) {
      setChangeControlRequired(defaultChangeControl || "No");
      setError(null);
    }
  }, [open, defaultChangeControl]);

  const handleDone = async () => {
    if (!emailId) {
      setError("No SCN record selected.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = {
        action: "APPROVE" as const,
        change_control_required: (changeControlRequired.toLowerCase() === "yes"
          ? "yes"
          : "no") as "yes" | "no",
      };
      const res: ScnApproveRejectResponse = await scnApproveReject(
        emailId,
        payload,
      );
      if (res?.success) {
        onDone(changeControlRequired);
        onClose();
      } else {
        setError(res?.message || "Failed to approve.");
      }
    } catch (err: any) {
      setError(err?.message || "An error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <CommonModal
      open={open}
      onClose={onClose}
      title="Approve"
      width={592}
      actions={[
        {
          label: "Cancel",
          variant: "outlined",
          onClick: onClose,
          classes: styles.actionButton,
        },
        {
          label: isSubmitting ? "Approving…" : "Done",
          variant: "primary",
          onClick: handleDone,
          classes: styles.actionButton,
          disabled: isSubmitting,
        },
      ]}
    >
      <Box>
        <Box mb={3}>
          <Box mb={2}>
            <span className={styles.radioLabel}>Change Control Required?</span>
          </Box>
          <Box display="flex" gap={3}>
            {["No", "Yes"].map((option) => (
              <label key={option} className={styles.radioOption}>
                <input
                  type="radio"
                  name="approveChangeControl"
                  value={option}
                  checked={changeControlRequired === option}
                  onChange={(e) => setChangeControlRequired(e.target.value)}
                  className={styles.radioInput}
                  disabled={isSubmitting}
                />
                {option}
              </label>
            ))}
          </Box>
        </Box>

        {isSubmitting && (
          <Box display="flex" alignItems="center" gap={1} mt={2}>
            <CircularProgress size={16} />
            <Typography fontSize={13}>Approving…</Typography>
          </Box>
        )}
        {error && (
          <Typography sx={{ color: "#d32f2f", fontSize: 13, mt: 1 }}>
            {error}
          </Typography>
        )}
      </Box>
    </CommonModal>
  );
};

export default ApproveModal;
