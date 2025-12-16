import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box, Grid } from "@mui/material";
import ArrowRight from "../../assets/icons/arrowRight.svg";
// import { ComplaintDetail } from 'src/types';
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import { usePollingClassify } from "@components/polling/PollingClassify";
import styles from "./DeviationsResult.module.scss";
import DeviationInterHeaderCard from "./DeviationsInterHeaderCard";
import InvestigationSummary from "./InvestigationSummary";

const DeviationsIntermediate: React.FC = () => {
  const [open, setOpen] = useState(false);
  // const [summary, setSummary] = useState(
  //   "STM-QCS-0800, General Laboratory Practices, dictates that no duplicate testing shall be done without justification to invalidate the original results and that an analyst may not proceed to repeat an assay without supervisor approval. In this case, JS did not follow the procedure. JS was hired on 21OCT2024 and has trained on STM-QCS-0800"
  // );
  const [summary, setSummary] = useState<string>("");
  const [openModifyDetails, setOpenModifyDetails] = useState(false);
  const [headerData, setHeaderData] = useState<any>(null); // holds editable header fields
  const [processingFile, setProcessingFile] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const { deviationId } = useParams<{ deviationId: string | undefined }>();
  const navigate = useNavigate();
  const { done } = usePollingClassify(processingFile, deviationId);

  const items = [
    { label: "Home", to: "/" },
    { label: "Deviations", to: "/deviations" },
    { label: deviationId?.toString() ?? "" },
  ];

  if (loading) return <p>Loading details...</p>;

  return (
    <Box className={styles.rootBox}>
      <CommonBreadcrumbs items={items} />
      <DeviationInterHeaderCard
        deviationData={headerData}
        caseStatus={"pending"}
        // caseStatus={complaintDetails?.caseStatus}
        createdAt={"2025-12-10T08:06:31.555512"}
        // createdAt={complaintDetails?.created_at}
        processingFile={processingFile}
        deviationId={deviationId}
      />
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
                // onClick={testClassify}
                disabled={summary.length === 0}
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
