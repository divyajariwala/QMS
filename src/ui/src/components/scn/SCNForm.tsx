import React, { useRef, useState } from "react";
import { Box, Stack, Button, Typography } from "@mui/material";
import FormInput from "@components/common/FormInput";
import editIcon from "../../assets/icons/editLight.svg";
import documentTextIcon from "../../assets/icons/documentext.svg";
import styles from "./SCNForm.module.scss";
import Frame from "../../assets/icons/Frame.svg";

interface SCNFormFieldsProps {
  formData: any;
  isEditing: boolean;
  onEditClick?: () => void;
  onInputChange: (field: string, value: any) => void;
  isUpload?: boolean;
}

const SCNFormFields: React.FC<SCNFormFieldsProps> = ({
  formData,
  isEditing,
  onEditClick,
  onInputChange,
  isUpload = false,
}) => {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploading(true);
      // Simulate upload
      setTimeout(() => {
        setUploading(false);
        // You can add logic to update formData or show uploaded file info here
      }, 1500);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setUploading(true);
      // Simulate upload
      setTimeout(() => {
        setUploading(false);
        // You can add logic to update formData or show uploaded file info here
      }, 1500);
    }
  };

  return (
    <Box className={styles.section}>
      {/* SCN Identification Section */}
      <Box>
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
          />
          <FormInput
            label="SCN Title"
            value={formData.changeTitle}
            onChange={(val) => onInputChange("changeTitle", val)}
            disabled
            className={styles.IdentificationInput}
          />
        </Stack>

        <Stack direction="row" spacing={4} className={styles.formRow}>
          <FormInput
            label="Supplier Name"
            value={formData.supplierName}
            onChange={(val) => onInputChange("supplierName", val)}
            disabled
            className={styles.IdentificationInput}
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
          {/* {!isUpload && (
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
          )} */}
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
            type="email"
            className={styles.inputLabel}
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
            />
            <FormInput
              label="Component Number"
              value={formData.componentNumber ?? ""}
              onChange={(val) => onInputChange("componentNumber", val)}
              disabled={!isEditing}
              placeholder="Input text"
              className={styles.inputLabel}
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
          />
          {!isUpload && <div style={{ width: "50%" }}></div>}
        </Stack>
      </Box>

      {/* Documentation */}
      <Box>
        <h2 className={styles.sectionTitle}>Documentation & Attachments</h2>

        {isUpload && (
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
          </Box>
        )}
        <div className={styles.fileUploadInfo}>
          <p>{formData?.attachments?.length || 0} file(s) uploaded</p>
          <div className={styles.fileList}>
            {formData?.attachments?.map((file: any, idx: number) => (
              <div key={idx} className={styles.fileItem}>
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
          </div>
        </div>
      </Box>
    </Box>
  );
};

export default SCNFormFields;
