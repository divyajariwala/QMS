import React from "react";
import { Box, Link } from "@mui/material";
import AISummaryIcon from "../../assets/icons/aiSummary.svg";
import styles from "./ComplaintAISummary.module.scss";

const ComplaintAISummary = ({ai_summary}: {ai_summary: string}) => {
  return (
    <Box className={styles.container}>
      <Box className={styles.header}>
        <img src={AISummaryIcon} alt="AI Summary Icon" className={styles.header__icon} />
        <Box component="span" className={styles.header__title}>
          AI Summary
        </Box>
      </Box>
      <Box component="div" className={styles.content}>
        {ai_summary}{" "}
        <Link href="#" underline="always">
          Read more
        </Link>
      </Box>
    </Box>
  );
};

export default ComplaintAISummary;