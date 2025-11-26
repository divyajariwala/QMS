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
import { getComplaintsApiResponse, CaseStatusKey, ComplaintDetail, Case } from 'src/types';
import PaginationComponent from '@components/pagination/PaginationComponent';
import { usePollingContext } from '@components/polling/PollingProvider';
import Notification from '@components/Notification/Notification';
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
  const [pagination, setPagination] = useState(initialPagination);
  const [complaintId, setComplaintId] = useState("");
  const [complaintDetail, setComplaintDetail] = useState<ComplaintDetail | null>(null);
  const [searchActive, setSearchActive] = useState<boolean>(false);
  const [openNotification, setOpenNotification] = useState<boolean>(false);

  const { caseStats, caseStatus } = data || {};
  const { pending, processed, overdue } = caseStats || {};
  const { user } = useAuth();
  const displayName = `${user?.profile?.given_name ?? ''}`.trim();

  const {  
    setShouldPoll,  
    falseCount,
    error,
    done,
    shouldPoll
  } = usePollingContext();

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

   const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string,
  ) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenNotification(false);
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
      setShouldPoll(true);
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

  useEffect(() => {
    const fetchOnSingleCardComplete = async () => {
      try {
        const res = await fetchComplaints(activeStatus, pageNumber);
        setData(res);
        setPagination(res?.pagination);
      } catch (err: any) {
        console.error(err.message);
      }
    };
    fetchOnSingleCardComplete();
  }, [falseCount]);



  // Normal fetch when user changes filters or pages
  useEffect(() => {
    fetchData();
  }, [activeStatus, pageNumber]);

  // When polling done, stop loading and refresh data
  useEffect(() => {
    const fetchOnAllComplete = async () => {
      try {
        const res = await fetchComplaints(activeStatus, pageNumber);
        setData(res);
        setPagination(res?.pagination);
      } catch (err: any) {
        console.error(err.message);
      }
    };
    if (done) {
      setShouldPoll(false);
      fetchOnAllComplete();
      if(error){
        setOpenNotification(true);
      }
    }
  }, [done]);

  const handleFileUploadSuccess = async () => {
    setOpenFileUpload(false);
    await fetchData();  // close modal here
  };

  const complaints = caseStatus?.[selected as CaseStatusKey];

  function transformToOutput(input: ComplaintDetail): Case[] {
    const cleanedCaseType = input.case_type.map((ct) => ct.trim());

    const outputObject: Case = {
      case_id: input.case_id,
      criticality: input.criticality,
      report_type: input.report_type,
      receipt_date: input.receipt_date,
      case_type: cleanedCaseType,
      text_extracted: input.text_extracted,
      created_at: input.created_at,
    };

    return [outputObject];
  }

  const searchResult = complaintDetail && transformToOutput(complaintDetail);

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
              handleOpen(e); setActiveStatus('pending'); setPageNumber(1); setSearchActive(false); setComplaintId('')
            }}>
              <img src={PlusIcon} alt="plus" />
              Add Manually
            </Button>
            <Button variant="contained" className={styles.primaryImportButton} onClick={() => {
              setOpenFileUpload(true); setActiveStatus('pending'); setPageNumber(1); setSearchActive(false); setComplaintId('')
            }}>
              Import
            </Button>
          </Stack>
        </Stack>
      </Stack>
      {/* For empty state */}
      {/* <ComplaintsEmptyState /> */}
      <ComplaintsStatusCard complaintStats={caseStats} />
      {!searchActive && <StatusTabs setPageNumber={setPageNumber} active={activeStatus} setActive={setActiveStatus} pending={pending} processed={processed} overdue={overdue} />}
      <ComplaintsFilter setSearchActive={setSearchActive} complaintId={complaintId} setComplaintId={setComplaintId} complaintDetail={complaintDetail} setComplaintDetail={setComplaintDetail} />
      {!searchActive && caseStats && complaints?.map((complaint, index) => {
        const loading = shouldPoll === true ? (!complaint?.text_extracted && activeStatus === 'pending') : false ;
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
      {searchActive && searchResult?.map((complaint, index) => {
        const loading = shouldPoll === true ? (!complaint?.text_extracted && activeStatus === 'pending') : false ;
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
      {!searchActive && complaints && complaints.length > 0 && <PaginationComponent pagination={pagination} onPageChange={handlePageChange} />}
      <Popup open={open} onClose={handleClose} onSubmit={handleCreateComplaint} setInputValue={setInputValue} inputValue={inputValue} />
      <FileUpload setOpenFileUpload={setOpenFileUpload} onSuccess={handleFileUploadSuccess} setProcessing={setShouldPoll} open={openFileUpload} onClose={() => setOpenFileUpload(false)} onFileSelect={handleFileSelect} />
      <Notification open={openNotification} onClose={handleCloseNotification} position="top" message={"Max retries reached"} type={"error"} />
    </Box>
  );
};

export default Complaints;