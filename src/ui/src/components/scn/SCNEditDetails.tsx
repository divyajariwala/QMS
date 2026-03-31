import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, Stack, Typography } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./SCNEditDetails.module.scss";
import SCNResultCard from "./SCNResultCard";
import SCNFormFields from "./SCNForm";
import RiskIcon from "../../assets/icons/Lead Icon.svg";
import { fetchScnDetails, editScn } from "src/services/scn";
import { mapScnDetailsToForm } from "src/utils/mapScnDetails";
import { mapScnFormToApi } from "src/utils/mapScnFormToApi";
import SCNFormSkeleton from "./skeleton/SCNFormSkeleton";
import AppButton from "@components/common/AppButton";

const SCNEditDetails: React.FC = () => {
  const { scnId } = useParams<{ scnId: string }>();

  const [isEditing, setIsEditing] = useState(false);
  const [validationErrors, setValidationErrors] = useState<
    Record<string, boolean>
  >({});

  // API-driven state (replaces mock data)
  const [formData, setFormData] = useState<any>(null);
  const [originalData, setOriginalData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  // Files selected in the upload section — sent along with the edit API call
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);

  // ── Fetch SCN details on mount / when scnId changes
  const loadDetails = async () => {
    if (!scnId) return;
    setLoading(true);
    setError(null);
    try {
      const res: any = await fetchScnDetails(scnId);
      if (res?.data) {
        const mapped = mapScnDetailsToForm(res.data);
        setFormData(mapped);
        setOriginalData(mapped);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to load SCN details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetails();
  }, [scnId]);

  // ── Breadcrumb
  const breadcrumbItems = [
    { label: "Home", to: "/" },
    { label: "SCN", to: "/scn/supplier" },
    { label: formData?.supplierRef || "Details" },
  ];

  // ── Save
  const handleSaveClick = async () => {
    if (isSubmitting || !scnId || !formData) return;

    // Validate required fields
    const errors: Record<string, boolean> = {};
    const requiredFields = [
      "proposedState",
      "supplierContactInfo",
      "changeTimingPlannedDate",
      "firstAffectedLotBatch",
      "materialNumber",
      "componentNumber",
    ];
    requiredFields.forEach((field) => {
      if (!formData[field as keyof typeof formData]) {
        errors[field] = true;
      }
    });
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }
    setValidationErrors({});

    setIsSubmitting(true);
    try {
      const apiFields = mapScnFormToApi(formData);
      // Pass any locally-selected files so they are uploaded alongside the edit
      const res = await editScn(
        scnId,
        apiFields,
        pendingFiles.length > 0 ? pendingFiles : undefined,
      );
      if (res?.success) {
        setIsEditing(false);
        setPendingFiles([]);
        // Refresh to show saved values
        await loadDetails();
      }
    } catch (err) {
      console.error("Save failed:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelClick = () => {
    setFormData({ ...originalData });
    setValidationErrors({});
    setPendingFiles([]);
    setIsEditing(false);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: value,
    }));
  };

  // ── Render helpers
  if (loading) {
    return (
      <Box component="main" className={styles.container}>
        <Stack direction="column" gap={2}>
          <CommonBreadcrumbs items={breadcrumbItems} />
          <SCNFormSkeleton />
        </Stack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box component="main" className={styles.container}>
        <Stack direction="column" gap={2}>
          <CommonBreadcrumbs items={breadcrumbItems} />
          <Typography color="error">{error}</Typography>
        </Stack>
      </Box>
    );
  }
  console.log(formData, "formData@@");
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
          {formData && (
            <SCNResultCard
              scn={{
                id: scnId || "",
                status: formData.status || "",
                scnNumber: formData.supplierRef || "",
                changeClassification:
                  formData.changeClassificationSupplier || "",
                supplierRef: formData.supplierRef || "",
                notificationDate: formData.notificationDate || "",
                plannedImplementationDate:
                  formData.changeTimingPlannedDate || "",
                changeType: formData.changeType || "",
                changeTitleSummary: formData.changeTitle || "",
                changeTitle: formData.changeTitle || "",
              }}
              isEditingCard
            />
          )}
        </Stack>

        {Object.keys(validationErrors).length > 0 && (
          <>
            <Box className={styles.divider} />
            {/* Overview Section */}
            <Box className={styles.overviewSection}>
              <h2 className={styles.sectionTitle}>Overview</h2>
              <p className={styles.validationMessage}>
                <>
                  <img src={RiskIcon} alt="Risk Icon" />
                  Please provide all required fields.
                </>
              </p>
            </Box>
          </>
        )}

        <Box className={styles.divider} />

        {/* Form */}
        {formData && (
          <SCNFormFields
            formData={formData}
            isEditing={isEditing}
            onEditClick={() => setIsEditing(true)}
            onInputChange={handleInputChange}
            validationErrors={validationErrors}
            showUploadSection={isEditing}
            onFilesChange={setPendingFiles}
          />
        )}

        {/* Action Buttons */}
        <Stack direction="row" spacing={2} className={styles.actionButtons}>
          {isEditing && (
            <>
              <AppButton
                variant="outlined"
                onClick={handleCancelClick}
                disabled={isSubmitting}
              >
                Cancel
              </AppButton>
              <AppButton
                variant="primary"
                onClick={handleSaveClick}
                disabled={isSubmitting}
                loading={isSubmitting}
              >
                Submit
              </AppButton>
            </>
          )}
        </Stack>
      </Stack>
    </Box>
  );
};

export default SCNEditDetails;
