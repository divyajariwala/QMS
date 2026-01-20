import React, { useMemo, useState, useEffect, useRef } from "react";
import {
  Box,
  Divider,
  Stack,
  Typography,
  Snackbar,
  Alert,
  CircularProgress,
} from "@mui/material";
import LeftArrow from "../../../assets/icons/leftArrow.svg";
import AISummary from "../../../assets/icons/aiSummary.svg";
import { Editor } from "@tinymce/tinymce-react";

import styles from "./executiveSummary.module.scss";
import { ExecutiveSummaryItem } from "./GradingTypes";

export interface ExecutiveSummaryProps {
  items: ExecutiveSummaryItem[];
  onBack: () => void;
  onSaveAndSubmit?: (
    payload: { label: string; content: string; isEdited: boolean }[]
  ) => void;
  disabled?: boolean;
  tinymceScriptSrc?: string;
  onNotify?: (message: string, severity?: "success" | "info" | "error") => void;
  summaryLoad: boolean;
}
type SummaryValue = { label: string; content: string; isEdited: boolean };

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  items,
  onBack,
  onSaveAndSubmit,
  disabled = false,
  tinymceScriptSrc,
  summaryLoad,
}) => {
  const [summaryValues, setSummaryValues] = useState<SummaryValue[]>(() =>
    items.map((i) => ({ label: i.label, content: i.content, isEdited: false }))
  );
  const [snack, setSnack] = useState<{
    open: boolean;
    message: string;
    severity?: "success" | "info" | "error";
  }>({
    open: false,
    message: "",
    severity: "info",
  });

  const ignoreFirstChangeRef = useRef<boolean[]>([]);
  useEffect(() => {
    setSummaryValues(
      items.map((i) => ({
        label: i.label,
        content: i.content,
        isEdited: false,
      }))
    );
    ignoreFirstChangeRef.current = items.map(() => false);
  }, [items]);

  const editorInit = useMemo(
    () => ({
      height: 200,
      menubar: false,
      statusbar: false,
      branding: false,
      plugins: [
        "advlist",
        "autolink",
        "lists",
        "link",
        "charmap",
        "preview",
        "anchor",
        "searchreplace",
        "visualblocks",
        "code",
        "fullscreen",
        "insertdatetime",
        "table",
        "help",
        "wordcount",
      ],
      toolbar:
        "undo redo | formatselect | " +
        "bold italic underline forecolor backcolor | alignleft aligncenter alignright alignjustify | " +
        "bullist numlist outdent indent | removeformat | help",
      content_style:
        "body { font-family: Inter, Roboto, Helvetica, Arial, sans-serif; font-size: 14px; }",
      placeholder: "Type here...",
    }),
    []
  );

  const handleEditorChange = (idx: number, newValue: string) => {
    if (!ignoreFirstChangeRef.current[idx]) {
      ignoreFirstChangeRef.current[idx] = true;
      return;
    }

    setSummaryValues((prev) => {
      const next = [...prev];
      next[idx] = {
        ...next[idx],
        content: newValue,
        isEdited: true,
      };
      return next;
    });
  };

  const handlePrimaryAction = () => {
    const payload = summaryValues.map(({ label, content, isEdited }) => ({
      label,
      content,
      isEdited,
    }));
    onSaveAndSubmit?.(payload);
  };

  return (
    <Box>
      <Box className={styles.headerRow}>
        <Stack direction="row" spacing={1} alignItems="center">
          {!disabled && (
            <img
              src={LeftArrow}
              alt={"left arrow"}
              onClick={onBack}
              className={styles.backIcon}
            />
          )}

          <Typography variant="h6" className={styles.title}>
            <img src={AISummary} alt={"ai summary"} />
            AI Generated Executive Summary
          </Typography>
        </Stack>
      </Box>
      <Divider className={styles.headerDivider} />
      <Box className={styles.contentBox}>
        {summaryLoad ? (
          <Box className={styles.loaderBox}>
            <CircularProgress size={24} />
            <Typography variant="body2" sx={{ ml: 1 }}>
              Loading summary...
            </Typography>
          </Box>
        ) : (
          <>
            {items?.length ? (
              items.map((item, idx) => (
                <Box key={`${item.label}-${idx}`} className={styles.section}>
                  <Typography
                    variant="subtitle2"
                    className={styles.sectionLabel}
                  >
                    {item.label}
                  </Typography>
                  <Editor
                    init={editorInit}
                    tinymceScriptSrc={tinymceScriptSrc}
                    id={`exec-summary-editor-${idx}`}
                    initialValue={item.content}
                    onEditorChange={(newValue: string) =>
                      handleEditorChange(idx, newValue)
                    }
                    disabled={disabled}
                  />
                </Box>
              ))
            ) : (
              <Box className={styles.loaderBox}>
                <Typography variant="body2" sx={{ ml: 1 }}>
                  No summary to load
                </Typography>
              </Box>
            )}
          </>
        )}
      </Box>
      <Divider className={styles.headerDivider} />
      <Box>
        <Stack direction="row" spacing={1} className={styles.footerRow}>
          {onSaveAndSubmit && !disabled && (
            <button
              className={styles.classifyBtn}
              onClick={handlePrimaryAction}
              disabled={!items?.length}
            >
              Save and Send to QMS
            </button>
          )}
        </Stack>
      </Box>
      <Snackbar
        open={snack.open}
        autoHideDuration={2500}
        onClose={() => setSnack((s) => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          severity={snack.severity ?? "info"}
          onClose={() => setSnack((s) => ({ ...s, open: false }))}
        >
          {snack.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ExecutiveSummary;
