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
} from "@mui/material";
import EditIcon from "../../assets/icons/edit.svg";

import styles from "./ComplaintCategory.module.scss";

interface ComplaintCategoryItem {
  id: string;
  label: string;
  level: number;
  crl: string;
  priority: string;
  unit: number;
  percentage: number;
  color: string;
  bgColor: string;
}



interface ComplaintCategoryProps {
  complaintCategories: ComplaintCategoryItem[];
  onSave?: (updatedItem: ComplaintCategoryItem) => void;
}

const ComplaintCategory: React.FC<ComplaintCategoryProps> = ({
  complaintCategories,
  onSave,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editedData, setEditedData] = useState<ComplaintCategoryItem | null>(null);

  const handleEditIconClick = (item: ComplaintCategoryItem) => {
    if (editingId === item.id) {
      if (editedData && onSave) onSave(editedData);
      setEditingId(null);
      setEditedData(null);
    } else {
      setEditingId(item.id);
      setEditedData({ ...item });
    }
  };

  const handleEditChange = (
    field: keyof ComplaintCategoryItem,
    value: string | number
  ) => {
    if (!editedData) return;
    setEditedData((prev) => (prev ? { ...prev, [field]: value } : null));
  };

  const colorClassMap: Record<string, string> = {
  "#43a047": styles.green,
  "#f57c00": styles.orange,
  "#e53935": styles.red,
};

  function getColorClassName(color: string): string {
     const normalizedColor = color.trim().toLowerCase();
    return colorClassMap[normalizedColor] || "";
  }

  return (
    <Paper variant="outlined" className={styles.rootPaper}>
      <Stack direction="row" alignItems="center" spacing={1} className={styles.headerStack}>
        <Box className={styles.headerTitle}>Complaint Category</Box>
      </Stack>

      <Box className={styles.subtitleBox}>Please review and modify.</Box>

      {complaintCategories.map((item) => {
        console.log(item.color)
        const isEditing = editingId === item.id;

        return (
          <Paper key={item.id} variant="outlined" className={styles.itemPaper}>
            {/* Static info */}
            <Box className={styles.itemTopBox}>
              <Box className={styles.labelBox}>{item.label}</Box>

              <Box className={styles.inlineFlexCenter}>
                <Box className={`${styles.percentageBox} ${getColorClassName(item.color)}`}>
                  {item.percentage}%
                </Box>

                <IconButton
                  aria-label={isEditing ? `save ${item.label}` : `edit ${item.label}`}
                  size="small"
                  className={styles.iconButton}
                  onClick={() => handleEditIconClick(item)}
                >
                  <img src={EditIcon} alt="Edit Icon" />
                </IconButton>
              </Box>
            </Box>

            <Grid
              container
              spacing={1}
              alignItems="center"
              className={isEditing ? styles.infoGrid : styles.infoGridNoMargin}
            >
              <Grid item xs={2}>
                <Box className={styles.infoGridItemLabel}>Level</Box>
                <Box className={styles.infoGridItemValue}>{item.level}</Box>
              </Grid>
              <Grid item xs={4}>
                <Box className={styles.infoGridItemLabel}>CRL</Box>
                <Box className={styles.infoGridItemValue}>{item.crl}</Box>
              </Grid>
              <Grid item xs={2}>
                <Box className={styles.infoGridItemLabel}>Priority</Box>
                <Box className={styles.infoGridItemValue}>{item.priority}</Box>
              </Grid>
              <Grid item xs={2}>
                <Box className={styles.infoGridItemLabel}>Unit</Box>
                <Box className={styles.infoGridItemValue}>{item.unit}</Box>
              </Grid>
            </Grid>

            {isEditing && editedData && (
              <>
                <Box className={styles.editingControlsBox}>
                  <Select
                    size="small"
                    value={editedData.label || ""}
                    onChange={(e) => handleEditChange("label", e.target.value)}
                    className={styles.selectMinSize}
                    classes={{ root: styles.editSelectRoot }}
                  >
                    {complaintCategories.map((opt) => (
                      <MenuItem key={opt.id} value={opt.label}>
                        {opt.label}
                      </MenuItem>
                    ))}
                  </Select>

                  <Box className={`${styles.percentageBox} ${getColorClassName(item.color)}`}>
                    {item.percentage}%
                  </Box>
                </Box>

                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={2}>
                    <Box className={styles.infoGridItemLabel}>Level</Box>
                    <TextField
                      size="small"
                      type="number"
                      value={editedData.level}
                      onChange={(e) => handleEditChange("level", Number(e.target.value))}
                      fullWidth
                      InputProps={{
                        classes: { input: styles.inputBaseInput },
                      }}
                    />
                  </Grid>

                  <Grid item xs={4}>
                    <Box className={styles.infoGridItemLabel}>CRL</Box>
                    <TextField
                      size="small"
                      value={editedData.crl}
                      onChange={(e) => handleEditChange("crl", e.target.value)}
                      fullWidth
                      InputProps={{
                        classes: { input: styles.inputBaseInput },
                      }}
                    />
                  </Grid>

                  <Grid item xs={2}>
                    <Box className={styles.infoGridItemLabel}>Priority</Box>
                    <Select
                      size="small"
                      value={editedData.priority}
                      onChange={(e) => handleEditChange("priority", e.target.value)}
                      fullWidth
                      className={styles.editSelectRoot}
                    >
                      <MenuItem value="High">High</MenuItem>
                      <MenuItem value="Medium">Medium</MenuItem>
                      <MenuItem value="Low">Low</MenuItem>
                    </Select>
                  </Grid>

                  <Grid item xs={2}>
                    <Box className={styles.infoGridItemLabel}>Unit</Box>
                    <TextField
                      size="small"
                      type="number"
                      value={editedData.unit}
                      onChange={(e) => handleEditChange("unit", Number(e.target.value))}
                      fullWidth
                      InputProps={{
                        classes: { input: styles.inputBaseInput },
                      }}
                    />
                  </Grid>
                </Grid>
              </>
            )}
          </Paper>
        );
      })}
    </Paper>
  );
};

export default ComplaintCategory;