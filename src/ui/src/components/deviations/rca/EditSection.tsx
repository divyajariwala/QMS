import React from "react";
import {
  FormControl,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import RCACategory from "../../../assets/icons/rcaCategory.svg";

import styles from "./RootCauseAnalysis.module.scss";

interface EditSectionProps {
  title: string;
  value: string;
  options: ReadonlyArray<string>;
  onChange: (next: string) => void;
}

const EditSection: React.FC<EditSectionProps> = ({
  title,
  value,
  options,
  onChange,
}) => {
  return (
    <div className={styles.rcaTimeline}>
      <Stack
        direction="row"
        alignItems="flex-start"
        className={styles.rcaSection}
      >
        <img
          src={RCACategory}
          alt="RCA Category Icon"
          className={styles.rcaMarker}
        />
        <Stack direction="column" className={styles.rcaSubSection}>
          <Typography variant="h6" className={styles.rcaSectionTitle}>
            {title}
          </Typography>
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            sx={{ width: "100%" }}
          >
            <FormControl size="small">
              <Select
                value={value || ""}
                displayEmpty
                onChange={(e) => onChange(String(e.target.value))}
                renderValue={(selected) =>
                  selected ? String(selected) : "Select"
                }
                sx={{
                  "& .MuiSelect-select": {
                    color: "#437EF7",
                    fontSize: "14px",
                    fontWeight: 500,
                    paddingTop: 0,
                    paddingBottom: 0,
                    backgroundColor: "#f5faff",
                  },
                  "&.Mui-disabled .MuiSelect-select": {
                    color: "#437EF7",
                    backgroundColor: "#f5faff",
                    WebkitTextFillColor: "#437EF7",
                  },
                  "& .MuiOutlinedInput-notchedOutline": {
                    border: "none",
                  },
                  "& .MuiSelect-icon": {
                    color: "#607d8b",
                  },
                }}
              >
                <MenuItem value="">
                  <em>Select</em>
                </MenuItem>
                {options.map((opt) => (
                  <MenuItem key={opt} value={opt}>
                    {opt}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </Stack>
      </Stack>
    </div>
  );
}

export default EditSection;