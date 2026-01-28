import React, { RefObject, useRef, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Button,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import styles from "./UploadSCN.module.scss";
import Frame from "../../assets/icons/Frame.svg";

interface UploadSCNModalProps {
  open: boolean;
  onClose: () => void;
  fileInputRef: RefObject<HTMLInputElement>;
}

const UPLOAD_ACCEPTED_FORMATS = [".pdf"];
const UPLOAD_PROGRESS_INTERVAL = 30;
const UPLOAD_PROGRESS_STEP = 2;

const mockExtractedData = {
  scnTitle: "SCN-12345",
  supplierName: "Supplier XYZ",
  plannedImplementationDate: "2026-01-07",
};

export const UploadSCNModal: React.FC<UploadSCNModalProps> = ({
  open,
  onClose,
  fileInputRef,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const progressRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const navigate = useNavigate();

  const simulateUpload = () => {
    if (progressRef.current) clearInterval(progressRef.current);

    progressRef.current = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev + UPLOAD_PROGRESS_STEP >= 100) {
          clearInterval(progressRef.current!);
          setUploading(false);
          setUploadSuccess(true);
          return 100;
        }
        return prev + UPLOAD_PROGRESS_STEP;
      });
    }, UPLOAD_PROGRESS_INTERVAL);
  };

  const handleFile = (file: File) => {
    setUploadError(null);

    if (!UPLOAD_ACCEPTED_FORMATS.includes(file.name.slice(-4).toLowerCase())) {
      setUploadError("Only PDF files are accepted.");
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    setUploadProgress(0);
    setUploading(true);
    setUploadSuccess(false);
    simulateUpload();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const handleDone = () => {
    navigate("/scn/upload-details", {
      state: { ...mockExtractedData, file: selectedFile?.name },
    });
    handleClose();
  };

  const handleClose = () => {
    if (progressRef.current) clearInterval(progressRef.current);
    setSelectedFile(null);
    setUploadProgress(0);
    setUploading(false);
    setUploadSuccess(false);
    setUploadError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle className={styles.dialogTitle}>File Upload</DialogTitle>
      <Box className={styles.divider} />
      <DialogContent>
        <Box
          className={styles.uploadArea}
          onClick={() => !uploading && fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          <Box>
            <img src={Frame} alt="Upload" />
          </Box>

          <Typography className={styles.uploadText}>
            Click or drag file to this area to upload
          </Typography>

          <Button
            variant="contained"
            disabled={uploading}
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            className={styles.browseButton}
          >
            Browse Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            hidden
            onChange={handleFileChange}
          />
        </Box>
        <Typography className={styles.uploadHint} mt={2}>
          Formats accepted are .pdf, csv and .xlsx
        </Typography>
        <Box className={styles.divider2} />

        <Typography className={styles.uploadText} mt={2}>
          0 file uploaded
        </Typography>
        {selectedFile && !uploadSuccess && (
          <Box mt={4}>
            <Typography mb={1}>Uploading…</Typography>
            <Box className="progress-bar-bg">
              <Box
                className="progress-bar"
                sx={{ width: `${uploadProgress}%` }}
              />
            </Box>
            <Typography mt={1}>{uploadProgress}%</Typography>
          </Box>
        )}

        {uploadSuccess && (
          <Box mt={4} textAlign="center">
            <CheckCircleIcon sx={{ color: "#22C55E", fontSize: 40 }} />
            <Typography fontWeight={600} mt={1}>
              Upload complete
            </Typography>
          </Box>
        )}

        {uploadError && (
          <Typography color="error" mt={2}>
            {uploadError}
          </Typography>
        )}
      </DialogContent>

      {/* <DialogActions sx={{ p: 4 }}>
        {uploadSuccess && (
          <Button variant="contained" onClick={handleDone}>
            Done
          </Button>
        )}
      </DialogActions> */}
    </Dialog>
  );
};
