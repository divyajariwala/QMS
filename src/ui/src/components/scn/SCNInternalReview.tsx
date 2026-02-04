import React, { useState } from "react";
import { Box, Stack, Button } from "@mui/material";
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
import ChangeSCNOutputModal from "./ChangeSCNOutputModal";

const SCNInternalReview: React.FC = () => {
  const [selected, setSelected] = useState<number>(0);
  const [selectedTab, setSelectedTab] = useState("Review");
  const [isEditing, setIsEditing] = useState(false);
  const [open, setOpen] = useState(false);

  const queueItems = [
    {
      id: "SCN-INT-000234",
      supplier: "Supplier ABC",
      status: "High",
      progress: 90,
      desc: "3 Raw material change",
      scnStatus: "New",
    },
    {
      id: "SCN-INT-000240",
      supplier: "Supplier ABC",
      status: "Medium",
      progress: 82,
      desc: "Packing and labeling changes",
      scnStatus: "New",
    },
    {
      id: "SCN-INT-000510",
      supplier: "Supplier ABC",
      status: "Low",
      progress: 72,
      desc: "Packing and labeling changes",
      scnStatus: "Needs Triage",
    },
    {
      id: "SCN-INT-000234",
      supplier: "Supplier ABC",
      status: "High",
      progress: 90,
      desc: "3 Raw material change",
    },
    {
      id: "SCN-INT-000240",
      supplier: "Supplier ABC",
      status: "Medium",
      progress: 82,
      desc: "Packing and labeling changes",
      scnStatus: "Needs Triage",
    },
    {
      id: "SCN-INT-000510",
      supplier: "Supplier ABC",
      status: "Low",
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

  const getClassificationClass = (status: string) => {
    switch (status) {
      case "Low":
        return styles.statusLow;
      case "Medium":
        return styles.statusMedium;
      case "High":
        return styles.statusHigh;
      default:
        return "";
    }
  };

  return (
    <Box component="main" className={styles.container}>
      <Stack gap={2}>
        {/* Content */}
        <Box className={styles.contentWrapper}>
          {/* left – Mail List */}
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
              >
                Filter
                <img src={filterIcon} alt="filter" />
              </Button>
            </Stack>

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
                {queueItems.map((item, index) => (
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
                  </Box>
                ))}
              </Stack>
            </Box>
          </Box>

          {/* right – Mail Content */}
          <Box className={styles.mailContent}>
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
                  className={`${styles.classificationStatus} ${getClassificationClass("High")}`}
                >
                  High
                </span>
              </Stack>
              <Stack direction="row" gap={1.5}>
                <AppButton variant="ghost">
                  <span className={styles.appButton}>
                    <img src={InfoIcon} alt="" />
                    Request info
                  </span>
                </AppButton>

                <AppButton variant="outlined" onClick={() => setOpen(true)}>
                  <span className={styles.appButton}>
                    <img src={UndoIcon} alt="" />
                    Change SCN Output
                  </span>
                </AppButton>

                <AppButton variant="outlined">
                  <span className={styles.appButton}>
                    <img src={CircleDeleteIcon} alt="" />
                    Reject
                  </span>
                </AppButton>

                <AppButton variant="primary">
                  <span className={styles.appButton}>
                    <img src={CheckIcon} alt="" />
                    Approve
                  </span>
                </AppButton>
              </Stack>
            </Box>
            <ButtonGroup selected={selectedTab} onSelect={setSelectedTab} />
            <SCNFormFields
              formData={scnDetail}
              isEditing={isEditing}
              onEditClick={() => setIsEditing(true)}
              // onInputChange={handleInputChange}
            />
            <ChangeSCNOutputModal
              open={open}
              onClose={() => setOpen(false)}
              onDone={(value) => {
                console.log("Selected Output:", value);
              }}
              defaultValue="SCN"
            />
          </Box>
        </Box>
      </Stack>
    </Box>
  );
};

export default SCNInternalReview;
