import * as React from "react";
import { Box, Typography, Stack, Button } from "@mui/material";
import PlusIcon from "../../assets/icons/plus.svg";
import ImportIcon from "../../assets/icons/import.svg";
import ComplaintsResult from "@components/complaint/ComplaintsResult";
import ComplaintsFilter from "@components/complaint/ComplaintsFilter";
import styles from "./Complaints.module.scss";
import ComplaintsEmptyState from "./ComplaintsEmptyState";

const complaintsData = [
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 02 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Adverse Event"],
    "Due Date": "Oct 09 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint", "Adverse Event"],
    "Due Date": "Oct 10 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 11 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Adverse Event"],
    "Due Date": "Oct 12 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint", "Adverse Event"],
    "Due Date": "Oct 13 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 14 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Adverse Event"],
    "Due Date": "Oct 15 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint", "Adverse Event"],
    "Due Date": "Oct 16 2025",
  },
  {
    Criticality: "NA",
    "Report Type": "NA",
    Category: "NA",
    "Receipt Date": "Aug 04 2025",
    "Case Type": ["Product Complaint"],
    "Due Date": "Oct 17 2025",
  },
];

const Complaints: React.FC = () => {
  return (
    <Box component="main">
      <Stack direction="column" gap={2.5}>
        <Typography
          color="#437EF7"
          sx={{
            fontFamily: "Inter",
            fontWeight: 500,
            fontSize: "14px",
            lineHeight: "20px",
            letterSpacing: "-0.1px",
          }}
        >
          Dashboard
        </Typography>
        <Stack
          direction="row"
          alignItems={"baseline"}
          justifyContent={"space-between"}
        >
          <Typography
            color="#272D37"
            sx={{
              fontFamily: "Inter",
              fontWeight: 600,
              fontSize: "28px",
              lineHeight: "38px",
              letterSpacing: "-1%",
            }}
            className=""
          >
            Complaints
          </Typography>
          <Stack className={styles.actions} direction="row" spacing={2}>
            <Button variant="outlined" className={styles.addManuallyButton}>
              <img src={PlusIcon} alt="plus" />
              Add Manually
            </Button>
            <Button variant="contained" className={styles.primaryImportButton}>
              <img src={ImportIcon} alt="import" />
              Import
            </Button>
          </Stack>
        </Stack>
      </Stack>
      {/* For empty state
      <ComplaintsEmptyState /> */}
      <ComplaintsFilter />
      {complaintsData.map((complaint, index) => (
        <ComplaintsResult key={index} complaint={complaint} />
      ))}
    </Box>
  );
};

export default Complaints;
