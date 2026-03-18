import React from "react";
import { Box } from "@mui/material";
import styles from "./SCNTabs.module.scss";

type SCNTab = "supplier_portal" | "internal_review";

interface SCNTabsProps {
  activeTab: SCNTab;
  setActiveTab: (tab: SCNTab) => void;
}

const SCNTabs: React.FC<SCNTabsProps> = ({ activeTab, setActiveTab }) => {
  const tabs: { key: SCNTab; label: string }[] = [
    { key: "supplier_portal", label: "Supplier Portal" },
    { key: "internal_review", label: "Internal Review" },
  ];

  const handleTabClick = (tabKey: SCNTab) => {
    setActiveTab(tabKey);
  };

  return (
    <Box className={styles.tabsContainer}>
      <Box className={styles.tabsList}>
        {tabs.map((tab) => (
          <Box
            key={tab.key}
            className={`${styles.tab} ${activeTab === tab.key ? styles.activeTab : styles.nonActiveTab}`}
            onClick={() => handleTabClick(tab.key)}
          >
            <span className={styles.tabLabel}>{tab.label}</span>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default SCNTabs;
