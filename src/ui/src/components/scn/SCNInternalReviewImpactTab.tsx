import React, { useState, useEffect } from "react";
import styles from "./SCNInternalReviewImpactTab.module.scss";
import { Box, CircularProgress, Stack, Typography } from "@mui/material";
import AppButton from "@components/common/AppButton";
import AISummaryIcon from "../../assets/icons/aiSummary.svg";
import EditIcon from "../../assets/icons/editIcon.svg";
import SelectedFields from "@components/common/SelectedFields";
import { scnEditClassify, toggleClassification } from "src/services/scn";
import SCNImpactTabSkeleton from "./skeleton/SCNImpactTabSkeleton";
import pdfIcon from "../../assets/icons/pdfIcon.svg";
import ArrowRightOrange from "../../assets/icons/arrowRightOrange.svg";
import AcceptIcon from "../../assets/icons/accept.svg";
import ChangeSCNOutputModal from "./modal/ChangeSCNOutputModal";
import RightIcon from "../../assets/icons/rightOrange.svg";
import InfoIcon from "../../assets/icons/information.svg";

export interface ImpactClassificationData {
  change_control_required?: string | null;
  cc_record_id?: string | null;
  final_classification?: string | null;
  change_classification_supplier?: string | null;
  final_risk_level?: string | null;
  final_assigned_team?: string | null;
  action_required?: string | null;
  ai_summary?: string | null;
}

export interface Props {
  classificationData?: ImpactClassificationData | null;
  isLoading?: boolean;
  /** The email_id of the currently selected SCN record, required for the save API call */
  emailId?: string;
  /** Called after a successful toggle so the parent can re-fetch the latest impact data */
  onRefresh?: () => Promise<void>;
  onReviewScnClick?: () => void;
  /** Complete SCN detail for things like Affected Items and Attachments */
  scnDetail?: any;
  onOutputClick?: () => void;
  onPreviewClick?: () => void;
  changeControlRequired?: string;
  onRequestInfoClick?: () => void;
}

const SCNInternalReviewImpactTab: React.FC<Props> = ({
  classificationData,
  isLoading,
  emailId,
  onRefresh,
  onReviewScnClick,
  scnDetail,
  onOutputClick,
  onPreviewClick,
  changeControlRequired,
  onRequestInfoClick,
}) => {
  const [selected, setSelected] = useState<"SCN" | "NON_SCN">("SCN");
  const [changeType, setChangeType] = useState("");
  const [scnClassification, setScnClassification] = useState("");
  const [actionsRequired, setActionsRequired] = useState("");
  const [assignedTo, setAssignedTo] = useState<string[]>([]);
  const [editMode, setEditMode] = useState(false);
  const [aiSummary, setAiSummary] = useState<string>("");
  const [riskLevel, setRiskLevel] = useState<string>("");
  const [predictedOutput, setPredictedOutput] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isToggling, setIsToggling] = useState(false);
  const [toggleError, setToggleError] = useState<string | null>(null);
  const [showOutputModal, setShowOutputModal] = useState(false);
  const [pendingStatus, setPendingStatus] = useState<"SCN" | "NON_SCN">("SCN");
  const [iframeLoading, setIframeLoading] = useState(true);
  const [isCCRequired, setIsCCRequired] = useState<string>("No");
  const [ccRecordId, setCcRecordId] = useState<string>("");

  const isFieldsDisabled = !editMode || selected === "NON_SCN" || isSaving;

  const attachments = scnDetail?.attachments || [];
  const allPdfs = attachments.filter((file: any) =>
    file.filename.toLowerCase().endsWith(".pdf"),
  );
  const primaryPdf = allPdfs[0];
  const remainingAttachments = attachments.filter(
    (file: any) => file !== primaryPdf,
  );

  // Populate from API data whenever classificationData changes
  useEffect(() => {
    if (!classificationData) return;

    if (classificationData.final_classification) {
      const cls = classificationData.final_classification.toUpperCase();
      setPredictedOutput(classificationData.final_classification);
      setSelected(cls === "SCN" ? "SCN" : "NON_SCN");
    }
    if (classificationData.change_classification_supplier) {
      setChangeType(classificationData.change_classification_supplier);
    }
    if (classificationData.final_risk_level) {
      setRiskLevel(classificationData.final_risk_level);
      const risk = classificationData.final_risk_level;
      // Map risk level to Minor/Moderate/Major classification label
      if (["minor", "low"].includes(risk.toLowerCase())) {
        setScnClassification("Minor");
      } else if (["moderate", "medium"].includes(risk.toLowerCase())) {
        setScnClassification("Moderate");
      } else {
        setScnClassification("Major");
      }
    }
    if (classificationData.final_assigned_team) {
      const teams = classificationData.final_assigned_team
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      setAssignedTo(teams);
    }
    if (classificationData.change_control_required) {
      const ccReq = classificationData.change_control_required.toLowerCase();
      setIsCCRequired(ccReq === "yes" ? "Yes" : "No");
    }
    if (classificationData.cc_record_id) {
      setCcRecordId(classificationData.cc_record_id);
    }
    if (classificationData.action_required != null) {
      setActionsRequired(classificationData.action_required || "");
    }
    if (classificationData.ai_summary) {
      setAiSummary(classificationData.ai_summary);
    }
  }, [classificationData]);

  const allTeams = [
    "Supplier Quality",
    "Manufacturing Engineering",
    "Operations",
    "Regulatory Affairs",
    "Technical Writing",
    "R&D",
    "Quality Engineering",
    "Quality Control",
    "Validation",
    "Software QA",
    "Supply Chain",
  ];

  const changeTypeOptions = [
    "Manufacturing Process Changes",
    "Manufacturing Site / Facility Changes",
    "Raw Material Changes",
    "Component or Part Design Changes",
    "Specification Changes",
    "Testing / Analytical Method Changes",
    "Supplier Sub-tier Changes",
    "Quality System Changes",
    "Regulatory Status Changes",
    "Packaging and Labeling Changes",
    "Storage and Distribution Changes",
    "Organizational / Ownership Changes",
    "Documentation Changes (Administrative)",
    "Discontinuation / Obsolescence",
  ];

  const scnClassificationOptions = ["Minor", "Moderate", "Major"];

  const AISuggestedBadge = () => (
    <span className={styles.aiBadge}>
      <img src={AISummaryIcon} alt="" /> AI Suggested
    </span>
  );

  const handleSelect = (field: string) => {
    setAssignedTo((prev) =>
      prev.includes(field) ? prev.filter((f) => f !== field) : [...prev, field],
    );
  };

  const handleRemove = (field: string) => {
    setAssignedTo((prev) => prev.filter((f) => f !== field));
  };

  const handleEdit = () => {
    setSaveError(null);
    setEditMode(true);
  };

  const handleSave = async () => {
    if (!emailId) {
      setSaveError("No SCN record selected.");
      return;
    }
    setIsSaving(true);
    setSaveError(null);
    try {
      const payload = {
        change_classification_supplier: changeType || undefined,
        change_control_required: isCCRequired.toLowerCase() as "yes" | "no",
        cc_record_id: ccRecordId || undefined,
        action_required: actionsRequired || undefined,
        final_risk_level:
          scnClassification.toLowerCase() === "minor"
            ? "minor"
            : scnClassification.toLowerCase() === "major"
              ? "major"
              : "moderate",
        final_assigned_team:
          assignedTo.length > 0 ? assignedTo.join(", ") : undefined,
      };
      const res = await scnEditClassify(emailId, payload);
      if (res?.success) {
        setEditMode(false);
        onRefresh?.();
      } else {
        setSaveError(res?.message || "Failed to save changes.");
      }
    } catch (err: any) {
      setSaveError(err?.message || "An error occurred while saving.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setSaveError(null);
    setEditMode(false);
  };

  const handleToggleClick = (value: "SCN" | "NON_SCN") => {
    if (value === selected) return;
    setPendingStatus(value);
    setShowOutputModal(true);
  };

  const handleConfirmToggle = async () => {
    if (!emailId || !pendingStatus) return;
    setIsToggling(true);
    setToggleError(null);
    try {
      const res = await toggleClassification(emailId, pendingStatus);
      const newClassification: "SCN" | "NON_SCN" =
        res?.new_classification === "SCN" ? "SCN" : "NON_SCN";
      setSelected(newClassification);
      setEditMode(false);
      setShowOutputModal(false);
      onRefresh?.();
    } catch (err: any) {
      setToggleError(
        err?.message || "Failed to change SCN output. Please try again.",
      );
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <>
      {isLoading ? (
        <SCNImpactTabSkeleton />
      ) : !classificationData ? (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          py={10}
          gap={1}
        >
          <Typography sx={{ color: "#6b7280", fontSize: 15, fontWeight: 500 }}>
            No classification data available yet.
          </Typography>
          <Typography sx={{ color: "#9ca3af", fontSize: 13 }}>
            Click &ldquo;Impact Review&rdquo; to run the AI assessment.
          </Typography>
        </Box>
      ) : (
        <>
          {/* <Stack
            direction="row"
            gap={1.5}
            justifyContent="flex-end"
            marginBottom={3}
            marginTop={1}
          >
            <AppButton variant="outlined" onClick={onOutputClick}>
              <span className={styles.appButton}>
                <img src={UndoIcon} alt="" />
                Change SCN Output
              </span>
            </AppButton>

            <AppButton
              variant="outlined"
              onClick={onRejectClick}
              className={styles.rejectButton}
            >
              <span className={styles.appButton}>
                <img src={CircleDeleteIcon} alt="" />
                Reject
              </span>
            </AppButton>

            <AppButton variant="primary" onClick={onApproveClick}>
              <span className={styles.appButton}>
                <img src={CheckIcon} alt="" />
                Approve
              </span>
            </AppButton>
          </Stack> */}

          <div className={styles.impactContainer}>
            <div className={styles.header}>
              <img src={AISummaryIcon} alt="AI Summary" />
              <Typography variant="h6">AI Summary</Typography>
            </div>

            <Typography className={styles.summaryText}>{aiSummary}</Typography>

            <div className={styles.affectedItems}>
              <Typography className={styles.title}>Affected Items</Typography>
              <Typography className={styles.itemRow}>
                <strong>Services:</strong> Release Testing Support, Incoming
                Inspection Service
              </Typography>
              <Typography className={styles.itemRow}>
                <strong>Material:</strong> Polymer Resin (lot-controlled)
              </Typography>
            </div>

            <div className={styles.chipsContainer}>
              <div className={styles.chip}>
                Predicted Output: <strong>{predictedOutput}</strong>
              </div>
              <div className={styles.chip}>
                Risk Level: <strong>{riskLevel}</strong>
              </div>
              <div className={styles.chip}>
                Assigned To: <strong>{assignedTo.join(", ")}</strong>
              </div>
            </div>
          </div>

          <Box marginTop={3}>
            <Stack
              direction="row"
              alignItems="center"
              justifyContent="space-between"
              marginBottom={1}
            >
              <Stack direction="row" gap={13}>
                <Typography className={styles.scnPredictedOutputLabel}>
                  SCN Predicted Output
                </Typography>
                <AISuggestedBadge />
              </Stack>
            </Stack>

            <Box className={styles.toggleGroup}>
              <AppButton
                className={`${styles.toggleBtn} ${selected === "SCN" ? styles.active : ""}`}
                variant="ghost"
                onClick={() => handleToggleClick("SCN")}
              >
                {isToggling && selected !== "SCN" ? (
                  <CircularProgress size={12} sx={{ color: "inherit" }} />
                ) : (
                  "SCN"
                )}
              </AppButton>
              <AppButton
                className={`${styles.toggleBtn} ${selected === "NON_SCN" ? styles.active : ""}`}
                variant="ghost"
                onClick={() => handleToggleClick("NON_SCN")}
              >
                {isToggling && selected !== "NON_SCN" ? (
                  <CircularProgress size={12} sx={{ color: "inherit" }} />
                ) : (
                  "Non SCN"
                )}
              </AppButton>
            </Box>
            {toggleError && (
              <Typography sx={{ color: "#d32f2f", fontSize: 12, mt: 0.5 }}>
                {toggleError}
              </Typography>
            )}
          </Box>
          <Box className={styles.divider} />
          <Box marginTop={3}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
            >
              <Stack direction="row" alignItems="center" gap={1.5}>
                <Typography variant="h6" className={styles.sectionTitle}>
                  Assessment Summary
                </Typography>
              </Stack>
              {!editMode && selected === "SCN" && (
                <AppButton
                  variant="outlined"
                  className={styles.editButton}
                  onClick={handleEdit}
                >
                  <span className={styles.appButton}>
                    <img src={EditIcon} alt="" /> Edit
                  </span>
                </AppButton>
              )}
            </Stack>
            {selected === "NON_SCN" ? (
              <div className={styles.lockedBanner}>
                <span className={styles.lockedBannerIcon}>ⓘ</span>
                Set <strong>Predicted Output</strong> to <strong>SCN</strong> to
                enable this section and edit assessment details.
              </div>
            ) : (
              <Typography className={styles.sectionSubtitle}>
                The Assessment Summary is enabled when the Predicted Output is
                set to SCN
              </Typography>
            )}

            <Typography
              variant="h6"
              className={styles.subSectionTitle}
              marginTop={3}
            >
              Change Control Summary
            </Typography>

            <Stack direction="row" spacing={6}>
              <Box sx={{ flex: 1 }}>
                <Stack direction="column" spacing={8}>
                  <Box flex={1}>
                    <Box sx={{ flex: 1 }}>
                      <Stack direction="column" spacing={8} marginTop={2}>
                        <Box flex={1}>
                          <Typography className={styles.inputLabel}>
                            Change Control Required?
                          </Typography>
                          <Stack direction="row" spacing={3}>
                            {["No", "Yes"].map((option) => (
                              <label key={option} className={styles.radioLabel}>
                                <input
                                  type="radio"
                                  name="ccRequired"
                                  value={option}
                                  checked={isCCRequired === option}
                                  onChange={(e) =>
                                    setIsCCRequired(e.target.value)
                                  }
                                  disabled={isFieldsDisabled}
                                />
                                {option}
                              </label>
                            ))}
                          </Stack>
                          <Box marginTop={2}>
                            <Typography className={styles.inputLabel}>
                              Change Control Record ID Number
                            </Typography>
                            <input
                              type="text"
                              className={styles.textInput}
                              value={ccRecordId}
                              onChange={(e) => setCcRecordId(e.target.value)}
                              disabled={isFieldsDisabled}
                              placeholder="CC-XXXXX"
                            />
                          </Box>
                        </Box>
                      </Stack>
                    </Box>
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      marginTop={2}
                    >
                      <Typography className={styles.inputLabel}>
                        Change Type
                      </Typography>
                      <AISuggestedBadge />
                    </Stack>

                    {!isFieldsDisabled ? (
                      <div className={styles.selectWrapper}>
                        <select
                          className={styles.selectInput}
                          value={changeType}
                          onChange={(e) => setChangeType(e.target.value)}
                        >
                          <option value="">Select Change Type</option>
                          {changeTypeOptions.map((option) => (
                            <option key={option} value={option}>
                              {option}
                            </option>
                          ))}
                        </select>
                        <div className={styles.selectArrow} />
                      </div>
                    ) : (
                      <input
                        type="text"
                        className={styles.textInput}
                        value={changeType}
                        disabled
                      />
                    )}
                    <Box className={styles.divider} />
                    <Box flex={1}>
                      <Typography
                        variant="h6"
                        className={styles.subSectionTitle}
                      >
                        SCN Summary
                      </Typography>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        marginTop={2}
                      >
                        <Typography className={styles.inputLabel}>
                          SCN Classification
                        </Typography>
                        <AISuggestedBadge />
                      </Stack>

                      {!isFieldsDisabled ? (
                        <div className={styles.selectWrapper}>
                          <select
                            className={styles.selectInput}
                            value={scnClassification}
                            onChange={(e) =>
                              setScnClassification(e.target.value)
                            }
                          >
                            {scnClassificationOptions.map((option) => (
                              <option key={option} value={option}>
                                {option}
                              </option>
                            ))}
                          </select>
                          <div className={styles.selectArrow} />
                        </div>
                      ) : (
                        <input
                          type="text"
                          className={styles.textInput}
                          value={scnClassification}
                          disabled
                        />
                      )}
                    </Box>
                  </Box>
                </Stack>
                <Box marginTop={3}>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography className={styles.inputLabel}>
                      Action(s) Required
                    </Typography>
                  </Stack>
                  <textarea
                    className={styles.textArea}
                    rows={4}
                    value={actionsRequired}
                    onChange={(e) => setActionsRequired(e.target.value)}
                    disabled={isFieldsDisabled}
                  />
                </Box>
              </Box>
              <Box className={styles.previewColumn} sx={{ flex: 1 }}>
                <Box className={styles.pdfPreviewContainer}>
                  {primaryPdf?.download_url ? (
                    <>
                      {iframeLoading && (
                        <Box className={styles.pdfLoader}>
                          <CircularProgress
                            size={32}
                            sx={{ color: "#fd5108" }}
                          />
                          <Typography variant="body2">
                            Loading preview...
                          </Typography>
                        </Box>
                      )}
                      <iframe
                        src={primaryPdf.download_url}
                        title="PDF Preview"
                        className={`${styles.pdfIframe} ${iframeLoading ? styles.hidden : ""}`}
                        onLoad={() => setIframeLoading(false)}
                      />
                      {primaryPdf?.download_url && (
                        <AppButton
                          variant="secondary"
                          className={styles.previewButton}
                          onClick={onPreviewClick}
                        >
                          Preview PDF
                          <img src={RightIcon} alt=">" />
                        </AppButton>
                      )}
                    </>
                  ) : (
                    <Box className={styles.noPdfMessage}>
                      <img
                        src={pdfIcon}
                        alt=""
                        className={styles.pdfPlaceholderIcon}
                      />
                      <Typography variant="body2">
                        No PDF available for preview.
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </Stack>
            <Box className={styles.divider} marginTop={4} />
            <Box>
              <Typography variant="h6" className={styles.sectionTitle}>
                Assign
              </Typography>

              <Box marginTop={2}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography className={styles.inputLabel}>
                    Assigned To
                  </Typography>
                  <AISuggestedBadge />
                </Stack>

                <SelectedFields
                  fields={allTeams}
                  selected={assignedTo}
                  onSelect={
                    editMode && selected === "SCN" ? handleSelect : undefined
                  }
                  onRemove={
                    editMode && selected === "SCN" ? handleRemove : undefined
                  }
                  label=""
                  disabled={isFieldsDisabled}
                />
              </Box>
            </Box>

            {editMode && (
              <Stack
                direction="row"
                justifyContent="flex-end"
                gap={2}
                marginTop={4}
                marginBottom={4}
              >
                {saveError && (
                  <Typography
                    sx={{ color: "#d32f2f", fontSize: 13, alignSelf: "center" }}
                  >
                    {saveError}
                  </Typography>
                )}
                <AppButton
                  variant="outlined"
                  className={styles.cancelBtn}
                  onClick={handleCancel}
                  disabled={isSaving}
                >
                  Cancel
                </AppButton>
                <AppButton
                  variant="primary"
                  className={styles.saveBtn}
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <span
                      style={{ display: "flex", alignItems: "center", gap: 6 }}
                    >
                      <CircularProgress size={14} sx={{ color: "inherit" }} />
                      Saving…
                    </span>
                  ) : (
                    "Save"
                  )}
                </AppButton>
              </Stack>
            )}
          </Box>

          {/* 7. Documentation & Attachments (Only if more than primary PDF) */}
          {remainingAttachments.length > 0 && (
            <Box marginTop={6}>
              <Typography variant="h6" className={styles.sectionTitle}>
                Documentation & Attachments
              </Typography>

              <Box className={styles.attachmentsContainer} marginTop={2}>
                {remainingAttachments.map((file: any, index: number) => (
                  <Box key={index} className={styles.attachmentCard}>
                    <Stack
                      direction="row"
                      alignItems="center"
                      justifyContent="space-between"
                    >
                      <Stack direction="row" alignItems="center" gap={1.5}>
                        <img src={pdfIcon} alt="pdf" />
                        <Typography className={styles.fileName}>
                          {file.filename}
                        </Typography>
                      </Stack>
                      {file.download_url && (
                        <a
                          href={file.download_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={styles.previewLink}
                          onClick={(e) => {
                            e.preventDefault();
                            onPreviewClick?.();
                          }}
                        >
                          Preview <img src={ArrowRightOrange} alt="" />
                        </a>
                      )}
                    </Stack>
                  </Box>
                ))}
              </Box>
            </Box>
          )}

          <Box className={styles.divider} marginTop={4} />
          <Stack
            direction="row"
            justifyContent="flex-end"
            marginTop={4}
            gap={2}
            marginBottom={4}
          >
            <AppButton
              variant="outlined"
              onClick={onRequestInfoClick}
              className={styles.rejectButton}
            >
              <span className={styles.appButton}>
                <img src={InfoIcon} alt="" />
                Request Info
              </span>
            </AppButton>

            <AppButton
              variant="primary"
              onClick={onReviewScnClick}
              className={styles.appButton}
            >
              <Stack direction="row" alignItems="center" gap={1}>
                <img src={AcceptIcon} alt="Accept" /> Review SCN
              </Stack>
            </AppButton>
          </Stack>
        </>
      )}
      <ChangeSCNOutputModal
        open={showOutputModal}
        onClose={() => setShowOutputModal(false)}
        onConfirm={handleConfirmToggle}
        currentStatus={selected}
        targetStatus={pendingStatus}
        isSubmitting={isToggling}
      />
    </>
  );
};

export default SCNInternalReviewImpactTab;
