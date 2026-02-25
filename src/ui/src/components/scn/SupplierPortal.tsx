import React, { useState, useRef, useEffect, useCallback } from "react";
import { Box, Stack, Button, Skeleton, Alert } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import PaginationComponent from "@components/pagination/PaginationComponent";
import styles from "./SupplierPortal.module.scss";
import SCNStatsQuickLinks from "./SCNStatsQuickLinks";
import scnUploadIcon from "../../assets/icons/scnUploadIcon.svg";
import SCNTabs from "./SCNTabs";
import SCNFilter, { FilterOptions } from "@components/scn/SCNFilter";
import { UploadSCNModal } from "./UploadSCNModal";
import SCNInternalReview from "./SCNInternalReview";
import SCNResultCard from "./SCNResultCard";
import { fetchScnSupplierList } from "src/services/scn";
import { ScnFinalItem, ScnFinalSummary } from "src/types";
import SupplierCardSkeleton from "./skeleton/SupplierCardSkeleton";

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

type SCNTab = "supplier_portal" | "internal_review";

const PAGE_SIZE = 50;

// ─── Adapter: ScnFinalItem → SCNResultCard's expected shape ──────────────────
// SCNResultCard expects: id, status, scnNumber, changeClassification,
// supplierRef, notificationDate, plannedImplementationDate, changeType,
// changeTitleSummary, changeTitle, overdueDays

function toCardItem(item: ScnFinalItem) {
  // Normalize status to match SCNResultCard's accepted union values
  const rawStatus = (item.status || "").replace(/_/g, " ").toUpperCase();
  let status: "SUPPLIER ACTION REQUIRED" | "PENDING REVIEW" | "IN REVIEW" =
    "PENDING REVIEW";
  if (rawStatus === "IN REVIEW" || rawStatus === "IN_REVIEW") {
    status = "IN REVIEW";
  } else if (rawStatus === "APPROVED" || rawStatus === "REJECTED") {
    // Show approved/rejected as-is — map them to a neutral status in the card
    status = "PENDING REVIEW";
  }

  return {
    id: item.email_id,
    status,
    scnNumber: item.scn_reference_number || "—",
    changeClassification: item.final_risk_level || "—", // HIGH / MEDIUM / LOW → maps to Major/Moderate/Minor styling
    supplierRef: item.supplier_name || "—",
    notificationDate: formatDate(item.notification_date),
    plannedImplementationDate: formatDate(item.planned_implementation_date),
    changeType: "Adverse Event" as const, // placeholder — not in scnFinalGet response
    changeTitleSummary: item.final_classification || "—",
    changeTitle: item.final_classification || "—",
  };
}

function formatDate(raw: string | null | undefined): string {
  if (!raw) return "—";
  const d = new Date(raw);
  if (isNaN(d.getTime())) return raw;
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

// Main Component

const SupplierPortal: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const searchTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const breadcrumbItems = [{ label: "Home", to: "/" }, { label: "SCN" }];
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [activeSCNTab, setActiveSCNTab] = useState<SCNTab>("supplier_portal");

  // API data
  const [items, setItems] = useState<ScnFinalItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [summary, setSummary] = useState<ScnFinalSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);

  // Search / filter
  const [scnNumber, setSCNNumber] = useState("");
  const [searchActive, setSearchActive] = useState(false);
  const [currentFilters, setCurrentFilters] = useState<FilterOptions>({
    all: true,
    approved: true,
    rejected: true,
    pendingReview: true,
    supplierActionRequired: true,
    inReview: true,
    openScns: true,
  });

  // Derived pagination object for PaginationComponent

  const pagination = {
    current_page: currentPage,
    total_pages: Math.max(1, Math.ceil(totalCount / PAGE_SIZE)),
    total_items: totalCount,
    items_per_page: PAGE_SIZE,
    has_next: currentPage < Math.ceil(totalCount / PAGE_SIZE),
    has_previous: currentPage > 1,
  };

  // Stats derived from API summary

  const stats: SCNStats = {
    total: summary?.total ?? 0,
    pendingReview: summary?.pending_review ?? 0,
    inReview: summary?.in_review ?? 0,
    supplierActionRequired: 0,
    openSCNs: (summary?.pending_review ?? 0) + (summary?.in_review ?? 0),
    approved: summary?.approved ?? 0,
    rejected: summary?.rejected ?? 0,
    SCNsSummary: summary?.total ?? 0,
  };

  // API fetch

  const loadData = useCallback(async (page: number, q: string) => {
    setLoading(true);
    setError(null);
    const offset = (page - 1) * PAGE_SIZE;
    try {
      const res = await fetchScnSupplierList(PAGE_SIZE, offset, q.trim());
      if (res.success) {
        setItems(res.data.items ?? []);
        setTotalCount(res.data.count ?? 0);
        setSummary(res.data.summary ?? null);
      } else {
        setError(res.message || "Failed to fetch SCN list.");
        setItems([]);
        setTotalCount(0);
      }
    } catch (err: any) {
      setError(
        err?.message || "An unexpected error occurred. Please try again.",
      );
      setItems([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load & page/tab changes
  useEffect(() => {
    if (activeSCNTab === "supplier_portal") {
      loadData(currentPage, scnNumber);
    }
  }, [currentPage, activeSCNTab]);

  // Handlers
  const handleUploadSCN = () => setUploadModalOpen(true);
  const handleCloseUploadModal = () => setUploadModalOpen(false);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSCNNumber(val);
    setSearchActive(val.trim() !== "");

    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    searchTimerRef.current = setTimeout(() => {
      setCurrentPage(1);
      loadData(1, val);
    }, 350);
  };

  const handleSearchClick = () => {
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    setCurrentPage(1);
    loadData(1, scnNumber);
  };

  // Clear search from SCNFilter's internal clear
  const handleSetSearchActive = (active: boolean) => {
    setSearchActive(active);
    if (!active) {
      setSCNNumber("");
      setCurrentPage(1);
      loadData(1, "");
    }
  };

  const handleSetSCNNumber = (val: string) => {
    setSCNNumber(val);
  };

  // doSearch shim — required by SCNFilter prop signature
  const doSearch = async (
    number: string,
    page: number = 1,
    _filters?: FilterOptions,
  ) => {
    setCurrentPage(page);
    loadData(page, number);
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

          {/* Stats – skeleton on first load, real data once summary arrives */}
          {loading && !summary ? (
            <Box sx={{ display: "flex", gap: 2, mt: 2, mb: 2 }}>
              {[1, 2, 3].map((i) => (
                <Skeleton
                  key={i}
                  variant="rounded"
                  width="33%"
                  height={100}
                  sx={{ borderRadius: "10px" }}
                />
              ))}
            </Box>
          ) : (
            <SCNStatsQuickLinks stats={stats} />
          )}

          {/* SCN List label */}
          <div className={styles.scnListLabel}>
            {loading ? "SCN List (…)" : `SCN List (${totalCount})`}
          </div>

          {/* Filter Section */}
          <SCNFilter
            scnNumber={scnNumber}
            setSCNNumber={handleSetSCNNumber}
            setSearchResults={() => {}}
            setSearchActive={handleSetSearchActive}
            setPagination={() => {}}
            doSearch={doSearch}
            filters={currentFilters}
            setFilters={setCurrentFilters}
            handleInputChange={handleInputChange}
            handleSearchClick={handleSearchClick}
          />

          {/* Error state */}
          {error && !loading && (
            <Alert
              severity="error"
              sx={{ mt: 2 }}
              action={
                <Button
                  size="small"
                  onClick={() => loadData(currentPage, scnNumber)}
                >
                  Retry
                </Button>
              }
            >
              {error}
            </Alert>
          )}

          {/* SCN List */}
          <Box className={styles.scnList}>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <SupplierCardSkeleton key={i} />
              ))
            ) : !error && items.length === 0 ? (
              <p className={styles.noResults}>
                {searchActive
                  ? `No SCNs found matching "${scnNumber}".`
                  : "No SCNs found."}
              </p>
            ) : (
              !error &&
              items.map((item) => (
                <SCNResultCard key={item.email_id} scn={toCardItem(item)} />
              ))
            )}
          </Box>

          {/* Pagination */}
          {!loading && !error && totalCount > PAGE_SIZE && (
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
