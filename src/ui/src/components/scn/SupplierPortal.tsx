import React, { useState, MouseEvent, useRef } from "react";
import { Box, Stack, Button, Typography } from "@mui/material";
import PlusIcon from "../../assets/icons/plus.svg";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import SCNStatusTabs from "@components/scn/SCNStatusTabs";
import SCNResultCard from "@components/scn/SCNResultCard";
import PaginationComponent from "@components/pagination/PaginationComponent";
import styles from "./SupplierPortal.module.scss";
import SCNStatsQuickLinks from "./SCNStatsQuickLinks";
import EmailIcon from "../../assets/icons/email.svg";
import scnUploadIcon from "../../assets/icons/scnUploadIcon.svg";
import SCNTabs from "./SCNTabs";
import SCNFilter, { FilterOptions } from "@components/scn/SCNFilter";
import { UploadSCNModal } from "./UploadSCNModal";
import { useNavigate } from "react-router-dom";
import SCNInternalReview from "./SCNInternalReview";

// Types
export interface SCNStats {
  total: number;
  pendingReview: number;
  inReview: number;
  supplierActionRequired: number;
  openSCNs: number;
  approved: number;
  rejected: number;
  SCNsSummary: number;
}

export interface SCNItem {
  id: string;
  status: "SUPPLIER ACTION REQUIRED" | "PENDING REVIEW" | "IN REVIEW";
  scnNumber: string;
  changeClassification: "Minor" | "Moderate" | "Major";
  supplierRef: string;
  notificationDate: string;
  plannedImplementationDate: string;
  changeType: "Adverse Event" | "Product Complaint";
  changeTitleSummary: string;
  overdueDays?: number;
  changeTitle?: string;
  firstAffectedLotBatch: string;
  materialNumber: string;
  componentNumber: string;
}

type SCNTabStatus = "all" | "under_review" | "processed" | "info_requested";
type SCNTab = "supplier_portal" | "internal_review";

const SupplierPortal: React.FC = () => {
  // Breadcrumb items
  const fileInputRef = useRef<HTMLInputElement>(null);
  const breadcrumbItems = [{ label: "Home", to: "/" }, { label: "SCN" }];
  // Modal state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const navigate = useNavigate();
  // Mock stats data
  const [stats] = useState<SCNStats>({
    total: 231,
    pendingReview: 100,
    inReview: 121,
    supplierActionRequired: 10,
    openSCNs: 10,
    approved: 80,
    rejected: 42,
    SCNsSummary: 122,
  });

  // Tab state
  // const [activeTab, setActiveTab] = useState<SCNTabStatus>("all");
  const [activeSCNTab, setActiveSCNTab] = useState<SCNTab>("supplier_portal");
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scnNumber, setSCNNumber] = useState<string>("");
  const [searchPageNumber, setSearchPageNumber] = useState<number>(1);
  const [searchActive, setSearchActive] = useState<boolean>(false);
  const [searchResults, setSearchResults] = useState<SCNItem[] | null>(null);
  const [searchPagination, setSearchPagination] = useState({
    current_page: 1,
    total_pages: 0,
    total_items: 0,
    items_per_page: 15,
    has_next: false,
    has_previous: false,
  });
  const [currentFilters, setCurrentFilters] = useState<FilterOptions>({
    all: true,
    approved: true,
    rejected: true,
    pendingReview: true,
    supplierActionRequired: true,
    inReview: true,
    openScns: true,
  });

  // Mock SCN data
  const [scnItems] = useState<SCNItem[]>([
    {
      id: "1",
      status: "IN REVIEW",
      scnNumber: "SCN-000231",
      changeClassification: "Moderate",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
      firstAffectedLotBatch: "Batch-001",
      materialNumber: "MAT-123",
      componentNumber: "COMP-456",
    },
    {
      id: "2",
      status: "PENDING REVIEW",
      scnNumber: "SCN-000235",
      changeClassification: "Major",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Product Complaint",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
      firstAffectedLotBatch: "Batch-001",
      materialNumber: "MAT-123",
      componentNumber: "COMP-456",
    },
    {
      id: "3",
      status: "IN REVIEW",
      scnNumber: "SCN-000236",
      changeClassification: "Minor",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Product Complaint",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
      firstAffectedLotBatch: "Batch-001",
      materialNumber: "MAT-123",
      componentNumber: "COMP-456",
    },
    {
      id: "4",
      status: "SUPPLIER ACTION REQUIRED",
      scnNumber: "SCN-000237",
      changeClassification: "Major",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
      firstAffectedLotBatch: "Batch-001",
      materialNumber: "MAT-123",
      componentNumber: "COMP-456",
    },
    {
      id: "5",
      status: "IN REVIEW",
      scnNumber: "SCN-000238",
      changeClassification: "Moderate",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
      firstAffectedLotBatch: "Batch-001",
      materialNumber: "MAT-123",
      componentNumber: "COMP-456",
    },
  ]);

  // Pagination mock
  const [pagination] = useState({
    current_page: 1,
    total_pages: 5,
    total_items: 231,
    items_per_page: 15,
    has_next: true,
    has_previous: false,
  });

  // Tab counts
  const tabCounts = {
    all: 231,
    under_review: 100,
    processed: 121,
    info_requested: 10,
  };

  // Handlers
  const handleAddEmailDocument = (event: MouseEvent<HTMLButtonElement>) => {
    navigate("/scn/add-email-document");
  };

  const handleUploadSCN = () => {
    setUploadModalOpen(true);
  };

  const handleCloseUploadModal = () => {
    setUploadModalOpen(false);
  };

  const handlePageChange = (newPage: number) => {
    setPageNumber(newPage);
  };

  const handleSearchPageChange = (newPage: number) => {
    setSearchPageNumber(newPage);
    if (scnNumber.trim() !== "") doSearch(scnNumber, newPage, currentFilters);
  };

  const handleSeeDetails = (scnId: string) => {
    console.log("See details for:", scnId);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSCNNumber(val);

    if (val.trim() === "") {
      setSearchActive(false);
      setSearchResults(null);
      setSearchPagination({
        current_page: 1,
        total_pages: 0,
        total_items: 0,
        items_per_page: 15,
        has_next: false,
        has_previous: false,
      });
    } else {
      setSearchActive(true);
      doSearch(val, 1, currentFilters);
    }
  };

  const handleSearchClick = () => {
    if (scnNumber.trim() !== "") {
      setSearchActive(true);
      doSearch(scnNumber, 1, currentFilters);
    }
  };

  // Search function - filters SCN items by number and status filters
  const doSearch = async (
    number: string,
    page: number = 1,
    filters?: FilterOptions,
  ) => {
    const formattedNumber = number.trim();

    // Always filter, even if search box is empty
    try {
      const activeFilters = filters || currentFilters;
      if (filters) setCurrentFilters(filters);

      let filtered = scnItems;

      // Filter by SCN number if provided
      if (formattedNumber) {
        filtered = filtered.filter((item) =>
          item.scnNumber.toLowerCase().includes(formattedNumber.toLowerCase()),
        );
      }

      // Apply status filters - only filter if 'all' is false (meaning specific statuses selected)
      if (activeFilters.all === false) {
        filtered = filtered.filter((item) => {
          if (activeFilters.pendingReview && item.status === "PENDING REVIEW")
            return true;
          if (
            activeFilters.supplierActionRequired &&
            item.status === "SUPPLIER ACTION REQUIRED"
          )
            return true;
          if (activeFilters.inReview && item.status === "IN REVIEW")
            return true;
          return false;
        });
      }

      setSearchResults(filtered);

      const itemsPerPage = 15;
      const totalItems = filtered.length;
      const totalPages = Math.ceil(totalItems / itemsPerPage);

      setSearchPagination({
        current_page: page,
        total_pages: totalPages,
        total_items: totalItems,
        items_per_page: itemsPerPage,
        has_next: page < totalPages,
        has_previous: page > 1,
      });
    } catch (err) {
      console.error("Search error:", err);
    }
  };

  return (
    <Box component="main" className={styles.supplierPortal}>
      <Stack direction="column" gap={1}>
        <CommonBreadcrumbs items={breadcrumbItems} />

        {/* Header Section */}
        <Stack
          direction="row"
          alignItems="flex-start"
          justifyContent="space-between"
          className={styles.headerSection}
        >
          <Box>
            <h1 className={styles.pageTitle}>SCN</h1>
            <p className={styles.pageSubtitle}>
              Submit and track Supplier Change Notifications (SCNs)
            </p>
          </Box>
        </Stack>
      </Stack>

      <SCNTabs activeTab={activeSCNTab} setActiveTab={setActiveSCNTab} />

      {/* Supplier portal tab */}
      {activeSCNTab === "supplier_portal" && (
        <div>
          <Stack
            direction="row"
            alignItems="flex-start"
            justifyContent="space-between"
            marginTop={3}
          >
            <h1 className={styles.pageSummaryTitle}>SCN Summary</h1>
            <Stack direction="row" spacing={2} className={styles.actions}>
              {/* <Button
                variant="outlined"
                className={styles.addManuallyButton}
                onClick={handleAddEmailDocument}
              >
                <span className={styles.plusIcon}>
                  <img src={EmailIcon} />
                </span>
                Add Email Document
              </Button> */}
              <Button
                variant="contained"
                className={styles.uploadButton}
                onClick={handleUploadSCN}
              >
                <span className={styles.uploadIcon}>
                  <img src={scnUploadIcon} />
                </span>
                Upload SCN
              </Button>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                accept=".pdf"
              />
            </Stack>
          </Stack>
          <SCNStatsQuickLinks stats={stats} />
          <div className={styles.scnListLabel}>
            SCN List (
            {searchActive ? searchResults?.length || 0 : scnItems.length})
          </div>
          {/* Filter Section */}
          <SCNFilter
            scnNumber={scnNumber}
            setSCNNumber={setSCNNumber}
            setSearchResults={setSearchResults}
            setSearchActive={setSearchActive}
            setPagination={setSearchPagination}
            doSearch={doSearch}
            filters={currentFilters}
            setFilters={setCurrentFilters}
            handleInputChange={handleInputChange}
            handleSearchClick={handleSearchClick}
          />

          {/* SCN List */}
          <Box className={styles.scnList}>
            {searchActive ? (
              searchResults && searchResults.length === 0 ? (
                <p className={styles.noResults}>
                  No SCNs found matching "{scnNumber}".
                </p>
              ) : (
                searchResults?.map((scn) => (
                  <SCNResultCard
                    key={scn.id}
                    scn={scn}
                    onSeeDetails={handleSeeDetails}
                  />
                ))
              )
            ) : scnItems.length === 0 ? (
              <p className={styles.noResults}>No SCNs found.</p>
            ) : (
              scnItems.map((scn) => (
                <SCNResultCard
                  key={scn.id}
                  scn={scn}
                  onSeeDetails={handleSeeDetails}
                />
              ))
            )}
          </Box>

          {/* Pagination */}
          {searchActive
            ? searchResults &&
              searchResults.length > 0 && (
                <PaginationComponent
                  pagination={searchPagination}
                  onPageChange={handleSearchPageChange}
                />
              )
            : scnItems.length > 0 && (
                <PaginationComponent
                  pagination={pagination}
                  onPageChange={handlePageChange}
                />
              )}
        </div>
      )}

      {/* Internal review tab */}
      {activeSCNTab === "internal_review" && <SCNInternalReview />}
      {/* Upload SCN Modal */}
      <UploadSCNModal
        open={uploadModalOpen}
        onClose={handleCloseUploadModal}
        fileInputRef={fileInputRef}
      />
    </Box>
  );
};

export default SupplierPortal;
