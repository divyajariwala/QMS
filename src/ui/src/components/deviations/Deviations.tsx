import React, { useState } from "react";
import { Box, Stack, Button } from "@mui/material";
import DeviationsResult from "./DeviationsResult";
import DeviationsFilter from "@components/deviations/DeviationsFilter";
import styles from "./Deviations.module.scss";
import { deviationsData } from "src/mockData/deviations";
import StatusTabs from "./StatusTabs";
import DeviationsStatusCard from "@components/commonCard/DeviationsStatusCard";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import { useAuth } from "react-oidc-context";
import FileUpload from "@components/FileUpload/FileUpload";
import { usePollingContext } from "@components/polling/PollingProvider";
import { useStatus } from "src/context/StatusProvider";

const Deviations = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [openFileUpload, setOpenFileUpload] = useState<boolean>(false);
  const { activeStatus, setActiveStatus } = useStatus();
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [searchActive, setSearchActive] = useState<boolean>(false);
  const [deviationId, setDeviationId] = useState("");
  const items = [{ label: "Home", to: "/" }, { label: "Deviations" }];
  const auth = useAuth();
  const displayName = `${auth?.user?.profile?.given_name ?? ""}`.trim();

  const { setShouldPoll, falseCount, error, done, shouldPoll } =
    usePollingContext();

  const handleFileUploadSuccess = async () => {
    setOpenFileUpload(false);
  };

  return (
    <Box component="main">
      <Stack direction="column" gap={1}>
        <CommonBreadcrumbs items={items} />
        <Stack
          direction="row"
          alignItems={"baseline"}
          justifyContent={"space-between"}
        >
          <Box className={styles.pageTitle}>
            Hey there, {displayName}!
            <Box className={styles.pageDetails}>
              Welcome to Deviations dashboard!
            </Box>
          </Box>
          <Stack className={styles.actions} direction="row" spacing={1}>
            <Button
              variant="contained"
              className={styles.primaryImportButton}
              onClick={() => {
                setOpenFileUpload(true);
                setActiveStatus("pending");
                setPageNumber(1);
                setSearchActive(false);
                setDeviationId("");
              }}
            >
              Import
            </Button>
          </Stack>
        </Stack>
        <div className={styles.statusCards}>
          {" "}
          <DeviationsStatusCard />
        </div>
        <div className={styles.statusTabs}>
          {" "}
          <StatusTabs
            activeIndex={activeIndex}
            setActiveIndex={setActiveIndex}
            pending={2}
            processed={2}
            overdue={2}
          />
        </div>
      </Stack>
      <DeviationsFilter />
      {deviationsData.map((deviation, index) => (
        <DeviationsResult key={index} deviation={deviation} />
      ))}
      <FileUpload
        setOpenFileUpload={setOpenFileUpload}
        onSuccess={handleFileUploadSuccess}
        setProcessing={setShouldPoll}
        open={openFileUpload}
        onClose={() => setOpenFileUpload(false)}
      />
    </Box>
  );
};

export default Deviations;
