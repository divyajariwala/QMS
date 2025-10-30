import React from "react";
import { Button, Stack, Typography } from "@mui/material";
import SecondaryImportIcon from "../../assets/icons/secondaryImport.svg";
import EmptyState from "../../assets/images/emptyState.svg";
import styles from "./ComplaintsEmptyState.module.scss";

const ComplaintsEmptyState: React.FC = () => {
  return (
    <Stack
      direction="column"
      alignItems={"center"}
      justifyContent={"center"}
      gap={3}
      height={"715px"}
      mt={2.5}
      className={styles.complaintsEmptyStateContainer}
    >
      <img src={EmptyState} alt="plus" width={"160px"} height={"160px"} />
      <Stack
        direction="column"
        alignItems={"center"}
        justifyContent={"center"}
        gap={1}
      >
        <Typography
          color="#202123"
          sx={{
            fontFamily: "Roboto",
            fontWeight: 400,
            fontSize: "20px",
            lineHeight: "28px",
          }}
        >
          There is currently no data to display.
        </Typography>
        <Typography
          color="#6D7175"
          sx={{
            fontFamily: "Roboto",
            fontWeight: 400,
            fontSize: "14px",
            lineHeight: "20px",
          }}
        >
          To begin, import a file for processing or manually input your
          narrative.
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
