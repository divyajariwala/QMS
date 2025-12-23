import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box, Grid } from "@mui/material";
import ArrowRight from "../../assets/icons/arrowRight.svg";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./DeviationsResult.module.scss";
import DeviationInterHeaderCard from "./DeviationsInterHeaderCard";
import InvestigationSummary from "./InvestigationSummary";
import { fetchDeviationDetailById } from "src/services/api.service";
import { DeviationDetail } from "src/types";

const DeviationsIntermediate: React.FC = () => {
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [deviationData, setDeviationData] = useState<DeviationDetail | null>(null)
  const { deviationId } = useParams<{ deviationId: string | undefined }>();
  const navigate = useNavigate();

  const items = [
    { label: "Home", to: "/" },
    { label: "Deviations", to: "/deviations" },
    { label: deviationId?.toString() ?? "" },
  ];

  const generateRCA = () => {
    navigate(`/approveDeviations/${deviationId}`);
  };

  async function fetchData() {
    setLoading(true);
    try {
      const data = await fetchDeviationDetailById(deviationId);
      setSummary(data.investigation_summary)
      setDeviationData(data);
    } catch (err: any) {
      console.log(err.message || "Failed to load complaint details.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <p>Loading details...</p>;

  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />
      {deviationData && (
        <DeviationInterHeaderCard deviationData={deviationData} />
      )}
      <Grid container spacing={3} className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <InvestigationSummary summary={summary} setSummary={setSummary} />
        </Grid>
        <Grid item xs={12} md={7.1}>
          <div className={styles.cardBox}>
            <div className={styles.cardTitle}>Root Cause Analysis</div>
            <div className={styles.emptyCategory}>
              <p className={styles.emptyCategoryText}>
                No root cause analysis has been created. Click Generate to
                create one.
              </p>
              <button
                className={styles.classifyBtn}
                disabled={!(summary?.trim().length > 0)}
                onClick={generateRCA}
              >
                Generate RCA <img src={ArrowRight} alt="" />
              </button>
            </div>
          </div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DeviationsIntermediate;
