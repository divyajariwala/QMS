import React, { useEffect, useState } from "react";
import CommonModal from "@components/common/CommonModal";
import { Box, CircularProgress, Typography } from "@mui/material";
import styles from "./RejectSCNModal.module.scss";
import { scnApproveReject } from "src/services/scn";

interface RejectSCNModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (comment: string) => void;
  emailId?: string;
}

const RejectSCNModal: React.FC<RejectSCNModalProps> = ({
  open,
  onClose,
  onSubmit,
  emailId,
}) => {
  const [comment, setComment] = useState("");
  const [touched, setTouched] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setError(null);
      setTouched(false);
    }
  }, [open]);

  const handleSubmit = async () => {
    setTouched(true);
    if (!comment.trim()) return;

    if (!emailId) {
      setError("No SCN record selected.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const res = await scnApproveReject(emailId, {
        action: "REJECT",
        reason_for_reject: comment,
      });
      if (res?.success) {
        onSubmit(comment);
        setComment("");
        setTouched(false);
        onClose();
      } else {
        setError(res?.message || "Failed to reject.");
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
      title="Reject"
      width={700}
      actions={[
        {
          label: "Cancel",
          variant: "outlined",
          onClick: onClose,
          classes: styles.actionButton,
        },
        {
          label: isSubmitting ? "Submitting…" : "Submit",
          variant: "primary",
          onClick: handleSubmit,
          classes: styles.actionButton,
          disabled: isSubmitting,
        },
      ]}
    >
      <Box>
        <Box mb={2}>
          <span className={styles.hadding}>
            Please share reason for rejection
          </span>
        </Box>
        <Box mb={1}>
          <span className={styles.label}>
            Comment <span>*</span>
          </span>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            onBlur={() => setTouched(true)}
            placeholder="Input text"
            className={styles.textarea}
            rows={5}
            disabled={isSubmitting}
          />
          {touched && !comment.trim() && (
            <div style={{ color: "#e53935", fontSize: 13, marginTop: 4 }}>
              Comment is required
            </div>
          )}
        </Box>

        {isSubmitting && (
          <Box display="flex" alignItems="center" gap={1} mt={1}>
            <CircularProgress size={16} />
            <Typography fontSize={13}>Submitting…</Typography>
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

export default RejectSCNModal;
