import React from "react";
import { Box } from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import ComplaintsDueDateChip from "../../components/complaint/ComplaintsDueDateChip";
import Calendar from "../../assets/icons/calendar.svg";
import CalendarTick from "../../assets/icons/calendarTick.svg";
import styles from "./DeviationsResult.module.scss";
import DeviationStatusStep from "./DeviationStatusStep";
import { getDueStatus } from "src/helpers";
import { DeviationProps, Status } from "src/types";

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