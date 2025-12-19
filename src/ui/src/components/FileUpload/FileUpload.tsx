import React, { useCallback, useState, useEffect } from "react";
import {
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  CircularProgress,
} from "@mui/material";
import CloudUploadIcon from "../../../src/assets/icons/upload.svg";
import DownloadIcon from "../../../src/assets/icons/vector.svg";
import CheckCircleIcon from "../../../src/assets/icons/uploadSuccess.svg";
import {
  uploadComplaintFile,
  uploadDeviationFile,
} from "src/services/api.service";
import { FileUploadPopupProps, fileUploadStatus } from "src/types";
import { useLocation } from "react-router-dom";
import styles from "./FileUpload.module.scss";

const FileUpload: React.FC<FileUploadPopupProps> = ({
  open,
  onClose,
  setProcessing,
  onSuccess,
}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [status, setStatus] = useState<fileUploadStatus>("idle");
  const [fileCount, setFileCount] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const location = useLocation();

  useEffect(() => {
    if (!open) {
      setStatus("idle");
      setFileCount(0);
      setIsDragActive(false);
      setErrorMsg(null);
    }
  }, [open]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragActive(false);
  }, []);

  const handleFileLoaded = async (file: File) => {
    setStatus("uploading");
    setErrorMsg(null);

    try {
      const path = location.pathname.toLowerCase();

      let response;
      if (path.includes("complaints")) {
        response = await uploadComplaintFile(file);
      } else if (path.includes("deviations")) {
        response = await uploadDeviationFile(file);
      }

      if (response && response.success) {
        // Sequentially update status with delays
        await new Promise((res) => setTimeout(res, 1000));
        setStatus("importing");
        await new Promise((res) => setTimeout(res, 1500));
        setStatus("extracting");
        await new Promise((res) => setTimeout(res, 2000));
        setStatus("success");
        await new Promise((res) => setTimeout(res, 2500));
        onSuccess?.();
        onClose?.(); // Call onClose callback from parent
        setProcessing(true);
      } else {
        throw new Error(response?.message || "Unknown error during upload");
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setErrorMsg(errorMessage || "File upload failed");
      setStatus("error");
    }
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragActive(false);
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileLoaded(e.dataTransfer.files[0]);
        e.dataTransfer.clearData();
      }
    },
    [handleFileLoaded]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileLoaded(e.target.files[0]);
      }
    },
    [handleFileLoaded]
  );

  const handleDownloadExample = () => {
    const path = location.pathname.toLowerCase();

    const columnHeader = path.includes("complaints")
      ? "Narrative"
      : path.includes("deviations")
      ? "Investigation Summary"
      : "Narrative"; // default fallback

    const html = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office"
          xmlns:x="urn:schemas-microsoft-com:office:excel"
          xmlns="http://www.w3.org/TR/REC-html40">
    <head>
      <!--[if gte mso 9]>
      <xml>
        <x:ExcelWorkbook>
          <x:ExcelWorksheets>
            <x:ExcelWorksheet>
              <x:Name>Sheet 1</x:Name>
              <x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions>
            </x:ExcelWorksheet>
          </x:ExcelWorksheets>
        </x:ExcelWorkbook>
      </xml>
      <![endif]-->
      <style>
        td, th {
          border: 1px solid black;
          padding: 5px;
        }
      </style>
    </head>
    <body>
      <table>
        <tr><th>Serial No</th><th>${columnHeader}</th></tr>
        <tr><td></td><td></td></tr>
        <tr><td></td><td></td></tr>
        <tr><td></td><td></td></tr>
      </table>
    </body>
    </html>
  `;

    const blob = new Blob([html], { type: "application/vnd.ms-excel" });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sample-template.xls"; // Note the .xls extension, not .xlsx
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleClickUploadArea = () => {
    document.getElementById("file-input")?.click();
  };

  const handleKeyDownUploadArea = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      document.getElementById("file-input")?.click();
    }
  };

  const renderStatusContent = () => {
    if (status === "idle" || status === "error") {
      return (
        <>
          <Box
            className={`${styles.uploadArea} ${
              isDragActive ? styles.uploadAreaActive : ""
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClickUploadArea}
            role="button"
            tabIndex={0}
            onKeyDown={handleKeyDownUploadArea}
          >
            <img
              src={CloudUploadIcon}
              alt="Upload"
              className={styles.uploadIcon}
            />
            <Box role="button" component="p" className={styles.helperText}>
              Click or drag file to this area to upload
            </Box>

            <input
              type="file"
              accept=".pdf,.csv,.xlsx,.PDF,.CSV,.XLSX"
              id="file-input"
              className={styles.fileInputHidden}
              onChange={handleFileChange}
              disabled={(status as fileUploadStatus) === "uploading"}
            />
          </Box>

          <Box className={styles.formatsLine}>
            Formats accepted are pdf, .csv and .xlsx
          </Box>

          <Box className={styles.helperText}>
            If you do not have a file you can use the sample below:
          </Box>

          <button
            className={styles.downloadButton}
            onClick={handleDownloadExample}
            disabled={(status as fileUploadStatus) === "uploading"}
          >
            <img
              src={DownloadIcon}
              alt="Download icon"
              className={styles.downloadButtonIcon}
            />
            Download Sample Template
          </button>

          {status === "error" && (
            <Box sx={{ color: "red", marginTop: 2 }}>
              Error uploading file: {errorMsg}
            </Box>
          )}
        </>
      );
    }

    const statusBoxProps = { className: styles.statusBox };

    if (status === "importing" || status === "uploading") {
      return (
        <Box {...statusBoxProps}>
          <CircularProgress className={styles.circularProgress} />
          <Box className={styles.statusTitle}>Importing file(s)</Box>
          <Box className={styles.statusSubtitle}>
            Please wait few seconds while we&apos;re extracting your data
          </Box>
        </Box>
      );
    }

    if (status === "extracting") {
      return (
        <Box {...statusBoxProps}>
          <CircularProgress className={styles.circularProgress} />
          <Box className={styles.statusTitle}>Extracting data</Box>
          <Box className={styles.statusSubtitle}>
            Please wait few seconds while we&apos;re extracting your data
          </Box>
        </Box>
      );
    }

    if (status === "success") {
      return (
        <Box {...statusBoxProps}>
          <img
            src={CheckCircleIcon}
            alt="Success"
            className={styles.successIcon}
          />
          <Box className={styles.statusTitle}>Extraction successful</Box>
          <Box className={styles.statusSubtitle}>
            Please wait while we redirect to the main page
          </Box>
        </Box>
      );
    }

    return null;
  };

  const dialogHeight = status === "idle" || status === "error" ? 448 : 334;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      PaperProps={{
        className: styles.dialogPaper,
        sx: { height: dialogHeight },
      }}
    >
      <DialogTitle className={styles.dialogTitle}>File Upload</DialogTitle>

      <DialogContent className={styles.dialogContent}>
        {renderStatusContent()}
      </DialogContent>
    </Dialog>
  );
};

export default FileUpload;