import React, { useState, useEffect, MouseEvent } from "react";
import { Box, Stack, Button } from "@mui/material";
import PlusIcon from "../../assets/icons/plus.svg";
import ComplaintsResult from "@components/complaint/ComplaintsResult";
import ComplaintsFilter from "@components/complaint/ComplaintsFilter";
import styles from "./Complaints.module.scss";
import NarrativeManual from "@components/Popup/NarrativeManual";
import FileUpload from "@components/FileUpload/FileUpload";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import StatusTabs from "./StatusTabs";
import ComplaintsStatusCard from "@components/commonCard/ComplaintsStatusCard";
import {
  createComplaint,
  fetchComplaints,
  searchComplaint,
} from "src/services/api.service";
import {
  getComplaintsApiResponse,
  CaseStatusKey,
  searchComplaintsApiResponse,
} from "src/types";
import PaginationComponent from "@components/pagination/PaginationComponent";
import { usePollingContext } from "@components/polling/PollingProvider";
import { PollingConfig } from "@components/polling/Polling";
import Notification from "@components/Notification/Notification";
import { useAuth } from "react-oidc-context";
import { useStatus } from "src/context/StatusProvider";
import Spinner from "@components/common/Spinner/Spinner";

const Complaints = () => {
  // Initial pagination state
  const initialPagination = {
    current_page: 1,
    total_pages: 0,
    total_items: 0,
    items_per_page: 15,
    has_next: false,
    has_previous: false,
  };

  // States
  const [open, setOpen] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>("");
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [searchPageNumber, setSearchPageNumber] = useState<number>(1);
  const [openFileUpload, setOpenFileUpload] = useState<boolean>(false);
  const { activeStatus, setActiveStatus } = useStatus();
  const [data, setData] = useState<getComplaintsApiResponse>();
  const [complaintDetail, setComplaintDetail] =
    useState<searchComplaintsApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [pagination, setPagination] = useState(initialPagination);
  const [searchPagination, setSearchPagination] = useState(initialPagination);
  const [complaintId, setComplaintId] = useState("");
  const [searchActive, setSearchActive] = useState<boolean>(false);
  const [openNotification, setOpenNotification] = useState<boolean>(false);

  // Data unpacking
  const { caseStats, caseStatus } = data || {};
  const { pending, processed, overdue } = caseStats || {};
  const auth = useAuth();
  const displayName = `${auth?.user?.profile?.given_name ?? ""}`.trim();

  // Polling context
  const {
    setShouldPoll,
    falseCount,
    error,
    done,
    shouldPoll,
    setPollingConfig,
  } = usePollingContext();

  useEffect(() => {
    const complaintsCfg: PollingConfig<getComplaintsApiResponse> = {
      endpoint: "dev/getComplaints?status=pending&page=1",
      getPendingItems: (data: getComplaintsApiResponse) => {
        const pending = data?.caseStatus.pending ?? [];
        return pending
          .filter((e: any) => e?.text_extracted === false)
          .map((e: any) => ({
            id: e?.case_id,
            text_extracted: e?.text_extracted,
          }));
      },
    };
    setPollingConfig(complaintsCfg);
  }, [setPollingConfig]);

  // Breadcrumb items
  const items = [{ label: "Home", to: "/" }, { label: "Complaints" }];

  // Complaints lists
  const normalComplaints = caseStatus?.[activeStatus as CaseStatusKey] || [];
  const searchComplaints = complaintDetail?.search_results || [];

  // Handle opening manual complaint modal
  const handleOpen = (event: MouseEvent<HTMLButtonElement>): void => {
    event.preventDefault();
    setOpen(true);
  };

  // Handle closing manual complaint modal
  const handleClose = (): void => {
    setOpen(false);
  };

  // Handle closing notification
  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") return;
    setOpenNotification(false);
  };

  // Create complaint logic
  const handleCreateComplaint = async () => {
    try {
      setOpen(false);
      const complaintPayload = { narrative: inputValue };
      await createComplaint(complaintPayload);
      await fetchData(1); // reset to page 1 to show fresh data
      setPageNumber(1);
      setSearchActive(false);
      setComplaintId("");
      setShouldPoll(true);
    } catch (err) {
      console.error("Failed to create complaint:", err);
    }
  };

  // Fetch complaints for normal mode
  const fetchData = async (page: number = pageNumber) => {
    setLoading(true);
    try {
      const res = await fetchComplaints(activeStatus, page);
      setData(res);
      setPagination(res?.pagination ?? initialPagination);
    } catch (err: any) {
      console.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search complaints with pagination
  const doSearch = async (id: string, page: number = 1) => {
    const formattedId = id.trim().replace(/\D/g, "");

    if (!formattedId) {
      return;
    }
    try {
      const detail = await searchComplaint(formattedId, page);
      setComplaintDetail(detail);
      setSearchPagination(detail?.pagination ?? initialPagination);
      setSearchPageNumber(detail?.pagination?.current_page ?? page);
    } catch (err) {
      console.error(err);
      setOpenNotification(true);
    }
  };

  // Change normal pagination page
  const handlePageChange = (newPage: number) => {
    setPageNumber(newPage);
    fetchData(newPage);
  };

  // Change search pagination page
  const handleSearchPageChange = (newPage: number) => {
    setSearchPageNumber(newPage);
    if (complaintId.trim() !== "") doSearch(complaintId, newPage);
  };

  // Polling related data refresh
  useEffect(() => {
    const fetchOnSingleCardComplete = async () => {
      try {
        const res = await fetchComplaints(activeStatus, pageNumber);
        setData(res);
        setPagination(res?.pagination ?? initialPagination);
      } catch (err: any) {
        console.error(err.message);
      }
    };
    fetchOnSingleCardComplete();
  }, [falseCount]);

  // Normal fetch on activeStatus or pageNum change
  useEffect(() => {
    if (!searchActive) fetchData();
  }, [activeStatus, pageNumber]);

  // Polling stop & data refresh
  useEffect(() => {
    const fetchOnAllComplete = async () => {
      try {
        const res = await fetchComplaints(activeStatus, pageNumber);
        setData(res);
        setPagination(res?.pagination ?? initialPagination);
      } catch (err: any) {
        console.error(err.message);
      }
    };
    if (done) {
      setShouldPoll(false);
      fetchOnAllComplete();
      if (error) setOpenNotification(true);
    }
  }, [done]);

  const handleFileUploadSuccess = async () => {
    setOpenFileUpload(false);
    await fetchData(); // Refresh on upload success
  };

  if (loading) return <Spinner />;

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
            <Button
              variant="outlined"
              className={styles.addManuallyButton}
              onClick={(e) => {
                handleOpen(e);
                setActiveStatus("pending");
                setPageNumber(1);
                setSearchActive(false);
                setComplaintId("");
              }}
            >
              <img src={PlusIcon} alt="plus" />
              Add Manually
            </Button>
            <Button
              variant="contained"
              className={styles.primaryImportButton}
              onClick={() => {
                setOpenFileUpload(true);
                setActiveStatus("pending");
                setPageNumber(1);
                setSearchActive(false);
                setComplaintId("");
              }}
            >
              Import
            </Button>
          </Stack>
        </Stack>
      </Stack>

      <ComplaintsStatusCard complaintStats={caseStats} />

      <ComplaintsFilter
        setPagination={setSearchPagination}
        setSearchActive={setSearchActive}
        complaintId={complaintId}
        setComplaintId={setComplaintId}
        setComplaintDetail={setComplaintDetail}
        doSearch={doSearch}
      />

      {!searchActive && (
        <>
          <StatusTabs
            setPageNumber={setPageNumber}
            active={activeStatus}
            setActive={setActiveStatus}
            pending={pending}
            processed={processed}
            overdue={overdue}
          />
          {normalComplaints.length === 0 ? (
            <p>No complaints found for status '{activeStatus}'.</p>
          ) : (
            normalComplaints.map((complaint, index) => (
              <ComplaintsResult
                key={complaint.case_id || index}
                complaint={complaint}
                selected={activeStatus}
                activeStatus={activeStatus}
                loading={
                  shouldPoll &&
                  !complaint.text_extracted &&
                  activeStatus === "pending"
                }
                searching={false}
              />
            ))
          )}
          {normalComplaints.length > 0 && (
            <PaginationComponent
              pagination={pagination}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}

      {searchActive && (
        <>
          {searchComplaints?.map((complaint, index) => (
            <ComplaintsResult
              key={complaint.case_id || index}
              complaint={complaint}
              selected={activeStatus}
              activeStatus={activeStatus}
              loading={
                shouldPoll &&
                !complaint.text_extracted &&
                activeStatus === "pending"
              }
              searching={true}
            />
          ))}
          {searchComplaints?.length > 0 && (
            <PaginationComponent
              pagination={searchPagination}
              onPageChange={handleSearchPageChange}
            />
          )}
        </>
      )}

      <NarrativeManual
        open={open}
        onClose={handleClose}
        onSubmit={handleCreateComplaint}
        setInputValue={setInputValue}
        inputValue={inputValue}
      />
      <FileUpload
        setOpenFileUpload={setOpenFileUpload}
        onSuccess={handleFileUploadSuccess}
        setProcessing={setShouldPoll}
        open={openFileUpload}
        onClose={() => setOpenFileUpload(false)}
      />
      <Notification
        open={openNotification}
        onClose={handleCloseNotification}
        position="top"
        message={"Max retries reached"}
        type={"error"}
      />
    </Box>
  );
};

export default Complaints;
