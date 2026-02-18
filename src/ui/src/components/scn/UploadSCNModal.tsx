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

interface UploadSCNModalProps {
  open: boolean;
  onClose: () => void;
  fileInputRef: RefObject<HTMLInputElement>;
}

const UPLOAD_ACCEPTED_FORMATS = [".pdf", ".csv", ".xlsx"];
const UPLOAD_PROGRESS_INTERVAL = 200;
const UPLOAD_PROGRESS_STEP = 5;

const mockExtractedData = {
  id: "1",
  status: "SUPPLIER ACTION REQUIRED" as const,
  scnNumber: "SCN-000231",
  changeClassification: "Lorem ipsum",
  supplierRef: "SCN-12345",
  supplierName: "Supplier XYZ",
  notificationDate: "Jan 04 2026",
  plannedImplementationDate: "Dec 23 2025",
  changeType: "Adverse Event" as const,
  changeTitleSummary:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud",
  overdueDays: 5,
  changeTitle: "SCN-12345",
  currentState:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
  proposedState:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
  justification:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
  temporaryChange: "No",
  supplierSitesAffected: "Low",
  supplierSitesAffected2: "Manufacturing",
  supplierContactInfo: "quality@xyz.com",
  changeTimingPlannedDate: "Dec 23 2025",
  firstAffectedLotBatch: "Input text",
  materialComponentNumber: "Component A",
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
  const [scnDetail, setScnDetail] = useState<unknown>(null);
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
      setUploadProgress(10);

      const response = await uploadScn(file);

      // if (!response) {
      //   throw new Error(response.message);
      // }

      setUploadProgress(100);
      setUploadSuccess(true);
    } catch (error: any) {
      setUploadError(error.message || "Upload failed");
      setSelectedFile(null);
    } finally {
      setUploading(false);
    }
  };

  // const handleFile = (file: File) => {
  //   setUploadError(null);
  //   const fileExt = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();

  //   if (!UPLOAD_ACCEPTED_FORMATS.includes(fileExt)) {
  //     setUploadError("Only PDF, CSV, or XLSX files are accepted.");
  //     setSelectedFile(null);
  //     return;
  //   }

  //   setSelectedFile(file);
  //   setUploadProgress(0);
  //   setUploading(true);
  //   setUploadSuccess(false);
  //   simulateUpload();
  // };

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
      const email_id = "123e4567-e89b-12d3-a456-426614171234";
      // setDetailLoading(true);
      const res: any = await fetchScnDetails(email_id);
      console.log(res, "testtestres");
      if (res?.data) {
        const mapped = mapScnDetailsToForm(res.data);
        setScnDetail(mapped);
        navigate("/scn/upload-details", {
          state: { ...mapped, file: selectedFile?.name },
        });
      }
    } catch (error) {
      console.error("Failed to fetch SCN details", error);
    } finally {
      // navigate("/scn/upload-details", {
      //   state: { scnDetail, file: selectedFile?.name },
      // });
    }

    // navigate("/scn/upload-details", {
    //   state: { ...mockExtractedData, file: selectedFile?.name },
    // });
    // handleClose();
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

            <Button
              variant="contained"
              onClick={handleDone}
              className={styles.doneButton}
            >
              Done
            </Button>
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
