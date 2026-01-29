import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Box, Button, Stack } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import SCNFormFields from "./SCNForm";
import styles from "./UploadDetails.module.scss";

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
  const initialData = location.state || {};
  // Allow editing by default after upload
  const [isEditing, setIsEditing] = useState(true);
  const [formData, setFormData] = useState({ ...initialData });
  const [originalData] = useState({ ...initialData });

  const breadcrumbItems = [
    { label: "Home", to: "/" },
    { label: "SCN", to: "/scn/supplier" },
    { label: "Upload SCN" },
  ];

  const handleSaveClick = () => {
    // API call to save formData would go here
    setIsEditing(false);
    navigate(`/scn/supplier/1`);
  };

  const handleCancelClick = () => {
    setFormData({ ...originalData });
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
              className={styles.submitButton}
            >
              Submit
            </Button>
          </>
        )}
      </Stack>
    </Box>
  );
};

export default UploadDetails;
