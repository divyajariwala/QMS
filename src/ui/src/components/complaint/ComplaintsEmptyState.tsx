import React from "react";
import { Button, Stack, Typography } from "@mui/material";
import SecondaryImportIcon from "../../assets/icons/secondaryImport.svg";
import EmptyState from "../../assets/images/emptyState.svg";
import styles from "./ComplaintsEmptyState.module.scss";

const ComplaintsEmptyState: React.FC = () => {
  return (
    <Stack className={styles.complaintsEmptyStateContainer}>
      <img
        src={EmptyState}
        alt="plus"
        className={styles.emptyStateImage}
      />
      <Stack className={styles.innerStack}>
        <Typography className={styles.headerText}>
          There is currently no data to display.
        </Typography>
        <Typography className={styles.subText}>
          To begin, import a file for processing or manually input your narrative.
        </Typography>
        <Button variant="outlined" className={styles.emptyStateImportButton}>
          <img src={SecondaryImportIcon} alt="import" />
          Import
        </Button>
      </Stack>
    </Stack>
  );
};

export default ComplaintsEmptyState;
