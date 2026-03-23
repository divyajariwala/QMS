import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  Box,
  Stack,
  Button,
  Menu,
  CircularProgress,
  Typography,
} from "@mui/material";
import styles from "./SCNInternalReview.module.scss";
import filterIcon from "../../assets/icons/filterListGray.svg";
import SearchIcon from "../../assets/icons/search.svg";
import ButtonGroup from "./ButtonGroup";
import SCNReviewForm from "./SCNReviewForm";
import AppButton from "@components/common/AppButton";
import InfoIcon from "../../assets/icons/information.svg";
import ChangeNotificationModal from "./modal/ChangeNotificationModal";
import SCNExtractedSourcesModal from "./modal/SCNExtractedSourcesModal";
import RightIcon from "../../assets/icons/rightBlue.svg";
import {
  fetchScnDetails,
  fetchScnList,
  editScn,
  scnClassify,
  scnClassificationResults,
} from "src/services/scn";
import { mapScnDetailsToForm } from "src/utils/mapScnDetails";
import { mapScnFormToApi } from "src/utils/mapScnFormToApi";
import ScnListSkeleton from "./skeleton/ScnListSkeleton";
import ApproveModal from "./modal/ApproveModal";
import RejectSCNModal from "./modal/RejectSCNModal";
import ChangeSCNOutputModal from "./modal/ChangeSCNOutputModal";
import SCNFormSkeleton from "./skeleton/SCNFormSkeleton";
import RequestInfoModal from "./modal/RequestInfoModal";
import SCNInternalReviewImpactTab, {
  ImpactClassificationData,
} from "./SCNInternalReviewImpactTab";
import SCNInternalReviewAuditTab from "./SCNInternalReviewAuditTab";
import ScnDetailsSkeleton from "./skeleton/ScnDetailsSkeleton";
import DashboardExample from "@components/scn/InternalReviewStatsComponents";
import ProductComplaints from "../../assets/icons/productComplaint.svg";
import AuditHistoryIcon from "../../assets/icons/revert.svg";
import CommonModal from "@components/common/CommonModal";
import Gauge from "@components/common/GaugeChart";

type FilterState = {
  supplier: string;
  plannedDate: string | null;
  daysRange: string;
  classification: string;
  riskLevel: string;
};

const LIMIT = 10;

const SCNInternalReview: React.FC = () => {
  const [selected, setSelected] = useState<number>(0);
  const [selectedTab, setSelectedTab] = useState("Impact Review");
  const [isEditing, setIsEditing] = useState(false);
  const [open, setOpen] = useState(false);
  // const [openPreview, setOpenPreview] = useState(false);
  const [openRequestInfo, setOpenRequestInfo] = useState(false);
  const [openAuditModal, setOpenAuditModal] = useState(false);
  const [openExtractedSourcesModal, setOpenExtractedSourcesModal] =
    useState(false);
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(
    null,
  );
  const filterMenuOpen = Boolean(filterAnchorEl);
  const [searchValue, setSearchValue] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");

  // Debounced search
  useEffect(() => {
    const handler = setTimeout(() => {
      if (searchValue.trim() !== appliedSearch) {
        resetDetailPanel();
        setAppliedSearch(searchValue.trim());
      }
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [searchValue]);

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };
  const defaultFilters: FilterState = {
    supplier: "",
    plannedDate: null,
    daysRange: "",
    classification: "",
    riskLevel: "",
  };

  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<FilterState>(defaultFilters);

  // Loading and error state
  const [loading, setLoading] = useState(false);
  const [isFirstLoad, setIsFirstLoad] = useState(true); // Control initial synchronized skeleton
  const [error, setError] = useState<string | null>(null);

  // SCN list state
  const [scns, setScns] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [riskLevelSummary, setRiskLevelSummary] = useState<any>(null);
  const [classificationSummary, setClassificationSummary] = useState<any>(null);
  const [scnVolumeTrend, setScnVolumeTrend] = useState<any>(null);
  const [avgProcessingTime, setAvgProcessingTime] = useState<any>(null);
  const [hasMore, setHasMore] = useState(true);
  const [isFetchingMore, setIsFetchingMore] = useState(false);
  const sentinelRef = useRef<HTMLDivElement>(null);

  // Filter options from API
  const [supplierNames, setSupplierNames] = useState<string[]>([]);
  const [classificationList, setClassificationList] = useState<string[]>([]);

  const [scnDetail, setScnDetail] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [impactReviewLoading, setImpactReviewLoading] = useState(false);
  const [isClassifying, setIsClassifying] = useState(false);
  const [impactClassificationData, setImpactClassificationData] =
    useState<ImpactClassificationData | null>(null);
  const [latestPdfUrl, setLatestPdfUrl] = useState<string | null>(null);
  const [openApprove, setOpenApprove] = useState(false);
  const [openReject, setOpenReject] = useState(false);
  const [openPreview, setOpenPreview] = useState(false);
  const [changeControlRequired, setChangeControlRequired] = useState("");
  const [recordId, setRecordId] = useState("");

  // Fetch SCN list with filters + search
  useEffect(() => {
    const loadList = async () => {
      setLoading(true);
      setError(null);
      setScns([]);
      setHasMore(true);
      try {
        const params = new URLSearchParams();
        params.append("limit", String(LIMIT));
        params.append("offset", "0");
        if (appliedFilters.supplier)
          params.append("supplier_name", appliedFilters.supplier);
        if (appliedFilters.classification)
          params.append(
            "change_classification_supplier",
            appliedFilters.classification,
          );
        if (appliedFilters.riskLevel)
          params.append(
            "final_risk_level",
            appliedFilters.riskLevel.toLowerCase(),
          );
        if (appliedFilters.plannedDate)
          params.append(
            "planned_implementation_date",
            appliedFilters.plannedDate,
          );
        if (appliedSearch) params.append("q", appliedSearch);
        const res = await fetchScnList(LIMIT, 0, params);
        const items = res?.data?.items || [];
        const count = res?.data?.count || 0;
        setScns(items);
        setTotal(count);
        setRiskLevelSummary(res?.data?.risk_level_summary || null);
        setClassificationSummary(res?.data?.classification_summary || null);
        setScnVolumeTrend(res?.data?.scn_volume_trend || null);
        setAvgProcessingTime(res?.data?.avg_processing_time || null);
        setHasMore(items.length >= LIMIT && items.length < count);
        // Populate filter dropdown options from the response
        if (res?.data?.supplier_names) {
          setSupplierNames(res.data.supplier_names);
        }
        if (res?.data?.change_classification_supplier_list) {
          setClassificationList(res.data.change_classification_supplier_list);
        }
        if (!items.length) {
          setIsFirstLoad(false);
        }
      } catch (err: any) {
        setError(err.message || "Failed to fetch SCN list");
        setIsFirstLoad(false);
      } finally {
        setLoading(false);
      }
    };
    loadList();
  }, [appliedFilters, appliedSearch]);

  const loadMore = useCallback(async () => {
    if (isFetchingMore || !hasMore) return;
    setIsFetchingMore(true);
    try {
      const newOffset = scns.length;
      const params = new URLSearchParams();
      params.append("limit", String(LIMIT));
      params.append("offset", String(newOffset));
      if (appliedFilters.supplier)
        params.append("supplier_name", appliedFilters.supplier);
      if (appliedFilters.classification)
        params.append(
          "change_classification_supplier",
          appliedFilters.classification,
        );
      if (appliedFilters.riskLevel)
        params.append(
          "final_risk_level",
          appliedFilters.riskLevel.toLowerCase(),
        );
      if (appliedFilters.plannedDate)
        params.append(
          "planned_implementation_date",
          appliedFilters.plannedDate,
        );
      if (appliedSearch) params.append("q", appliedSearch);
      const res = await fetchScnList(LIMIT, newOffset, params);
      const items = res?.data?.items || [];
      setScns((prev) => [...prev, ...items]);
      setHasMore(items.length >= LIMIT && newOffset + items.length < total);
    } catch (err: any) {
      console.error("Load more failed:", err);
    } finally {
      setIsFetchingMore(false);
    }
  }, [
    isFetchingMore,
    hasMore,
    scns.length,
    appliedFilters,
    appliedSearch,
    total,
  ]);

  useEffect(() => {
    const node = sentinelRef.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) loadMore();
      },
      { threshold: 0.1 },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [loadMore]);

  const handleSelectScn = async (item: any) => {
    if (!item?.email_id) return;
    setSelectedEmailId(item.email_id);
    try {
      setDetailLoading(true);
      // Call both APIs in parallel
      const [resDetail, resImpact]: any = await Promise.all([
        fetchScnDetails(item.email_id),
        scnClassificationResults(item.email_id),
      ]);

      if (resDetail?.data) {
        const mapped = mapScnDetailsToForm(resDetail.data);
        setScnDetail(mapped);

        const attachments: any[] = resDetail.data.attachments || [];
        const doneWithUrl = attachments.filter(
          (a) => a.status === "DONE" && !!a.download_url,
        );
        const latestAttachment = doneWithUrl.sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        )[0];
        setLatestPdfUrl(latestAttachment?.download_url ?? null);
      }

      if (resImpact?.success !== false) {
        const data: ImpactClassificationData =
          resImpact?.data ?? resImpact ?? {};
        setImpactClassificationData(data);
      } else {
        setImpactClassificationData(null);
      }
    } catch (error) {
      console.error("Failed to fetch SCN details or impact results", error);
    } finally {
      setDetailLoading(false);
      setIsFirstLoad(false);
    }
  };
  const [validationErrors, setValidationErrors] = useState<
    Record<string, boolean>
  >({});

  const handleSaveClick = async () => {
    if (!selectedEmailId || !scnDetail) return;

    const errors: Record<string, boolean> = {};
    let hasError = false;

    // Required fields to validate
    const requiredFields = [
      "proposedState",
      "supplierContactInfo",
      "changeTimingPlannedDate",
      "firstAffectedLotBatch",
      "materialNumber",
      "componentNumber",
    ];

    requiredFields.forEach((field) => {
      if (!scnDetail[field as keyof typeof scnDetail]) {
        errors[field] = true;
        hasError = true;
      }
    });

    if (hasError) {
      setValidationErrors(errors);
      return;
    }

    setValidationErrors({});

    try {
      const apiFields = mapScnFormToApi(scnDetail);
      const res = await editScn(selectedEmailId, apiFields);
      if (res?.success) {
        setIsEditing(false);
        await handleSelectScn({ email_id: selectedEmailId });
      }
    } catch (error) {
      console.error("Edit failed:", error);
    }
  };

  const handleCancelClick = async () => {
    if (!selectedEmailId) return;
    setValidationErrors({});
    setIsEditing(false);
    await handleSelectScn({ email_id: selectedEmailId });
  };

  // Removed handleImpactReview as per new flow requirements

  /** Fetches the latest impact classification data for the selected SCN */
  const loadImpactData = useCallback(async () => {
    if (!selectedEmailId) return;
    setImpactReviewLoading(true);
    try {
      const res = await scnClassificationResults(selectedEmailId);
      if (res?.success === false) {
        setImpactClassificationData(null);
      } else {
        const data: ImpactClassificationData = res?.data ?? res ?? {};
        setImpactClassificationData(data);
      }
    } catch (err) {
      console.error("Failed to load Impact Assessment data:", err);
      setImpactClassificationData(null);
    } finally {
      setImpactReviewLoading(false);
    }
  }, [selectedEmailId]);

  const handleTabSelect = async (tab: string) => {
    setSelectedTab(tab);
    if (tab === "Impact Review" && selectedEmailId) {
      await loadImpactData();
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setScnDetail((prev: any) => ({
      ...prev,
      [field]: value,
    }));
  };

  const getClassificationClass = (status: string) => {
    switch (status) {
      case "Minor":
        return styles.statusLow;
      case "Moderate":
        return styles.statusMedium;
      case "Major":
        return styles.statusHigh;
      default:
        return "";
    }
  };

  const handleFilterChange = <K extends keyof FilterState>(
    key: K,
    value: FilterState[K],
  ) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const queueItems = useMemo(() => {
    return scns.map((item) => ({
      scn_reference_number: item.scn_reference_number,
      supplier_name: item.supplier_name,
      change_classification_supplier: item.change_classification_supplier,
      completion_score: item.completion_score || 0,
      status: item.status,
      email_id: item.email_id,
      notification_date: item.notification_date,
      planned_implementation_date: item.planned_implementation_date,
      final_risk_level: item.final_risk_level,
    }));
  }, [scns]);

  const resetDetailPanel = () => {
    setSelectedEmailId(null);
    setScnDetail(null);
    setImpactClassificationData(null);
    setSelected(0);
    setSelectedTab("Impact Review");
    setScnVolumeTrend(null);
    setAvgProcessingTime(null);
    setIsFirstLoad(true);
  };

  const handleApplyFilters = () => {
    resetDetailPanel();
    setAppliedFilters(filters);
    handleFilterClose();
  };

  const handleClearFilters = () => {
    resetDetailPanel();
    setFilters(defaultFilters);
    setAppliedFilters(defaultFilters);
    handleFilterClose();
  };

  useEffect(() => {
    if (scns.length > 0 && !selectedEmailId) {
      setSelected(0);
      handleSelectScn(scns[0]);
    }
  }, [scns]);

  const getStatusClass = (status: string) => {
    switch (status) {
      case "SUPPLIER ACTION REQUIRED":
        return styles.statusRed;
      case "PENDING REVIEW":
        return styles.statusYellow;
      case "IN_REVIEW":
        return styles.statusGreen;
      case "APPROVED":
        return styles.statusApproved;
      case "REJECTED":
        return styles.statusRejected;
      default:
        return "";
    }
  };

  return (
    <Box component="main" className={styles.container}>
      <DashboardExample
        total={total}
        riskLevelSummary={riskLevelSummary}
        classificationSummary={classificationSummary}
        scnVolumeTrend={scnVolumeTrend}
        avgProcessingTime={avgProcessingTime}
        onRiskLevelClick={(level) => {
          resetDetailPanel();
          setFilters((prev) => ({ ...prev, riskLevel: level }));
          setAppliedFilters((prev) => ({ ...prev, riskLevel: level }));
        }}
      />

      <Stack gap={2}>
        {/* Content */}
        <Box className={styles.contentWrapper}>
          {/* left – Queue List */}
          <Box className={styles.mailList}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              className={styles.mailHeader}
            >
              <span className={styles.mailHeaderTitle}>Queue ({total})</span>
            </Stack>

            <Box className={styles.mailListSub}>
              <Stack
                direction="row"
                gap={1}
                alignItems="center"
                marginBottom={2}
              >
                <div className={styles.searchBar}>
                  <div className={styles.inputWrapper}>
                    <img
                      src={SearchIcon}
                      alt="Search"
                      className={styles.searchIcon}
                    />
                    <input
                      type="text"
                      placeholder="Search here..."
                      aria-label="Search by SCN number"
                      className={styles.searchInput}
                      value={searchValue}
                      onChange={(e) => {
                        const value = e.target.value;
                        setSearchValue(value);
                      }}
                    />
                  </div>
                </div>
                <Box>
                  <Button
                    size="small"
                    variant="outlined"
                    className={styles.filterButton}
                    onClick={(event) => setFilterAnchorEl(event.currentTarget)}
                  >
                    Filter
                    <img src={filterIcon} alt="filter" />
                  </Button>
                  {/* Filter Dropdown */}
                  {filterMenuOpen && (
                    <Menu
                      anchorEl={filterAnchorEl}
                      open={filterMenuOpen}
                      onClose={handleFilterClose}
                      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
                      transformOrigin={{ vertical: "top", horizontal: "right" }}
                      PaperProps={{
                        className: styles.filterPopover,
                      }}
                    >
                      <div className={styles.filterContent}>
                        {/* Supplier */}
                        <div className={styles.fieldGroup}>
                          <label className={styles.label}>Supplier</label>
                          <div className={styles.selectWrapper}>
                            <select
                              value={filters.supplier}
                              onChange={(e) =>
                                handleFilterChange("supplier", e.target.value)
                              }
                              className={styles.selectInput}
                            >
                              <option value="">All Suppliers</option>
                              {supplierNames.map((option) => (
                                <option key={option} value={option}>
                                  {option}
                                </option>
                              ))}
                            </select>
                            <span className={styles.selectArrow} />
                          </div>
                        </div>

                        {/* Planned Date */}
                        {/* <div className={styles.fieldGroup}>
                    <label className={styles.label}>
                      Planned Implementation Date
                    </label>
                    <div className={styles.dateWrapper}>
                      <input
                        type={filters.plannedDate ? "date" : "text"}
                        value={filters.plannedDate || ""}
                        onChange={(e) =>
                          handleFilterChange("plannedDate", e.target.value)
                        }
                        onFocus={(e) => (e.target.type = "date")}
                        onBlur={(e) => {
                          if (!e.target.value) e.target.type = "text";
                        }}
                        className={`${styles.inputField} ${styles.dateInput}`}
                        placeholder="Jan 04 2026"
                      />
                      <img
                        src={CalendarIcon}
                        alt="calendar"
                        className={styles.calendarIcon}
                      />
                    </div>
                  </div> */}

                        {/* Days Since Notification */}
                        {/* <div className={styles.fieldGroup}>
                    <label className={styles.label}>
                      Days Since Notification
                    </label>
                    <div className={styles.selectWrapper}>
                      <select
                        value={filters.daysRange}
                        onChange={(e) =>
                          handleFilterChange("daysRange", e.target.value)
                        }
                        className={styles.selectInput}
                      >
                        <option value="">Input text</option>
                        <option value="0-30">0–30</option>
                        <option value="31-60">31–60</option>
                        <option value="61-90">61–90</option>
                        <option value="90">90+</option>
                      </select>
                      <span className={styles.selectArrow} />
                    </div>
                  </div> */}

                        {/* Classification */}
                        <div className={styles.fieldGroup}>
                          <label className={styles.label}>
                            Change Classification
                          </label>
                          <div className={styles.selectWrapper}>
                            <select
                              value={filters.classification}
                              onChange={(e) =>
                                handleFilterChange(
                                  "classification",
                                  e.target.value,
                                )
                              }
                              className={styles.selectInput}
                            >
                              <option value="">All Classifications</option>
                              {classificationList.map((option) => (
                                <option key={option} value={option}>
                                  {option}
                                </option>
                              ))}
                            </select>
                            <span className={styles.selectArrow} />
                          </div>
                        </div>

                        {/* Buttons */}
                        <div className={styles.buttonRow}>
                          <button
                            className={styles.clearButton}
                            onClick={handleClearFilters}
                          >
                            Clear
                          </button>

                          <button
                            className={styles.applyButton}
                            onClick={handleApplyFilters}
                          >
                            Apply
                          </button>
                        </div>
                      </div>
                    </Menu>
                  )}
                </Box>
              </Stack>

              {loading || isFirstLoad ? (
                <ScnListSkeleton count={6} />
              ) : error ? (
                <div className={styles.errorMsg}>{error}</div>
              ) : queueItems.length === 0 ? (
                <div className={styles.noDataMsg}>
                  {appliedSearch
                    ? "No results found for your search."
                    : "No SCNs available."}
                </div>
              ) : (
                <Stack className={styles.queueList}>
                  {queueItems.map((item, index) => (
                    <Box
                      key={item.scn_reference_number}
                      className={`${styles.queueCard} ${selected === index ? styles.active : ""}`}
                      onClick={() => {
                        setSelected(index);
                        setSelected(index);
                        handleSelectScn(item);
                        setSelectedTab("Impact Review");
                      }}
                    >
                      <span
                        className={`${styles.status} ${getStatusClass(item.status)}`}
                      >
                        {item.status}
                      </span>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                        marginTop={0.5}
                      >
                        <span className={styles.scnId}>
                          {item.scn_reference_number}
                        </span>

                        <span
                          className={`${styles.classificationStatus} ${getClassificationClass(item.final_risk_level)}`}
                        >
                          {item.final_risk_level}
                        </span>
                      </Stack>

                      <p className={styles.supplier}>{item.supplier_name}</p>
                      <div className={styles.progressText}>
                        <span className={styles.textLabel}>Completeness</span>
                        <span className={styles.progressNumber}>
                          {item.completion_score}%
                        </span>
                      </div>
                      <div className={styles.progress}>
                        <div
                          className={styles.progressFill}
                          style={{ width: `${item.completion_score}%` }}
                        />
                      </div>
                      <div className={styles.textTag}>
                        <img src={ProductComplaints} alt="product complaint" />
                        {item.change_classification_supplier}
                      </div>
                    </Box>
                  ))}
                </Stack>
              )}
              {/* Infinite scroll sentinel */}
              {!loading && !error && hasMore && (
                <div ref={sentinelRef} style={{ height: 1 }} />
              )}
              {isFetchingMore && (
                <Box display="flex" justifyContent="center" py={2}>
                  <CircularProgress size={20} sx={{ color: "#437ef7" }} />
                </Box>
              )}
              {!loading && !isFetchingMore && !hasMore && scns.length > 0 && (
                <Box
                  sx={{
                    textAlign: "center",
                    color: "#9ca3af",
                    fontSize: "12px",
                    py: 1.5,
                  }}
                >
                  All items loaded
                </Box>
              )}
            </Box>
          </Box>

          {/* right – Mail Content */}

          <Box className={styles.mailContent}>
            {detailLoading || isFirstLoad ? (
              <>
                <ScnDetailsSkeleton />
                <SCNFormSkeleton />
              </>
            ) : (
              <>
                <Stack
                  direction="row"
                  spacing={2}
                  justifyContent="space-between"
                >
                  <Stack direction="column" gap={2}>
                    {/* <span className={styles.scnStatus}>{scnDetail?.status}</span> */}

                    <Box className={styles.mailContentHader}>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                        marginTop={0.5}
                        gap={2}
                      >
                        <span className={styles.scnId}>
                          {scnDetail?.supplierRef}
                        </span>
                        <button
                          className={styles.auditHistory}
                          onClick={() => setOpenAuditModal(true)}
                        >
                          <img src={AuditHistoryIcon} alt="" />
                          Audit History
                        </button>
                        {/* <span
                        className={`${styles.classificationStatus} ${getClassificationClass("Minor")}`}
                      >
                        Minor
                      </span> */}
                      </Stack>
                    </Box>
                    <Box className={styles.detailText}>
                      <span>{scnDetail?.supplierName}</span>
                      <span>Supplier SCN: {scnDetail?.supplierRef}</span>
                      <span>
                        Submitted: {scnDetail?.createdAt?.split("T")[0]}
                      </span>
                    </Box>
                  </Stack>

                  <Box
                    onClick={() => setOpenExtractedSourcesModal(true)}
                    sx={{ cursor: "pointer" }}
                  >
                    <Gauge
                      value={
                        scnDetail?.extractedFieldSources?.confidence_score ?? 0
                      }
                      size={100}
                    />
                  </Box>
                </Stack>
                {/* <ButtonGroup
                  selected={selectedTab}
                  onSelect={handleTabSelect}
                /> */}
                {selectedTab === "Review SCN" && (
                  <Box>
                    {/* <Stack
                      direction="row"
                      gap={1.5}
                      justifyContent="flex-end"
                      marginBottom={3}
                      marginTop={1}
                    >
                      <AppButton
                        variant="outlined"
                        onClick={() => setOpenRequestInfo(true)}
                      >
                        <span className={styles.appButton}>
                          <img src={InfoIcon} alt="" />
                          Request info
                        </span>
                      </AppButton>
                    </Stack> */}
                    {scnDetail && (
                      <SCNReviewForm
                        formData={scnDetail}
                        isEditing={isEditing}
                        onEditClick={() => setIsEditing(true)}
                        onInputChange={handleInputChange}
                        isUpload={false}
                        validationErrors={validationErrors}
                        onBackToSummary={() => handleTabSelect("Impact Review")}
                        onApprove={() => setOpenApprove(true)}
                        onReject={() => setOpenReject(true)}
                        onSave={handleSaveClick}
                        onCancel={handleCancelClick}
                      />
                    )}
                    {isEditing && (
                      <Box className={styles.divider} marginTop={3} />
                    )}
                  </Box>
                )}
                {selectedTab === "Impact Review" && (
                  <Box>
                    {isClassifying ? (
                      <Box className={styles.classifyingContainer}>
                        <div className={styles.loader}></div>
                        <Typography className={styles.statusSubtitle}>
                          Please wait for the file to be processed
                        </Typography>
                      </Box>
                    ) : (
                      <SCNInternalReviewImpactTab
                        classificationData={impactClassificationData}
                        isLoading={impactReviewLoading}
                        emailId={selectedEmailId ?? undefined}
                        onRefresh={loadImpactData}
                        onReviewScnClick={() => handleTabSelect("Review SCN")}
                        scnDetail={scnDetail}
                        onApproveClick={() => setOpenApprove(true)}
                        onRejectClick={() => setOpenReject(true)}
                        onOutputClick={() => setOpenPreview(true)}
                        onPreviewClick={() => setOpen(true)}
                        changeControlRequired={changeControlRequired}
                        recordId={recordId}
                      />
                    )}
                  </Box>
                )}
              </>
            )}

            <ChangeNotificationModal
              open={open}
              onClose={() => setOpen(false)}
              pdfUrl={latestPdfUrl}
            />

            {/* <ChangeSCNOutputModal
              open={openPreview}
              onClose={() => setOpenPreview(false)}
              emailId={selectedEmailId ?? undefined}
              onDone={(value) => {
                console.log("Selected Output:", value);
              }}
              defaultValue={
                (impactClassificationData?.final_classification as
                  | "SCN"
                  | "NON_SCN") || "SCN"
              }
            /> */}
            {/* Modals moved to parent for shared access */}
            <ChangeSCNOutputModal
              open={openPreview}
              onClose={() => setOpenPreview(false)}
              emailId={selectedEmailId ?? undefined}
              onDone={(newCls) => {
                setOpenPreview(false);
                loadImpactData();
              }}
              defaultValue={
                (impactClassificationData?.final_classification as
                  | "SCN"
                  | "NON_SCN") || "SCN"
              }
            />

            <ApproveModal
              open={openApprove}
              onClose={() => setOpenApprove(false)}
              emailId={selectedEmailId ?? undefined}
              onDone={(changeControl, ccRecordId) => {
                setChangeControlRequired(changeControl);
                setRecordId(ccRecordId);
                setOpenApprove(false);
                loadImpactData();
              }}
              defaultChangeControl={changeControlRequired}
              defaultRecordId={recordId}
            />

            <RejectSCNModal
              open={openReject}
              onClose={() => setOpenReject(false)}
              emailId={selectedEmailId ?? undefined}
              onSubmit={(comment) => {
                setOpenReject(false);
                loadImpactData();
              }}
            />

            <RequestInfoModal
              open={openRequestInfo}
              onClose={() => setOpenRequestInfo(false)}
              emailId={selectedEmailId ?? undefined}
              onDone={() => setOpenRequestInfo(false)}
            />

            <SCNExtractedSourcesModal
              open={openExtractedSourcesModal}
              onClose={() => setOpenExtractedSourcesModal(false)}
              sources={scnDetail?.extractedFieldSources}
            />

            <CommonModal
              open={openAuditModal}
              onClose={() => setOpenAuditModal(false)}
              title="Version History"
              width={800}
            >
              <SCNInternalReviewAuditTab
                scnId={scnDetail?.supplierRef ?? null}
              />
            </CommonModal>
          </Box>
        </Box>
      </Stack>
    </Box>
  );
};

export default SCNInternalReview;
