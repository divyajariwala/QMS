import React, { useState, useRef, useEffect, useCallback } from "react";
import { Box, Stack, Button, Alert } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import PaginationComponent from "@components/pagination/PaginationComponent";
import styles from "./SupplierPortal.module.scss";
import SCNStatsQuickLinks from "./SCNStatsQuickLinks";
import scnUploadIcon from "../../assets/icons/scnUploadIcon.svg";
import SCNFilter, { FilterOptions } from "@components/scn/SCNFilter";
import { UploadSCNModal } from "./UploadSCNModal";
import SCNInternalReview from "./SCNInternalReview";
import SCNResultCard from "./SCNResultCard";
import { fetchScnSupplierList } from "src/services/scn";
import { ScnFinalItem, ScnFinalSummary } from "src/types";
import SupplierCardSkeleton from "./skeleton/SupplierCardSkeleton";
import SCNStatsSkeleton from "./skeleton/SCNStatsSkeleton";
import TransformIcon from "../../assets/icons/transform.svg";

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
const AUTO_REFRESH_MS = 5 * 60 * 1000; // 5 minutes

function filtersToApiParam(f: FilterOptions): string | undefined {
  if (f.all) return undefined;
  const mapping: { key: keyof FilterOptions; apiVal: string }[] = [
    { key: "approved", apiVal: "approved" },
    { key: "rejected", apiVal: "rejected" },
    { key: "inReview", apiVal: "in_review" },
    { key: "pendingReview", apiVal: "pending_review" },
  ];

  const selected = mapping
    .filter(({ key }) => f[key])
    .map(({ apiVal }) => apiVal);

  if (selected.length === 0 || selected.length === mapping.length)
    return undefined;

  return selected.join(",");
}

// ─── Adapter: ScnFinalItem → SCNResultCard's expected shape ──────────────────
// SCNResultCard expects: id, status, scnNumber, changeClassification,
// supplierRef, notificationDate, plannedImplementationDate, changeType,
// changeTitleSummary, changeTitle, overdueDays

function toCardItem(item: ScnFinalItem) {
  // Normalize status: replace underscores with spaces, uppercase
  const rawStatus = (item.status || "").replace(/_/g, " ").toUpperCase();

  type CardStatus =
    | "SUPPLIER ACTION REQUIRED"
    | "PENDING REVIEW"
    | "IN REVIEW"
    | "APPROVED"
    | "REJECTED";

  let status: CardStatus = "PENDING REVIEW";
  if (rawStatus === "IN REVIEW" || rawStatus === "IN_REVIEW") {
    status = "IN REVIEW";
  } else if (rawStatus === "APPROVED") {
    status = "APPROVED";
  } else if (rawStatus === "REJECTED") {
    status = "REJECTED";
  } else if (rawStatus === "SUPPLIER ACTION REQUIRED") {
    status = "SUPPLIER ACTION REQUIRED";
  }

  return {
    id: item.email_id,
    status,
    scnNumber: item.scn_reference_number || "—",
    changeClassification: item.final_risk_level || "—",
    supplierRef: item.supplier_name || "—",
    notificationDate: formatDate(item.notification_date),
    plannedImplementationDate: formatDate(item.planned_implementation_date),
    changeType: item?.change_classification_supplier,
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
    all: false,
    approved: false,
    rejected: false,
    pendingReview: false,
    supplierActionRequired: false,
    inReview: false,
    openScns: false,
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

  const loadData = useCallback(
    async (
      page: number,
      q: string,
      filters?: FilterOptions,
      isSilent = false,
    ) => {
      if (!isSilent) {
        setLoading(true);
        setError(null);
      }
      const offset = (page - 1) * PAGE_SIZE;
      const filterParam = filters ? filtersToApiParam(filters) : undefined;
      try {
        const res = await fetchScnSupplierList(
          PAGE_SIZE,
          offset,
          q.trim(),
          filterParam,
        );
        if (res.success) {
          setItems(res.data.items ?? []);
          setTotalCount(res.data.count ?? 0);
          setSummary(res.data.summary ?? null);
        } else {
          if (!isSilent) {
            setError(res.message || "Failed to fetch SCN list.");
            setItems([]);
            setTotalCount(0);
          }
        }
      } catch (err: any) {
        if (!isSilent) {
          setError(
            err?.message || "An unexpected error occurred. Please try again.",
          );
          setItems([]);
          setTotalCount(0);
        }
      } finally {
        if (!isSilent) setLoading(false);
      }
    },
    [],
  );

  // Initial load & page/tab/filter changes
  useEffect(() => {
    if (activeSCNTab === "supplier_portal") {
      loadData(currentPage, scnNumber, currentFilters);
    }
  }, [currentPage, activeSCNTab, currentFilters]);

  // Auto-refresh every AUTO_REFRESH_MS (5 minutes) (silent — no spinner, no flicker)
  useEffect(() => {
    if (activeSCNTab !== "supplier_portal") return;
    const id = setInterval(
      () => loadData(currentPage, scnNumber, currentFilters, true),
      AUTO_REFRESH_MS,
    );
    return () => clearInterval(id);
  }, [activeSCNTab, currentPage, scnNumber, currentFilters, loadData]);

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
    if (val.trim() === "") {
      setCurrentPage(1);
      loadData(1, "", currentFilters);
    }
  };

  const handleSearchClick = () => {
    setCurrentPage(1);
    loadData(1, scnNumber, currentFilters);
  };

  return (
    <Box component="main" className={styles.supplierPortal}>
      <Stack direction="column" gap={1}>
        <Stack direction="row" justifyContent="space-between">
          <CommonBreadcrumbs items={breadcrumbItems} />
          <span
            className={styles.switchReviewer}
            onClick={() =>
              setActiveSCNTab(
                activeSCNTab === "supplier_portal"
                  ? "internal_review"
                  : "supplier_portal",
              )
            }
          >
            <img src={TransformIcon} alt="transform icon" />
            {activeSCNTab === "supplier_portal"
              ? "Switch to Reviewer"
              : "Switch to Supplier"}
          </span>
        </Stack>
        {/* Header Section */}
        {activeSCNTab === "supplier_portal" ? (
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            className={styles.headerSection}
          >
            <Box>
              <h1 className={styles.pageTitle}>SCN Supplier</h1>
              <p className={styles.pageSubtitle}>
                A centralized view where users can access and respond to SCNs,
                track submission status, and review feedback in one place
              </p>
            </Box>
            <Box>
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
            </Box>
          </Stack>
        ) : (
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            className={styles.headerSection}
          >
            <Box>
              <h1 className={styles.pageTitle}>SCN Reviewer</h1>
              <p className={styles.pageSubtitle}>
                A centralized view where reviewers can evaluate SCN submissions,
                provide feedback, and approve or request revisions efficiently
              </p>
            </Box>
          </Stack>
        )}
      </Stack>

      {/* Supplier portal tab */}
      {activeSCNTab === "supplier_portal" && (
        <div>
          {/* Stats – skeleton on first load, real data once summary arrives */}
          {loading && !summary ? (
            <SCNStatsSkeleton />
          ) : (
            <SCNStatsQuickLinks stats={stats} />
          )}

          <Stack direction="row" justifyContent="space-between">
            {/* SCN List label */}
            <div className={styles.scnListLabel}>
              {loading ? "SCN List (…)" : `SCN List (${totalCount})`}
            </div>

            {/* Filter Section */}
            <SCNFilter
              scnNumber={scnNumber}
              filters={currentFilters}
              setFilters={setCurrentFilters}
              handleInputChange={handleInputChange}
              handleSearchClick={handleSearchClick}
            />
          </Stack>

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
