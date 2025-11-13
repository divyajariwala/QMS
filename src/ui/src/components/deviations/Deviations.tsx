import React, { useState } from 'react';
import { Box, Stack, Button } from "@mui/material";
import DeviationsResult from "./DeviationsResult";
import DeviationsFilter from "@components/deviations/DeviationsFilter";
import styles from "./Deviations.module.scss";
import { deviationsData, caseStatsMock } from 'src/mockData/mockData';
import StatusTabs from './StatusTabs';
import DeviationsStatusCard from '@components/commonCard/DeviationsStatusCard';
import CommonBreadcrumbs from '@components/commonBreadCrumbs/CommonBreadcrumbs';
import { useAuth } from "../../auth/useAuth";

const Deviations = () => {
  const [selected, setSelected] = useState('Root Cause Analysis');
  const items = [
    { label: 'Home', to: '/' },
    { label: 'Deviations' },
  ];
  const { user } = useAuth();
  const displayName = `${user?.profile?.given_name ?? ""}`.trim();

  return (
    <Box component="main">
      <Stack direction="column" gap={1}>
        <CommonBreadcrumbs items={items} />
        <Stack
          direction="row"
          alignItems={"baseline"}
          justifyContent={"space-between"}
        >
          <Box className={styles.pageTitle}>
            Hey there, {displayName}!
            <Box className={styles.pageDetails}>
              Welcome to Deviations dashboard!
            </Box>
          </Box>
          <Stack className={styles.actions} direction="row" spacing={1}>
            <Button variant="contained" className={styles.primaryImportButton}>
              Import
            </Button>
          </Stack>
        </Stack>
        <div className={styles.statusCards}> <DeviationsStatusCard complaintStats={caseStatsMock} /></div>
        <div className={styles.statusTabs}> <StatusTabs /></div>
      </Stack>
      <DeviationsFilter />
      {deviationsData.map((deviation, index) => (
        <DeviationsResult key={index} deviation={deviation} />
      ))}
    </Box>
  );
};

export default Deviations;