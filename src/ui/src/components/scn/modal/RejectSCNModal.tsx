import React, { useState } from "react";
import CommonModal from "@components/common/CommonModal";
import AppButton from "@components/common/AppButton";
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
      width={500}
      actions={[]}
    >
      <Box>
        <Box mb={2}>
          <span className={styles.hadding}>
            Please share reason for rejection
          </span>
        </Box>
        <Box mb={3}>
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
        <Box display="flex" justifyContent="center" gap={2} mt={4}>
          <AppButton
            variant="outlined"
            // style={{ minWidth: 137, height: 46 }}
            onClick={onClose}
          >
            Cancel
          </AppButton>
          <AppButton
            variant="primary"
            // style={{ minWidth: 137, height: 46 }}
            onClick={handleSubmit}
          >
            Submit
          </AppButton>
        </Box>
      </Box>
    </CommonModal>
  );
};

export default RejectSCNModal;
