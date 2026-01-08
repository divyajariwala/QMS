import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Box, Grid } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./DeviationsResult.module.scss";
import { fetchDeviationDetailById } from "src/services/api.service";
import { DeviationDetail } from "src/types";
import Notification from "@components/Notification/Notification";
import Grading from "./grading/Grading";
import DeviationHeaderCard from "./DeviationsHeaderCard";

const GradingDetails: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<"success" | "error">("success");
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [deviationData, setDeviationData] = useState<DeviationDetail | null>(
    null
  );
  const { deviationId } = useParams<{ deviationId: string | undefined }>();

  const handleShowNotification = () => {
    setOpen(true);
  };
  const handleCloseNotification = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") {
      return;
    }
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

  if (loading) return <p>Loading details...</p>;
  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />
      {deviationData && <DeviationHeaderCard deviationData={deviationData} />}
      <Box className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <Grading />
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
