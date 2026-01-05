import React, {
  useMemo,
  useRef,
  useState,
  useEffect,
  forwardRef,
  useImperativeHandle,
} from "react";
import { Box, Paper, Stack } from "@mui/material";

import {
  RootCauseAnalysisProps,
  RcaRecord,
  DropdownData,
  RcaSection,
  ApiRcaItem,
} from "./RCATypes";
import styles from "./RootCauseAnalysis.module.scss";
import RcaTabs from "./RCATabs";
import RcaHeader from "./RCAHeader";
import RcaView from "./RCAView";
import RcaEdit from "./RCAEdit";
import Notification from "@components/Notification/Notification";
import { fetchRcaCategories, submitRca } from "src/services/api.service";
import { useParams } from "react-router-dom";

export interface RootCauseAnalysisHandle {
  submit: () => void;
}

const RootCauseAnalysis = forwardRef<
  RootCauseAnalysisHandle,
  RootCauseAnalysisProps
>((props, ref) => {
  const { rcaData, onSubmitSuccess } = props;
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<"success" | "error">("success");
  const [message, setMessage] = useState<string>("");
  const [baselineRcas, setBaselineRcas] = useState<RcaRecord[]>([]);
  const [rcas, setRcas] = useState<RcaRecord[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [preEditSnapshot, setPreEditSnapshot] = useState<RcaRecord | null>(
    null
  );
  const [dropdownData, setDropdownData] = useState<DropdownData | null>(null);
  const [isSubmittedSuccessfully, setIsSubmittedSuccessfully] =
    useState<boolean>(false);
  const selectedRca = useMemo(() => rcas[selectedIndex], [rcas, selectedIndex]);
  const { deviationId } = useParams<{ deviationId: string | "" }>();

  const externalSaveFn = useRef<(() => void) | null>(null);

  useImperativeHandle(ref, () => ({
    submit: submitRCA,
  }));

  useEffect(() => {
    fetchRcaCat();
  }, []);

  const fetchRcaCat = async () => {
    try {
      const res = await fetchRcaCategories();
      console.log(res);
      setDropdownData(res.data);
    } catch (err: any) {
      console.error(err.message);
    }
  };

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

  const handleTabChange = (_: React.SyntheticEvent, newIndex: number) => {
    setSelectedIndex(newIndex);
    setIsEditing(false);
    setPreEditSnapshot(null);
  };

  useEffect(() => {
    if (Array.isArray(rcaData) && rcaData.length > 0) {
      const mapped: RcaRecord[] = rcaData.map((item, idx) => {
        const tabName = `RCA ${idx + 1}`;
        return {
          id: `rca-${idx + 1}`,
          name: tabName,
          sections: [
            {
              key: "issues",
              title: "Causal factor",
              value: item.issues_category ?? "",
              explanation: item.issues ?? "",
            },
            {
              key: "major",
              title: "Major root cause category",
              value: item.major_root_cause_category ?? "",
              explanation: item.major_root_cause_category_validated ?? "",
            },
            {
              key: "near",
              title: "Near root cause",
              value: item.near_root_cause_category ?? "",
              explanation: item.near_root_cause ?? "",
            },
            {
              key: "root",
              title: "Root cause",
              value: item.root_cause_category ?? "",
              explanation: item.root_cause ?? "",
            },
          ],
          meta: {
            createdFrom: "seed",
            createdAt: new Date().toISOString(),
          },
        };
      });
      setBaselineRcas(mapped);
      setRcas(mapped);
      setSelectedIndex(0);
      setIsEditing(false);
      setPreEditSnapshot(null);
    } else {
      setBaselineRcas([]);
      setRcas([]);
      setSelectedIndex(0);
      setIsEditing(false);
      setPreEditSnapshot(null);
    }
  }, [rcaData]);

  const handleAddRca = () => {
    const maxNum =
      rcas.length > 0
        ? Math.max(...rcas.map((rca) => parseInt(rca.name.split(" ")[1])))
        : 0;
    const nextNum = maxNum + 1;
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
    const issuesVal = updated.sections
      .find((s) => s.key === "issues")
      ?.value?.trim();
    const isOther =
      !!issuesVal &&
      dropdownData?.Factors?.some(
        (f) =>
          f.factor_name === "Other Issues" &&
          f.ProblemCategories?.some((pc) => pc.name === issuesVal)
      );

    const requireAll =
      !isOther &&
      updated.sections.some((sec) => !sec.value || sec.value.trim() === "");

    if (!issuesVal || requireAll) {
      setType("error");
      setMessage(
        isOther
          ? "Select an Issue under Other Issues"
          : "All dropdowns must be selected"
      );
      handleShowNotification();
      return;
    }

    const next = [...rcas];
    next[selectedIndex] = updated;
    setRcas(next);
    setIsEditing(false);
    setPreEditSnapshot(null);
  };

  const buildApiItemFromRca = (rca: RcaRecord): ApiRcaItem => {
    const issues = readSection(rca, "issues");
    const major = readSection(rca, "major");
    const near = readSection(rca, "near");
    const root = readSection(rca, "root");

    return {
      deviation_id: deviationId,
      issues: issues.explanation || issues.value || "",
      issues_category: issues.value || "",
      major_root_cause_category: major.value || "",
      major_root_cause_category_validated:
        major.explanation || major.value || "",
      near_root_cause: near.explanation || near.value || "",
      near_root_cause_category: near.value || "",
      root_cause: root.explanation || root.value || "",
      root_cause_category: root.value || "",
    };
  };

  const buildPayload = (): ApiRcaItem | ApiRcaItem[] => {
    if (rcas.length === 1) return buildApiItemFromRca(rcas[0]);
    return rcas.map(buildApiItemFromRca);
  };

  const submitRCA = async () => {
    try {
      const payload = buildPayload();
      await submitRca(payload);
      setIsSubmittedSuccessfully(true);
      onSubmitSuccess();
      setType("success");
      setMessage("RCA successfully submitted");
      handleShowNotification();
    } catch (err) {
      setType("error");
      setMessage("Submission failed: Try again");
      handleShowNotification();
      console.error("Failed to submit rca:", err);
    }
  };

  const readSection = (rca: RcaRecord, key: RcaSection["key"]) => {
    return (
      rca.sections.find((s) => s.key === key) ?? {
        value: "",
        explanation: "",
      }
    );
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
      const next = [...rcas];
      next[selectedIndex] = preEditSnapshot;
      setRcas(next);
    }
    setIsEditing(false);
    setPreEditSnapshot(null);
  };
  const onResetAll = () => {
    const currentId = rcas[selectedIndex]?.id;
    const baselineRca = baselineRcas.find((r) => r.id === currentId);
    if (baselineRca) {
      const next = [...rcas];
      next[selectedIndex] = JSON.parse(JSON.stringify(baselineRca));
      setRcas(next);
    }
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
      {rcaData.length > 0 && (
        <>
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
              isSubmittedSuccessfully={isSubmittedSuccessfully}
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
            isSubmittedSuccessfully={isSubmittedSuccessfully}
            rcas={rcas}
          />

          {!isEditing && selectedRca && <RcaView rca={selectedRca} />}

          {isEditing && selectedRca && (
            <RcaEdit
              rca={selectedRca}
              onSave={handleSaveRca}
              registerOnSave={(fn) => {
                externalSaveFn.current = fn;
              }}
              dropdownData={dropdownData}
            />
          )}
        </>
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
});

export default RootCauseAnalysis;
