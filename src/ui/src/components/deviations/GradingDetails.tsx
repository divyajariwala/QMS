import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box, Grid } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./DeviationsResult.module.scss";
import { fetchDeviationDetailById } from "src/services/api.service";
import { DeviationDetail } from "src/types";
import Notification from "@components/Notification/Notification";
import Grading from "./grading/Grading";
import GradingHeaderCard from "./GradingHeaderCard";

const GradingDetails: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<"success" | "error">("success");
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [deviationData, setDeviationData] = useState<DeviationDetail | null>(
    null
  );
  const [uiStatus, setUiStatus] = useState<GradingUiStatus>("pending");
  const navigate = useNavigate();
  const { deviationId } = useParams<{ deviationId: string | undefined }>();
  type GradingUiStatus = "pending" | "in_review" | "processed";

  const handleShowNotification = () => setOpen(true);
  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") return;
    setOpen(false);
  };

  const items = [
    { label: "Home", to: "/" },
    { label: "Deviations", to: "/deviations" },
    { label: deviationId?.toString() ?? "" },
  ];

  useEffect(() => {
    async function init() {
      setLoading(true);
      try {
        const data = await fetchDeviationDetailById(deviationId);
        setDeviationData(data);
        setUiStatus("pending");
      } catch (err: any) {
        setType("error");
        setMessage("Failed to start grading");
        handleShowNotification();
        console.log(err.message || "Failed to initialize deviation details.");
      } finally {
        setLoading(false);
      }
    }
    if (deviationId) init();
  }, [deviationId]);

  const handleBackToDeviations = () => {
    navigate("/deviations");
  };

  if (loading) return <p>Loading details...</p>;
  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />
      {deviationData && (
        <GradingHeaderCard
          deviationData={deviationData}
          status={uiStatus}
          onBack={uiStatus === "processed" ? handleBackToDeviations : undefined}
        />
      )}
      <Box className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <Grading
            onEnterReview={() => setUiStatus("in_review")}
            onProcessed={() => setUiStatus("processed")}
          />
        </Grid>
      </Box>
      <Notification
        open={open}
        onClose={handleCloseNotification}
        position="top"
        type={type}
        message={message}
      />
    </Box>
  );
};

export default GradingDetails;
