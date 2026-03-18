import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Box, Stack, Button, TextField } from "@mui/material";
import CommonBreadcrumbs from "@components/commonBreadCrumbs/CommonBreadcrumbs";
import styles from "./SCNAddEmailDoc.module.scss";
import CheckIcon from "../../assets/icons/circle-checkmark.svg";
import filterIcon from "../../assets/icons/filter.svg";
import SearchIcon from "../../assets/icons/search.svg";
import AdverseEventIcon from "../../assets/icons/adverseEvent.svg";

const SCNAddEmailDoc: React.FC = () => {
  const { scnId } = useParams<{ scnId: string }>();
  const navigate = useNavigate();

  const [selectedMail, setSelectedMail] = useState<number>(0);

  const breadcrumbItems = [
    { label: "Home", to: "/" },
    { label: "SCN", to: "/scn/supplier" },
    { label: "Add Email Document" },
  ];

  const handleCreateSCN = () => {
    navigate("/scn/supplier");
  };

  return (
    <Box component="main" className={styles.container}>
      <Stack gap={2}>
        <CommonBreadcrumbs items={breadcrumbItems} />

        {/* Header */}
        <Stack
          direction="row"
          justifyContent="space-between"
          className={styles.headerSection}
        >
          <Box>
            <h1 className={styles.pageTitle}>Add Email Document</h1>
            <p className={styles.pageSubtitle}>
              Submit and track Supplier Change Notifications (SCNs)
            </p>
          </Box>

          <Button
            variant="contained"
            className={styles.createSCNButton}
            onClick={handleCreateSCN}
          >
            <img src={CheckIcon} className={styles.uploadIcon} />
            Create SCN Request
          </Button>
        </Stack>

        {/* Content */}
        <Box className={styles.contentWrapper}>
          {/* left – Mail List */}
          <Box className={styles.mailList}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              className={styles.mailHeader}
            >
              <span className={styles.mailHeaderTitle}>Mails (60)</span>
              <Button
                size="small"
                variant="outlined"
                className={styles.filterButton}
              >
                Filter
                <img src={filterIcon} alt="filter" />
              </Button>
            </Stack>

            <Box className={styles.mailListSub}>
              <div className={styles.searchBar}>
                <form
                  className={styles.inputWrapper}
                  onSubmit={(e) => e.preventDefault()}
                >
                  <img
                    src={SearchIcon}
                    alt="Search"
                    className={styles.searchIcon}
                  />
                  <input
                    type="search"
                    placeholder="Search here..."
                    aria-label="Search by SCN number"
                    className={styles.searchInput}
                  />
                  <button type="button" className={styles.searchButton}>
                    Search
                  </button>
                </form>
              </div>

              <Box className={styles.mailItems}>
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((item, index) => (
                  <Box
                    key={index}
                    className={`${styles.mailItem} ${
                      selectedMail === index ? styles.active : ""
                    }`}
                    onClick={() => setSelectedMail(index)}
                  >
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      className={styles.mailMeta}
                    >
                      <span>supplier@mail.com</span>
                      <span>5hrs ago</span>
                    </Stack>
                    <p className={styles.mailSubject}>
                      Subject - Lorem ipsum dolor sit amet, cons...
                    </p>
                    <span className={styles.mailTag}>
                      <img src={AdverseEventIcon} alt="" /> Tag - Lorem ipsum
                    </span>
                  </Box>
                ))}
              </Box>
            </Box>
          </Box>

          {/* right – Mail Content */}
          <Box className={styles.mailContent}>
            <span className={styles.mailDate}>28TH Jan 2026, 10:40 PM</span>

            <h2 className={styles.mailTitle}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </h2>

            <p className={styles.mailFrom}>From: supplier@mail.com</p>

            <Box className={styles.narrativeBox}>
              <h4>Narrative</h4>
              <p>
                Education:
                <br />
                Travenzil Pen Function: Dose Confirmation
                <br />
                <br />
                The patient can ensure that the dose was delivered by first
                observing the medication within the syringe prior to injection
                and visually confirming the medication is no longer in the
                syringe following the injection.
              </p>
            </Box>
          </Box>
        </Box>
      </Stack>
    </Box>
  );
};

export default SCNAddEmailDoc;
