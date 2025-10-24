import React, { useState } from "react";
import {
  Button,
  Divider,
  InputAdornment,
  MenuItem,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import styles from "./ComplaintsFilter.module.scss";
import { GridSearchIcon } from "@mui/x-data-grid";
import moreFilterIcon from "../../assets/icons/moreFilter.svg";

const ComplaintsFilter: React.FC = () => {
  const [search, setSearch] = useState<string>("");
  const [caseType, setCaseType] = useState<string>("");
  const [criticality, setCriticality] = useState<string>("");
  return (
    <Stack
      direction={"row"}
      alignItems={"center"}
      justifyContent={"space-between"}
      mt={2.5}
      className={styles.complaintsFilterCard}
    >
      <TextField
        className={styles.searchField}
        placeholder="Search here..."
        size="small"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        variant="outlined"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <GridSearchIcon />
            </InputAdornment>
          ),
        }}
      />
      <Divider orientation="vertical" flexItem />
      <Select
        id="case-type"
        size="small"
        label=""
        displayEmpty
        value={caseType}
        onChange={(e) => setCaseType(e.target.value)}
        className={styles.selectField}
        renderValue={(selected) => {
          if (selected === "") {
            return "Select Case Type";
          }
          return selected;
        }}
      >
        <MenuItem value={"Case Type 1"}>Case Type 1</MenuItem>
        <MenuItem value={"Case Type 2"}>Case Type 2</MenuItem>
        <MenuItem value={"Case Type 3"}>Case Type 3</MenuItem>
      </Select>
      <Divider orientation="vertical" flexItem />
      <Select
        id="criticality"
        size="small"
        label=""
        displayEmpty
        value={criticality}
        onChange={(e) => setCriticality(e.target.value)}
        className={styles.selectField}
        renderValue={(selected) => {
          if (selected === "") {
            return "Select Criticality";
          }
          return selected;
        }}
      >
        <MenuItem value={"Criticality 1"}>Criticality 1</MenuItem>
        <MenuItem value={"Criticality 2"}>Criticality 2</MenuItem>
        <MenuItem value={"Criticality 3"}>Criticality 3</MenuItem>
      </Select>
      <Button variant="outlined" className={styles.searchButton}>
        Search
      </Button>
      <Button variant="outlined" className={styles.moreFilterButton}>
        <img src={moreFilterIcon} alt="More filter" />
        More Filter
      </Button>
    </Stack>
  );
};

export default ComplaintsFilter;
