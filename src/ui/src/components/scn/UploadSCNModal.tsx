import React, { RefObject, useRef, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  Button,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import styles from "./UploadSCN.module.scss";
import Frame from "../../assets/icons/Frame.svg";
import UploadIcon from "../../assets/icons/scnUploadIcon.svg";
import UploadDoneIcon from "../../assets/icons/greenTickDone.svg";
import { fetchScnDetails, uploadScn } from "src/services/scn";
import { mapScnDetailsToForm } from "src/utils/mapScnDetails";
import Loader from "@components/Loader";

interface UploadSCNModalProps {
  open: boolean;
  onClose: () => void;
  fileInputRef: RefObject<HTMLInputElement>;
}

const UPLOAD_ACCEPTED_FORMATS = [".pdf", ".csv", ".xlsx"];
const UPLOAD_PROGRESS_INTERVAL = 200;
const UPLOAD_PROGRESS_STEP = 5;

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
  const [emailId, setEmailId] = useState<any>(null);
  const navigate = useNavigate();
  const [detailLoading, setDetailLoading] = useState(false);
  const [processingDone, setProcessingDone] = useState(false);

  const simulateUpload = () => {
    if (progressRef.current) clearInterval(progressRef.current);
    setUploadProgress(0);

    progressRef.current = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressRef.current!);
          return 90;
        }
        return prev + UPLOAD_PROGRESS_STEP;
      });
    }, UPLOAD_PROGRESS_INTERVAL);
  };

  const handleFile = async (file: File) => {
    setUploadError(null);

    const fileExt = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();

    if (!UPLOAD_ACCEPTED_FORMATS.includes(fileExt)) {
      setUploadError("Only PDF, CSV, or XLSX files are accepted.");
      setSelectedFile(null);
      return;
    }

    try {
      setSelectedFile(file);
      setUploading(true);
      setUploadSuccess(false);
      simulateUpload();

      const response = await uploadScn(file);
      setEmailId(response);
      if (progressRef.current) clearInterval(progressRef.current);
      setUploadProgress(100);
      setUploadSuccess(true);
      setTimeout(() => setProcessingDone(true), 80000);
    } catch (error: any) {
      if (progressRef.current) clearInterval(progressRef.current);
      setUploadProgress(0);
      setUploadError(error.message || "Upload failed");
      setSelectedFile(null);
    } finally {
      setUploading(false);
    }
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

  const handleDone = async () => {
    try {
      const email_id = emailId?.data?.email_id;
      setDetailLoading(true);
      const res: any = await fetchScnDetails(email_id);

      if (res?.success) {
        const mapped = mapScnDetailsToForm(res.data);
        navigate("/scn/upload-details", {
          state: { ...mapped, email_id, file: selectedFile?.name },
        });
        setDetailLoading(false);
      }
    } catch (error: any) {
      setUploadError(error?.message || "Failed to fetch SCN details");
      setDetailLoading(false);
      console.error("Failed to fetch SCN details", error);
    }
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
    <Dialog
      open={open}
      onClose={handleClose}
      PaperProps={{
        sx: {
          width: "649px",
          maxWidth: `${!selectedFile && !uploadSuccess ? "547px" : "660px"}`,
          borderRadius: "10px",
        },
      }}
    >
      <DialogTitle className={styles.dialogTitle}>File Upload</DialogTitle>
      <Box className={styles.divider} />

      <DialogContent>
        {!selectedFile && !uploadSuccess && (
          <Box className={styles.contentWrapper}>
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
                accept=".pdf,.csv,.xlsx"
                hidden
                onChange={handleFileChange}
              />
            </Box>
            <Typography className={styles.uploadHint}>
              Formats accepted are .pdf, .csv and .xlsx
            </Typography>
            <Box className={styles.divider2} />
            <Typography className={styles.uploadFileCount}>
              0 file uploaded
            </Typography>
          </Box>
        )}

        {/* PHASE 2: UPLOADING STATE */}
        {uploading && (
          <Box className={styles.processWrapper}>
            <Box className={styles.iconCircleBlue}>
              <img src={UploadIcon} alt="uploading" />
            </Box>
            <Typography className={styles.statusTitle}>Uploading...</Typography>
            <Typography className={styles.statusSubtitle}>1 file</Typography>

            <Box className={styles.progressBarContainer}>
              <Box
                className={styles.progressBarFill}
                sx={{ width: `${uploadProgress}%` }}
              />
            </Box>

            <Box className={styles.progressLabels}>
              <Typography>Upload progress</Typography>
              <Typography>{uploadProgress}%</Typography>
            </Box>
          </Box>
        )}

        {/* PHASE 3: UPLOAD COMPLETE STATE */}
        {uploadSuccess && (
          <Box className={styles.processWrapper}>
            <Box className={styles.iconCircleGreen}>
              <img
                src={UploadDoneIcon}
                alt="Upload Complete"
                className={styles.uploadCompleteIcon}
              />
            </Box>

            <Typography className={styles.statusTitle}>
              Upload complete
            </Typography>
            <Typography className={styles.statusSubtitle}>
              1 file uploaded successfully
            </Typography>

            {!processingDone ? (
              <>
                <div className={styles.loader}></div>
                <Typography className={styles.statusSubtitle}>
                  Please wait for the file to be processed
                </Typography>
              </>
            ) : (
              <Button
                variant="contained"
                onClick={handleDone}
                className={styles.doneButton}
              >
                {detailLoading ? <Loader /> : "Done"}
              </Button>
            )}
          </Box>
        )}

        {uploadError && (
          <Box p={3} textAlign="center">
            <Typography color="error">{uploadError}</Typography>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};
