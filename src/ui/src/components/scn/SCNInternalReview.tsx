import React, { useState } from "react";
import { Box, Stack, Button, Chip } from "@mui/material";
import styles from "./SCNInternalReview.module.scss";
import filterIcon from "../../assets/icons/filter.svg";
import SearchIcon from "../../assets/icons/search.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";

const SCNInternalReview: React.FC = () => {
  const [selected, setSelected] = useState<number>(0);
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

                    <Stack direction="row" justifyContent="space-between">
                      <span className={styles.scnId}>{item.id}</span>
                      <Chip
                        label={item.status}
                        size="small"
                        className={
                          item.status === "High" ? styles.high : styles.medium
                        }
                      />
                    </Stack>

                    <p className={styles.supplier}>{item.supplier}</p>
                    <div className={styles.progressText}>
                      <span className={styles.textLabel}>Completeness</span>
                      <span className={styles.progressNumber}>{item.progress}%</span>
                    </div>
                    <div className={styles.progress}>
                      <div
                        className={styles.progressFill}
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>

                    <p className={styles.desc}>{item.desc}</p>
                  </Box>
                ))}
              </Stack>
            </Box>
          </Box>

          {/* right – Mail Content */}
          <Box className={styles.mailContent}></Box>
        </Box>
      </Stack>
    </Box>
  );
};

export default SCNInternalReview;
