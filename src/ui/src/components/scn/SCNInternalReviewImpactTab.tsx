import React, { useState, useEffect } from "react";
import styles from "./SCNInternalReviewImpactTab.module.scss";
import UndoIcon from "../../assets/icons/undoBlack.svg";
import { Box, CircularProgress, Stack, Typography } from "@mui/material";
import AppButton from "@components/common/AppButton";
import CircleDeleteIcon from "../../assets/icons/circle-delete.svg";
import AISummaryIcon from "../../assets/icons/aiSummary.svg";
import CheckIcon from "../../assets/icons/circle-checkmark.svg";
import EditIcon from "../../assets/icons/editLight.svg";
import SelectedFields from "@components/common/SelectedFields";
import ChangeSCNOutputModal from "./modal/ChangeSCNOutputModal";
import ApproveModal from "./modal/ApproveModal";
import RejectSCNModal from "./modal/RejectSCNModal";
import SCNImpactTabSkeleton from "./skeleton/SCNImpactTabSkeleton";
import { scnEditClassify } from "src/services/scn";

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

interface Props {
  classificationData?: ImpactClassificationData | null;
  isLoading?: boolean;
  /** The email_id of the currently selected SCN record, required for the save API call */
  emailId?: string;
}

const SCNInternalReviewImpactTab: React.FC<Props> = ({
  classificationData,
  isLoading,
  emailId,
}) => {
  const [selected, setSelected] = useState<"SCN" | "NON_SCN">("SCN");
  const [changeControlRequired, setChangeControlRequired] = useState("");
  const [recordId, setRecordId] = useState("");
  const [changeType, setChangeType] = useState("");
  const [scnClassification, setScnClassification] = useState("");
  const [openPreview, setOpenPreview] = useState(false);
  const [actionsRequired, setActionsRequired] = useState("");
  const [openApprove, setOpenApprove] = useState(false);
  const [openReject, setOpenReject] = useState(false);
  const [assignedTo, setAssignedTo] = useState<string[]>([]);
  const [editMode, setEditMode] = useState(false);
  const [aiSummary, setAiSummary] = useState<string>("");
  const [riskLevel, setRiskLevel] = useState<string>("");
  const [predictedOutput, setPredictedOutput] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Populate from API data whenever classificationData changes
  useEffect(() => {
    if (!classificationData) return;

    if (classificationData.final_classification) {
      const cls = classificationData.final_classification.toUpperCase();
      setPredictedOutput(classificationData.final_classification);
      setSelected(cls === "SCN" ? "SCN" : "NON_SCN");
    }
    if (classificationData.change_control_required != null) {
      // API returns "NO" / "YES"
      const val = classificationData.change_control_required.toUpperCase();
      setChangeControlRequired(val === "NO" ? "No" : "Yes");
    }
    // if (classificationData.cc_record_id != null) {
    //   setRecordId(classificationData.cc_record_id || "");
    // }
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
    if (classificationData.action_required != null) {
      setActionsRequired(classificationData.action_required || "");
    }
    if (classificationData.ai_summary) {
      setAiSummary(classificationData.ai_summary);
    }
  }, [classificationData]);

  const allTeams = [
    "Quality Team",
    "Manufacturing Team",
    "Supply Chain Team",
    "Regulatory Team",
    "Team 4",
    "Team5",
  ];

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

  const isFieldsDisabled =
    selected === "NON_SCN" || (selected === "SCN" && !editMode);

  const handleEdit = () => {
    setSaveError(null);
    setEditMode(true);
  };

  /** Build the payload from current state and call the scnEditClassify PUT API */
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
        change_control_required: changeControlRequired
          ? (changeControlRequired.toLowerCase() as "yes" | "no")
          : undefined,
        action_required: actionsRequired || undefined,
        final_risk_level: riskLevel || undefined,
        final_assigned_team:
          assignedTo.length > 0 ? assignedTo.join(", ") : undefined,
      };
      const res = await scnEditClassify(emailId, payload);
      if (res?.success) {
        setEditMode(false);
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
          <Stack
            direction="row"
            gap={1.5}
            justifyContent="flex-end"
            marginBottom={3}
            marginTop={1}
          >
            <AppButton variant="outlined" onClick={() => setOpenPreview(true)}>
              <span className={styles.appButton}>
                <img src={UndoIcon} alt="" />
                Change SCN Output
              </span>
            </AppButton>

            <AppButton variant="outlined" onClick={() => setOpenReject(true)}>
              <span className={styles.appButton}>
                <img src={CircleDeleteIcon} alt="" />
                Reject
              </span>
            </AppButton>

            <AppButton
              variant="primary"
              className={styles.appButton}
              onClick={() => setOpenApprove(true)}
            >
              <span className={styles.appButton}>
                <img src={CheckIcon} alt="" />
                Approve
              </span>
            </AppButton>
          </Stack>

          <div className={styles.impactContainer}>
            <div className={styles.header}>
              <img src={AISummaryIcon} alt="AI Summary" />
              <Typography variant="h6">AI Summary</Typography>
            </div>

            <Typography className={styles.summaryText}>{aiSummary}</Typography>

            {/* <div className={styles.affectedItems}>
          <Typography className={styles.title}>Affected Items</Typography>
          <Typography className={styles.itemRow}>
            <strong>Services:</strong> Release Testing Support, Incoming
            Inspection Service
          </Typography>
          <Typography className={styles.itemRow}>
            <strong>Material:</strong> Polymer Resin (lot-controlled)
          </Typography>
        </div> */}

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
              <Stack direction="row" alignItems="center" gap={2}>
                <Typography className={styles.inputLabel}>
                  SCN Predicted Output
                </Typography>
                <AISuggestedBadge />
              </Stack>
            </Stack>
            <Box className={styles.toggleGroup}>
              <AppButton
                className={`${styles.toggleBtn} ${selected === "SCN" ? styles.active : ""}`}
                variant="ghost"
                onClick={() => {
                  setSelected("SCN");
                  setEditMode(false);
                }}
              >
                SCN
              </AppButton>
              <AppButton
                className={`${styles.toggleBtn} ${selected === "NON_SCN" ? styles.active : ""}`}
                variant="ghost"
                onClick={() => {
                  setSelected("NON_SCN");
                  setEditMode(false);
                }}
              >
                Non SCN
              </AppButton>
            </Box>
          </Box>

          <Box marginTop={4}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
            >
              <Typography variant="h6" className={styles.sectionTitle}>
                Assessment Summary
              </Typography>
              {!editMode && selected === "SCN" && (
                <AppButton
                  variant="primary"
                  className={styles.editButton}
                  onClick={handleEdit}
                >
                  <span className={styles.appButton}>
                    <img src={EditIcon} alt="" /> Edit
                  </span>
                </AppButton>
              )}
            </Stack>
            <Typography className={styles.sectionSubtitle}>
              The Assessment Summary is enabled when the Predicted Output is set
              to SCN
            </Typography>

            <Typography
              variant="subtitle1"
              className={styles.subSectionTitle}
              marginTop={3}
            >
              Change Control Summary
            </Typography>

            <Stack direction="row" spacing={8} marginTop={2}>
              <Box>
                <Typography className={styles.inputLabel}>
                  Change Control Required?
                </Typography>
                <Stack direction="row" spacing={3} marginTop={1}>
                  {["No", "Yes"].map((option) => (
                    <label key={option} className={styles.radioLabel}>
                      <input
                        type="radio"
                        name="changeControl"
                        value={option}
                        checked={changeControlRequired === option}
                        onChange={(e) =>
                          setChangeControlRequired(e.target.value)
                        }
                        disabled={isFieldsDisabled}
                      />
                      {option}
                    </label>
                  ))}
                </Stack>
              </Box>

              <Box flex={1} maxWidth="400px">
                <Typography className={styles.inputLabel}>
                  Record ID Number
                </Typography>
                <input
                  type="text"
                  className={styles.textInput}
                  value={recordId}
                  readOnly
                  disabled
                  style={{ opacity: 0.5, cursor: "not-allowed" }}
                />
              </Box>
            </Stack>
          </Box>

          <Box marginTop={4}>
            <Typography variant="h6" className={styles.sectionTitle}>
              SCN Summary
            </Typography>

            <Stack direction="row" spacing={8} marginTop={2}>
              <Box flex={1}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography className={styles.inputLabel}>
                    Change Type
                  </Typography>
                  <AISuggestedBadge />
                </Stack>

                <input
                  type="text"
                  className={styles.textInput}
                  value={changeType}
                  onChange={(e) => setChangeType(e.target.value)}
                  disabled={isFieldsDisabled}
                />
              </Box>

              <Box flex={1}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography className={styles.inputLabel}>
                    SCN Classification
                  </Typography>
                  <AISuggestedBadge />
                </Stack>

                <Stack direction="row" spacing={3} marginTop={1}>
                  {["Minor", "Moderate", "Major"].map((option) => (
                    <label key={option} className={styles.radioLabel}>
                      <input
                        type="radio"
                        name="scnClassification"
                        value={option}
                        checked={scnClassification === option}
                        onChange={(e) => setScnClassification(e.target.value)}
                        disabled={isFieldsDisabled}
                      />
                      {option}
                    </label>
                  ))}
                </Stack>
              </Box>
            </Stack>

            <Box marginTop={3}>
              <Stack direction="row" justifyContent="space-between">
                <Typography className={styles.inputLabel}>
                  Action(s) Required
                </Typography>
                <AISuggestedBadge />
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

          <Box marginTop={4}>
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
                fields={assignedTo ? assignedTo : allTeams}
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

          <ChangeSCNOutputModal
            open={openPreview}
            onClose={() => setOpenPreview(false)}
            emailId={emailId}
            onDone={(newClassification) => {
              setSelected(newClassification);
              setPredictedOutput(newClassification);
            }}
            defaultValue={selected}
          />

          <ApproveModal
            open={openApprove}
            onClose={() => setOpenApprove(false)}
            emailId={emailId}
            onDone={(changeControl, ccRecordId) => {
              setChangeControlRequired(changeControl);
              setRecordId(ccRecordId);
              setOpenApprove(false);
            }}
            defaultChangeControl={changeControlRequired}
            defaultRecordId={recordId}
          />

          <RejectSCNModal
            open={openReject}
            onClose={() => setOpenReject(false)}
            emailId={emailId}
            onSubmit={(comment) => {
              setOpenReject(false);
            }}
          />
        </>
      )}
    </>
  );
};

export default SCNInternalReviewImpactTab;
