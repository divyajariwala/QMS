import React from "react";
import { Box } from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import ComplaintsDueDateChip from "../../components/complaint/ComplaintsDueDateChip";
import Calendar from "../../assets/icons/calendar.svg";
import CalendarTick from "../../assets/icons/calendarTick.svg";
import styles from "./DeviationsResult.module.scss";
import DeviationStatusStep from "./DeviationStatusStep";

interface DeviationProps {
  deviation: {
    "Recieved Date": string,
    "Processed Date": string,
    "Due Date": string,
    "rcaStatus": string,
    "gradingStatus": string
  };
}

type Status = "completed" | "active" | "inactive";


const getDueStatus = (
  dateStr: string
): {
  type: "Overdue" | "Today" | "Tomorrow" | "Due";
  label: string;
} => {
  const dueDate = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return {
      type: "Overdue",
      label: `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) === 1 ? "" : "s"}`,
    };
  } else if (diffDays === 0) {
    return { type: "Today", label: "Due Today" };
  } else if (diffDays === 1) {
    return { type: "Tomorrow", label: "Due Tomorrow" };
  } else {
    const formattedDate = dueDate
      .toLocaleDateString("en-US", { year: "numeric", month: "short", day: "2-digit" })
      .replace(/,/g, "");
    return { type: "Due", label: `Due on ${formattedDate}` };
  }
};

const DeviationsResult: React.FC<DeviationProps> = ({ deviation }) => {

  return (
    <div className={styles.complaintsCardContainer}>
      <div className={styles.headerRow}>
        <Box>
          <div className={styles.container}>
            <span className={styles.idText}>IN REVIEW</span>
          </div>
          <div className={styles.container}>
            <span className={styles.caseNumberText}>DV-12345</span>

            <div className={styles.dateGroup}>
              <img src={Calendar} className={styles.dateIcon} />
              <span className={styles.label}>Received Date: </span>
              <span className={styles.date}>{deviation["Recieved Date"]}</span>
            </div>

            <div className={styles.dateGroup}>
              <img src={CalendarTick} className={styles.dateIcon} />
              <span className={styles.label}>Processed Date: </span>
              <span className={styles.date}>{deviation["Processed Date"]}</span>
            </div>
          </div>
        </Box>
        <ComplaintsDueDateChip
          type={getDueStatus(deviation["Due Date"]).type}
          label={getDueStatus(deviation["Due Date"]).label}
        />
      </div>

      <div className={styles.infoRow}>
        Deviation description
      </div>

      <div className={styles.bottomRow}>
        <Box className={styles.shortDescription}>
          <DeviationStatusStep rcaStatus={deviation.rcaStatus as Status} gradingStatus={deviation.gradingStatus as Status} />
        </Box>
        <div className={styles.seeDetailsRow}>
          <Box className={styles.seeDetailsText}>Start analysis</Box>
          <KeyboardArrowRightIcon style={{ cursor: "pointer" }} />
        </div>
      </div>
    </div>
  );
};

export default DeviationsResult;