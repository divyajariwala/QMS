import React, { useEffect, useState } from "react";
import CommonModal from "@components/common/CommonModal";
import { Box } from "@mui/material";
import styles from "./ApproveModal.module.scss";

interface ApproveModalProps {
  open: boolean;
  onClose: () => void;
  onDone: (changeControlRequired: string, recordId: string) => void;
  defaultChangeControl?: string;
  defaultRecordId?: string;
  recordIdOptions?: string[];
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
}) => {
  const [changeControlRequired, setChangeControlRequired] =
    useState<string>(defaultChangeControl);
  const [recordId, setRecordId] = useState<string>(
    defaultRecordId || recordIdOptions[0],
  );

  const handleDone = () => {
    onDone(changeControlRequired, recordId);
    onClose();
  };

  useEffect(() => {
    if (changeControlRequired === "No") {
      setRecordId("");
    }
  }, [changeControlRequired]);

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
          label: "Done",
          variant: "primary",
          onClick: handleDone,
          classes: styles.actionButton,
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
              disabled={changeControlRequired === "No"}
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
      </Box>
    </CommonModal>
  );
};

export default ApproveModal;
