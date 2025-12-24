import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { Box, Grid } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./DeviationsResult.module.scss";
import InvestigationSummary from "./InvestigationSummary";
import RootCauseAnalysis, {
  RootCauseAnalysisHandle,
} from "./rca/RootCauseAnalysis";
import DeviationHeaderCard from "./DeviationsHeaderCard";
import {
  fetchDeviationDetailById,
  generateRCA,
} from "src/services/api.service";
import { DeviationDetail } from "src/types";
import Notification from "@components/Notification/Notification";

const DeviationDetails: React.FC = () => {
  const [open, setOpen] = useState(false);
    const [type, setType] = useState<"success" | "error">("success");
    const [message, setMessage] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [rcaData, setRcaData] = useState<any[]>([]);
  const [deviationData, setDeviationData] = useState<DeviationDetail | null>(
    null
  );
  const [isRcaSubmitted, setIsRcaSubmitted] = useState<boolean>(false);
  const { deviationId } = useParams<{ deviationId: string | undefined }>();

  const rcaRef = useRef<RootCauseAnalysisHandle>(null);

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
        setSummary(data.investigation_summary);
        setDeviationData(data);
        const payload = {
          deviationId,
          investigation_summary: data.investigation_summary,
        };
        const rcaDetails = await generateRCA(payload);
        setRcaData(Array.isArray(rcaDetails?.data) ? rcaDetails.data : []);
      } catch (err: any) {
         setType("error");
         setMessage("Failed to generate RCA");
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
      {deviationData && (
        <DeviationHeaderCard
          deviationData={deviationData}
          onSubmit={() => rcaRef.current?.submit()}
          isRcaSubmitted={isRcaSubmitted}
        />
      )}
      <Grid container spacing={3} className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <InvestigationSummary summary={summary} setSummary={setSummary} />
        </Grid>
        <Grid item xs={12} md={7.1}>
          <RootCauseAnalysis
            ref={rcaRef}
            rcaData={rcaData}
            onSubmitSuccess={() => setIsRcaSubmitted(true)}
          />
        </Grid>
      </Grid>
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

export default DeviationDetails;
