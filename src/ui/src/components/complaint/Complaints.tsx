import React, { useState, useEffect, MouseEvent } from 'react';
import { Box, Stack, Button } from '@mui/material';
import PlusIcon from '../../assets/icons/plus.svg';
import ComplaintsResult from '@components/complaint/ComplaintsResult';
import ComplaintsFilter from '@components/complaint/ComplaintsFilter';
import styles from './Complaints.module.scss';
import Popup from '@components/Popup/Popup';
import FileUpload from '@components/FileUpload/FileUpload';
import CommonBreadcrumbs from '@components/commonBreadCrumbs/CommonBreadcrumbs';
import StatusTabs from './StatusTabs';
import ComplaintsStatusCard from '@components/commonCard/ComplaintsStatusCard';
import { createComplaint, fetchComplaints } from 'src/services/api.service';
import { getComplaintsApiResponse, CaseStatusKey } from 'src/types';
import PaginationComponent from '@components/pagination/PaginationComponent';
import { usePolling } from '@components/polling/Polling';
import { useAuth } from '../../auth/useAuth';

const Complaints = () => {
  const initialPagination = {
    current_page: 1,
    total_pages: 0,
    total_items: 0,
    items_per_page: 15,
    has_next: true,
    has_previous: false,
  };

  const [open, setOpen] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>('');
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [openFileUpload, setOpenFileUpload] = useState<boolean>(false);
  const [activeStatus, setActiveStatus] = useState<'pending' | 'processed' | 'overdue'>('pending');
  const [data, setData] = useState<getComplaintsApiResponse>();
  const [loading, setLoading] = useState<boolean>(true);
  const [processingFile, setProcessingFile] = useState<boolean>(false);
  const [pagination, setPagination] = useState(initialPagination);

  const { caseStats, caseStatus } = data || {};
  const { pending, processed, overdue } = caseStats || {};
  const { user } = useAuth();
  const displayName = `${user?.profile?.given_name ?? ''}`.trim();

  const { done, falseCount, error } = usePolling(processingFile);

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
      setOpen(false);
      const complaintPayload = {
        narrative: inputValue,
      };
      await createComplaint(complaintPayload);
      const res = await fetchComplaints(activeStatus, pageNumber);
      setData(res);
      setPagination(res?.pagination);
      setProcessingFile(true);
    } catch (error) {
      console.error('Failed to create complaint:', error);
    }
  };

  const handlePageChange = (newPage: number) => {
    setPageNumber(newPage);
  };

  const selected = activeStatus;

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetchComplaints(activeStatus, pageNumber);
      setData(res);
      setPagination(res?.pagination);
    } catch (err: any) {
      console.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Normal fetch when user changes filters or pages
  useEffect(() => {
    fetchData();
  }, [activeStatus, pageNumber, falseCount]);

  // When polling done, stop loading and refresh data
  useEffect(() => {
    if (done) {
      setProcessingFile(false);
      fetchData();
    }
  }, [done]);

  const handleFileUploadSuccess = async () => {
    await fetchData();  // close modal here
  };

  const complaints = caseStatus?.[selected as CaseStatusKey];

  console.log(error);

  if (loading) return <p>Loading complaints...</p>;

  return (
    <Box component="main">
      <Stack direction="column" gap={1}>
        <CommonBreadcrumbs items={items} />
        <Stack direction="row" alignItems={'baseline'} justifyContent={'space-between'}>
          <Box className={styles.pageTitle}>
            Hey there, {displayName}!
            <Box className={styles.pageDetails}>Welcome to Complaints dashboard!</Box>
          </Box>

          <Stack className={styles.actions} direction="row" spacing={2}>
            <Button variant="outlined" className={styles.addManuallyButton} onClick={(e) => {
              handleOpen(e); setActiveStatus('pending'); setPageNumber(1)
            }}>
              <img src={PlusIcon} alt="plus" />
              Add Manually
            </Button>
            <Button variant="contained" className={styles.primaryImportButton} onClick={() => {
              setOpenFileUpload(true); setActiveStatus('pending'); setPageNumber(1)
            }}>
              Import
            </Button>
          </Stack>
        </Stack>
      </Stack>
      {/* For empty state */}
      {/* <ComplaintsEmptyState /> */}
      <ComplaintsStatusCard complaintStats={caseStats} />
      <StatusTabs setPageNumber={setPageNumber} active={activeStatus} setActive={setActiveStatus} pending={pending} processed={processed} overdue={overdue} />
      <ComplaintsFilter />
      {caseStats && complaints?.map((complaint, index) => {
        const loading = !complaint.text_extracted && activeStatus === 'pending';
        return (
          <ComplaintsResult
            key={index}
            complaint={complaint}
            selected={selected}
            activeStatus={activeStatus}
            loading={loading}
          />
        );
      })}
      {complaints && complaints.length > 0 && <PaginationComponent pagination={pagination} onPageChange={handlePageChange} />}
      <Popup open={open} onClose={handleClose} onSubmit={handleCreateComplaint} setInputValue={setInputValue} inputValue={inputValue} />
      <FileUpload setOpenFileUpload={setOpenFileUpload} onSuccess={handleFileUploadSuccess} setProcessing={setProcessingFile} open={openFileUpload} onClose={() => setOpenFileUpload(false)} onFileSelect={handleFileSelect} />
    </Box>
  );
};

export default Complaints;