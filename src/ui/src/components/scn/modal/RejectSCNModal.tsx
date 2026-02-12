import React, { useState } from "react";
import CommonModal from "@components/common/CommonModal";
import { Box } from "@mui/material";
import styles from "./RejectSCNModal.module.scss";

interface RejectSCNModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (comment: string) => void;
}

const RejectSCNModal: React.FC<RejectSCNModalProps> = ({
  open,
  onClose,
  onSubmit,
}) => {
  const [comment, setComment] = useState("");
  const [touched, setTouched] = useState(false);

  const handleSubmit = () => {
    setTouched(true);
    if (comment.trim()) {
      onSubmit(comment);
      setComment("");
      setTouched(false);
      onClose();
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
          label: "Submit",
          variant: "primary",
          onClick: handleSubmit,
          classes: styles.actionButton,
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
          />
          {touched && !comment.trim() && (
            <div style={{ color: "#e53935", fontSize: 13, marginTop: 4 }}>
              Comment is required
            </div>
          )}
        </Box>
      </Box>
    </CommonModal>
  );
};

export default RejectSCNModal;
