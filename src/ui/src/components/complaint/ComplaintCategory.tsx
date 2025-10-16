import React, { useState } from 'react';
import {
  Box,
  Grid,
  IconButton,
  Paper,
  Stack,
  Typography,
  Select,
  MenuItem,
  TextField,
} from '@mui/material';
import EditIcon from "../../assets/icons/edit.svg";

interface ComplaintCategoryItem {
  id: string; // Unique ID
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
  const [editedData, setEditedData] = useState<ComplaintCategoryItem | null>(
    null
  );

  const handleEditIconClick = (item: ComplaintCategoryItem) => {
    if (editingId === item.id) {
      // Save current edited data and exit edit mode
      if (editedData && onSave) onSave(editedData);
      setEditingId(null);
      setEditedData(null);
    } else {
      // Enter edit mode for this item
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

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, height: "100%" }}>
      <Stack direction="row" alignItems="center" spacing={1} mb={1}>
        <Typography
          sx={{
            fontFamily: "Roboto, sans-serif",
            fontWeight: 600,
            fontSize: 18,
            lineHeight: 1,
            letterSpacing: "0.04em",
            verticalAlign: "bottom",
            color: "#000000",
          }}
        >
          Complaint Category
        </Typography>
      </Stack>

      <Typography
        sx={{
          fontFamily: "Inter, sans-serif",
          fontWeight: 400,
          fontSize: 14,
          lineHeight: "24px",
          letterSpacing: "-0.1px",
          color: "#5F6D7E",
          mb: 2,
        }}
      >
        Please review and modify.
      </Typography>

      {complaintCategories.map((item) => {
        const isEditing = editingId === item.id;

        return (
          <Paper
            key={item.id}
            variant="outlined"
            sx={{ p: 2, mb: 2, borderRadius: 1 }}
          >
            {/* Static info (always visible) */}
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 1,
              }}
            >
              <Typography
                sx={{
                  fontFamily: "Inter, sans-serif",
                  fontWeight: 500,
                  fontSize: 15,
                  lineHeight: "22px",
                  letterSpacing: "-0.1px",
                  color: "#272D37",
                }}
              >
                {item.label}
              </Typography>
              <Box sx={{ display: "inline-flex", alignItems: "center", gap: 0.5 }}>
                <Typography
                  sx={{
                    color: item.color,
                    fontWeight: 600,
                    fontSize: 14,
                    mr: 2,
                  }}
                >
                  {item.percentage}%
                </Typography>
                <IconButton
                  aria-label={isEditing ? `save ${item.label}` : `edit ${item.label}`}
                  size="small"
                  sx={{ padding: 0, color: "inherit" }}
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
              sx={{ fontSize: 13, mb: isEditing ? 2 : 0 }}
            >
              <Grid item xs={2}>
                <Typography
                  sx={{
                    fontFamily: "Inter, sans-serif",
                    fontWeight: 500,
                    fontSize: 14,
                    lineHeight: "20px",
                    letterSpacing: "-0.1px",
                    color: "#5F6D7E",
                  }}
                >
                  Level
                </Typography>
                <Typography sx={{ fontWeight: 600, fontSize: 15 }}>
                  {item.level}
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography
                  sx={{
                    fontFamily: "Inter, sans-serif",
                    fontWeight: 500,
                    fontSize: 14,
                    lineHeight: "20px",
                    letterSpacing: "-0.1px",
                    color: "#5F6D7E",
                  }}
                >
                  CRL
                </Typography>
                <Typography sx={{ fontWeight: 600, fontSize: 15 }}>
                  {item.crl}
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography
                  sx={{
                    fontFamily: "Inter, sans-serif",
                    fontWeight: 500,
                    fontSize: 14,
                    lineHeight: "20px",
                    letterSpacing: "-0.1px",
                    color: "#5F6D7E",
                  }}
                >
                  Priority
                </Typography>
                <Typography sx={{ fontWeight: 600, fontSize: 15 }}>
                  {item.priority}
                </Typography>
              </Grid>
              <Grid item xs={2}>
                <Typography
                  sx={{
                    fontFamily: "Inter, sans-serif",
                    fontWeight: 500,
                    fontSize: 14,
                    lineHeight: "20px",
                    letterSpacing: "-0.1px",
                    color: "#5F6D7E",
                  }}
                >
                  Unit
                </Typography>
                <Typography sx={{ fontWeight: 600, fontSize: 15 }}>
                  {item.unit}
                </Typography>
              </Grid>
            </Grid>

            {/* Editable fields (only visible when editing) */}
            {isEditing && editedData && (
              <>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                    mt: 6,
                  }}
                >
                  {/* Editable dropdown for label */}
                  <Select
                    size="small"
                    value={editedData?.label || ""}
                    onChange={(e) => handleEditChange("label", e.target.value)}
                    sx={{ minWidth: 289, minHeight: 40 }}
                  >
                    {complaintCategories.map((opt) => (
                      <MenuItem key={opt.id} value={opt.label}>
                        {opt.label}
                      </MenuItem>
                    ))}
                  </Select>

                  {/* Show percentage */}
                  <Typography
                    sx={{ color: item.color, fontWeight: 600, fontSize: 14, mr: 2 }}
                  >
                    {item.percentage}%
                  </Typography>
                </Box>

                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={2}>
                    <Typography
                      sx={{
                        fontFamily: "Inter, sans-serif",
                        fontWeight: 500,
                        fontSize: 14,
                        lineHeight: "20px",
                        letterSpacing: "-0.1px",
                        color: "#5F6D7E",
                      }}
                    >
                      Level
                    </Typography>
                    <TextField
                      size="small"
                      type="number"
                      value={editedData.level}
                      onChange={(e) => handleEditChange("level", Number(e.target.value))}
                      fullWidth
                      sx={{
                        "& .MuiInputBase-input": {
                          fontFamily: "Inter, sans-serif",
                          fontWeight: 600,
                          fontSize: "15px",
                          lineHeight: "22px",
                          letterSpacing: "-0.1px",
                        },
                      }}
                    />
                  </Grid>

                  <Grid item xs={4}>
                    <Typography
                      sx={{
                        fontFamily: "Inter, sans-serif",
                        fontWeight: 500,
                        fontSize: 14,
                        lineHeight: "20px",
                        letterSpacing: "-0.1px",
                        color: "#5F6D7E",
                      }}
                    >
                      CRL
                    </Typography>
                    <TextField
                      size="small"
                      value={editedData.crl}
                      onChange={(e) => handleEditChange("crl", e.target.value)}
                      fullWidth
                      sx={{
                        "& .MuiInputBase-input": {
                          fontFamily: "Inter, sans-serif",
                          fontWeight: 600,
                          fontSize: "15px",
                          lineHeight: "22px",
                          letterSpacing: "-0.1px",
                        },
                      }}
                    />
                  </Grid>

                  <Grid item xs={2}>
                    <Typography
                      sx={{
                        fontFamily: "Inter, sans-serif",
                        fontWeight: 500,
                        fontSize: 14,
                        lineHeight: "20px",
                        letterSpacing: "-0.1px",
                        color: "#5F6D7E",
                      }}
                    >
                      Priority
                    </Typography>
                    <Select
                      size="small"
                      value={editedData.priority}
                      onChange={(e) => handleEditChange("priority", e.target.value)}
                      fullWidth
                      sx={{
                        fontFamily: "Inter, sans-serif",
                        fontWeight: 600,
                        fontSize: 15,
                        lineHeight: "22px",
                        letterSpacing: "-0.1px",
                      }}
                    >
                      <MenuItem value="High">High</MenuItem>
                      <MenuItem value="Medium">Medium</MenuItem>
                      <MenuItem value="Low">Low</MenuItem>
                    </Select>
                  </Grid>

                  <Grid item xs={2}>
                    <Typography
                      sx={{
                        fontFamily: "Inter, sans-serif",
                        fontWeight: 500,
                        fontSize: 14,
                        lineHeight: "20px",
                        letterSpacing: "-0.1px",
                        color: "#5F6D7E",
                      }}
                    >
                      Unit
                    </Typography>
                    <TextField
                      size="small"
                      type="number"
                      value={editedData.unit}
                      onChange={(e) => handleEditChange("unit", Number(e.target.value))}
                      fullWidth
                      sx={{
                        "& .MuiInputBase-input": {
                          fontFamily: "Inter, sans-serif",
                          fontWeight: 600,
                          fontSize: "15px",
                          lineHeight: "22px",
                          letterSpacing: "-0.1px",
                        },
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