import React from "react";
import { Box, Link } from "@mui/material";
import AISummaryIcon from "../../assets/icons/aiSummary.svg";
import styles from "./ComplaintAISummary.module.scss";

const ComplaintAISummary: React.FC = () => {
  return (
    <Box className={styles.container}>
      <Box className={styles.header}>
        <img src={AISummaryIcon} alt="AI Summary Icon" className={styles.header__icon} />
        <Box component="span" className={styles.header__title}>
          AI Summary
        </Box>
      </Box>
      <Box component="div" className={styles.content}>
        A patient can ensure that the medication was delivered by first observing
        the medication within the syringe prior to injection and visually
        confirming the medication is no longer in the syringe following the
        injection. Dose delivery for the Pen is confirmed by seeing the gray
        plunger at the top of the clear base.{" "}
        <Link href="#" underline="always">
          Read more
        </Link>
      </Box>
    </Box>
  );
};

export default ComplaintAISummary;