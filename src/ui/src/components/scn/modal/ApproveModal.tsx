import React, { useState } from "react";
import CommonModal from "@components/common/CommonModal";
import AppButton from "@components/common/AppButton";
import { Box } from "@mui/material";

interface ApproveModalProps {
  open: boolean;
  onClose: () => void;
  onDone: (changeControlRequired: string, recordId: string) => void;
  defaultChangeControl?: string;
  defaultRecordId?: string;
}

const ApproveModal: React.FC<ApproveModalProps> = ({
  open,
  onClose,
  onDone,
  defaultChangeControl = "Yes",
  defaultRecordId = "",
}) => {
  const [changeControlRequired, setChangeControlRequired] =
    useState<string>(defaultChangeControl);
  const [recordId, setRecordId] = useState<string>(defaultRecordId);

  const handleDone = () => {
    onDone(changeControlRequired, recordId);
    onClose();
  };

  return (
    <CommonModal
      open={open}
      onClose={onClose}
      title="Approve"
      width={500}
      actions={[]}
    >
      <Box sx={{ p: 2 }}>
        <Box mb={3}>
          <Box mb={2}>
            <span style={{ fontWeight: 500, fontSize: 15 }}>
              Change Control Required?
            </span>
          </Box>
          <Box display="flex" gap={3}>
            {["No", "Yes"].map((option) => (
              <label
                key={option}
                style={{ display: "flex", alignItems: "center", gap: 6 }}
              >
                <input
                  type="radio"
                  name="changeControl"
                  value={option}
                  checked={changeControlRequired === option}
                  onChange={() => setChangeControlRequired(option)}
                  style={{ accentColor: "#3b82f6", width: 16, height: 16 }}
                />
                {option}
              </label>
            ))}
          </Box>
        </Box>
        <Box mb={3}>
          <Box mb={1}>
            <span style={{ fontWeight: 500, fontSize: 15 }}>
              Select Record ID Number
            </span>
          </Box>
          <input
            type="text"
            value={recordId}
            onChange={(e) => setRecordId(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              border: "1px solid #ddd",
              borderRadius: 6,
              fontSize: 15,
              backgroundColor: "#f9fafb",
              outline: "none",
            }}
          />
        </Box>
        <Box display="flex" justifyContent="center" gap={2} mt={4}>
          <AppButton
            variant="outlined"
            style={{ minWidth: 137, height: 46 }}
            onClick={onClose}
          >
            Cancel
          </AppButton>
          <AppButton
            variant="primary"
            style={{ minWidth: 137, height: 46 }}
            onClick={handleDone}
          >
            Done
          </AppButton>
        </Box>
      </Box>
    </CommonModal>
  );
};

export default ApproveModal;
