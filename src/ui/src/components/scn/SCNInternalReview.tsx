import React, { useEffect, useMemo, useState } from "react";
import { Box, Stack, Button, Menu } from "@mui/material";
import styles from "./SCNInternalReview.module.scss";
import filterIcon from "../../assets/icons/filter.svg";
import SearchIcon from "../../assets/icons/search.svg";
import ButtonGroup from "./ButtonGroup";
import SCNFormFields from "./SCNForm";
import AppButton from "@components/common/AppButton";
import InfoIcon from "../../assets/icons/information.svg";
import CheckIcon from "../../assets/icons/circle-checkmark.svg";
import CircleDeleteIcon from "../../assets/icons/circle-delete.svg";
import UndoIcon from "../../assets/icons/undo.svg";
import CalendarIcon from "../../assets/icons/calendar.svg";
import ChangeSCNOutputModal from "./modal/ChangeSCNOutputModal";
import ChangeNotificationModal from "./modal/ChangeNotificationModal";
import RightIcon from "../../assets/icons/rightBlue.svg";
import { fetchScnDetails, fetchScnList } from "src/services/scn";
import SCNFormSkeleton from "./skeleton/SCNFormSkeleton";
import RequestInfoModal from "./modal/RequestInfoModal";
import SCNInternalReviewImpactTab from "./SCNInternalReviewImpactTab";
import FormInput from "@components/common/FormInput";
import SCNInternalReviewAuditTab from "./SCNInternalReviewAuditTab";

type FilterState = {
  supplier: string;
  plannedDate: string | null;
  daysRange: string;
  classification: string;
};

const SCNInternalReview: React.FC = () => {
  const [selected, setSelected] = useState<number>(0);
  const [selectedTab, setSelectedTab] = useState("Review");
  const [isEditing, setIsEditing] = useState(false);
  const [open, setOpen] = useState(false);
  const [openPreview, setOpenPreview] = useState(false);
  const [openRequestInfo, setOpenRequestInfo] = useState(false);

  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(
    null,
  );
  const filterMenuOpen = Boolean(filterAnchorEl);

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

  const queueItems = [
    {
      id: "SCN-INT-000234",
      supplier: "Supplier ABC",
      status: "Minor",
      progress: 90,
      desc: "3 Raw material change",
      scnStatus: "New",
    },
    {
      id: "SCN-INT-000240",
      supplier: "Supplier ABC",
      status: "Moderate",
      progress: 82,
      desc: "Packing and labeling changes",
      scnStatus: "New",
    },
    {
      id: "SCN-INT-000510",
      supplier: "Supplier ABC",
      status: "Major",
      progress: 72,
      desc: "Packing and labeling changes",
      scnStatus: "Needs Triage",
    },
    {
      id: "SCN-INT-000234",
      supplier: "Supplier ABC",
      status: "Minor",
      progress: 90,
      desc: "3 Raw material change",
    },
    {
      id: "SCN-INT-000240",
      supplier: "Supplier ABC",
      status: "Moderate",
      progress: 82,
      desc: "Packing and labeling changes",
      scnStatus: "Needs Triage",
    },
    {
      id: "SCN-INT-000510",
      supplier: "Supplier ABC",
      status: "Major",
      progress: 72,
      desc: "Packing and labeling changes",
      scnStatus: "IN-REVIEW",
    },
  ];

  const [scnDetail] = useState({
    id: "1",
    status: "SUPPLIER ACTION REQUIRED" as const,
    scnNumber: "SCN-000231",
    changeClassification: "Lorem ipsum",
    supplierRef: "SCN-12345",
    supplierName: "Supplier XYZ",
    notificationDate: "Jan 04 2026",
    plannedImplementationDate: "Dec 23 2025",
    changeType: "Adverse Event" as const,
    changeTitleSummary:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
    overdueDays: 5,
    changeTitle: "SCN-12345",
    currentState:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    proposedState:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    justification:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    temporaryChange: "No",
    supplierSitesAffected: "Low",
    supplierSitesAffected2: "Manufacturing",
    supplierContactInfo: "quality@xyz.com",
    changeTimingPlannedDate: "Dec 23 2025",
    firstAffectedLotBatch: "Input text",
    materialComponentNumber: "Component A",
  });
  const [scns, setScns] = useState([]);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadList();
  }, [offset]);

  const loadList = async () => {
    const res = await fetchScnList(50, offset);
    console.log(res, "res@@");
    // setScns(res?.data?.items);
    // setTotal(res?.data?.count);
  };

  const handleSelectScn = async (item: any) => {
    // if (!item?.email_id) {
    //   setScnDetails(MOCK_SCN_DETAIL);
    //   return;
    // }

    try {
      const res: any = await fetchScnDetails(item.email_id);

      // if (res?.data) {
      //   setScnDetails(res.data);
      // } else {
      //   setScnDetails(MOCK_SCN_DETAIL);
      // }
    } catch (error) {
      console.warn("SCN detail API failed → using mock");
    }
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

  // const handleApplyFilters = () => {
  //   setAppliedFilters(filters);
  //   setFilterAnchorEl(null);
  // };

  // const handleClearFilters = () => {
  //   setFilters(defaultFilters);
  //   setAppliedFilters(defaultFilters);
  //   setFilterAnchorEl(null);
  // };

  const filteredQueueItems = useMemo(() => {
    return queueItems.filter((item) => {
      if (
        appliedFilters.supplier &&
        item.supplier !== appliedFilters.supplier
      ) {
        return false;
      }

      if (
        appliedFilters.classification &&
        item.status !== appliedFilters.classification
      ) {
        return false;
      }

      if (appliedFilters.daysRange) {
        const days = Number(item.progress); // example mapping
        const [min, max] = appliedFilters.daysRange.split("-");

        if (max) {
          if (days < Number(min) || days > Number(max)) return false;
        } else {
          if (days < Number(min)) return false;
        }
      }

      return true;
    });
  }, [queueItems, appliedFilters]);

  const handleApplyFilters = () => {
    setAppliedFilters(filters);
    handleFilterClose();
  };

  const handleClearFilters = () => {
    setFilters(defaultFilters);
    setAppliedFilters(defaultFilters);
    handleFilterClose();
  };

  return (
    <Box component="main" className={styles.container}>
      <Stack gap={2}>
        {/* Content */}
        <Box className={styles.contentWrapper}>
          {/* left – Mail List */}
          {/* <ScnListSkeleton /> */}
          <Box className={styles.mailList}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              className={styles.mailHeader}
            >
              <span className={styles.mailHeaderTitle}>Queue (6)</span>
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
                  onSubmit={(e) => e.preventDefault()}
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
                  />
                  <button type="button" className={styles.searchButton}>
                    Search
                  </button>
                </form>
              </div>

              <Stack className={styles.queueList}>
                {filteredQueueItems.map((item, index) => (
                  <Box
                    key={item.id}
                    className={`${styles.queueCard} ${
                      selected === index ? styles.active : ""
                    }`}
                    onClick={() => setSelected(index)}
                  >
                    <span className={styles.scnStatus}>{item.scnStatus}</span>

                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                      marginTop={0.5}
                    >
                      <span className={styles.scnId}>{item.id}</span>

                      <span
                        className={`${styles.classificationStatus} ${getClassificationClass(item.status)}`}
                      >
                        {item.status}
                      </span>
                    </Stack>

                    <p className={styles.supplier}>{item.supplier}</p>
                    <div className={styles.progressText}>
                      <span className={styles.textLabel}>Completeness</span>
                      <span className={styles.progressNumber}>
                        {item.progress}%
                      </span>
                    </div>
                    <div className={styles.progress}>
                      <div
                        className={styles.progressFill}
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                    <span className={styles.desc}>{item.desc}</span>
                    <div className={styles.textTag}>Manufacturing Change</div>
                  </Box>
                ))}
              </Stack>
            </Box>
          </Box>

          {/* right – Mail Content */}
          {/* <ScnDetailsSkeleton /> */}
          <Box className={styles.mailContent}>
            <Box>
              <span className={styles.scnStatus}>New</span>
              <Box className={styles.mailContentHader}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                  marginTop={0.5}
                  gap={2}
                >
                  <span className={styles.scnId}>SCN-INT-000234</span>
                  <span
                    className={`${styles.classificationStatus} ${getClassificationClass("Minor")}`}
                  >
                    Minor
                  </span>
                </Stack>
              </Box>
            </Box>
            <Box className={styles.detailText}>
              <span>Supplier XYZ</span>
              <span>Supplier SCN: SCN-12345</span>
              <span>Submitted 2026-01-10</span>
              <span>Owner: Unassigned</span>
            </Box>
            <ButtonGroup selected={selectedTab} onSelect={setSelectedTab} />
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
                <Box className={styles.docxMain}>
                  <section className={styles.section}>
                    <p>
                      <b>Reason for Change:</b> End-of-life replacement of
                      legacy equipment/material.
                    </p>
                  </section>

                  {/* Affected Items */}
                  <section className={styles.section}>
                    <h3>Affected Items</h3>
                    <div className={styles.tableMain}>
                      <div className={styles.tableTitle}>Affected Items</div>
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

                  {/* Impact Assessment */}
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
                </AppButton>
                {/* <SCNFormSkeleton /> */}
                <SCNFormFields
                  formData={scnDetail}
                  isEditing={isEditing}
                  onEditClick={() => setIsEditing(true)}
                  // onInputChange={handleInputChange}
                />
                {isEditing && <Box className={styles.divider} marginTop={3} />}
              </Box>
            )}
            {selectedTab === "Impact Assessment" && (
              <Box>
                <SCNInternalReviewImpactTab />
              </Box>
            )}

            {selectedTab === "Audit" && <SCNInternalReviewAuditTab />}
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
              {isEditing && (
                <>
                  <AppButton
                    variant="outlined"
                    // onClick={handleCancelClick}
                    className={styles.actionButton}
                  >
                    Cancel
                  </AppButton>
                  <AppButton
                    variant="primary"
                    // onClick={handleSaveClick}
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
