import React, { useState } from "react";
import {
  Box,
  Grid,
  IconButton,
  Paper,
  Stack,
  Select,
  MenuItem,
  TextField,
  Typography,
} from "@mui/material";
import EditIcon from "../../assets/icons/pencil.svg";
import CloseIcon from "../../assets/icons/closeCross.svg";
import CheckIcon from "../../assets/icons/greenTick.svg";
import styles from "./ComplaintCategory.module.scss";
import { ComplaintCategoryProps, ComplaintCategoryItem } from "src/types";

const ComplaintCategory: React.FC<ComplaintCategoryProps> = ({
  complaintCategories,
  setComplaintCategories,
  caseStatus,
  crlList,
  labelList
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editedData, setEditedData] = useState<ComplaintCategoryItem | null>(null);

  const handleStartEdit = (item: ComplaintCategoryItem) => {
    setEditingId(item.id);
    setEditedData({ ...item });
  };

  const handleConfirmEdit = () => {
    if (editedData) {
      const updatedCategories = complaintCategories.map((cat) =>
        cat.id === editedData.id ? editedData : cat
      );
      setComplaintCategories(updatedCategories);
    }
    setEditingId(null);
    setEditedData(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditedData(null);
  };

  const handleEditChange = (
    field: keyof ComplaintCategoryItem,
    value: string | number
  ) => {
    if (!editedData) return;
    setEditedData((prev) => (prev ? { ...prev, [field]: value } : null));
  };

  const getPercentageClass = (percentage: number): string => {
    if (percentage >= 70) {
      return styles.percentageGreen;
    } else if (percentage >= 40) {
      return styles.percentageOrange;
    } else {
      return styles.percentageRed;
    }
  };

  return (
    <Paper variant="outlined" className={styles.rootPaper}>
      <Stack direction="row" alignItems="center" spacing={1} className={styles.headerStack}>
        <Box className={styles.headerTitle}>Complaint Category</Box>
      </Stack>
      <Box className={styles.subtitleBox}>Please review and modify.</Box>

      {complaintCategories?.map((item) => {
        const isEditing = editingId === item.id;

        if (isEditing && editedData) {
          return (
            <Paper key={item.id} className={styles.editModePaper} elevation={0}>
              {/* Top row: label select + percentage badge */}
              <Stack direction="row" justifyContent="flex-start" alignItems="center" sx={{ mb: 2 }}>
                <Select
                  size="small"
                  value={editedData.label || ""}
                  onChange={(e) => handleEditChange("label", e.target.value)}
                  className={styles.selectMinSize}
                  classes={{ root: styles.editSelectRoot }}
                >
                  {labelList?.map((opt, index) => (
                      <MenuItem key={index} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                </Select>

                <Box className={`${styles.percentageBox} ${getPercentageClass(editedData.percentage)}`}>
                  {Math.round(editedData.percentage)}%
                </Box>
              </Stack>

              {/* Fields grid */}
              <Grid container spacing={2} alignItems="center" className={styles.editGrid}>
                <Grid item xs>
                  <Typography className={styles.editLabel}>Level</Typography>
                  <TextField
                    size="small"
                    type="number"
                    value={editedData.level}
                    onChange={(e) => handleEditChange("level", Number(e.target.value))}
                    fullWidth
                    InputProps={{ classes: { input: styles.inputBaseInput }, inputProps: { min: 1, max: 3 } }}
                    variant="outlined"
                    className={styles.editField}
                  />
                </Grid>

                <Grid item xs>
                  <Typography className={styles.editLabel}>CRL</Typography>
                  <Select
                    size="small"
                    value={editedData.crl}
                    onChange={(e) => handleEditChange("crl", e.target.value)}
                    fullWidth
                    className={styles.editSelectRoot}
                    variant="outlined"
                  >
                    {/* Replace this with your real CRL options */}
                    {crlList?.map((opt, index) => (
                      <MenuItem key={index} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                  </Select>
                </Grid>

                <Grid item xs>
                  <Typography className={styles.editLabel}>Priority</Typography>
                  <Select
                    size="small"
                    value={editedData.priority}
                    onChange={(e) => handleEditChange("priority", e.target.value)}
                    fullWidth
                    className={styles.editSelectRoot}
                    variant="outlined"
                  >
                    <MenuItem value="High">High</MenuItem>
                    <MenuItem value="Medium">Medium</MenuItem>
                    <MenuItem value="Low">Low</MenuItem>
                  </Select>
                </Grid>

                <Grid item xs>
                  <Typography className={styles.editLabel}>Unit</Typography>
                  <TextField
                    size="small"
                    type="number"
                    value={editedData.unit}
                    onChange={(e) => handleEditChange("unit", Number(e.target.value))}
                    fullWidth
                    InputProps={{ classes: { input: styles.inputBaseInput }, inputProps: { min: 0 } }}
                    variant="outlined"
                    className={styles.editField}
                  />
                </Grid>
              </Grid>

              {/* Buttons row */}
              <Grid container justifyContent="flex-end" mt={2} mr={2} spacing={1} className={styles.buttonsRow}>
                <Grid item>
                  <IconButton
                    size="small"
                    aria-label="cancel edit"
                    onClick={handleCancelEdit}
                    className={styles.cancelButton}
                  >
                    <img src={CloseIcon} alt="Cancel" />
                  </IconButton>
                </Grid>
                <Grid item>
                  <IconButton
                    size="small"
                    aria-label="confirm edit"
                    onClick={handleConfirmEdit}
                    className={styles.confirmButton}
                  >
                    <img src={CheckIcon} alt="Confirm" />
                  </IconButton>
                </Grid>
              </Grid>
            </Paper>
          );
        }

        /* Non-edit mode */
        return (
          <Paper key={item.id} variant="outlined" className={styles.nonEditPaper}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography className={styles.nonEditLabel}>{item.label}</Typography>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Box className={`${styles.percentageBox} ${getPercentageClass(item.percentage)}`}>
                  {Math.round(item.percentage)}%
                </Box>
                {(caseStatus === "pending" || caseStatus === "overdue") && <IconButton
                  aria-label={`edit ${item.label}`}
                  size="small"
                  onClick={() => handleStartEdit(item)}
                  className={styles.editIconButton}
                >
                  <img src={EditIcon} alt="Edit Icon" />
                </IconButton>}
              </Stack>
            </Stack>

            <Grid container spacing={2} alignItems="center" className={styles.nonEditGrid}>
              <Grid item xs={2}>
                <Typography className={styles.nonEditFieldLabel}>Level</Typography>
                <Typography className={styles.nonEditFieldValue}>{item.level}</Typography>
              </Grid>

              <Grid item xs={4}>
                <Typography className={styles.nonEditFieldLabel}>CRL</Typography>
                <Typography className={styles.nonEditFieldValueBold}>{item.crl}</Typography>
              </Grid>

              <Grid item xs={2}>
                <Typography className={styles.nonEditFieldLabel}>Priority</Typography>
                <Typography className={styles.nonEditFieldValue}>{item.priority}</Typography>
              </Grid>

              <Grid item xs={2}>
                <Typography className={styles.nonEditFieldLabel}>Unit</Typography>
                <Typography className={styles.nonEditFieldValue}>{item.unit}</Typography>
              </Grid>
            </Grid>
          </Paper>
        );
      })}
    </Paper>
  );
};

export default ComplaintCategory;