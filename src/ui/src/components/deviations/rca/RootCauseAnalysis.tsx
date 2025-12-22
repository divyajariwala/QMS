import React, { useMemo, useRef, useState } from "react";
import { Box, Paper, Stack } from "@mui/material";

import { initialRcas, RcaRecord } from "./RCAMockdata"; // adjust path as needed
import styles from "./RootCauseAnalysis.module.scss";
import RcaTabs from "./RCATabs";
import RcaHeader from "./RCAHeader";
import RcaView from "./RCAView";
import RcaEdit from "./RCAEdit";
import Notification from "@components/Notification/Notification";

const RootCauseAnalysis: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<"success" | "error">("success");
  const [message, setMessage] = useState<string>("");
  const [baselineRcas] = useState<RcaRecord[]>(initialRcas);
  const [rcas, setRcas] = useState<RcaRecord[]>(initialRcas);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [preEditSnapshot, setPreEditSnapshot] = useState<RcaRecord | null>(
    null
  );

  const handleShowNotification = () => {
    setOpen(true);
  };
  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const selectedRca = useMemo(() => rcas[selectedIndex], [rcas, selectedIndex]);

  const externalSaveFn = useRef<(() => void) | null>(null);

  const handleTabChange = (_: React.SyntheticEvent, newIndex: number) => {
    setSelectedIndex(newIndex);
    setIsEditing(false);
    setPreEditSnapshot(null);
  };

  const handleAddRca = () => {
    const nextNum = rcas.length + 1;
    const newRca: RcaRecord = {
      id: `rca-${nextNum}`,
      name: `RCA ${nextNum}`,
      sections: [
        {
          key: "issues",
          title: "Causal factor",
          value: "",
          explanation: "",
        },
        {
          key: "major",
          title: "Major root cause category",
          value: "",
          explanation: "",
        },
        {
          key: "near",
          title: "Near root cause",
          value: "",
          explanation: "",
        },
        {
          key: "root",
          title: "Root cause",
          value: "",
          explanation: "",
        },
      ],
      meta: { createdFrom: "add", createdAt: new Date().toISOString() },
    };
    const next = [...rcas, newRca];
    setRcas(next);
    setSelectedIndex(next.length - 1);
    setIsEditing(true);
    setPreEditSnapshot(newRca);
  };

  const handleDeleteSelected = () => {
    if (!rcas.length) return;
    const next = [...rcas];
    next.splice(selectedIndex, 1);
    setRcas(next);
    setSelectedIndex(0);
    setIsEditing(false);
    setPreEditSnapshot(null);
  };

  const handleEditStart = () => {
    if (selectedRca) {
      setPreEditSnapshot(JSON.parse(JSON.stringify(selectedRca)));
      setIsEditing(true);
    }
  };

  const handleSaveRca = (updated: RcaRecord) => {
    const hasEmpty = updated.sections.some(
      (sec) => !sec.value || sec.value.trim() === ""
    );
    if (hasEmpty) {
      setType("error");
      setMessage("All dropdowns must be selected");
      handleShowNotification();
      return;
    }
    const next = [...rcas];
    next[selectedIndex] = updated;
    setRcas(next);
    setIsEditing(false);
    setPreEditSnapshot(null);
  };

  const handleCancelEdit = () => {
    const current = rcas[selectedIndex];
    const isNew = current?.meta?.createdFrom === "add";

    if (isNew) {
      const next = [...rcas];
      next.splice(selectedIndex, 1);
      setRcas(next);
      setSelectedIndex(0);
    } else if (preEditSnapshot) {
      // Revert to pre-edited snapshot
      const next = [...rcas];
      next[selectedIndex] = preEditSnapshot;
      setRcas(next);
    }
    setIsEditing(false);
    setPreEditSnapshot(null);
  };

  const onResetAll = () => {
    const restored = JSON.parse(JSON.stringify(baselineRcas));

    const currentId = rcas[selectedIndex]?.id;
    const keptIndex =
      currentId != null ? restored.findIndex((r) => r.id === currentId) : -1;

    const nextIndex =
      keptIndex >= 0
        ? keptIndex
        : Math.min(selectedIndex, Math.max(restored.length - 1, 0));

    setRcas(restored);
    setSelectedIndex(nextIndex);
    setIsEditing(false);
    setPreEditSnapshot(null);
  };

  const triggerExternalSave = () => externalSaveFn.current?.();

  return (
    <Paper variant="outlined" className={styles.rootPaper}>
      <Stack
        direction="row"
        alignItems="center"
        spacing={1}
        className={styles.headerStack}
      >
        <Box className={styles.headerTitle}>Root Cause Analysis</Box>
      </Stack>
      <Box className={styles.subtitleBox}>Please review and modify.</Box>

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          mb: 2,
        }}
      >
        <RcaTabs
          rcas={rcas}
          selectedIndex={selectedIndex}
          onChange={handleTabChange}
          onAdd={handleAddRca}
        />
      </Box>

      <RcaHeader
        currentTitle={selectedRca?.name ?? ""}
        isEditing={isEditing}
        onEdit={handleEditStart}
        onDelete={handleDeleteSelected}
        onCancelEdit={handleCancelEdit}
        onSave={triggerExternalSave}
        onReset={onResetAll}
        showReset={selectedRca?.meta?.createdFrom !== "add"}
      />

      {!isEditing && selectedRca && <RcaView rca={selectedRca} />}

      {isEditing && selectedRca && (
        <RcaEdit
          rca={selectedRca}
          onSave={handleSaveRca}
          registerOnSave={(fn) => {
            externalSaveFn.current = fn;
          }}
        />
      )}
      <Notification
        open={open}
        onClose={handleCloseNotification}
        position="top"
        type={type}
        message={message}
      />
    </Paper>
  );
};

export default RootCauseAnalysis;
