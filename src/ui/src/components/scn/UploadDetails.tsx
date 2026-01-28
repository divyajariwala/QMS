import React from "react";
import { useLocation } from "react-router-dom";
import { Box, Typography, Button, Stack, Grid } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import "./UploadDetails.scss";

const UploadDetails: React.FC = () => {
  const location = useLocation();
  const data = location.state || {};

  const breadcrumbItems = [
    { label: "Home", to: "/" },
    { label: "Supplier Portal", to: "/scn/supplier" },
    { label: "Upload SCN" },
  ];

  return (
    <Box className="upload-details">
      <Box sx={{ marginBottom: "24px" }}>
        <CommonBreadcrumbs items={breadcrumbItems} />
      </Box>
      <Typography
        variant="h5"
        gutterBottom
        sx={{
          fontWeight: 600,
          fontSize: 20,
          lineHeight: "28px",
          marginBottom: "24px",
        }}
      >
        Upload SCN
      </Typography>
      <Grid container spacing={3} sx={{ marginBottom: "32px" }}>
        <Grid item xs={12} sm={6}>
          <Typography className="form-label">SCN Title</Typography>
          <Typography className="form-value">{data.scnTitle || "-"}</Typography>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Typography className="form-label">
            Planned Implementation Date
          </Typography>
          <Typography className="form-value">
            {data.plannedImplementationDate || "-"}
          </Typography>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Typography className="form-label">Supplier Name</Typography>
          <Typography className="form-value">
            {data.supplierName || "-"}
          </Typography>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Typography className="form-label">File Name</Typography>
          <Typography className="form-value">{data.file || "-"}</Typography>
        </Grid>
        {/* Add more fields as needed, matching screenshot order */}
      </Grid>
      <Button
        variant="contained"
        href="/scn/supplier"
        sx={{
          background: "#437EF7",
          color: "#fff",
          fontWeight: 700,
          fontSize: 16,
          borderRadius: "6px",
          padding: "12px 65px",
          textTransform: "none",
          boxShadow: "none",
          "&:hover": {
            background: "#1d4ed8",
          },
        }}
      >
        Back to Portal
      </Button>
    </Box>
  );
};

export default UploadDetails;
