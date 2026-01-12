import { useState, useEffect, MouseEvent } from "react";
import { useParams } from "react-router-dom";
import { Paper, Stack, Box, Button, Typography } from "@mui/material";
import styles from "./InvestigationSummary.module.scss";
import PlusIcon from "../../assets/icons/plus.svg";
import EmptyImg from "../../assets/images/emptyState.svg";
import { saveInvestigationSummary } from "src/services/deviations";

type Props = {
  summary: string;
  setSummary: (value: string) => void;
  onAddCard?: () => void;
};

const InvestigationSummary = ({ summary = "", setSummary }: Props) => {
  const hasSummary = summary?.trim().length > 0;
  const [draft, setDraft] = useState<string>(summary);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const { deviationId } = useParams<{ deviationId: string | undefined }>();

  useEffect(() => {
    if (!isEditing) {
      setDraft(summary);
    }
  }, [summary, isEditing]);

  const startEditing = (event?: MouseEvent<HTMLButtonElement>): void => {
    event?.preventDefault();
    setDraft(summary);
    setIsEditing(true);
  };

  const cancelEditing = (): void => {
    setDraft(summary); // revert to original
    setIsEditing(false);
  };

const saveEditing = async () => {
  try {
    const next = draft.trim();
    setSummary(next);
    setIsEditing(false);
    const payload = {
      deviationId: deviationId,
      summary: next,
    };
    await saveInvestigationSummary(payload);
  } catch (err) {
    console.error("Failed to save investigation summary:", err);
  }
};

  useEffect(() => {
    if (!isEditing) return;
    const handler = (e: KeyboardEvent) => {
      const isSave = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s";
      const isEsc = e.key === "Escape";

      if (isSave) {
        e.preventDefault();
        saveEditing();
      } else if (isEsc) {
        e.preventDefault();
        cancelEditing();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isEditing, draft]);

  return (
    <Paper variant="outlined" className={styles.investigationSummary}>
      <Stack
        direction="row"
        alignItems="center"
        spacing={1}
        className={styles.header}
      >
        <Box className={styles.title}>Investigation Summary</Box>
      </Stack>

      <Box className={hasSummary ? styles.body : styles.bodyEmpty}>
        {isEditing ? (
          <Stack spacing={2} className={styles.editorContainer}>
            <textarea
              id="summary"
              autoFocus
              className={styles.textarea}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
            />
            <Stack direction="row" spacing={1} justifyContent="flex-end">
              <Button
                variant="outlined"
                onClick={cancelEditing}
                className={styles.btnCancel}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                onClick={saveEditing}
                disabled={draft?.trim().length === 0}
                className={styles.btnSubmit}
              >
                Submit
              </Button>
            </Stack>
          </Stack>
        ) : (
          <>
            {hasSummary ? (
              <Stack spacing={2} className={styles.summaryContainer}>
                <Box className={styles.summaryText}>{summary}</Box>
              </Stack>
            ) : (
              <Stack
                alignItems="center"
                justifyContent="center"
                spacing={2}
                className={styles.emptyState}
              >
                <img
                  className={styles.emptyStateImage}
                  src={EmptyImg}
                  alt="Empty"
                />
                <Typography className={styles.headerText}>
                  There is currently no data to display.
                </Typography>
                <Typography className={styles.subText}>
                  To begin RCA, please manually input the investigation summary.
                </Typography>
                <Stack direction="row" spacing={1}>
                  <Button
                    variant="text"
                    onClick={startEditing}
                    className={styles.addBtn}
                  >
                    <img src={PlusIcon} alt="plus" />
                    Add Manually
                  </Button>
                </Stack>
              </Stack>
            )}
          </>
        )}
      </Box>
    </Paper>
  );
};

export default InvestigationSummary;
