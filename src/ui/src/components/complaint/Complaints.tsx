import React, { useState, useEffect, MouseEvent } from 'react';
import { Box, Stack, Button } from "@mui/material";
import PlusIcon from "../../assets/icons/plus.svg";
import ImportIcon from "../../assets/icons/import.svg";
import ComplaintsResult from "@components/complaint/ComplaintsResult";
import ComplaintsFilter from "@components/complaint/ComplaintsFilter";
import styles from "./Complaints.module.scss";
import ComplaintsEmptyState from "./ComplaintsEmptyState";
import Popup from "@components/Popup/Popup";
import FileUpload from '@components/FileUpload/FileUpload';
import CommonBreadcrumbs from '@components/commonBreadCrumbs/CommonBreadcrumbs';
import StatusTabs from './StatusTabs';
import ComplaintsStatusCard from '@components/commonCard/ComplaintsStatusCard';
import { createComplaint } from 'src/services/api.service';
import { fetchComplaints } from 'src/services/api.service';
import { getComplaintsApiResponse, CaseStatusKey } from 'src/types';
import { MockComplaintsApiResponse } from 'src/mockData/mockData';
import { mapped } from 'src/constants';
import { useAuth } from "../../auth/useAuth";

const Complaints = () => {
  const [open, setOpen] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>('');
  const [openFileUpload, setOpenFileUpload] = useState<boolean>(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [data, setData] = useState<getComplaintsApiResponse>();
  const [loading, setLoading] = useState<boolean>(true);
  const { caseStats, caseStatus } = data || {};
  const { pending, processed, overdue } = caseStats || {};
  const { user } = useAuth();
  const displayName = `${user?.profile?.given_name ?? ""}`.trim();
  const items = [
    { label: 'Home', to: '/' },
    { label: 'Complaints' },
  ];
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


  const handleCreateComplaint = async () => {
    try {
      const complaintPayload = {
        narrative: inputValue,
      };
      const result = await createComplaint(complaintPayload);
      console.log("Complaint created:", result);
    } catch (error) {
      console.error("Failed to create complaint:", error);
    } finally {
      setOpen(false)
    }
  };

  const selected = mapped[activeIndex]

  useEffect(() => {
  const fetchData = async () => {
    try {
      // const res = await fetchComplaints();
      setData(MockComplaintsApiResponse);
    } catch (err: any) {
      console.log(err.message)
    } finally {
      setLoading(false);
    }
  };

  fetchData();
}, []);

const complaints = caseStatus?.[selected as CaseStatusKey];

if (loading) return <p>Loading complaints...</p>;

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
              Welcome to Complaints dashboard!
            </Box>
          </Box>

          <Stack className={styles.actions} direction="row" spacing={2}>
            <Button variant="outlined" className={styles.addManuallyButton} onClick={handleOpen}>
              <img src={PlusIcon} alt="plus" />
              Add Manually
            </Button>
            <Button variant="contained" className={styles.primaryImportButton} onClick={() => setOpenFileUpload(true)}>
              Import
            </Button>
          </Stack>
        </Stack>
      </Stack>
      {/* For empty state */}
      {/* <ComplaintsEmptyState /> */}
      <ComplaintsStatusCard complaintStats={caseStats} />
       <StatusTabs activeIndex={activeIndex} setActiveIndex={setActiveIndex} pending={pending} processed={processed} overdue={overdue} />
      <ComplaintsFilter />
      {caseStats && complaints?.map((complaint, index) => (
        <ComplaintsResult key={index} complaint={complaint} selected={selected}/>
      ))}
      <Popup open={open} onClose={handleClose} onSubmit={handleCreateComplaint} setInputValue={setInputValue} inputValue={inputValue} />
      <FileUpload
        open={openFileUpload}
        onClose={() => setOpenFileUpload(false)}
        onFileSelect={handleFileSelect}
      />
    </Box>
  );
};

export default Complaints;