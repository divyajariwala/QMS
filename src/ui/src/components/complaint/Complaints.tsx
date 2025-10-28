import React, { useState, MouseEvent } from 'react';
import { Box, Stack, Button, Breadcrumbs, Link, Typography } from "@mui/material";
import PlusIcon from "../../assets/icons/plus.svg";
import ImportIcon from "../../assets/icons/import.svg";
import ComplaintsResult from "@components/complaint/ComplaintsResult";
import ComplaintsFilter from "@components/complaint/ComplaintsFilter";
import styles from "./Complaints.module.scss";
import ComplaintsEmptyState from "./ComplaintsEmptyState";
import Popup from "@components/Popup/Popup";
import FileUpload from '@components/FileUpload/FileUpload';
import { complaintsData } from 'src/mockData/mockData';
import ComplaintsBreadcrumbs from './ComplaintsBreadcrumbs';
import StatusTabs from './StatusTabs';
import StatusCards from './StatusCards';
import { useAuth } from "../../auth/useAuth";

const Complaints = () => {
  const [open, setOpen] = useState<boolean>(false);
  const [openFileUpload, setOpenFileUpload] = useState<boolean>(false);
  const { user } = useAuth();
  const displayName = `${user?.profile?.given_name ?? ""}`.trim();
  const handleFileSelect = (file: File) => {
    console.log('Selected file:', file);
  };

  const handleOpen = (event: MouseEvent<HTMLButtonElement>): void => {
    event.preventDefault();
    setOpen(true);
  };
  const handleClose = (): void => {
    setOpen(false);
  };

  const handleSubmit = (value: string): void => {
    alert(`Submitted value: ${value}`);
    setOpen(false);
  };

  return (
    <Box component="main">
      <Stack direction="column" gap={2.5}>
        <ComplaintsBreadcrumbs/>
        <Stack
          direction="row"
          alignItems={"baseline"}
          justifyContent={"space-between"}
        >
          <Box className={styles.pageTitle}>
            Hey there, {displayName}!
            <Box className={styles.pageDetails}>
           Welcome to Complaints dashboard!
          </Box>
          </Box>
          
          <Stack className={styles.actions} direction="row" spacing={2}>
            <Button variant="outlined" className={styles.addManuallyButton} onClick={handleOpen}>
              <img src={PlusIcon} alt="plus" />
              Add Manually
            </Button>
            <Button variant="contained" className={styles.primaryImportButton} onClick={() => setOpenFileUpload(true)}>
              <img src={ImportIcon} alt="import" />
              Import
            </Button>
          </Stack>
        </Stack>
      </Stack>
      {/* For empty state */}
      {/* <ComplaintsEmptyState /> */}
      <StatusCards />
      <div className={styles.statusTabs}> <StatusTabs /></div>
      <ComplaintsFilter />
      {complaintsData.map((complaint, index) => (
        <ComplaintsResult key={index} complaint={complaint} />
      ))}
      <Popup open={open} onClose={handleClose} onSubmit={handleSubmit} />
      <FileUpload
        open={openFileUpload}
        onClose={() => setOpenFileUpload(false)}
        onFileSelect={handleFileSelect}
      />
    </Box>
  );
};

export default Complaints;