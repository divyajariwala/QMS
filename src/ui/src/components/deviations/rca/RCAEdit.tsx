import React, { useEffect, useState, useMemo, useCallback } from "react";
import { Box } from "@mui/material";

import { RcaRecord, RcaSection, DropdownData } from "./RCATypes";
import styles from "./RootCauseAnalysis.module.scss";
import EditSection from "./EditSection";

interface RcaEditProps {
  rca: RcaRecord;
  onSave: (updated: RcaRecord) => void;
  registerOnSave?: (fn: () => void) => void;
  dropdownData: DropdownData | null;
}

const RcaEdit: React.FC<RcaEditProps> = ({
  rca,
  onSave,
  registerOnSave,
  dropdownData,
}) => {
  const [draft, setDraft] = useState(() => JSON.parse(JSON.stringify(rca)));

  const issuesList = useMemo(
    () =>
      (dropdownData?.Factors ?? [])
        .flatMap((f) => f.ProblemCategories?.map((pc) => pc.name) ?? [])
        .filter(Boolean),
    [dropdownData]
  );

  const issueToFactor = useMemo(() => {
    const map = new Map<string, string>();
    (dropdownData?.Factors ?? []).forEach((f) => {
      (f.ProblemCategories ?? []).forEach((pc) => {
        if (pc?.name) map.set(pc.name, f.factor_name);
      });
    });
    return map;
  }, [dropdownData]);

  const isOtherIssueSelected = useMemo(() => {
    const val = draft.sections.find(
      (s: RcaSection) => s.key === "issues"
    )?.value;
    return val && issueToFactor.get(val) === "Other Issues";
  }, [draft.sections, issueToFactor]);

  const majorList = useMemo(
    () =>
      (dropdownData?.MajorRootCauseCategories ?? [])
        .map((m) => m.description)
        .filter(Boolean),
    [dropdownData]
  );

  const nearListFor = useCallback(
    (majorDesc: string) => {
      const major = (dropdownData?.MajorRootCauseCategories ?? []).find(
        (m) => m.description === majorDesc
      );

      const details = major?.properties?.details ?? [];
      return details
        .map((d) =>
          "NearRootCauses" in d ? d.NearRootCauses : (d as any).name
        )
        .filter(Boolean) as string[];
    },
    [dropdownData]
  );

  const rootListFor = useCallback(
    (majorDesc: string, nearName: string) => {
      const major = (dropdownData?.MajorRootCauseCategories ?? []).find(
        (m) => m.description === majorDesc
      );

      const details = major?.properties?.details ?? [];

      const match = details.find((d) => {
        const label =
          "NearRootCauses" in d ? d.NearRootCauses : (d as any).name;
        return label === nearName;
      });

      return (match?.rootcauses ?? [])
        .map((rc) => rc.name)
        .filter(Boolean) as string[];
    },
    [dropdownData]
  );

  type Key = RcaSection["key"];
  const previousValue = (key: Key): string | undefined => {
    const prevKey =
      key === "issues"
        ? undefined
        : key === "major"
        ? "issues"
        : key === "near"
        ? "major"
        : "near";
    return prevKey
      ? draft.sections.find((s: RcaSection) => s.key === prevKey)?.value
      : undefined;
  };

  const optionsFor = (key: Key): ReadonlyArray<string> => {
    if (key === "issues")
      return issuesList.filter(
        (item: string | undefined): item is string => item !== undefined
      );
    const prev = previousValue(key);
    if (key === "major")
      return isOtherIssueSelected
        ? []
        : majorList.filter(
            (item: string | undefined): item is string => item !== undefined
          );
    if (key === "near") return prev ? nearListFor(prev) : [];
    if (key === "root") {
      const nearPrev = previousValue("root");
      const majorPrev = previousValue("near");
      return nearPrev && majorPrev ? rootListFor(majorPrev, nearPrev) : [];
    }
    return [];
  };

  const originalValue = (key: Key): string | undefined => {
    const s = rca.sections.find((sec) => sec.key === key);
    return s?.value;
  };

  const setValue = (key: Key, value: string) => {
    setDraft((d: RcaRecord) => {
      const wasValue = originalValue(key);
      const valueChanged = wasValue !== value;
      const next = {
        ...d,
        sections: d.sections.map((s: RcaSection) => {
          if (s.key !== key) {
            const explanation = valueChanged ? "" : s.explanation;
            return { ...s, explanation };
          }
          const explanation = valueChanged ? "" : s.explanation;
          return { ...s, value, explanation };
        }),
      };
      if (key === "issues") {
        next.sections = next.sections.map((s: RcaSection) =>
          s.key === "major" || s.key === "near" || s.key === "root"
            ? { ...s, value: "" }
            : s
        );
      } else if (key === "major") {
        next.sections = next.sections.map((s: RcaSection) =>
          s.key === "near" || s.key === "root" ? { ...s, value: "" } : s
        );
      } else if (key === "near") {
        next.sections = next.sections.map((s: RcaSection) =>
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

  const shouldRender = (key: Key) => {
    if (key === "issues") return true;
    return !isOtherIssueSelected;
  };

  return (
    <Box className={styles.maxRcaHeight}>
      {draft.sections.map((s: RcaSection) =>
        shouldRender(s.key) ? (
          <EditSection
            key={s.key}
            title={s.title}
            value={s.value}
            options={optionsFor(s.key)}
            onChange={(val: string) => setValue(s.key, val)}
          />
        ) : null
      )}
    </Box>
  );
};

export default RcaEdit;
