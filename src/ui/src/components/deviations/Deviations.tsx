import React, { useState, useEffect } from "react";
import { Box, Stack, Button } from "@mui/material";
import DeviationsResult from "./DeviationsResult";
import DeviationsFilter from "@components/deviations/DeviationsFilter";
import styles from "./Deviations.module.scss";
import StatusTabs from "./StatusTabs";
import DeviationsStatusCard from "@components/commonCard/DeviationsStatusCard";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import { useAuth } from "react-oidc-context";
import FileUpload from "@components/FileUpload/FileUpload";
import { useStatus } from "src/context/StatusProvider";
import { fetchDeviations, searchDeviation } from "src/services/deviations";
import Notification from "@components/Notification/Notification";
import { getDeviationsApiResponse } from "src/types";
import PaginationComponent from "@components/pagination/PaginationComponent";

import { usePollingContext } from "@components/polling/PollingProvider";
import { PollingConfig } from "@components/polling/Polling";

const Deviations = () => {
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
  const [data, setData] = useState<getDeviationsApiResponse>();
  const [openFileUpload, setOpenFileUpload] = useState<boolean>(false);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [searchPageNumber, setSearchPageNumber] = useState<number>(1);
  const [searchActive, setSearchActive] = useState<boolean>(false);
  const [deviationId, setDeviationId] = useState("");
  const [loading, setLoading] = useState<boolean>(true);
  const [pagination, setPagination] = useState(initialPagination);
  const [searchPagination, setSearchPagination] = useState(initialPagination);
  const [deviationDetail, setDeviationDetail] =
    useState<getDeviationsApiResponse | null>(null);
  const [openNotification, setOpenNotification] = useState<boolean>(false);

  //Context
  const { activeStatus, setActiveStatus } = useStatus();

  //Polling
  const {
    falseCount,
    error,
    done,
    shouldPoll,
    setShouldPoll,
    setPollingConfig,
  } = usePollingContext();

  useEffect(() => {
    const deviationsCfg: PollingConfig = {
      endpoint: "dev/getDeviation?status=pending&page=1",
      getPendingItems: (data: any) => {
        const pending = data?.deviations ?? [];
        return pending
          .filter((e: any) => e?.text_extracted === false)
          .map((e: any) => ({
            id: e?.deviation_id,
            text_extracted: e?.text_extracted,
          }));
      },
    };
    setPollingConfig(deviationsCfg);
  }, [setPollingConfig, setShouldPoll]);

  // Data unpacking
  const { deviationStats, deviations } = data || {};
  const { pending, processed, overdue } = deviationStats || {};
  const auth = useAuth();
  const displayName = `${auth?.user?.profile?.given_name ?? ""}`.trim();

  // Deviation lists
  const normalDeviations = deviations || [];
  const searchDeviations = deviationDetail?.deviations || [];

  // Breadcrumb items
  const items = [{ label: "Home", to: "/" }, { label: "Deviations" }];

  // Fetch complaints for normal mode
  const fetchData = async (page: number = pageNumber) => {
    setLoading(true);
    try {
      const res = await fetchDeviations(activeStatus, page);
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
      const detail = await searchDeviation(formattedId, page);
      setDeviationDetail(detail);
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
    if (deviationId.trim() !== "") doSearch(deviationId, newPage);
  };
  // Polling related data refresh
  useEffect(() => {
    const fetchOnSingleCardComplete = async () => {
      try {
        const res = await fetchDeviations(activeStatus, pageNumber);
        setData(res);
        setPagination(res?.pagination ?? initialPagination);
      } catch (err: any) {
        console.error(err.message);
      }
    };
    fetchOnSingleCardComplete();
  }, [falseCount]);

  useEffect(() => {
    if (!searchActive) fetchData();
  }, [activeStatus, pageNumber]);

  useEffect(() => {
    const fetchOnAllComplete = async () => {
      try {
        const res = await fetchDeviations(activeStatus, pageNumber);
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
    await fetchData();
  };
  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") return;
    setOpenNotification(false);
  };

  if (loading) return <p>Loading deviations...</p>;

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
            <Button
              variant="contained"
              className={styles.primaryImportButton}
              onClick={() => {
                setOpenFileUpload(true);
                setActiveStatus("pending");
                setPageNumber(1);
                setSearchActive(false);
                setDeviationId("");
              }}
            >
              Import
            </Button>
          </Stack>
        </Stack>
        <div className={styles.statusCards}>
          {" "}
          <DeviationsStatusCard deviationStats={deviationStats} />
        </div>
      </Stack>
      <DeviationsFilter
        setPagination={setSearchPagination}
        setSearchActive={setSearchActive}
        deviationId={deviationId}
        setDeviationId={setDeviationId}
        setDeviationDetail={setDeviationDetail}
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
          {normalDeviations.length === 0 ? (
            <p>No deviations found for status '{activeStatus}'.</p>
          ) : (
            normalDeviations.map((deviation, index) => (
              <DeviationsResult
                key={deviation.deviation_id || index}
                deviation={deviation}
                selected={activeStatus}
                activeStatus={activeStatus}
                loading={
                  shouldPoll &&
                  !deviation.text_extracted &&
                  activeStatus === "pending"
                }
                searching={false}
              />
            ))
          )}
          {normalDeviations.length > 0 && (
            <PaginationComponent
              pagination={pagination}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
      {searchActive && (
        <>
          {searchDeviations?.map((deviation, index) => (
            <DeviationsResult
              key={deviation.deviation_id || index}
              deviation={deviation}
              selected={activeStatus}
              activeStatus={activeStatus}
              loading={
                shouldPoll &&
                !deviation.text_extracted &&
                activeStatus === "pending"
              }
              searching={true}
            />
          ))}
          {searchDeviations?.length > 0 && (
            <PaginationComponent
              pagination={searchPagination}
              onPageChange={handleSearchPageChange}
            />
          )}
        </>
      )}
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

export default Deviations;
