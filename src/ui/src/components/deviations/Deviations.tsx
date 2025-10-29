import React, { useState } from 'react';
import { Box, Stack, Button } from "@mui/material";
import DeviationsResult from "./DeviationsResult";
import DeviationsFilter from "@components/deviations/DeviationsFilter";
import styles from "./Deviations.module.scss";
import { deviationsData } from 'src/mockData/mockData';
import StatusTabs from './StatusTabs';
import StatusCards from './StatusCards';
import ButtonGroup from './ButtonGroup';
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
      <Stack direction="column" gap={2.5}>
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
          <Stack className={styles.actions} direction="row" spacing={2}>
            <Button variant="contained" className={styles.primaryImportButton}>
              Import
            </Button>
          </Stack>
        </Stack>
        <div>
      <ButtonGroup selected={selected} onSelect={setSelected} />
    </div>
        <div className={styles.statusCards}> <StatusCards /></div>
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