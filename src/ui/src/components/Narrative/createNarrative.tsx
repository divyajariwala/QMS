import React, { useRef, useState, DragEvent, ChangeEvent } from "react";
import {
  Box,
  Button,
  Chip,
  Container,
  Divider,
  Grid,
  Link,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import InsertDriveFileOutlinedIcon from "@mui/icons-material/InsertDriveFileOutlined";
import Document from "../../assets/icons/document.svg";
import ExcelIcon from "../../assets/icons/excel.svg";
import styles from "./createNarrative.module.scss";
import { UploadedDoc } from '../../types';

const MAX_BYTES = 10 * 1024 * 1024; // 10MB file size limit
const ACCEPT_EXT = ".xls"; 

const CreateNarrative: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [uploadedDocs, setUploadedDocs] = useState<UploadedDoc[]>([]);
  const [narrative, setNarrative] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isNarrativeFocused, setIsNarrativeFocused] = React.useState(false);

  const onBrowseClick = () => fileInputRef.current?.click();

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    processFiles(files);
    e.target.value = "";
  };

  const processFiles = (files: File[]) => {
    let localError: string | null = null;
    const toAdd: UploadedDoc[] = [];

    files.forEach((file) => {
      const lower = file.name.toLowerCase();
      if (!lower.endsWith(ACCEPT_EXT)) {
        localError = `Only ${ACCEPT_EXT} files are allowed.`;
        return;
      }
      if (file.size > MAX_BYTES) {
        localError = "Maximum size is 10MB.";
        return;
      }
      toAdd.push({ name: file.name, size: file.size, type: file.type });
    });

    if (toAdd.length) {
      setUploadedDocs((prev) => [...prev, ...toAdd]);
    }
    setError(localError);
  };

  const canClassify = narrative.trim().length > 0 || uploadedDocs.length > 0;

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

  return (
    <Box className={styles.root} sx={{ bgcolor: "background.default" }}>
        <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3} }}>
            <Typography className={styles.uploadNarrative} gutterBottom >
                Upload narrative
            </Typography>

            <Grid container spacing={3} alignItems="stretch" className={styles.mainGrid} >
                {/* Left card */}
                <Grid item xs={12} md={6} className={styles.equalCol}>
                    <Paper elevation={1} className={`${styles.card} ${styles.stretchCard}`}>
                        <Typography variant="h6" fontWeight={700} gutterBottom>
                            Upload Your Document
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            You may drag and drop a document below or upload a document from your computer.
                        </Typography>

                        <Box
                            className={`${styles.dropZone} ${isDragging ? styles["dropZone--dragging"] : ""}`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            role="button"
                            aria-label="Drag and drop your document here"
                            tabIndex={0}
                        >
                            <Stack alignItems="center" spacing={1.5}>
                                <img className={styles["dropZone__icon"]}
                                    src={Document}
                                    alt="Document"
                                />
                                <Typography fontWeight={700} textAlign="center">
                                    Drag & Drop Your Document Here
                                </Typography>

                                <div className={styles.orDivider} aria-hidden="true">
                                    <span>OR</span>
                                </div>

                                <Button
                                    onClick={onBrowseClick}
                                    variant="contained"
                                    size="medium"
                                    className={styles.uploadBtn}
                                >
                                    Upload document
                                </Button>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept={ACCEPT_EXT}
                                    onChange={handleFileChange}
                                    hidden
                                />
                            </Stack>
                        </Box>

                        <Grid container spacing={2} sx={{ mt: 2 }}>
                            <Grid item xs={12} sm={6}>
                                <Typography variant="caption" color="text.secondary">
                                    Supported Format: <b>XLS</b>
                                </Typography>
                            </Grid>
                            <Grid item xs={12} sm={6} textAlign={{ xs: "left", sm: "right" }}>
                                <Typography variant="caption" color="text.secondary">
                                    Maximum Size: <b>10MB</b>
                                </Typography>
                            </Grid>
                        </Grid>

                        <Paper elevation={0} className={styles.exampleCard}>
                            <div className={styles.cardRow}>
                                <div className={styles.left}>
                                    <div className={styles.fileBadge} aria-hidden="true">
                                         <img className=""
                                            src={ExcelIcon}
                                            alt="Excel"
                                         />
                                    </div>

                                    <Typography className={styles.title}>Document Example</Typography>

                                    <Typography className={styles.copy}>
                                        You can download the attached example and use them as a
                                        starting point for your own file.
                                    </Typography>
                                </div>

                                <div className={styles.right}>
                                <Button
                                    variant="outlined"
                                    onClick={handleDownloadExample}
                                    className={styles.downloadBtn}
                                >
                                    Download
                                </Button>
                                </div>
                            </div>
                        </Paper>

                    {error && (
                        <Typography className={styles.errorText}role="alert">
                        {error}
                        </Typography>
                    )}
                    </Paper>
                </Grid>

                {/* Right card */}
                <Grid item xs={12} md={6} className={styles.equalCol}>
                    <Paper elevation={1} className={`${styles.card} ${styles.stretchCard}`}>
                        <Typography variant="h6" fontWeight={700}>
                            Documents Uploaded ({uploadedDocs.length})
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Once the file upload is complete, you can start grading the files.
                        </Typography>

                        {/* <TextField
                            placeholder="Manually input narrative"
                            required
                            value={narrative}
                            onChange={(e) => setNarrative(e.target.value)}
                            multiline
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                            sx={{
                                flex: 1,
                                minHeight: 0,
                                display: "flex",
                                "& .MuiInputBase-root": {
                                    height: "100%",
                                    alignItems: "stretch",
                                },
                                "& .MuiInputBase-inputMultiline": {
                                    height: "100% !important",
                                },
                                "& textarea": {
                                    height: "100% !important",
                                    resize: "none",
                                    overflow: "auto",
                                },
                            }}
                        /> */}
                        <Box className={styles.narrativeWrap}>
                            <TextField
                                aria-label="Manually input narrative"
                                placeholder=""                // turn OFF native placeholder
                                required
                                value={narrative}
                                onChange={(e) => setNarrative(e.target.value)}
                                onFocus={() => setIsNarrativeFocused(true)}
                                onBlur={() => setIsNarrativeFocused(false)}
                                multiline
                                fullWidth
                                InputLabelProps={{ shrink: false }}
                                sx={{
                                    flex: 1,
                                    minHeight: 0,
                                    display: "flex",
                                    "& .MuiInputBase-root": {
                                        height: "100%",
                                        alignItems: "stretch",
                                    },
                                    "& .MuiInputBase-inputMultiline": {
                                        height: "100% !important",
                                    },
                                    "& textarea": {
                                        height: "100% !important",
                                        resize: "none",
                                        overflow: "auto",
                                    },
                                }}
                            />

                            {/* Overlay placeholder with red dot (shown only when empty) */}
                            {!narrative && !isNarrativeFocused && (
                                <div className={styles.narrativePlaceholder}>
                                    <span>Manually input narrative</span>
                                    <span className={styles.requiredDot} aria-hidden="true" />
                                </div>
                            )}
                        </Box>

                        {!!uploadedDocs.length && (
                            <>
                            <Divider sx={{ my: 2 }} />
                            <Stack spacing={1}>
                                {uploadedDocs.map((doc, idx) => (
                                <Stack key={`${doc.name}-${idx}`} direction="row" spacing={1} alignItems="center">
                                    <InsertDriveFileOutlinedIcon fontSize="small" />
                                    <Typography variant="body2">{doc.name}</Typography>
                                </Stack>
                                ))}
                            </Stack>
                            </>
                        )}
                    </Paper>
                </Grid>

                <Box mt={2} display="flex" justifyContent={{ xs: "stretch", sm: "flex-end" }} sx={{marginLeft: 'auto', borderRadius:'4px'}}>
                    <Button
                        variant="contained"
                        size="large"
                        disabled={!canClassify}
                        sx={{
                            minWidth: 140,
                            color: '#fff',
                            bgcolor: '#415385',   
                            textTransform: 'capitalize !Important',            
                            '&:hover': { bgcolor: '#354673' },  
                            "&.Mui-disabled": {
                            bgcolor: "#415385",
                            color: "#fff",
                            backgroundImage: "linear-gradient(rgba(255,255,255,0.45), rgba(255,255,255,0.45))",
                            boxShadow: "none",
                            },
                        }}
                        onClick={() => alert("Classify clicked")}

                    >
                        Classify
                    </Button>
                </Box>
            </Grid>

        </Container>
    </Box>
  );
};

export default CreateNarrative;
