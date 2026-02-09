import React, { useState } from "react";
import { Box, Typography, Button } from "@mui/material";
import CommonModal from "@components/common/CommonModal";
import styles from "./ChangeSCNOutputModal.module.scss";

interface ChangeSCNOutputModalProps {
  open: boolean;
  onClose: () => void;
  onDone: (value: "SCN" | "NON_SCN") => void;
  defaultValue?: "SCN" | "NON_SCN";
}

const ChangeSCNOutputModal: React.FC<ChangeSCNOutputModalProps> = ({
  open,
  onClose,
  onDone,
  defaultValue = "SCN",
}) => {
  const [selected, setSelected] = useState<"SCN" | "NON_SCN">(defaultValue);

  const handleDone = () => {
    onDone(selected);
    onClose();
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
            >
              SCN
            </Button>

            <Button
              className={`${styles.toggleBtn} ${
                selected === "NON_SCN" ? styles.active : ""
              }`}
              onClick={() => setSelected("NON_SCN")}
            >
              Non SCN
            </Button>
          </Box>
        </Box>
      </Box>
    </CommonModal>
  );
};

export default ChangeSCNOutputModal;
