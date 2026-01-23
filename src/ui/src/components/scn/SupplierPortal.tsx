import React, { useState, MouseEvent, useRef } from "react";
import { Box, Stack, Button } from "@mui/material";
import PlusIcon from "../../assets/icons/plus.svg";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import SCNStatusTabs from "@components/scn/SCNStatusTabs";
import SCNResultCard from "@components/scn/SCNResultCard";
import PaginationComponent from "@components/pagination/PaginationComponent";
import styles from "./SupplierPortal.module.scss";
import SCNStatsQuickLinks from "./SCNStatsQuickLinks";
import scnPlusIcon from "../../assets/icons/scnPlus.svg";
import scnUploadIcon from "../../assets/icons/scnUploadIcon.svg";
import SCNTabs from "./SCNTabs";
import SCNFilter from "@components/scn/SCNFilter";

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
  changeClassification: "Low" | "Medium" | "High";
  supplierRef: string;
  notificationDate: string;
  plannedImplementationDate: string;
  changeType: "Adverse Event" | "Product Complaint";
  changeTitleSummary: string;
  overdueDays?: number;
  changeTitle?: string;
}

type SCNTabStatus = "all" | "under_review" | "processed" | "info_requested";
type SCNTab = "supplier_portal" | "internal_review";

const SupplierPortal: React.FC = () => {
  // Breadcrumb items
  const fileInputRef = useRef<HTMLInputElement>(null);
  const breadcrumbItems = [
    { label: "Home", to: "/" },
    { label: "Supplier Portal" },
  ];

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

  // Mock SCN data
  const [scnItems] = useState<SCNItem[]>([
    {
      id: "1",
      status: "SUPPLIER ACTION REQUIRED",
      scnNumber: "SCN-000231",
      changeClassification: "Low",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
    },
    {
      id: "2",
      status: "PENDING REVIEW",
      scnNumber: "SCN-000235",
      changeClassification: "High",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Product Complaint",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
    },
    {
      id: "3",
      status: "IN REVIEW",
      scnNumber: "SCN-000236",
      changeClassification: "Medium",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Product Complaint",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
    },
    {
      id: "4",
      status: "SUPPLIER ACTION REQUIRED",
      scnNumber: "SCN-000237",
      changeClassification: "Low",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
    },
    {
      id: "5",
      status: "IN REVIEW",
      scnNumber: "SCN-000238",
      changeClassification: "Medium",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
      changeTitle: "Lorem ipsum dolor",
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
  const handleAddManually = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    console.log("Add SCN Manually clicked");
  };

  const handleUploadSCN = () => {
    console.log("Upload SCN clicked");
  };

  const handlePageChange = (newPage: number) => {
    setPageNumber(newPage);
  };

  const handleSearchPageChange = (newPage: number) => {
    setSearchPageNumber(newPage);
    if (scnNumber.trim() !== "") doSearch(scnNumber, newPage);
  };

  const handleSeeDetails = (scnId: string) => {
    console.log("See details for:", scnId);
  };

  // Search function - filters SCN items by number
  const doSearch = async (number: string, page: number = 1) => {
    const formattedNumber = number.trim();

    if (!formattedNumber) {
      return;
    }

    try {
      // Filter scnItems by matching SCN number (case-insensitive)
      const filtered = scnItems.filter((item) =>
        item.scnNumber.toLowerCase().includes(formattedNumber.toLowerCase()),
      );

      setSearchResults(filtered);

      // Calculate pagination based on filtered results
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
            <h1 className={styles.pageTitle}>Supplier Portal</h1>
            <p className={styles.pageSubtitle}>
              Submit and track Supplier Change Notifications (SCNs)
            </p>
          </Box>
          <Stack direction="row" spacing={2} className={styles.actions}>
            <Button
              variant="outlined"
              className={styles.addManuallyButton}
              onClick={handleAddManually}
            >
              <span className={styles.plusIcon}>
                <img src={scnPlusIcon} />
              </span>
              Add SCN Manually
            </Button>
            <Button
              variant="contained"
              className={styles.uploadButton}
              onClick={() => fileInputRef.current?.click()}
            >
              <span className={styles.uploadIcon}>
                <img src={scnUploadIcon} />
              </span>
              Upload SCN
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleUploadSCN}
              style={{ display: "none" }}
              accept=".pdf"
            />
          </Stack>
        </Stack>
      </Stack>

      <SCNTabs activeTab={activeSCNTab} setActiveTab={setActiveSCNTab} />
      {/* Combined Stats and Quick Links Card */}
      <SCNStatsQuickLinks stats={stats} />

      <div className={styles.scnListLabel}>
        SCN List ({searchActive ? searchResults?.length || 0 : scnItems.length})
      </div>
      {/* Filter Section */}
      <SCNFilter
        scnNumber={scnNumber}
        setSCNNumber={setSCNNumber}
        setSearchResults={setSearchResults}
        setSearchActive={setSearchActive}
        setPagination={setSearchPagination}
        doSearch={doSearch}
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
    </Box>
  );
};

export default SupplierPortal;
