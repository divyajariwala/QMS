import React, { useCallback, useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  useTheme,
  CircularProgress,
} from '@mui/material';
import CloudUploadIcon from '../../../src/assets/icons/upload.svg';
import DownloadIcon from '../../../src/assets/icons/vector.svg';
import CheckCircleIcon from '../../../src/assets/icons/uploadSuccess.svg';

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

  // Reset state on open/close
  useEffect(() => {
    if (!open) {
      setStatus('idle');
      setFileCount(0);
      setIsDragActive(false);
    }
  }, [open]);

  // Simulate status progression after file selected
  useEffect(() => {
    if (status === 'importing') {
      const timer = setTimeout(() => {
        setStatus('extracting');
      }, 2000);
      return () => clearTimeout(timer);
    }
    if (status === 'extracting') {
      const timer = setTimeout(() => {
        setStatus('success');
      }, 3000);
      return () => clearTimeout(timer);
    }
    if (status === 'success') {
      const timer = setTimeout(() => {
        onClose();
      }, 2500);
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

  // Different content depending on upload status
  const renderStatusContent = () => {
    if (status === 'idle') {
      return (
        <>
          <Box
            sx={{
              mt: 3,
              mb: 2,
              p: 2,
              width: 499,
              height: 150,
              border: `1.5px dashed ${isDragActive ? theme.palette.primary.main : theme.palette.grey[400]
                }`,
              borderRadius: 1,
              textAlign: 'center',
              cursor: 'pointer',
              color: isDragActive ? theme.palette.primary.main : theme.palette.text.secondary,
              transition: 'border-color 0.3s, color 0.3s',
              userSelect: 'none',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              gap: 2
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClickUploadArea}
            role="button"
            tabIndex={0}
            onKeyDown={handleKeyDownUploadArea}
          >
            <img src={CloudUploadIcon} />
            <Typography
              variant="body2"
              component="p"
              sx={{
                fontFamily: "'Inter', sans-serif",
                fontWeight: 400,
                fontStyle: 'normal',
                fontSize: '16px',
                lineHeight: 1,
                letterSpacing: 0,
                userSelect: 'none',
              }}
            >
              Click or drag file to this area to upload
            </Typography>
            <input
              type="file"
              accept=".pdf,.csv,.xlsx"
              id="file-input"
              hidden
              onChange={handleFileChange}
            />
          </Box>

          <Typography
            variant="caption"
            color="text.secondary"
            display="block"
            mb={3}
            sx={{
              fontFamily: "'Inter', sans-serif",
              fontWeight: 400,
              fontStyle: 'normal',
              fontSize: '16px',
              lineHeight: 1,
              letterSpacing: 0,
              color: '#9D9D9D',
              borderBottom: '1px solid #9D9D9D',
              pb: 2,
              pt: 1
            }}
          >
            Formats accepted are pdf, .csv and .xlsx
          </Typography>

          <Typography
            variant="body2"
            sx={{
              fontFamily: "'Inter', sans-serif",
              fontWeight: 400,
              fontStyle: 'normal',
              fontSize: '16px',
              lineHeight: 1,
              letterSpacing: 0,
              mb: 3,
              color: '#525252'
            }}
          >
            If you do not have a file you can use the sample below:
          </Typography>

          <Button
            variant="outlined"
            startIcon={<img src={DownloadIcon} alt="Download icon" style={{ width: 18, height: 18 }} />}
            fullWidth
            sx={{
              backgroundColor: 'white',
              textTransform: 'none',
              justifyContent: 'flex-start',
              pl: 3,
              borderRadius: '8px',
              fontFamily: "'Inter', sans-serif",
              fontWeight: 400,
              fontStyle: 'normal',
              fontSize: '16px',
              lineHeight: 1,
              letterSpacing: 0,
              gap: 1,
              width: 503,
              height: 44,
              color: '#606260'

            }}
            onClick={handleDownloadExample}
          >
            Download Sample Template
          </Button>
        </>
      );
    }

    const statusBoxStyles = {
      height: 250,
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center' as const,
      userSelect: 'none',
    };

    if (status === 'importing') {
      return (
        <Box sx={statusBoxStyles}>
          <CircularProgress sx={{ color: theme.palette.info.light, mb: 2 }} />
          <Typography variant="subtitle1" gutterBottom sx={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 500,
            fontStyle: 'normal',
            fontSize: '18px',
            lineHeight: '28px',
            letterSpacing: 0,
            textAlign: 'center',
            color: '#535353'
          }}>
            Importing file(s) {fileCount}/{TOTAL_FILES}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 400,
            fontStyle: 'normal',
            fontSize: '14px',
            lineHeight: '20px',
            letterSpacing: 0,
            textAlign: 'center',
            width: 276,
            height: 40
          }}>
            Please wait few seconds while we&apos;re extracting your data
          </Typography>
        </Box>
      );
    }
    if (status === 'extracting') {
      return (
        <Box sx={statusBoxStyles}>
          <CircularProgress sx={{ color: theme.palette.info.light, mb: 2 }} />
          <Typography variant="subtitle1" gutterBottom sx={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 500,
            fontStyle: 'normal',
            fontSize: '18px',
            lineHeight: '28px',
            letterSpacing: 0,
            textAlign: 'center',
            color: '#535353'
          }}>
            Extracting data {fileCount}/{TOTAL_FILES}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 400,
            fontStyle: 'normal',
            fontSize: '14px',
            lineHeight: '20px',
            letterSpacing: 0,
            textAlign: 'center',
            width: 276,
            height: 40
          }}>
            Please wait few seconds while we&apos;re extracting your data
          </Typography>
        </Box>
      );
    }
    if (status === 'success') {
      return (
        <Box sx={statusBoxStyles}>
          <img src={CheckCircleIcon} />
          <Typography
            variant="subtitle1"
            gutterBottom
            sx={{
              fontFamily: "'Inter', sans-serif",
              fontWeight: 500,
              fontStyle: 'normal',
              fontSize: '18px',
              lineHeight: '28px',
              letterSpacing: 0,
              textAlign: 'center',
              color: '#535353'
            }}
          >
            Extraction successful
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 400,
            fontStyle: 'normal',
            fontSize: '14px',
            lineHeight: '20px',
            letterSpacing: 0,
            textAlign: 'center',
            width: 276,
            height: 40
          }}
          >
            Please wait while we redirect to the main page
          </Typography>
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
        sx: {
          width: 551,
          borderRadius: 2,
          height: dialogHeight
        },
      }}
    >
      <DialogTitle
        sx={{
          width: '551px',
          height: '64px',
          borderBottom: `1px solid ${theme.palette.divider}`,
          display: 'flex',
          alignItems: 'center',
          px: 2,
          userSelect: 'none',
          fontFamily: "'Inter', sans-serif",
          fontWeight: 600,
          fontStyle: 'normal',
          fontSize: '20px',
          lineHeight: 1,
          letterSpacing: 0,
        }}
      >
        File Upload
      </DialogTitle>

      <DialogContent>{renderStatusContent()}</DialogContent>
    </Dialog>
  );
};

export default FileUpload;