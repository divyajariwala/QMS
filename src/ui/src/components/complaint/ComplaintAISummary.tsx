import React, { useState } from "react";
import { Box, Link } from "@mui/material";
import AISummaryIcon from "../../assets/icons/aiSummary.svg";
import styles from "./ComplaintAISummary.module.scss";

interface ComplaintAISummaryProps {
  ai_summary: string;
}

const MAX_LENGTH = 500;

const ComplaintAISummary: React.FC<ComplaintAISummaryProps> = ({ ai_summary }) => {
  const [expanded, setExpanded] = useState(false);

  if (!ai_summary) return null;

  const isLong = ai_summary.length > MAX_LENGTH;
  const displayedText = !isLong || expanded ? ai_summary : ai_summary.slice(0, MAX_LENGTH) + "...";

  return (
    <Box className={styles.container}>
      <Box className={styles.header}>
        <img
          src={AISummaryIcon}
          alt="AI Summary Icon"
          className={styles.header__icon}
        />
        <Box component="span" className={styles.header__title}>
          AI Summary
        </Box>
      </Box>

      <Box component="div" className={styles.content}>
        {displayedText}{" "}
        {isLong && (
          <Link
            underline="always"
            onClick={() => setExpanded((prev) => !prev)}
            sx={{ cursor: "pointer" }}
            aria-expanded={expanded}
          >
            {expanded ? "" : "Read more"}
          </Link>
        )}
      </Box>
    </Box>
  );
};

export default ComplaintAISummary;