import React from 'react';
import { Box, Link, Typography } from '@mui/material';
import AISummaryIcon from "../../assets/icons/aiSummary.svg";

const ComplaintAISummary: React.FC = () => {
  return (
    <Box
      sx={{
        border: "1.5px solid",
        borderColor: "primary.main",
        borderRadius: 2,
        mt: 3,
        padding: (theme) => theme.spacing(1, 2),
        width: "100%",
        boxSizing: "border-box",
        fontFamily: (theme) => theme.typography.fontFamily,
        mb: 2,
        backgroundColor: "background.paper", // white background from theme
      }}
    >
      <Box
        sx={{
          display: "inline-flex",
          alignItems: "center",
          paddingX: 0.75,
          fontWeight: "bold",
          fontSize: 12,
          marginBottom: 0.5,
          gap: 0.5,
          backgroundColor: "background.paper", // ensure label background also white
        }}
      >
        <img src={AISummaryIcon} alt="AI Summary Icon" />
        <Typography
          component="span"
          sx={{
            fontFamily: "'Roboto', sans-serif",
            fontWeight: 600,
            fontSize: 16,
            lineHeight: "100%",
            letterSpacing: "4%",
            color: '#000000'
          }}
        >
          AI Summary
        </Typography>
      </Box>
      <Typography
        sx={{
          fontFamily: "'Roboto', sans-serif",
          fontWeight: 400,
          fontSize: 16,
          lineHeight: "100%",
          letterSpacing: "4%",
          mt: 1,
          pl: 2,
          mb: 2,
          color: '#272D37'
        }}
      >
        A patient can ensure that the medication was delivered by first observing
        the medication within the syringe prior to injection and visually
        confirming the medication is no longer in the syringe following the
        injection. Dose delivery for the Pen is confirmed by seeing the gray
        plunger at the top of the clear base.{" "}
        <Link
          href="#"
          underline="always"
          sx={{
            fontFamily: 'Roboto, sans-serif',
            fontWeight: 400,
            fontStyle: 'normal',
            fontSize: '16px',
            lineHeight: 1,
            letterSpacing: '0.04em',
            textDecorationThickness: 'auto',
            textDecorationOffset: '0px',
            color: '#0089EB'
          }}
        >
          Read more
        </Link>
      </Typography>
    </Box>
  );
};

export default ComplaintAISummary;