import React from "react";
import { Button, Stack, Tab, Tabs } from "@mui/material";
import PlusIcon from "../../../assets/icons/plus.svg";

import { RcaRecord } from "./RCATypes";
import styles from "./RootCauseAnalysis.module.scss";

interface RcaTabsProps {
  rcas: RcaRecord[];
  pendingRca?: RcaRecord | null;
  selectedIndex: number;
  onChange: (_: React.SyntheticEvent, newIndex: number) => void;
  onAdd: () => void;
  isSubmittedSuccessfully: boolean;
}

const RcaTabs: React.FC<RcaTabsProps> = ({
  rcas,
  pendingRca,
  selectedIndex,
  onChange,
  onAdd,
  isSubmittedSuccessfully,
}) => {
  return (
    <Stack
      direction="row"
      alignItems="center"
      spacing={2}
      sx={{ mb: 1, justifyContent: "space-between", width: "100%" }}
    >
      <Tabs
        value={selectedIndex}
        onChange={onChange}
        aria-label="RCA tabs"
        variant="scrollable"
        TabIndicatorProps={{ style: { display: "none" } }}
        className={styles.rcaTabs}
      >
        {rcas.map((r) => (
          <Tab
            key={r.id}
            label={r.name}
            className={styles.rcaTab}
            sx={{
              "&.Mui-selected": {
                backgroundColor: "#DAE0E6",
              },
            }}
          />
        ))}
        {pendingRca && (
          <Tab
            key={pendingRca.id}
            label={pendingRca.name}
            className={styles.rcaTab}
            sx={{
              "&.Mui-selected": {
                backgroundColor: "#DAE0E6",
              },
            }}
          />
        )}
      </Tabs>
      <Stack direction="row" spacing={1}>
        {!isSubmittedSuccessfully && (
          <Button variant="text" onClick={onAdd} className={styles.addBtn} disabled={rcas.length > 2}>
            Add RCA
            <img src={PlusIcon} alt="plus" />
          </Button>
        )}
      </Stack>
    </Stack>
  );
};

export default RcaTabs;
