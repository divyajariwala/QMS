import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Box, Stack, Button, Menu, CircularProgress } from "@mui/material";
import styles from "./SCNInternalReview.module.scss";
import filterIcon from "../../assets/icons/filter.svg";
import SearchIcon from "../../assets/icons/search.svg";
import ButtonGroup from "./ButtonGroup";
import SCNFormFields from "./SCNForm";
import AppButton from "@components/common/AppButton";
import InfoIcon from "../../assets/icons/information.svg";
import AiSummaryIcon from "../../assets/icons/aiSummary.svg";
import UndoIcon from "../../assets/icons/undo.svg";
import CalendarIcon from "../../assets/icons/calendar.svg";
import ChangeSCNOutputModal from "./modal/ChangeSCNOutputModal";
import ChangeNotificationModal from "./modal/ChangeNotificationModal";
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
import SCNFormSkeleton from "./skeleton/SCNFormSkeleton";
import RequestInfoModal from "./modal/RequestInfoModal";
import SCNInternalReviewImpactTab, {
  ImpactClassificationData,
} from "./SCNInternalReviewImpactTab";
import SCNInternalReviewAuditTab from "./SCNInternalReviewAuditTab";
import ScnDetailsSkeleton from "./skeleton/ScnDetailsSkeleton";

type FilterState = {
  supplier: string;
  plannedDate: string | null;
  daysRange: string;
  classification: string;
};

const LIMIT = 10;

const SCNInternalReview: React.FC = () => {
  const [selected, setSelected] = useState<number>(0);
  const [selectedTab, setSelectedTab] = useState("Review");
  const [isEditing, setIsEditing] = useState(false);
  const [open, setOpen] = useState(false);
  const [openPreview, setOpenPreview] = useState(false);
  const [openRequestInfo, setOpenRequestInfo] = useState(false);
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(
    null,
  );
  const filterMenuOpen = Boolean(filterAnchorEl);
  const [searchValue, setSearchValue] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };
  const defaultFilters: FilterState = {
    supplier: "",
    plannedDate: null,
    daysRange: "",
    classification: "",
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
  const [hasMore, setHasMore] = useState(true);
  const [isFetchingMore, setIsFetchingMore] = useState(false);
  const sentinelRef = useRef<HTMLDivElement>(null);

  const [scnDetail, setScnDetail] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [impactReviewLoading, setImpactReviewLoading] = useState(false);
  const [impactClassificationData, setImpactClassificationData] =
    useState<ImpactClassificationData | null>(null);

  // Fetch SCN list with filters
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
        if (appliedFilters.plannedDate)
          params.append(
            "planned_implementation_date",
            appliedFilters.plannedDate,
          );
        const res = await fetchScnList(LIMIT, 0, params);
        const items = res?.data?.items || [];
        const count = res?.data?.count || 0;
        setScns(items);
        setTotal(count);
        setHasMore(items.length >= LIMIT && items.length < count);
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
  }, [appliedFilters]);

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
      if (appliedFilters.plannedDate)
        params.append(
          "planned_implementation_date",
          appliedFilters.plannedDate,
        );
      const res = await fetchScnList(LIMIT, newOffset, params);
      const items = res?.data?.items || [];
      setScns((prev) => [...prev, ...items]);
      setHasMore(items.length >= LIMIT && newOffset + items.length < total);
    } catch (err: any) {
      console.error("Load more failed:", err);
    } finally {
      setIsFetchingMore(false);
    }
  }, [isFetchingMore, hasMore, scns.length, appliedFilters, total]);

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
      const res: any = await fetchScnDetails(item.email_id);
      if (res?.data) {
        const mapped = mapScnDetailsToForm(res.data);
        setScnDetail(mapped);
      }
    } catch (error) {
      console.error("Failed to fetch SCN details", error);
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

  const handleImpactReview = async () => {
    if (!selectedEmailId) return;
    setImpactReviewLoading(true);
    try {
      await scnClassify(selectedEmailId);
      setSelectedTab("Impact Assessment");
      const res = await scnClassificationResults(selectedEmailId);
      if (res?.success === false) {
        setImpactClassificationData(null);
      } else {
        const data: ImpactClassificationData = res?.data ?? res ?? {};
        setImpactClassificationData(data);
      }
    } catch (err) {
      console.error("Impact Review failed:", err);
      setImpactClassificationData(null);
    } finally {
      setImpactReviewLoading(false);
    }
  };

  const handleTabSelect = async (tab: string) => {
    setSelectedTab(tab);
    if (tab === "Impact Assessment" && selectedEmailId) {
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
    const mapped = scns.map((item) => ({
      scn_reference_number: item.scn_reference_number,
      supplier_name: item.supplier_name,
      change_classification_supplier: item.change_classification_supplier,
      completion_score: item.completion_score || 0,
      status: item.status,
      email_id: item.email_id,
      notification_date: item.notification_date,
      planned_implementation_date: item.planned_implementation_date,
    }));

    if (!appliedSearch) return mapped;

    return mapped.filter(
      (item) =>
        item.scn_reference_number
          ?.toLowerCase()
          .includes(appliedSearch.toLowerCase()) ||
        item.supplier_name?.toLowerCase().includes(appliedSearch.toLowerCase()),
    );
  }, [scns, appliedSearch]);

  const handleApplyFilters = () => {
    setAppliedFilters(filters);
    handleFilterClose();
  };

  const handleClearFilters = () => {
    setFilters(defaultFilters);
    setAppliedFilters(defaultFilters);
    handleFilterClose();
  };

  useEffect(() => {
    if (scns.length > 0 && !selectedEmailId) {
      const firstItem = scns[0];
      setSelected(0);
      handleSelectScn(firstItem);
    }
  }, [scns]);

  return (
    <Box component="main" className={styles.container}>
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
              <Button
                size="small"
                variant="outlined"
                className={styles.filterButton}
                onClick={(event) => setFilterAnchorEl(event.currentTarget)}
              >
                Filter
                <img src={filterIcon} alt="filter" />
              </Button>
            </Stack>
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
                        <option value="">Supplier 1</option>
                        {["Supplier ABC", "Supplier XYZ"].map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                      <span className={styles.selectArrow} />
                    </div>
                  </div>

                  {/* Planned Date */}
                  <div className={styles.fieldGroup}>
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
                  </div>

                  {/* Days Since Notification */}
                  <div className={styles.fieldGroup}>
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
                  </div>

                  {/* Classification */}
                  <div className={styles.fieldGroup}>
                    <label className={styles.label}>
                      Change Classification
                    </label>
                    <div className={styles.selectWrapper}>
                      <select
                        value={filters.classification}
                        onChange={(e) =>
                          handleFilterChange("classification", e.target.value)
                        }
                        className={styles.selectInput}
                      >
                        <option value="">Classification 1</option>
                        <option value="Minor">Minor</option>
                        <option value="Moderate">Moderate</option>
                        <option value="Major">Major</option>
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

            <Box className={styles.mailListSub}>
              <div className={styles.searchBar}>
                <form
                  className={styles.inputWrapper}
                  onSubmit={(e) => {
                    e.preventDefault();
                    setAppliedSearch(searchValue.trim());
                  }}
                >
                  <img
                    src={SearchIcon}
                    alt="Search"
                    className={styles.searchIcon}
                  />
                  <input
                    type="search"
                    placeholder="Search here..."
                    aria-label="Search by SCN number"
                    className={styles.searchInput}
                    value={searchValue}
                    onChange={(e) => {
                      const value = e.target.value;
                      setSearchValue(value);
                      // If user clears input, reset search automatically
                      if (value.trim() === "") {
                        setAppliedSearch("");
                      }
                    }}
                  />
                  <button type="submit" className={styles.searchButton}>
                    Search
                  </button>
                </form>
              </div>

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
                        handleSelectScn(item);
                        setSelectedTab("Review");
                      }}
                    >
                      <span className={styles.scnStatus}>{item.status}</span>

                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                        marginTop={0.5}
                      >
                        <span className={styles.scnId}>
                          {item.scn_reference_number}
                        </span>

                        {/* <span
                          className={`${styles.classificationStatus} ${getClassificationClass(item.status)}`}
                        >
                          {item.status}
                        </span> */}
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
                <Box>
                  <span className={styles.scnStatus}>{scnDetail?.status}</span>
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
                      {/* <span
                        className={`${styles.classificationStatus} ${getClassificationClass("Minor")}`}
                      >
                        Minor
                      </span> */}
                    </Stack>
                  </Box>
                </Box>
                <Box className={styles.detailText}>
                  <span>{scnDetail?.supplierName}</span>
                  <span>Supplier SCN: {scnDetail?.supplierRef}</span>
                  <span>Submitted: {scnDetail?.createdAt?.split("T")[0]}</span>
                  {/* <span>Owner: Unassigned</span> */}
                </Box>
                <ButtonGroup
                  selected={selectedTab}
                  onSelect={handleTabSelect}
                />
                {selectedTab === "Review" && (
                  <Box>
                    <Stack
                      direction="row"
                      gap={1.5}
                      justifyContent="flex-end"
                      marginBottom={3}
                      marginTop={1}
                    >
                      <AppButton
                        variant="outlined"
                        onClick={handleImpactReview}
                        disabled={impactReviewLoading}
                      >
                        <span className={styles.appButton}>
                          {impactReviewLoading ? (
                            <CircularProgress
                              size={14}
                              sx={{ color: "inherit" }}
                            />
                          ) : (
                            <img src={AiSummaryIcon} alt="" />
                          )}
                          Impact Review
                        </span>
                      </AppButton>

                      <AppButton
                        variant="outlined"
                        onClick={() => setOpenRequestInfo(true)}
                      >
                        <span className={styles.appButton}>
                          <img src={InfoIcon} alt="" />
                          Request info
                        </span>
                      </AppButton>

                      <AppButton
                        variant="primary"
                        onClick={() => setOpenPreview(true)}
                      >
                        <span className={styles.appButton}>
                          <img src={UndoIcon} alt="" />
                          Change SCN Output
                        </span>
                      </AppButton>
                    </Stack>
                    {/* <Box className={styles.docxMain}>
                      <section className={styles.section}>
                        <p>
                          <b>Reason for Change:</b> End-of-life replacement of
                          legacy equipment/material.
                        </p>
                      </section>

                      <section className={styles.section}>
                        <h3>Affected Items</h3>
                        <div className={styles.tableMain}>
                          <div className={styles.tableTitle}>
                            Affected Items
                          </div>
                          <table className={styles.table}>
                            <thead>
                              <tr>
                                <th>Type</th>
                                <th>Identifier</th>
                                <th>Description</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr>
                                <td>Service</td>
                                <td>SRV-6803</td>
                                <td>Release testing support</td>
                              </tr>
                              <tr>
                                <td>Service</td>
                                <td>SRV-1313</td>
                                <td>Incoming inspection service</td>
                              </tr>
                              <tr>
                                <td>Material</td>
                                <td>MAT-524871</td>
                                <td>Polymer resin, lot controlled</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </section>

                
                      <section className={styles.section}>
                        <h3>Impact Assessment</h3>
                        <p>
                          <b>Regulatory Impact Likelihood:</b> High
                        </p>
                      </section>
                    </Box>
                    <AppButton
                      className={styles.previewButton}
                      variant="outlined"
                      onClick={() => setOpen(true)}
                    >
                      <span className={styles.previewIcon}>
                        Preview
                        <img src={RightIcon} alt=">" />
                      </span>
                    </AppButton> */}
                    {/* <SCNFormSkeleton /> */}
                    {scnDetail && (
                      <SCNFormFields
                        formData={scnDetail}
                        isEditing={isEditing}
                        onEditClick={() => setIsEditing(true)}
                        onInputChange={handleInputChange}
                        isUpload={false}
                        validationErrors={validationErrors}
                      />
                    )}
                    {isEditing && (
                      <Box className={styles.divider} marginTop={3} />
                    )}
                  </Box>
                )}
                {selectedTab === "Impact Assessment" && (
                  <Box>
                    <SCNInternalReviewImpactTab
                      classificationData={impactClassificationData}
                      isLoading={impactReviewLoading}
                    />
                  </Box>
                )}

                {selectedTab === "Audit" && <SCNInternalReviewAuditTab />}
              </>
            )}

            <ChangeNotificationModal
              open={open}
              onClose={() => setOpen(false)}
            />

            <ChangeSCNOutputModal
              open={openPreview}
              onClose={() => setOpenPreview(false)}
              onDone={(value) => {
                console.log("Selected Output:", value);
              }}
              defaultValue="SCN"
            />
            <RequestInfoModal
              open={openRequestInfo}
              onClose={() => setOpenRequestInfo(false)}
              onSubmit={(fields, comment) => {
                console.log("Requested fields:", fields);
                console.log("Comment:", comment);
              }}
              allFields={[
                "Supplier Name",
                "SCN Title",
                "Supplier Site(s) Affected",
                "Supplier Contact Information",
                "Material / Component Number",
                "Proposed State",
                "Supplier Change Classification",
                "Planned Implementation Date",
                "First Affected Lot / Batch",
                "Document Upload",
              ]}
              initialSelected={["Supplier Name", "SCN Title"]}
            />

            <Stack direction="row" spacing={2} justifyContent="flex-end">
              {isEditing && selectedTab === "Review" && (
                <>
                  <AppButton
                    variant="outlined"
                    onClick={handleCancelClick}
                    className={styles.actionButton}
                  >
                    Cancel
                  </AppButton>
                  <AppButton
                    variant="primary"
                    onClick={handleSaveClick}
                    className={styles.actionButton}
                  >
                    Save
                  </AppButton>
                </>
              )}
            </Stack>
          </Box>
        </Box>
      </Stack>
    </Box>
  );
};

export default SCNInternalReview;
