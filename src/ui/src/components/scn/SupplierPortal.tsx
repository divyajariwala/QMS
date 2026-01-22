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
  changeClassification: string;
  supplierRef: string;
  notificationDate: string;
  plannedImplementationDate: string;
  changeType: "Adverse Event" | "Product Complaint";
  changeTitleSummary: string;
  overdueDays?: number;
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
  const [activeTab, setActiveTab] = useState<SCNTabStatus>("all");
  const [activeSCNTab, setActiveSCNTab] = useState<SCNTab>("supplier_portal");
  const [pageNumber, setPageNumber] = useState<number>(1);

  // Mock SCN data
  const [scnItems] = useState<SCNItem[]>([
    {
      id: "1",
      status: "SUPPLIER ACTION REQUIRED",
      scnNumber: "SCN-000231",
      changeClassification: "Lorem ipsum",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
    },
    {
      id: "2",
      status: "PENDING REVIEW",
      scnNumber: "SCN-000235",
      changeClassification: "Lorem ipsum",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Product Complaint",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
    },
    {
      id: "3",
      status: "IN REVIEW",
      scnNumber: "SCN-000236",
      changeClassification: "Lorem ipsum",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Product Complaint",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
    },
    {
      id: "4",
      status: "SUPPLIER ACTION REQUIRED",
      scnNumber: "SCN-000237",
      changeClassification: "Lorem ipsum",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
    },
    {
      id: "5",
      status: "IN REVIEW",
      scnNumber: "SCN-000238",
      changeClassification: "Lorem ipsum",
      supplierRef: "SCN-12345",
      notificationDate: "Jan 04 2026",
      plannedImplementationDate: "Jan 07 2026",
      changeType: "Adverse Event",
      changeTitleSummary:
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
      overdueDays: 5,
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

  const handleSeeDetails = (scnId: string) => {
    console.log("See details for:", scnId);
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

      {/* Tabs Section */}
      {/* <SCNStatusTabs
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        counts={tabCounts}
        setPageNumber={setPageNumber}
      /> */}

      {/* SCN List */}
      <Box className={styles.scnList}>
        SCN List (231)
        {scnItems.length === 0 ? (
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
      {scnItems.length > 0 && (
        <PaginationComponent
          pagination={pagination}
          onPageChange={handlePageChange}
        />
      )}
    </Box>
  );
};

export default SupplierPortal;
