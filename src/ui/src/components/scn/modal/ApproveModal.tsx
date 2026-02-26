import React, { useEffect, useState } from "react";
import CommonModal from "@components/common/CommonModal";
import { Box, CircularProgress, Typography } from "@mui/material";
import styles from "./ApproveModal.module.scss";
import { scnApproveReject } from "src/services/scn";
import { ScnApproveRejectResponse } from "src/types";

interface ApproveModalProps {
  open: boolean;
  onClose: () => void;
  onDone: (changeControlRequired: string, recordId: string) => void;
  defaultChangeControl?: string;
  defaultRecordId?: string;
  recordIdOptions?: string[];
  emailId?: string;
}

const ApproveModal: React.FC<ApproveModalProps> = ({
  open,
  onClose,
  onDone,
  defaultChangeControl = "Yes",
  defaultRecordId = "",
  recordIdOptions = [
    "CC-23451",
    "CC-23452",
    "CC-23453",
    "CC-23454",
    "CC-23455",
  ],
  emailId,
}) => {
  const [changeControlRequired, setChangeControlRequired] =
    useState<string>(defaultChangeControl);
  const [recordId, setRecordId] = useState<string>(
    defaultRecordId || recordIdOptions[0],
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (changeControlRequired === "No") {
      setRecordId("");
    }
  }, [changeControlRequired]);

  // Reset error when modal opens/closes
  useEffect(() => {
    if (open) setError(null);
  }, [open]);

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
        onDone(changeControlRequired, res.data?.cc_record_id ?? recordId);
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
            {/* NO Radio */}
            <label className={styles.radioOption}>
              <input
                type="radio"
                name="changeControl"
                value="No"
                checked={changeControlRequired === "No"}
                onChange={(e) => setChangeControlRequired(e.target.value)}
                className={styles.radioInput}
                disabled={isSubmitting}
              />
              No
            </label>
            {/* YES Radio */}
            <label className={styles.radioOption}>
              <input
                type="radio"
                name="changeControl"
                value="Yes"
                checked={changeControlRequired === "Yes"}
                onChange={(e) => setChangeControlRequired(e.target.value)}
                className={styles.radioInput}
                disabled={isSubmitting}
              />
              Yes
            </label>
          </Box>
        </Box>
        <Box>
          <Box mb={1}>
            <span className={styles.radioLabel}>Select Record ID Number</span>
          </Box>
          <div className={styles.selectWrapper}>
            <select
              value={recordId}
              onChange={(e) => setRecordId(e.target.value)}
              disabled={changeControlRequired === "No" || isSubmitting}
              className={styles.selectInput}
            >
              {recordIdOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            <span className={styles.selectArrow} />
          </div>
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
