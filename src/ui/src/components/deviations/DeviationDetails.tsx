import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Box, Grid } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./DeviationsResult.module.scss";
import InvestigationSummary from "./InvestigationSummary";
import RootCauseAnalysis from "./rca/RootCauseAnalysis";
import DeviationHeaderCard from "./DeviationsHeaderCard";
import {
  fetchDeviationDetailById,
  generateRCA,
} from "src/services/api.service";
import { DeviationDetail } from "src/types";

const DeviationDetails: React.FC = () => {
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [deviationData, setDeviationData] = useState<DeviationDetail | null>(
    null
  );
  const { deviationId } = useParams<{ deviationId: string | undefined }>();

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
      } catch (err: any) {
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
      <Grid container spacing={3} className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <InvestigationSummary summary={summary} setSummary={setSummary} />
        </Grid>
        <Grid item xs={12} md={7.1}>
          <RootCauseAnalysis />
        </Grid>
      </Grid>
    </Box>
  );
};

export default DeviationDetails;
