import React, { useRef, useState } from "react";
import { Box, CircularProgress, Stack } from "@mui/material";
import FormInput from "@components/common/FormInput";
import editIcon from "../../assets/icons/editIcon.svg";
import documentTextIcon from "../../assets/icons/documentext.svg";
import documentAlertIcon from "../../assets/icons/documentalert.svg";
import styles from "./SCNReviewForm.module.scss";
import AppButton from "@components/common/AppButton";
import CircleDeleteIcon from "../../assets/icons/circle-delete.svg";
import CheckIcon from "../../assets/icons/circle-checkmark.svg";
import LeftArrowIcon from "../../assets/icons/leftArrow.svg";
interface SCNReviewFormProps {
  formData: any;
  isEditing: boolean;
  onEditClick?: () => void;
  onInputChange: (field: string, value: any) => void;
  isUpload?: boolean;
  showUploadSection?: boolean;
  onFilesChange?: (files: File[]) => void;
  validationErrors?: Record<string, boolean>;
  onBackToSummary?: () => void;
  onApprove?: () => void;
  onReject?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  isSaving?: boolean;
}

const SCNReviewForm: React.FC<SCNReviewFormProps> = ({
  formData,
  isEditing,
  onEditClick,
  onInputChange,
  isUpload = false,
  showUploadSection,
  onFilesChange,
  validationErrors = {},
  onBackToSummary,
  onApprove,
  onReject,
  onSave,
  onCancel,
  isSaving = false,
}) => {
  const [activeTab, setActiveTab] = useState<
    "SCN Identification" | "Materials / Products Impacted"
  >("SCN Identification");
  // showUploadSection defaults to isUpload so existing callers are unaffected
  const shouldShowUpload = showUploadSection ?? isUpload;
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Which tabs have validation errors — so we can show a red badge
  const TAB1_FIELDS = ["proposedState", "supplierContactInfo"];
  const TAB2_FIELDS = [
    "changeTimingPlannedDate",
    "firstAffectedLotBatch",
    "materialNumber",
    "componentNumber",
  ];
  const FIELD_LABELS: Record<string, string> = {
    proposedState: "Proposed State",
    supplierContactInfo: "Supplier Contact Information",
    changeTimingPlannedDate: "Planned Implementation Date",
    firstAffectedLotBatch: "First Affected Lot / Batch",
    materialNumber: "Material Numbers",
    componentNumber: "Component Numbers",
  };
  const tab1HasError = TAB1_FIELDS.some((f) => validationErrors[f]);
  const tab2HasError = TAB2_FIELDS.some((f) => validationErrors[f]);
  const errorFields = Object.keys(validationErrors).filter(
    (f) => validationErrors[f],
  );

  const addFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const newFiles = Array.from(files);
    setUploading(true);
    // Simulate async upload processing
    setTimeout(() => {
      setUploadedFiles((prev) => {
        const next = [...prev, ...newFiles];
        onFilesChange?.(next);
        return next;
      });
      setUploading(false);
      // Reset input so same file can be selected again
      if (fileInputRef.current) fileInputRef.current.value = "";
    }, 1200);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    addFiles(e.target.files);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    addFiles(e.dataTransfer.files);
  };

  const handleRemoveUploadedFile = (index: number) => {
    setUploadedFiles((prev) => {
      const next = prev.filter((_, i) => i !== index);
      onFilesChange?.(next);
      return next;
    });
  };

  return (
    <Box className={styles.formContainer}>
      {!isUpload && (
        <Box className={styles.tabHeaderContainer}>
          <h2 className={styles.mainTitle}>Review Extracted Info</h2>
          <div className={styles.tabHeader}>
            <button
              className={`${styles.tabItem} ${activeTab === "SCN Identification" ? styles.activeTab : ""}`}
              onClick={() => setActiveTab("SCN Identification")}
            >
              <img src={documentTextIcon} alt="" />
              SCN Identification
              {tab1HasError && <span className={styles.tabErrorDot}>●</span>}
            </button>
            <button
              className={`${styles.tabItem} ${activeTab === "Materials / Products Impacted" ? styles.activeTab : ""}`}
              onClick={() => setActiveTab("Materials / Products Impacted")}
            >
              <img src={documentAlertIcon} alt="" />
              Materials / Products Impacted
              {tab2HasError && <span className={styles.tabErrorDot}>●</span>}
            </button>
          </div>
        </Box>
      )}

      {activeTab === "SCN Identification" ? (
        <Box className={styles.section}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <h2 className={styles.sectionTitle}>SCN Identification</h2>
            {!isEditing && onEditClick && (
              <AppButton
                variant="outlined"
                className={styles.editButtonSmall}
                onClick={onEditClick}
              >
                <img src={editIcon} alt="edit" className={styles.editIcon} />
                Edit
              </AppButton>
            )}
          </Stack>

          <Stack direction="row" spacing={4} className={styles.formRow}>
            <FormInput
              label="SCN Title"
              value={formData.changeTitle}
              onChange={(val) => onInputChange("changeTitle", val)}
              disabled={!isEditing}
              className={styles.IdentificationInput}
              required
            />
            <Box className={styles.formGroup}>
              <label className={styles.formLabel}>Temporary Change</label>
              <div className={styles.radioGroup}>
                {["No", "Yes"].map((option) => (
                  <label key={option} className={styles.radioLabel}>
                    <input
                      type="radio"
                      name="temporaryChange"
                      value={option}
                      checked={formData.temporaryChange === option}
                      onChange={(e) =>
                        onInputChange("temporaryChange", e.target.value)
                      }
                      disabled={!isEditing}
                    />
                    {option}
                  </label>
                ))}
              </div>
            </Box>
          </Stack>

          <Box>
            <h2 className={styles.sectionTitle}>Current State</h2>
            <FormInput
              label="Current State Description"
              value={formData.currentState}
              onChange={(val) => onInputChange("currentState", val)}
              disabled={!isEditing}
              multiline
              rows={4}
              className={styles.inputLabel}
            />
          </Box>

          <Box>
            <FormInput
              label="Proposed State"
              value={formData.proposedState}
              onChange={(val) => onInputChange("proposedState", val)}
              disabled={!isEditing}
              multiline
              rows={4}
              className={styles.inputLabel}
              required
              error={validationErrors.proposedState}
            />
          </Box>

          <Box>
            <FormInput
              label="Justification"
              value={formData.justification}
              onChange={(val) => onInputChange("justification", val)}
              disabled={!isEditing}
              multiline
              rows={4}
              className={styles.inputLabel}
            />
          </Box>

          <Stack direction="row" spacing={4} className={styles.formRow}>
            <FormInput
              label="Supplier Contact Information"
              value={formData.supplierContactInfo}
              onChange={(val) => onInputChange("supplierContactInfo", val)}
              disabled={!isEditing}
              type="text"
              className={styles.inputLabel}
              required
              error={validationErrors.supplierContactInfo}
            />
            <FormInput
              label="Change Date"
              value={formData.notificationDate}
              onChange={(val) => onInputChange("notificationDate", val)}
              disabled={!isEditing}
              type="date"
              className={styles.inputLabel}
            />
          </Stack>
        </Box>
      ) : (
        <Box className={styles.section}>
          <Box className={styles.sectionTiming}>
            <h2 className={styles.sectionTitle}>Change Timing</h2>
            <Stack direction="row" spacing={4} className={styles.formRow}>
              <FormInput
                label="Supplier Site(s) Affected"
                value={formData.supplierSitesAffected2 ?? ""}
                onChange={(val) => onInputChange("supplierSitesAffected2", val)}
                disabled={!isEditing}
                placeholder="e.g. Manufacturing, Testing"
                className={styles.inputLabel}
              />
              <FormInput
                label="Planned Implementation Date"
                value={formData.changeTimingPlannedDate}
                onChange={(val) =>
                  onInputChange("changeTimingPlannedDate", val)
                }
                disabled={!isEditing}
                type="date"
                className={styles.inputLabel}
                required
                error={validationErrors.changeTimingPlannedDate}
              />
            </Stack>
          </Box>

          <Box>
            <h2 className={styles.sectionTitle}>
              Materials / Products Impacted
            </h2>
            <Stack direction="row" spacing={4} className={styles.formRow}>
              <FormInput
                label="Material Numbers"
                value={formData.materialNumber ?? ""}
                onChange={(val) => onInputChange("materialNumber", val)}
                disabled={!isEditing}
                placeholder="Input text"
                className={styles.inputLabel}
                required
                error={validationErrors.materialNumber}
              />
              <FormInput
                label="Component Numbers"
                value={formData.componentNumber ?? ""}
                onChange={(val) => onInputChange("componentNumber", val)}
                disabled={!isEditing}
                placeholder="Input text"
                className={styles.inputLabel}
                required
                error={validationErrors.componentNumber}
              />
            </Stack>
            <Stack direction="row" spacing={4} className={styles.formRow}>
              <FormInput
                label="First Affected Lot / Batch"
                value={formData.firstAffectedLotBatch ?? ""}
                onChange={(val) => onInputChange("firstAffectedLotBatch", val)}
                disabled={!isEditing}
                placeholder="Input text"
                className={styles.inputLabel}
                required
                error={validationErrors.firstAffectedLotBatch}
              />
              <div style={{ width: "50%" }}></div>
            </Stack>
          </Box>
        </Box>
      )}

      {!isUpload && (
        <Box className={styles.bottomActions} marginTop={4}>
          {isEditing ? (
            <Stack direction="column" spacing={1.5}>
              {errorFields.length > 0 && (
                <Box className={styles.validationErrorBanner}>
                  <p className={styles.validationErrorTitle}>
                    Please fill in the required fields:
                  </p>
                  <ul className={styles.validationErrorList}>
                    {errorFields.map((f) => (
                      <li key={f}>{FIELD_LABELS[f] ?? f}</li>
                    ))}
                  </ul>
                </Box>
              )}
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <AppButton
                  variant="outlined"
                  onClick={onCancel}
                  disabled={isSaving}
                >
                  Cancel
                </AppButton>
                <AppButton
                  variant="primary"
                  onClick={onSave}
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <span className={styles.savingText}>
                      <CircularProgress size={14} sx={{ color: "inherit" }} />
                      Saving…
                    </span>
                  ) : (
                    "Save"
                  )}
                </AppButton>
              </Stack>
            </Stack>
          ) : (
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
            >
              <AppButton variant="outlined" onClick={onBackToSummary}>
                <Stack direction="row" alignItems="center" gap={1}>
                  <img src={LeftArrowIcon} alt="" /> Back to Summary
                </Stack>
              </AppButton>
              <Stack direction="row" spacing={2}>
                <AppButton
                  variant="outlined"
                  // className={styles.rejectButton}
                  onClick={onReject}
                >
                  <Stack direction="row" alignItems="center" gap={1}>
                    <img src={CircleDeleteIcon} alt="" /> Reject
                  </Stack>
                </AppButton>
                <AppButton
                  variant="primary"
                  // className={styles.approveButton}
                  onClick={onApprove}
                >
                  <Stack direction="row" alignItems="center" gap={1}>
                    <img src={CheckIcon} alt="" /> Approve
                  </Stack>
                </AppButton>
              </Stack>
            </Stack>
          )}
        </Box>
      )}
    </Box>
  );
};

export default SCNReviewForm;
