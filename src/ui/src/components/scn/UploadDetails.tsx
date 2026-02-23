import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Box, Button, Stack, CircularProgress } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import SCNFormFields from "./SCNForm";
import styles from "./UploadDetails.module.scss";
import { editScn } from "src/services/scn";
import { mapScnFormToApi } from "src/utils/mapScnFormToApi";

interface SCNItem {
  id: string;
  status: "SUPPLIER ACTION REQUIRED" | "PENDING REVIEW" | "IN REVIEW";
  scnNumber: string;
  changeClassification: string;
  supplierRef: string;
  notificationDate: string;
  plannedImplementationDate: string;
  changeType: "Adverse Event" | "Product Complaint";
  changeTitleSummary: string;
  overdueDays?: number;
  changeTitle?: string;
}

const UploadDetails: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  // Use uploaded/extracted data as initial form values
  const locationState = (location.state as any) || {};
  const emailId: string = locationState.email_id || "";
  const initialData = locationState;
  // Allow editing by default after upload
  const [isEditing, setIsEditing] = useState(true);
  const [formData, setFormData] = useState({ ...initialData });
  const [originalData] = useState({ ...initialData });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);

  const breadcrumbItems = [
    { label: "Home", to: "/" },
    { label: "SCN", to: "/scn/supplier" },
    { label: "Upload SCN" },
  ];

  const handleSaveClick = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      const apiFields = mapScnFormToApi(formData);
      const res = await editScn(
        emailId,
        apiFields,
        pendingFiles.length > 0 ? pendingFiles : undefined,
      );
      if (res?.success) {
        setIsEditing(false);
        setPendingFiles([]);
        navigate(`/scn/supplier/${formData.email_id}`);
      }
    } catch (err) {
      console.error("Save failed:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelClick = () => {
    setFormData({ ...originalData });
    setPendingFiles([]);
    setIsEditing(true); // Stay editable after upload
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev: SCNItem) => ({
      ...prev,
      [field]: value,
    }));
  };
  return (
    <Box className={styles.uploadDetails}>
      <CommonBreadcrumbs items={breadcrumbItems} />
      <Box className={styles.formContainer}>
        <SCNFormFields
          formData={formData}
          isEditing={isEditing}
          onEditClick={() => setIsEditing(true)}
          onInputChange={handleInputChange}
          isUpload
          onFilesChange={setPendingFiles}
        />
      </Box>

      <Stack direction="row" spacing={2} className={styles.actionButtons}>
        {isEditing && (
          <>
            <Button
              variant="outlined"
              onClick={handleCancelClick}
              className={styles.cancelButton}
            >
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={handleSaveClick}
              disabled={isSubmitting}
              className={styles.submitButton}
              startIcon={
                isSubmitting ? (
                  <CircularProgress size={16} sx={{ color: "white" }} />
                ) : undefined
              }
            >
              {isSubmitting ? "Submitting…" : "Submit"}
            </Button>
          </>
        )}
      </Stack>
    </Box>
  );
};

export default UploadDetails;
