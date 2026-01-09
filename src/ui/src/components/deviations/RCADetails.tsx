import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { Box, Grid } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./DeviationsResult.module.scss";
import InvestigationSummary from "./InvestigationSummary";
import RootCauseAnalysis, {
  RootCauseAnalysisHandle,
} from "./rca/RootCauseAnalysis";
import RCAHeaderCard from "./RCAHeaderCard";
import {
  fetchDeviationDetailById,
  generateRCA as generateRCAApi, 
} from "src/services/api.service";
import { DeviationDetail } from "src/types";
import Notification from "@components/Notification/Notification";
import ArrowRight from "../../assets/icons/arrowRight.svg";

const RCADetails: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<"success" | "error">("success");
  const [message, setMessage] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [rcaData, setRcaData] = useState<any[]>([]);
  const [isGeneratingRCA, setIsGeneratingRCA] = useState<boolean>(false);
  const [deviationData, setDeviationData] = useState<DeviationDetail | null>(
    null
  );
  const [isRcaSubmitted, setIsRcaSubmitted] = useState<boolean>(false);
  const { deviationId } = useParams<{ deviationId: string | undefined }>();

  const rcaRef = useRef<RootCauseAnalysisHandle>(null);

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
      if (!deviationId) return;
      setLoading(true);
      try {
        const data = await fetchDeviationDetailById(deviationId);
        setSummary(data.investigation_summary);
        setDeviationData(data);
      } catch (err: any) {
        setType("error");
        setMessage("Failed to load deviation details");
        handleShowNotification();
        console.log(err?.message || "Failed to initialize deviation details.");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [deviationId]);

  useEffect(() => {
    if (isRcaSubmitted && deviationId) {
      fetchDeviationDetailById(deviationId)
        .then((data) => setDeviationData(data))
        .catch((err) => {
          console.error(
            "Failed to refresh deviation details after RCA submission:",
            err
          );
        });
    }
  }, [isRcaSubmitted, deviationId]);

  const handleGenerateRCA = async () => {
    if (!deviationId) return;
    setIsGeneratingRCA(true);
    try {
      const payload = {
        deviationId,
        investigation_summary: summary,
      };
      const rcaDetails = await generateRCAApi(payload);
      const prepared = Array.isArray(rcaDetails?.data) ? rcaDetails.data : [];
      setRcaData(prepared);

      setType("success");
      setMessage("RCA generated successfully");
      handleShowNotification();
    } catch (err: any) {
      setType("error");
      setMessage("Failed to generate RCA");
      handleShowNotification();
      console.error(err?.message || "generateRCA failed");
    } finally {
      setIsGeneratingRCA(false);
    }
  };

  if (loading) return <p>Loading details...</p>;

  const hasRCA = rcaData?.length > 0;

  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />

      {deviationData && (
        <RCAHeaderCard
          deviationData={deviationData}
          onSubmit={() => rcaRef.current?.submit()}
          isRcaSubmitted={isRcaSubmitted}
          hasRCA={hasRCA}
        />
      )}

      <Grid container spacing={3} className={styles.gridWithMarginTop} mt={1}>
        <Grid item xs={12} md={4.9}>
          <InvestigationSummary summary={summary} setSummary={setSummary} />
        </Grid>

        <Grid item xs={12} md={7.1}>
          {hasRCA ? (
            <RootCauseAnalysis
              ref={rcaRef}
              rcaData={rcaData}
              onSubmitSuccess={() => setIsRcaSubmitted(true)}
            />
          ) : (
            <div className={styles.cardBox}>
              <div className={styles.cardTitle}>Root Cause Analysis</div>
              <div className={styles.emptyCategory}>
                <p className={styles.emptyCategoryText}>
                  No root cause analysis has been created. Click Generate RCA to
                  create one.
                </p>
                <button
                  className={styles.classifyBtn}
                  disabled={isGeneratingRCA || !(summary?.trim().length > 0)}
                  onClick={handleGenerateRCA}
                  aria-busy={isGeneratingRCA}
                >
                  {isGeneratingRCA ? "Generating ..." : "Generate RCA"}{" "}
                  <img src={ArrowRight} alt="" />
                </button>
              </div>
            </div>
          )}
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

export default RCADetails;
