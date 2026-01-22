import React from "react";
import { Box } from "@mui/material";
import styles from "./SCNStatusTabs.module.scss";

type SCNTabStatus = "all" | "under_review" | "processed" | "info_requested";

interface SCNStatusTabsProps {
  activeTab: SCNTabStatus;
  setActiveTab: (tab: SCNTabStatus) => void;
  counts: {
    all: number;
    under_review: number;
    processed: number;
    info_requested: number;
  };
  setPageNumber: (page: number) => void;
}

const SCNStatusTabs: React.FC<SCNStatusTabsProps> = ({
  activeTab,
  setActiveTab,
  counts,
  setPageNumber,
}) => {
  const tabs: { key: SCNTabStatus; label: string }[] = [
    { key: "all", label: "All" },
    { key: "under_review", label: "Under review" },
    { key: "processed", label: "Processed" },
    { key: "info_requested", label: "Info requested" },
  ];

  const handleTabClick = (tabKey: SCNTabStatus) => {
    setActiveTab(tabKey);
    setPageNumber(1);
  };

  return (
    <Box className={styles.tabsContainer}>
      <Box className={styles.tabsList}>
        {tabs.map((tab) => (
          <Box
            key={tab.key}
            className={`${styles.tab} ${activeTab === tab.key ? styles.activeTab : ""}`}
            onClick={() => handleTabClick(tab.key)}
          >
            <span className={styles.tabLabel}>{tab.label}</span>
            <span
              className={`${styles.tabCount} ${activeTab === tab.key ? styles.activeCount : ""}`}
            >
              {counts[tab.key]}
            </span>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default SCNStatusTabs;