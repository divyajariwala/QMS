import React, { useState, useEffect } from 'react';
import { Box, Stack } from '@mui/material';
import AdverseEventCard from './AdverseEventCard';
import AdverseEventFilter from './AdverseEventFilter';
import styles from './AdverseEvent.module.scss';
import CommonBreadcrumbs from '@components/commonBreadCrumbs/CommonBreadcrumbs';
import { searchAdverseEvent, fetchAdverseEvent } from 'src/services/api.service';
import { getAdverseEventsApiResponse, searchAdverseEventsApiResponse } from 'src/types';
import PaginationComponent from '@components/pagination/PaginationComponent';
import { useAuth } from 'react-oidc-context';

const AdverseEvent = () => {
  // Initial pagination state
  const initialPagination = {
    current_page: 1,
    total_pages: 0,
    total_items: 0,
    items_per_page: 15,
    has_next: false,
    has_previous: false,
  };

  const [pageNumber, setPageNumber] = useState<number>(1);
  const [data, setData] = useState<getAdverseEventsApiResponse>();
  const [complaintDetail, setComplaintDetail] = useState<searchAdverseEventsApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [pagination, setPagination] = useState(initialPagination);
  const [searchPagination, setSearchPagination] = useState(initialPagination);
  const [complaintId, setComplaintId] = useState('');
  const [searchActive, setSearchActive] = useState<boolean>(false);
  const { user } = useAuth();
  const displayName = `${user?.profile?.given_name ?? ''}`.trim();

  // Breadcrumb items
  const items = [
    { label: 'Home', to: '/' },
    { label: 'Adverse Event' },
  ];

  // Complaints lists
  const normalComplaints = data?.adverse_events || [];
  const searchComplaints = complaintDetail?.adverse_events || [];

  // Fetch complaints for normal mode
  const fetchData = async (page: number = pageNumber) => {
    setLoading(true);
    try {
      const res = await fetchAdverseEvent(page);
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
    const formattedId = id.trim().replace(/\D/g, '');

    if (!formattedId) {
      return;
    }
    try {
      const detail = await searchAdverseEvent(formattedId, page);
      setComplaintDetail(detail);
      setSearchPagination(detail?.pagination ?? initialPagination);
    } catch (err) {
      console.error(err);
    }
  };

  // Change normal pagination page
  const handlePageChange = (newPage: number) => {
    setPageNumber(newPage);
    fetchData(newPage);
  };

  // Change search pagination page
  const handleSearchPageChange = (newPage: number) => {
    if (complaintId.trim() !== '') doSearch(complaintId, newPage);
  };

  // Normal fetch on activeStatus or pageNum change
  useEffect(() => {
    if (!searchActive) fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageNumber]);

  if (loading) return <p>Loading adverse events...</p>;

  return (
    <Box component="main">
      <Stack direction="column" gap={1}>
        <CommonBreadcrumbs items={items} />
        <Stack direction="row" alignItems={'baseline'} justifyContent={'space-between'}>
          <Box className={styles.pageTitle}>
            Hey there, {displayName}!
            <Box className={styles.pageDetails}>Welcome to Adverse Event!</Box>
          </Box>
        </Stack>
      </Stack>
      <AdverseEventFilter
        setPagination={setSearchPagination}
        setSearchActive={setSearchActive}
        complaintId={complaintId}
        setComplaintId={setComplaintId}
        setComplaintDetail={setComplaintDetail}
        doSearch={doSearch}
      />

      {!searchActive && (
        <>
          {normalComplaints.length === 0 ? (
            <p>No complaints found for adverse events.</p>
          ) : (
            normalComplaints.map((complaint, index) => (
              <AdverseEventCard
                key={complaint.case_id || index}
                complaint={complaint}
              />
            ))
          )}
          {normalComplaints.length > 0 && (
            <PaginationComponent pagination={pagination} onPageChange={handlePageChange} />
          )}
        </>
      )}

      {searchActive && (
        <>
          {searchComplaints?.map((complaint, index) => (
              <AdverseEventCard
                key={complaint.case_id || index}
                complaint={complaint}
              />
            ))
          }
          {searchComplaints?.length > 0 && (
            <PaginationComponent pagination={searchPagination} onPageChange={handleSearchPageChange} />
          )}
        </>
      )}
    </Box>
  );
};

export default AdverseEvent;