import React, { useRef, useState } from "react";
import {
  Box,
  Stack,
  Button,
  Typography,
  CircularProgress,
} from "@mui/material";
import FormInput from "@components/common/FormInput";
import editIcon from "../../assets/icons/editLight.svg";
import documentTextIcon from "../../assets/icons/documentext.svg";
import styles from "./SCNForm.module.scss";
import Frame from "../../assets/icons/Frame.svg";
import RiskIcon from "../../assets/icons/Lead Icon.svg";

interface SCNFormFieldsProps {
  formData: any;
  isEditing: boolean;
  onEditClick?: () => void;
  onInputChange: (field: string, value: any) => void;
  isUpload?: boolean;
  /** Show the drag-and-drop upload area regardless of isUpload layout mode.
   *  Defaults to the value of isUpload for backwards compatibility. */
  showUploadSection?: boolean;
  /** Called whenever the locally-selected file list changes so parents can
   *  include the files when calling the save / edit API. */
  onFilesChange?: (files: File[]) => void;
  validationErrors?: Record<string, boolean>;
}

const SCNFormFields: React.FC<SCNFormFieldsProps> = ({
  formData,
  isEditing,
  onEditClick,
  onInputChange,
  isUpload = false,
  showUploadSection,
  onFilesChange,
  validationErrors = {},
}) => {
  // showUploadSection defaults to isUpload so existing callers are unaffected
  const shouldShowUpload = showUploadSection ?? isUpload;
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    <Box className={styles.section}>
      {/* SCN Identification Section */}
      <Box>
        {!isUpload && (
          <h2 className={styles.sectionTitleforReview}>Extracted info</h2>
        )}
        {!isUpload && Object.keys(validationErrors).length > 0 && (
          <span className={styles.validationMessage}>
            <img src={RiskIcon} alt="" />
            Review required on {Object.keys(validationErrors).length} field(s)
          </span>
        )}
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
        >
          <h2 className={styles.sectionTitle}>SCN Identification</h2>
          {!isEditing && onEditClick && (
            <Button
              variant="contained"
              size="small"
              className={styles.editButtonSmall}
              onClick={onEditClick}
            >
              <img src={editIcon} alt="edit" className={styles.editIcon} />
              Edit
            </Button>
          )}
        </Stack>

        <Stack direction="row" spacing={4} className={styles.formRow}>
          <FormInput
            label="Supplier SCN Reference"
            value={formData.supplierRef}
            onChange={(val) => onInputChange("supplierRef", val)}
            disabled
            className={styles.IdentificationInput}
            required
          />
          <FormInput
            label="SCN Title"
            value={formData.changeTitle}
            onChange={(val) => onInputChange("changeTitle", val)}
            disabled
            className={styles.IdentificationInput}
            required
          />
        </Stack>

        <Stack direction="row" spacing={4} className={styles.formRow}>
          <FormInput
            label="Supplier Name"
            value={formData.supplierName}
            onChange={(val) => onInputChange("supplierName", val)}
            disabled
            className={styles.IdentificationInput}
            required
          />
          {isUpload && (
            <FormInput
              label="Planned Implementation Date"
              value={formData.plannedImplementationDate}
              onChange={(val) =>
                onInputChange("plannedImplementationDate", val)
              }
              disabled={!isEditing}
              type="date"
              placeholder="Input text"
              className={styles.inputLabel}
            />
          )}
          {!isUpload && (
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
          )}
        </Stack>
      </Box>

      {/* Current State Section */}
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

      {/* Proposed State Section */}
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

      {/* Justification Section */}
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

      {/* Temporary Change and Supplier Sites Section */}
      <Box>
        <Stack direction="row" spacing={4} className={styles.formRow}>
          {isUpload && (
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
          )}
          <Box className={styles.formGroup}>
            <label className={styles.formLabel}>
              Supplier Site(s) Affected
            </label>
            <div className={styles.radioGroup}>
              {["Manufacturing", "Testing"].map((site) => (
                <label key={site} className={styles.radioLabel}>
                  <input
                    type="checkbox"
                    name="siteAffectedType"
                    value={site}
                    checked={formData.supplierSitesAffected2 === site}
                    onChange={(e) =>
                      onInputChange("supplierSitesAffected2", e.target.value)
                    }
                    disabled={!isEditing}
                  />
                  {site}
                </label>
              ))}
            </div>
          </Box>
          {!isUpload && (
            <Box className={styles.formGroup}>
              <label className={styles.formLabel}>
                Supplier Change Classification
              </label>
              <div className={styles.checkboxGroup}>
                {["Minor", "Moderate", "Major"].map((level) => (
                  <label key={level} className={styles.checkboxLabel}>
                    <input
                      type="radio"
                      checked={formData.supplierSitesAffected === level}
                      onChange={() =>
                        onInputChange("supplierSitesAffected", level)
                      }
                      disabled={!isEditing}
                    />
                    {level}
                  </label>
                ))}
              </div>
            </Box>
          )}
        </Stack>

        <Stack direction="row" spacing={4}>
          {/* {isUpload && (
            <Box className={styles.formGroup}>
              <label className={styles.formLabel}>Impact Level</label>
              <div className={styles.checkboxGroup}>
                {["Minor", "Moderate", "Major"].map((level) => (
                  <label key={level} className={styles.checkboxLabel}>
                    <input
                      type="radio"
                      checked={formData.supplierSitesAffected === level}
                      onChange={() =>
                        onInputChange("supplierSitesAffected", level)
                      }
                      disabled={!isEditing}
                    />
                    {level}
                  </label>
                ))}
              </div>
            </Box>
          )} */}
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
          {!isUpload && (
            <FormInput
              label="Notification Date"
              value={formData.notificationDate}
              onChange={(val) => onInputChange("notificationDate", val)}
              disabled={!isEditing}
              type="date"
              className={styles.inputLabel}
            />
          )}
          {isUpload && <div style={{ width: "50%" }}></div>}
        </Stack>
        {isUpload && (
          <Stack direction="row" spacing={4} mt={2} className={styles.formRow}>
            <FormInput
              label="Notification Date"
              value={formData.notificationDate}
              onChange={(val) => onInputChange("notificationDate", val)}
              disabled={!isEditing}
              type="date"
              className={styles.inputLabel}
            />
            <div style={{ width: "50%" }}></div>
          </Stack>
        )}
      </Box>

      {/* Change Timing */}
      <Box className={styles.sectionTiming} pt={2}>
        <h2 className={styles.sectionTitle}>Change Timing</h2>
        <Stack direction="row" spacing={4} className={styles.formRow}>
          <FormInput
            label="Planned Implementation Date"
            value={formData.changeTimingPlannedDate}
            onChange={(val) => onInputChange("changeTimingPlannedDate", val)}
            disabled={!isEditing}
            type="date"
            className={styles.inputLabel}
            required
            error={validationErrors.changeTimingPlannedDate}
          />

          <div style={{ width: "50%" }}></div>
        </Stack>
      </Box>

      {/* Materials Impacted */}
      <Box
        sx={{
          borderBottom: "1px solid #e5e7eb",
        }}
      >
        <h2 className={styles.sectionTitle}>Materials / Products Impacted</h2>

        {!isUpload && (
          <Stack direction="row" spacing={4} className={styles.formRow}>
            <FormInput
              label="Material Number"
              value={formData.materialNumber ?? ""}
              onChange={(val) => onInputChange("materialNumber", val)}
              disabled={!isEditing}
              placeholder="Input text"
              className={styles.inputLabel}
              required
              error={validationErrors.materialNumber}
            />
            <FormInput
              label="Component Number"
              value={formData.componentNumber ?? ""}
              onChange={(val) => onInputChange("componentNumber", val)}
              disabled={!isEditing}
              placeholder="Input text"
              className={styles.inputLabel}
              required
              error={validationErrors.componentNumber}
            />
          </Stack>
        )}
        <Stack direction="row" spacing={4} className={styles.formRow}>
          {isUpload && (
            <FormInput
              label="Material / Component Number"
              value={formData.materialComponentNumber ?? ""}
              onChange={(val) => onInputChange("materialComponentNumber", val)}
              disabled={!isEditing}
              placeholder="Input text"
              className={styles.inputLabel}
            />
          )}
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
          {!isUpload && <div style={{ width: "50%" }}></div>}
        </Stack>
      </Box>

      {/* Documentation */}
      <Box>
        <h2 className={styles.sectionTitle}>Documentation & Attachments</h2>

        {shouldShowUpload && (
          <Box className={styles.contentWrapper}>
            <Box
              className={styles.uploadArea}
              onClick={() => !uploading && fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
            >
              <Box>
                {uploading ? (
                  <CircularProgress size={36} sx={{ color: "#437ef7" }} />
                ) : (
                  <img src={Frame} alt="Upload" />
                )}
              </Box>

              <Typography className={styles.uploadText}>
                {uploading
                  ? "Uploading file, please wait…"
                  : "Click or drag file to this area to upload"}
              </Typography>

              {!uploading && (
                <Button
                  variant="contained"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                  className={styles.browseButton}
                >
                  Browse Files
                </Button>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.csv,.xlsx"
                multiple
                hidden
                onChange={handleFileChange}
              />
            </Box>
          </Box>
        )}
        <div className={styles.fileUploadInfo}>
          {(formData?.attachments?.length || 0) + uploadedFiles.length > 0 && (
            <p>
              {(formData?.attachments?.length || 0) + uploadedFiles.length}{" "}
              file(s) uploaded
            </p>
          )}
          <div className={styles.fileList}>
            {/* Server-side attachments (read-only with View link) */}
            {formData?.attachments?.map((file: any, idx: number) => (
              <div key={`server-${idx}`} className={styles.fileItem}>
                <div className={styles.fileDetails}>
                  <span className={styles.fileIcon}>
                    <img src={documentTextIcon} alt="document" />
                  </span>
                  <span className={styles.fileInfo}>
                    <span className={styles.fileName}>{file.filename}</span>
                  </span>
                </div>
                {file.download_url && (
                  <a
                    href={file.download_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.viewLink}
                  >
                    View
                  </a>
                )}
              </div>
            ))}

            {/* Locally uploaded files (with remove button) */}
            {uploadedFiles.map((file, idx) => (
              <div key={`local-${idx}`} className={styles.fileItem}>
                <div className={styles.fileDetails}>
                  <span className={styles.fileIcon}>
                    <img src={documentTextIcon} alt="document" />
                  </span>
                  <span className={styles.fileInfo}>
                    <span className={styles.fileName}>{file.name}</span>
                    <span className={styles.fileSize}>
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                  </span>
                </div>
                <button
                  type="button"
                  className={styles.removeFileBtn}
                  onClick={() => handleRemoveUploadedFile(idx)}
                  title="Remove file"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      </Box>
    </Box>
  );
};

export default SCNFormFields;
