import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Box, Stack, Button } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./SCNEditDetails.module.scss";
import SCNResultCard from "./SCNResultCard";
import SCNFormFields from "./SCNForm";

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

const SCNEditDetails: React.FC = () => {
  const { scnId } = useParams<{ scnId: string }>();
  const [isEditing, setIsEditing] = useState(false);

  // Mock data - Replace with API call based on scnId
  const [scnDetail] = useState({
    id: scnId || "1",
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
  });

  const [formData, setFormData] = useState({ ...scnDetail });

  const breadcrumbItems = [
    { label: "Home", to: "/" },
    { label: "Supplier Portal", to: "/scn/supplier" },
    { label: scnDetail.scnNumber },
  ];

  const handleSaveClick = () => {
    // API call to save formData would go here
    setIsEditing(false);
  };

  const handleCancelClick = () => {
    setFormData({ ...scnDetail });
    setIsEditing(false);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <Box component="main" className={styles.container}>
      <Stack direction="column" gap={2}>
        <CommonBreadcrumbs items={breadcrumbItems} />

        {/* Header Section */}
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="flex-start"
        >
          <SCNResultCard scn={scnDetail} isEditingCard />
        </Stack>

        <Box className={styles.divider} />

        {/* Overview Section */}
        <Box className={styles.overviewSection}>
          <h2 className={styles.sectionTitle}>Overview</h2>
          <p className={styles.sectionContent}>
            {scnDetail.changeTitleSummary}
          </p>
        </Box>

        <Box className={styles.divider} />

        <SCNFormFields
          formData={formData}
          isEditing={isEditing}
          onEditClick={() => setIsEditing(true)}
          onInputChange={handleInputChange}
        />
        {/* Action Buttons */}
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
      </Stack>
    </Box>
  );
};

export default SCNEditDetails;
