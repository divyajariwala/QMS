import React from "react";
import {
  Dialog,
  DialogContent,
  IconButton,
  Box,
  Typography,
  Stack,
} from "@mui/material";
import CloseIcon from "../../../assets/icons/close.svg";
import styles from "./SCNExtractedSourcesModal.module.scss";
import Gauge from "@components/common/GaugeChart";

interface Props {
  open: boolean;
  onClose: () => void;
  sources?: any;
}

const formatKey = (key: string) => {
  return key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
};

const renderExtractedValue = (
  value: string,
  originalKey: string,
  confidence?: number,
) => {
  const lines = value
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  const renderFieldHeader = (label: string, score?: number) => (
    <Box className={styles.fieldHeader}>
      <Typography className={styles.parsedKey}>{label}</Typography>
      {score !== undefined && (
        <Box className={styles.miniGaugeWrapper}>
          <Gauge value={score} size={80} />
        </Box>
      )}
    </Box>
  );

  const renderFallbackKey = () =>
    renderFieldHeader(formatKey(originalKey), confidence);

  // 1. Table format (multiple lines, all contain |)
  if (lines.length > 0 && lines.every((l) => l.includes("|"))) {
    // Check if the lines actually have consistent columns (or just render what's there)
    return (
      <Box className={styles.keyValueBox}>
        {renderFallbackKey()}
        <Box className={styles.tableContainer}>
          <table className={styles.dataTable}>
            <thead>
              <tr>
                {lines[0].split("|").map((header, i) => (
                  <th key={i}>{header.trim()}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {lines.slice(1).map((row, i) => (
                <tr key={i}>
                  {row.split("|").map((cell, j) => (
                    <td key={j}>{cell.trim()}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      </Box>
    );
  }

  // Helper to clean extracted keys (e.g. remove trailing colon)
  const cleanKey = (k: string) => k.replace(/:$/, "").trim();

  // 2. Key-Value separated by | (single line)
  if (lines.length === 1 && lines[0].includes("|")) {
    const parts = lines[0].split("|");
    const extractedKey = parts[0].trim();
    return (
      <Box className={styles.keyValueBox}>
        {renderFieldHeader(cleanKey(extractedKey), confidence)}
        <Typography className={styles.parsedValue}>
          {parts.slice(1).join("|").trim()}
        </Typography>
      </Box>
    );
  }

  // 3. Key-Value separated by | (spanning multiple lines)
  if (lines.length > 1 && lines[0].includes("|")) {
    const parts = lines[0].split("|");
    const extractedKey = parts[0].trim();
    return (
      <Box className={styles.keyValueBox}>
        {renderFieldHeader(cleanKey(extractedKey), confidence)}
        <Box className={styles.parsedValue}>
          {parts[1]?.trim() && <div>{parts.slice(1).join("|").trim()}</div>}
          {lines.slice(1).map((line, idx) => (
            <div key={idx}>{line}</div>
          ))}
        </Box>
      </Box>
    );
  }

  // 4. Starts with a colon keyword (e.g. "From: Kestrel")
  if (lines.length === 1 && lines[0].includes(":")) {
    const colonIdx = lines[0].indexOf(":");
    if (colonIdx > 0 && colonIdx < 50) {
      const extractedKey = lines[0].substring(0, colonIdx).trim();
      const valPart = lines[0].substring(colonIdx + 1).trim();
      return (
        <Box className={styles.keyValueBox}>
          {renderFieldHeader(extractedKey, confidence)}
          <Typography className={styles.parsedValue}>{valPart}</Typography>
        </Box>
      );
    }
  }

  // Fallback: Render original key and all lines directly
  return (
    <Box className={styles.keyValueBox}>
      {renderFallbackKey()}
      <Box className={styles.parsedValue}>
        {lines.map((line, idx) => (
          <div key={idx}>{line}</div>
        ))}
      </Box>
    </Box>
  );
};

const SCNExtractedSourcesModal: React.FC<Props> = ({
  open,
  onClose,
  sources,
}) => {
  const hasSources = sources && Object.keys(sources).length > 0;
  const confidenceMap = sources?.field_confidence_map || {};
  const overallConfidence = sources?.confidence_score ?? 0;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ className: styles.paper }}
    >
      <IconButton className={styles.close} onClick={onClose}>
        <img src={CloseIcon} alt="X" />
      </IconButton>

      <DialogContent className={styles.content}>
        <div className={styles.title}>Extracted Field Sources</div>

        <Box className={styles.gaugeContainer}>
          <Gauge value={overallConfidence} />
          <Box className={styles.statContainer}>
            <Box className={styles.statRow}>
              <Stack direction="row" spacing={1} alignItems="center">
                <span className={`${styles.dot} ${styles.greenDot}`} />
                <span className={styles.statLabel}>Good</span>
              </Stack>
              <span className={styles.statValue}>0.7 - 1.0</span>
            </Box>
            <Box className={styles.statRow}>
              <Stack direction="row" spacing={1} alignItems="center">
                <span className={`${styles.dot} ${styles.yellowDot}`} />
                <span className={styles.statLabel}>Medium</span>
              </Stack>
              <span className={styles.statValue}>0.4 - 0.7</span>
            </Box>
            <Box className={styles.statRowLast}>
              <Stack direction="row" spacing={1} alignItems="center">
                <span className={`${styles.dot} ${styles.redDot}`} />
                <span className={styles.statLabel}>Poor</span>
              </Stack>
              <span className={styles.statValue}>0.0 - 0.4</span>
            </Box>
          </Box>
        </Box>

        <Box className={styles.sourcesList}>
          {hasSources ? (
            Object.entries(sources).map(([key, value]) => {
              if (
                !value ||
                typeof value !== "string" ||
                key === "confidence_score" ||
                key === "field_confidence_map" ||
                key === "created_at" ||
                key === "updated_at"
              ) {
                return null;
              }
              const fieldConfidence = confidenceMap[key];
              return (
                <Box key={key} className={styles.sourceItem}>
                  {renderExtractedValue(value, key, fieldConfidence)}
                </Box>
              );
            })
          ) : (
            <Box className={styles.emptyState}>
              No extracted sources available.
            </Box>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default SCNExtractedSourcesModal;
