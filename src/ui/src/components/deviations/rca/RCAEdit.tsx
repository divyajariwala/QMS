import React, { useEffect, useState } from "react";
import {
  Box,
} from "@mui/material";

import { RcaRecord, RcaSection } from "./RCAMockdata"; 
import styles from "./RootCauseAnalysis.module.scss";
import EditSection from "./EditSection";

interface RcaEditProps {
  rca: RcaRecord;
  onSave: (updated: RcaRecord) => void;
  registerOnSave?: (fn: () => void) => void; 
}

const RcaEdit: React.FC<RcaEditProps> = ({ rca, onSave, registerOnSave }) => {
  const [draft, setDraft] = useState<RcaRecord>(() =>
    JSON.parse(JSON.stringify(rca))
  );

  const BASE_OPTIONS = {
    issues: [
      "Company personnel issue",
      "Training issue",
      "Process/manufacturing equipment issue",
      "Supplier issue",
    ] as const,
    major: [
      "Procedure Issue",
      "Process/manufacturing equipment issue",
      "Documentation issue",
      "Design issue",
    ] as const,
    near: [
      "Company personnel issue",
      "Process/manufacturing equipment issue",
      "Measurement / test method issue",
      "Material issue",
    ] as const,
    root: [
      "Procedure Issue",
      "Documentation issue",
      "Process/manufacturing equipment issue",
      "Training issue",
    ] as const,
  };

  const LINKED_OPTIONS: Record<
    string,
    Record<string, ReadonlyArray<string>>
  > = {
    major: {
      "Company personnel issue": [
        "Procedure Issue",
        "Training issue",
        "Documentation issue",
      ],
      "Training issue": ["Procedure Issue", "Documentation issue"],
      "Process/manufacturing equipment issue": [
        "Process/manufacturing equipment issue",
        "Design issue",
        "Procedure Issue",
      ],
      "Supplier issue": ["Documentation issue", "Procedure Issue"],
    },
    near: {
      "Procedure Issue": [
        "Company personnel issue",
        "Measurement / test method issue",
        "Documentation issue",
      ],
      "Process/manufacturing equipment issue": [
        "Process/manufacturing equipment issue",
        "Material issue",
      ],
      "Documentation issue": [
        "Company personnel issue",
        "Process/manufacturing equipment issue",
      ],
      "Design issue": [
        "Process/manufacturing equipment issue",
        "Material issue",
      ],
      "Training issue": ["Company personnel issue", "Documentation issue"],
    },
    root: {
      "Company personnel issue": ["Procedure Issue", "Training issue"],
      "Measurement / test method issue": [
        "Documentation issue",
        "Procedure Issue",
      ],
      "Process/manufacturing equipment issue": [
        "Process/manufacturing equipment issue",
        "Procedure Issue",
      ],
      "Material issue": [
        "Documentation issue",
        "Process/manufacturing equipment issue",
      ],
      "Documentation issue": ["Procedure Issue", "Training issue"],
    },
  };

  type Key = RcaSection["key"];
  const getPrevKey = (key: Key): Key | undefined =>
    key === "issues"
      ? undefined
      : key === "major"
      ? "issues"
      : key === "near"
      ? "major"
      : "near";

  const previousValue = (key: RcaSection["key"]): string | undefined => {
    const prevKey = getPrevKey(key);
    return prevKey
      ? draft.sections.find((s) => s.key === prevKey)?.value
      : undefined;
  };

  const optionsFor = (key: Key): ReadonlyArray<string> => {
    if (key === "issues") return BASE_OPTIONS.issues;
    const prev = previousValue(key);
    if (key === "major")
      return (prev && LINKED_OPTIONS.major[prev]) || BASE_OPTIONS.major;
    if (key === "near")
      return (prev && LINKED_OPTIONS.near[prev]) || BASE_OPTIONS.near;
    if (key === "root")
      return (prev && LINKED_OPTIONS.root[prev]) || BASE_OPTIONS.root;
    return [];
  };

  const originalValue = (key: Key): string | undefined => {
    const s = rca.sections.find((sec) => sec.key === key);
    return s?.value;
  };

  const setValue = (key: RcaSection["key"], value: string) => {
    setDraft((d) => {
      const next = {
        ...d,
        sections: d.sections.map((s) => {
          if (s.key !== key) return s;
          const wasValue = originalValue(key);
          const explanation = wasValue !== value ? "" : s.explanation; 
          return { ...s, value, explanation };
        }),
      };
      if (key === "issues") {
        next.sections = next.sections.map((s) =>
          s.key === "major" || s.key === "near" || s.key === "root"
            ? { ...s, value: "" }
            : s
        );
      } else if (key === "major") {
        next.sections = next.sections.map((s) =>
          s.key === "near" || s.key === "root" ? { ...s, value: "" } : s
        );
      } else if (key === "near") {
        next.sections = next.sections.map((s) =>
          s.key === "root" ? { ...s, value: "" } : s
        );
      }
      return next;
    });
  };

  const save = () => onSave(draft);

  useEffect(() => {
    registerOnSave?.(save);
  }, [registerOnSave, draft]);

  return (
    <Box className={styles.maxRcaHeight}>
      {draft.sections.map((s) => (
        <EditSection
          key={s.key}
          title={s.title}
          value={s.value}
          options={optionsFor(s.key)}
          onChange={(val) => setValue(s.key, val)}
        />
      ))}
    </Box>
  );
};

export default RcaEdit;
