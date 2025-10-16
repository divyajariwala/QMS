import React, { useCallback, useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  useTheme,
  CircularProgress,
} from '@mui/material';
import CloudUploadIcon from '../../../src/assets/icons/upload.svg';
import DownloadIcon from '../../../src/assets/icons/vector.svg';
import CheckCircleIcon from '../../../src/assets/icons/uploadSuccess.svg';
import styles from './FileUpload.module.scss';

interface FileUploadPopupProps {
  open: boolean;
  onClose: () => void;
  onFileSelect: (file: File) => void;
}

type Status = 'idle' | 'importing' | 'extracting' | 'success';

const TOTAL_FILES = 3;

const FileUpload: React.FC<FileUploadPopupProps> = ({
  open,
  onClose,
  onFileSelect
}) => {
  const theme = useTheme();
  const [isDragActive, setIsDragActive] = useState(false);
  const [status, setStatus] = useState<Status>('idle');
  const [fileCount, setFileCount] = useState(0);

  useEffect(() => {
    if (!open) {
      setStatus('idle');
      setFileCount(0);
      setIsDragActive(false);
    }
  }, [open]);

  useEffect(() => {
    if (status === 'importing') {
      const timer = setTimeout(() => setStatus('extracting'), 2000);
      return () => clearTimeout(timer);
    }
    if (status === 'extracting') {
      const timer = setTimeout(() => setStatus('success'), 3000);
      return () => clearTimeout(timer);
    }
    if (status === 'success') {
      const timer = setTimeout(() => onClose(), 2500);
      return () => clearTimeout(timer);
    }
  }, [status, onClose]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragActive(false);
  }, []);

  const handleFileLoaded = (file: File) => {
    setFileCount(TOTAL_FILES);
    setStatus('importing');
    onFileSelect(file);
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
    const blob = new Blob(
      [new Uint8Array([0x50, 0x57, 0x43, 0x2d, 0x58, 0x4c, 0x53])],
      { type: "application/vnd.ms-excel" }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "document-example.xls";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClickUploadArea = () => {
    document.getElementById('file-input')?.click();
  };

  const handleKeyDownUploadArea = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      document.getElementById('file-input')?.click();
    }
  };

  const renderStatusContent = () => {
    if (status === 'idle') {
      return (
        <>
          <Box
            className={`${styles.uploadArea} ${isDragActive ? styles.uploadAreaActive : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClickUploadArea}
            role="button"
            tabIndex={0}
            onKeyDown={handleKeyDownUploadArea}
          >
            <img src={CloudUploadIcon} alt="Upload" className={styles.uploadIcon} />
            <Box
              component="p"
              className={styles.helperText}
            >
              Click or drag file to this area to upload
            </Box>

            <input
              type="file"
              accept=".pdf,.csv,.xlsx"
              id="file-input"
              className={styles.fileInputHidden}
              onChange={handleFileChange}
            />
          </Box>

          <Box className={styles.formatsLine}>
            Formats accepted are pdf, .csv and .xlsx
          </Box>

          <Box className={styles.helperText}>
            If you do not have a file you can use the sample below:
          </Box>

          <Button
            variant="outlined"
            startIcon={<img src={DownloadIcon} alt="Download icon" className={styles.downloadButtonIcon} />}
            className={styles.downloadButton}
            onClick={handleDownloadExample}
          >
            Download Sample Template
          </Button>
        </>
      );
    }

    const statusBoxProps = { className: styles.statusBox };

    if (status === 'importing') {
      return (
        <Box {...statusBoxProps}>
          <CircularProgress className={styles.circularProgress} />
          <Box className={styles.statusTitle}>
            Importing file(s) {fileCount}/{TOTAL_FILES}
          </Box>
          <Box className={styles.statusSubtitle}>
            Please wait few seconds while we&apos;re extracting your data
          </Box>
        </Box>
      );
    }

    if (status === 'extracting') {
      return (
        <Box {...statusBoxProps}>
          <CircularProgress className={styles.circularProgress} />
          <Box className={styles.statusTitle}>
            Extracting data {fileCount}/{TOTAL_FILES}
          </Box>
          <Box className={styles.statusSubtitle}>
            Please wait few seconds while we&apos;re extracting your data
          </Box>
        </Box>
      );
    }

    if (status === 'success') {
      return (
        <Box {...statusBoxProps}>
          <img src={CheckCircleIcon} alt="Success" className={styles.successIcon} />
          <Box className={styles.statusTitle}>
            Extraction successful
          </Box>
          <Box className={styles.statusSubtitle}>
            Please wait while we redirect to the main page
          </Box>
        </Box>
      );
    }

    return null;
  };

  const dialogHeight = status === 'idle' ? 448 : 334;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      PaperProps={{
        className: styles.dialogPaper,
        sx: { height: dialogHeight },
      }}
    >
      <DialogTitle
        className={styles.dialogTitle}
      >
        File Upload
      </DialogTitle>

      <DialogContent className={styles.dialogContent}>
        {renderStatusContent()}
      </DialogContent>
    </Dialog>
  );
};

export default FileUpload;