import React, { useMemo, useState, useEffect } from "react";
import { Box, Divider, Paper, Stack, Typography } from "@mui/material";
import LeftArrow from "../../../assets/icons/leftArrow.svg";
import AISummary from "../../../assets/icons/aiSummary.svg";
import { Editor } from "@tinymce/tinymce-react";

import styles from "./executiveSummary.module.scss";
import { ExecutiveSummaryItem } from "./mockdata";

export interface ExecutiveSummaryProps {
  items: ExecutiveSummaryItem[];
  onBack: () => void;
  onPrimaryAction?: (payload: { label: string; content: string }[]) => void;
  disabled?: boolean;
}

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  items,
  onBack,
  onPrimaryAction,
  disabled = false,
}) => {
  const [summaryValues, setSummaryValues] = useState<
    { label: string; content: string }[]
  >(() => items.map((i) => ({ label: i.label, content: i.content })));

  useEffect(() => {
    setSummaryValues(
      items.map((i) => ({ label: i.label, content: i.content }))
    );
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
      placeholder: "Type or refine the AI-generated summary here...",
      readonly: disabled ? 1 : 0,
    }),
    [disabled]
  );

  const handleEditorChange = (idx: number, newValue: string) => {
    setSummaryValues((prev) => {
      const next = [...prev];
      next[idx] = { ...next[idx], content: newValue };
      return next;
    });
  };

  const handlePrimaryAction = () => {
    const payload = summaryValues.map(({ label, content }) => ({
      label,
      content,
    }));
    onPrimaryAction?.(payload);
  };

  return (
    <Paper variant="outlined" className={styles.summaryRoot}>
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
        {items?.length ? (
          items.map((item, idx) => (
            <Box key={`${item.label}-${idx}`} className={styles.section}>
              <Typography variant="subtitle2" className={styles.sectionLabel}>
                {item.label}
              </Typography>

              <Editor
                init={editorInit}
                tinymceScriptSrc={import.meta.env.VITE_TINYMCE_CDN}
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
          <Typography variant="body2" color="text.secondary">
            No summary available.
          </Typography>
        )}
      </Box>
      <Divider className={styles.headerDivider} />
      <Box>
        <Stack direction="row" spacing={1} className={styles.footerRow}>
          {onPrimaryAction && !disabled && (
            <button
              className={styles.classifyBtn}
              onClick={handlePrimaryAction}
            >
              Save and Send to QMS
            </button>
          )}
        </Stack>
      </Box>
    </Paper>
  );
};

export default ExecutiveSummary;
