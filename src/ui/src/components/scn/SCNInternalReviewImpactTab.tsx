import React, { useState } from "react";
import styles from "./SCNInternalReviewImpactTab.module.scss";
import UndoIcon from "../../assets/icons/undoBlack.svg";
import { Box, Stack, Typography } from "@mui/material";
import AppButton from "@components/common/AppButton";
import CircleDeleteIcon from "../../assets/icons/circle-delete.svg";
import AISummaryIcon from "../../assets/icons/aiSummary.svg";
import CheckIcon from "../../assets/icons/circle-checkmark.svg";
import EditIcon from "../../assets/icons/editLight.svg";
import SelectedFields from "@components/common/SelectedFields";
import ChangeSCNOutputModal from "./modal/ChangeSCNOutputModal";
import ApproveModal from "./modal/ApproveModal";
import RejectSCNModal from "./modal/RejectSCNModal";

const SCNInternalReviewImpactTab: React.FC = () => {
  const [selected, setSelected] = useState<"SCN" | "NON_SCN">("SCN");
  const [changeControlRequired, setChangeControlRequired] = useState("Yes");
  const [recordId, setRecordId] = useState("CC-23451");
  const [changeType, setChangeType] = useState("SCN-12345");
  const [scnClassification, setScnClassification] = useState("Minor");
  const [openPreview, setOpenPreview] = useState(false);
  const [actionsRequired, setActionsRequired] = useState(
    "Please provide Planned Implementation Date.",
  );
  const [openApprove, setOpenApprove] = useState(false);
  const [openReject, setOpenReject] = useState(false);
  const [assignedTo, setAssignedTo] = useState<string[]>([
    "Quality Team",
    "Manufacturing Team",
  ]);
  const [editMode, setEditMode] = useState(false);

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

  const handleEdit = () => setEditMode(true);
  const handleSave = () => setEditMode(false);
  const handleCancel = () => setEditMode(false);

  return (
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

        <Typography className={styles.summaryText}>
          Pinnacle Laboratories is implementing a controlled change to replace
          end-of-life legacy equipment/material. The change is managed under
          their quality system and requires customer review.
        </Typography>

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
            Predicted Output: <strong>SCN</strong>
          </div>
          <div className={styles.chip}>
            Risk Level: <strong>High</strong>
          </div>
          <div className={styles.chip}>
            Assigned To: <strong>Quality Team, Manufacturing Team</strong>
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
          The Assessment Summary is enabled when the Predicted Output is set to
          SCN
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
                    onChange={(e) => setChangeControlRequired(e.target.value)}
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
              onChange={(e) => setRecordId(e.target.value)}
              disabled={isFieldsDisabled}
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
              <Typography className={styles.inputLabel}>Change Type</Typography>
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
            <Typography className={styles.inputLabel}>Assigned To</Typography>
            <AISuggestedBadge />
          </Stack>

          <SelectedFields
            fields={allTeams}
            selected={assignedTo}
            onSelect={editMode && selected === "SCN" ? handleSelect : undefined}
            onRemove={editMode && selected === "SCN" ? handleRemove : undefined}
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
          <AppButton
            variant="outlined"
            className={styles.cancelBtn}
            onClick={handleCancel}
          >
            Cancel
          </AppButton>
          <AppButton
            variant="primary"
            className={styles.saveBtn}
            onClick={handleSave}
          >
            Save
          </AppButton>
        </Stack>
      )}

      <ChangeSCNOutputModal
        open={openPreview}
        onClose={() => setOpenPreview(false)}
        onDone={(value) => {
          console.log("Selected Output:", value);
        }}
        defaultValue="SCN"
      />

      <ApproveModal
        open={openApprove}
        onClose={() => setOpenApprove(false)}
        onDone={(changeControl, recordId) => {
          setChangeControlRequired(changeControl);
          setRecordId(recordId);
          setOpenApprove(false);
          // You can add further logic here (e.g., API call, notification)
        }}
        defaultChangeControl={changeControlRequired}
        defaultRecordId={recordId}
      />

      <RejectSCNModal
        open={openReject}
        onClose={() => setOpenReject(false)}
        onSubmit={(comment) => {
          setOpenReject(false);
          // You can add further logic here (e.g., API call, notification)
          console.log("Rejected with comment:", comment);
        }}
      />
    </>
  );
};

export default SCNInternalReviewImpactTab;
