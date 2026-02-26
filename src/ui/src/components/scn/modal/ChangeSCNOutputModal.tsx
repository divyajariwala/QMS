import React, { useState, useEffect } from "react";
import { Box, CircularProgress, Typography, Button } from "@mui/material";
import CommonModal from "@components/common/CommonModal";
import styles from "./ChangeSCNOutputModal.module.scss";
import { toggleClassification } from "src/services/scn";

interface ChangeSCNOutputModalProps {
  open: boolean;
  onClose: () => void;
  onDone: (newClassification: "SCN" | "NON_SCN") => void;
  defaultValue?: "SCN" | "NON_SCN";
  emailId?: string;
}

const ChangeSCNOutputModal: React.FC<ChangeSCNOutputModalProps> = ({
  open,
  onClose,
  onDone,
  defaultValue = "SCN",
  emailId,
}) => {
  const [selected, setSelected] = useState<"SCN" | "NON_SCN">(defaultValue);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setSelected(defaultValue);
      setError(null);
    }
  }, [open, defaultValue]);

  const handleDone = async () => {
    if (!emailId) {
      setError("No SCN record selected.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await toggleClassification(emailId, selected);
      const newClassification: "SCN" | "NON_SCN" =
        res?.new_classification === "SCN" ? "SCN" : "NON_SCN";
      onDone(newClassification);
      onClose();
    } catch (err: any) {
      setError(
        err?.message || "Failed to change SCN output. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

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
          label: "Done",
          variant: "primary",
          onClick: handleDone,
          disabled: isSubmitting,
          classes: styles.actionButton,
        },
      ]}
    >
      <Box className={styles.wrapper}>
        <Typography className={styles.note}>
          <strong>Note:</strong> AI has predicted an output any change to that
          output will redirect the user to the Impact Assessment page. The
          Assessment Summary is enabled when the Predicted Output is set to SCN.
        </Typography>

        <Box className={styles.section}>
          <Typography className={styles.label}>SCN Predicted Output</Typography>

          <Box className={styles.toggleGroup}>
            <Button
              className={`${styles.toggleBtn} ${
                selected === "SCN" ? styles.active : ""
              }`}
              onClick={() => setSelected("SCN")}
              disabled={isSubmitting}
            >
              SCN
            </Button>

            <Button
              className={`${styles.toggleBtn} ${
                selected === "NON_SCN" ? styles.active : ""
              }`}
              onClick={() => setSelected("NON_SCN")}
              disabled={isSubmitting}
            >
              Non SCN
            </Button>
          </Box>
        </Box>

        {isSubmitting && (
          <Box display="flex" alignItems="center" gap={1} mt={2}>
            <CircularProgress size={16} />
            <Typography fontSize={13}>Updating…</Typography>
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

export default ChangeSCNOutputModal;
