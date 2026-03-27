import React, { useState, useEffect } from "react";
import CommonModal from "@components/common/CommonModal";
import SelectedFields from "@components/common/SelectedFields";
import FormInput from "@components/common/FormInput";
import { Box, CircularProgress, Typography } from "@mui/material";
import { scnApproveReject } from "src/services/scn";
import styles from "./RequestInfoModal.module.scss";

interface RequestInfoModalProps {
  open: boolean;
  onClose: () => void;
  onDone: () => void;
  emailId?: string;
}

const AVAILABLE_FIELDS = [
  "scn_title_summary",
  "supplier_name",
  "supplier_sites_affected",
  "supplier_contact_information",
  "change_classification_supplier",
  "planned_implementation_date",
  "first_affected_lot_batch",
  "current_state_long_text",
  "proposed_state_long_text",
  "justification_long_text",
  "temporary_change",
  "notification_date",
  "description",
];

const RequestInfoModal: React.FC<RequestInfoModalProps> = ({
  open,
  onClose,
  onDone,
  emailId,
}) => {
  const [selected, setSelected] = useState<string[]>([]);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setSelected([]);
      setComment("");
      setError(null);
    }
  }, [open]);

  const handleSelect = (field: string) => {
    setSelected((prev) =>
      prev.includes(field) ? prev.filter((f) => f !== field) : [...prev, field],
    );
  };

  const handleRemove = (field: string) => {
    setSelected((prev) => prev.filter((f) => f !== field));
  };

  const handleSubmit = async () => {
    if (!emailId) {
      setError("No SCN record selected.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = {
        action: "REQUEST_INFO" as const,
        fields: selected.join(","),
        comment,
      };
      const res = await scnApproveReject(emailId, payload);
      if (res?.success) {
        onDone();
        onClose();
      } else {
        setError(res?.message || "Failed to request info.");
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
      title="Request info"
      width={800}
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
          disabled: selected.length === 0 || !comment.trim() || isSubmitting,
          classes: styles.actionButton,
        },
      ]}
    >
      <div className={styles.wrapper}>
        <div className={styles.title}>Please select the fields to request</div>
        <SelectedFields
          fields={AVAILABLE_FIELDS}
          selected={selected}
          onSelect={handleSelect}
          onRemove={handleRemove}
        />
        <div>
          <div className={styles.commentLabel}>
            Comment<span className={styles.required}>*</span>
          </div>
          <FormInput
            label=""
            value={comment}
            onChange={setComment}
            placeholder="Input text"
            multiline
            rows={3}
            className={styles.commentBox}
            disabled={isSubmitting}
          />
        </div>
        {isSubmitting && (
          <Box display="flex" alignItems="center" gap={1} mt={2}>
            <CircularProgress size={16} />
            <Typography fontSize={13}>Submitting…</Typography>
          </Box>
        )}
        {error && (
          <Typography sx={{ color: "#d32f2f", fontSize: 13, mt: 1 }}>
            {error}
          </Typography>
        )}
      </div>
    </CommonModal>
  );
};

export default RequestInfoModal;
