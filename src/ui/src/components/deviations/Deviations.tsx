import React, { useState, MouseEvent } from 'react';
import { Box, Stack, Button } from "@mui/material";
import ImportIcon from "../../assets/icons/import.svg";
import DeviationsResult from "./DeviationsResult";
import ComplaintsFilter from "@components/complaint/ComplaintsFilter";
import styles from "./Deviations.module.scss";
import { deviationsData } from 'src/mockData/mockData';
import DeviationsBreadcrumbs from './DeviationsBreadcrumbs';

const Deviations = () => {
  return (
    <Box component="main">
      <Stack direction="column" gap={2.5}>
        <DeviationsBreadcrumbs/>
        <Stack
          direction="row"
          alignItems={"baseline"}
          justifyContent={"space-between"}
        >
          <Box className={styles.pageTitle}>
            Deviations
          </Box>
          <Stack className={styles.actions} direction="row" spacing={2}>
            <Button variant="contained" className={styles.primaryImportButton}>
              <img src={ImportIcon} alt="import" />
              Import
            </Button>
          </Stack>
        </Stack>
      </Stack>
      <ComplaintsFilter />
      {deviationsData.map((deviation, index) => (
        <DeviationsResult key={index} deviation={deviation} />
      ))}
    </Box>
  );
};

export default Deviations;