import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Box, Stack, Button } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import FormInput from "@components/common/FormInput";
import styles from "./SCNEditDetails.module.scss";
import SCNResultCard from "./SCNResultCard";
import editIcon from "../../assets/icons/editLight.svg";
import documentTextIcon from "../../assets/icons/documentext.svg";

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
  const navigate = useNavigate();
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

  const handleEditClick = () => {
    setIsEditing(true);
  };

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

        <Box className={styles.section}>
          {/* SCN Identification Section */}
          <Box>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
            >
              <h2 className={styles.sectionTitle}>SCN Identification</h2>
              {!isEditing && (
                <Button
                  variant="contained"
                  size="small"
                  className={styles.editButtonSmall}
                  onClick={handleEditClick}
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
                onChange={(val) => handleInputChange("supplierRef", val)}
                disabled
              />
              <FormInput
                label="SCN Title"
                value={formData.changeTitle}
                onChange={(val) => handleInputChange("changeTitle", val)}
                disabled
              />
            </Stack>

            <Stack direction="row" spacing={4} className={styles.formRow}>
              <FormInput
                label="Supplier Name"
                value={formData.supplierName}
                onChange={(val) => handleInputChange("supplierName", val)}
                disabled
              />
              <FormInput
                label="Planned Implementation Date"
                value={formData.plannedImplementationDate}
                onChange={(val) =>
                  handleInputChange("plannedImplementationDate", val)
                }
                disabled={!isEditing}
                type="date"
                placeholder="Input text"
                className={styles.inputLabel}
              />
            </Stack>
          </Box>

          {/* Current State Section */}
          <Box>
            <h2 className={styles.sectionTitle}>Current State</h2>
            <FormInput
              label="Current State Description"
              value={formData.currentState}
              onChange={(val) => handleInputChange("currentState", val)}
              disabled={!isEditing}
              multiline
              rows={4}
              className={styles.inputLabel}
            />
          </Box>

          {/* Proposed State Section */}
          <Box>
            <FormInput
              label="Proposed State Description"
              value={formData.proposedState}
              onChange={(val) => handleInputChange("proposedState", val)}
              disabled={!isEditing}
              multiline
              rows={4}
              className={styles.inputLabel}
            />
          </Box>

          {/* Justification Section */}
          <Box>
            {/* <h2 className={styles.sectionTitle}>Justification</h2> */}
            <FormInput
              label="Justification"
              value={formData.justification}
              onChange={(val) => handleInputChange("justification", val)}
              disabled={!isEditing}
              multiline
              rows={4}
              className={styles.inputLabel}
            />
          </Box>

          {/* Temporary Change and Supplier Sites Section */}
          <Box>
            <Stack direction="row" spacing={4} className={styles.formRow}>
              <Box className={styles.formGroup}>
                <label className={styles.formLabel}>Temporary Change</label>
                <div className={styles.radioGroup}>
                  <label className={styles.radioLabel}>
                    <input
                      type="radio"
                      name="temporaryChange"
                      value="No"
                      checked={formData.temporaryChange === "No"}
                      onChange={(e) =>
                        handleInputChange("temporaryChange", e.target.value)
                      }
                      disabled={!isEditing}
                    />
                    No
                  </label>
                  <label className={styles.radioLabel}>
                    <input
                      type="radio"
                      name="temporaryChange"
                      value="Yes"
                      checked={formData.temporaryChange === "Yes"}
                      onChange={(e) =>
                        handleInputChange("temporaryChange", e.target.value)
                      }
                      disabled={!isEditing}
                    />
                    Yes
                  </label>
                </div>
              </Box>
              <Box className={styles.formGroup}>
                <label className={styles.formLabel}>
                  Supplier Site(s) Affected
                </label>
                <div className={styles.radioGroup}>
                  <label className={styles.radioLabel}>
                    <input
                      type="radio"
                      name="Manufacturing"
                      value="Manufacturing"
                      checked={
                        formData.supplierSitesAffected2 === "Manufacturing"
                      }
                      onChange={(e) =>
                        handleInputChange(
                          "supplierSitesAffected2",
                          e.target.value,
                        )
                      }
                      disabled={!isEditing}
                    />
                    Manufacturing
                  </label>
                  <label className={styles.radioLabel}>
                    <input
                      type="radio"
                      name="Testing"
                      value="Testing"
                      checked={formData.supplierSitesAffected2 === "Testing"}
                      onChange={(e) =>
                        handleInputChange(
                          "supplierSitesAffected2",
                          e.target.value,
                        )
                      }
                      disabled={!isEditing}
                    />
                    Testing
                  </label>
                </div>
              </Box>
            </Stack>
            <Stack direction="row" spacing={4} className={styles.formRow}>
              <Box className={styles.formGroup}>
                <label className={styles.formLabel}>
                  Supplier Site(s) Affected
                </label>
                <div className={styles.checkboxGroup}>
                  <label className={styles.checkboxLabel}>
                    <input
                      type="radio"
                      checked={formData.supplierSitesAffected === "Low"}
                      onChange={(e) =>
                        handleInputChange(
                          "supplierSitesAffected",
                          e.target.checked ? "Low" : "",
                        )
                      }
                      disabled={!isEditing}
                    />
                    Low
                  </label>
                  <label className={styles.checkboxLabel}>
                    <input
                      type="radio"
                      checked={formData.supplierSitesAffected === "Medium"}
                      onChange={(e) =>
                        handleInputChange(
                          "supplierSitesAffected",
                          e.target.checked ? "Medium" : "",
                        )
                      }
                      disabled={!isEditing}
                    />
                    Medium
                  </label>
                  <label className={styles.checkboxLabel}>
                    <input
                      type="radio"
                      checked={formData.supplierSitesAffected === "High"}
                      onChange={(e) =>
                        handleInputChange(
                          "supplierSitesAffected",
                          e.target.checked ? "High" : "",
                        )
                      }
                      disabled={!isEditing}
                    />
                    High
                  </label>
                </div>
              </Box>
              <FormInput
                label="Supplier Contact Information"
                value={formData.supplierContactInfo}
                onChange={(val) =>
                  handleInputChange("supplierContactInfo", val)
                }
                disabled={!isEditing}
                type="email"
                className={styles.inputLabel}
              />
            </Stack>
            <Stack direction="row" spacing={4} className={styles.formRow}>
              <FormInput
                label="Notification Date"
                value={formData.notificationDate}
                onChange={(val) => handleInputChange("notificationDate", val)}
                disabled={!isEditing}
                type="date"
                className={styles.inputLabel}
              />
              <div style={{ width: "50%" }}></div>
            </Stack>
          </Box>
          <Box className={styles.divider} />
          {/* Change Timing Section */}
          <Box>
            <h2 className={styles.sectionTitle}>Change Timing</h2>
            <Stack direction="row" spacing={4} className={styles.formRow}>
              <FormInput
                label="Planned Implementation Date"
                value={formData.changeTimingPlannedDate}
                onChange={(val) =>
                  handleInputChange("changeTimingPlannedDate", val)
                }
                disabled={!isEditing}
                type="date"
                className={styles.inputLabel}
              />
              <FormInput
                label="First Affected Lot / Batch"
                value={formData.firstAffectedLotBatch}
                onChange={(val) =>
                  handleInputChange("firstAffectedLotBatch", val)
                }
                disabled={!isEditing}
                placeholder="Input text"
                className={styles.inputLabel}
              />
            </Stack>
          </Box>
          <Box className={styles.divider} />
          {/* Materials / Products Impacted Section */}
          <Box>
            <h2 className={styles.sectionTitle}>
              Materials / Products Impacted
            </h2>
            <FormInput
              label="Material / Component Number"
              value={formData.materialComponentNumber}
              onChange={(val) =>
                handleInputChange("materialComponentNumber", val)
              }
              disabled={!isEditing}
              placeholder="Input text"
              className={styles.inputLabel}
            />
          </Box>

          {/* Documentation & Attachments Section */}
          <Box>
            <h2 className={styles.sectionTitle}>Documentation & Attachments</h2>
            <div className={styles.fileUploadInfo}>
              <p>1 file uploaded</p>
              <div className={styles.fileList}>
                <div className={styles.fileItem}>
                  <div className={styles.fileDetails}>
                    <span className={styles.fileIcon}>
                      <img src={documentTextIcon} alt="document" />
                    </span>
                    <span className={styles.fileInfo}>
                      <span className={styles.fileName}>
                        Supplier file 1.pdf
                      </span>
                      <span className={styles.fileSize}>3.67 MB</span>
                    </span>
                  </div>

                  <a href="#" className={styles.viewLink}>
                    View
                  </a>
                </div>
                <div className={styles.fileItem}>
                  <div className={styles.fileDetails}>
                    <span className={styles.fileIcon}>
                      <img src={documentTextIcon} alt="document" />
                    </span>
                    <span className={styles.fileInfo}>
                      <span className={styles.fileName}>
                        Supplier file 2.pdf
                      </span>
                      <span className={styles.fileSize}>5.67 MB</span>
                    </span>
                  </div>
                  <a href="#" className={styles.viewLink}>
                    View
                  </a>
                </div>
              </div>
            </div>
          </Box>
        </Box>
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
