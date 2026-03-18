import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  IconButton,
  CircularProgress,
  Box,
} from "@mui/material";
import CloseIcon from "../../../assets/icons/close.svg";
import styles from "./ChangeNotificationModal.module.scss";

interface Props {
  open: boolean;
  onClose: () => void;
  pdfUrl?: string | null;
}

const ChangeNotificationModal: React.FC<Props> = ({
  open,
  onClose,
  pdfUrl,
}) => {
  const [iframeLoading, setIframeLoading] = useState(true);

  const handleClose = () => {
    setIframeLoading(true);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ className: styles.paper }}
    >
      <IconButton className={styles.close} onClick={handleClose}>
        <img src={CloseIcon} alt="X" />
      </IconButton>

      <DialogContent className={styles.content}>
        {pdfUrl ? (
          <Box className={styles.pdfContainer}>
            {iframeLoading && (
              <Box className={styles.pdfLoader}>
                <CircularProgress size={36} sx={{ color: "#437ef7" }} />
              </Box>
            )}
            <iframe
              src={pdfUrl}
              title="PDF Preview"
              className={styles.pdfIframe}
              onLoad={() => setIframeLoading(false)}
              style={{ display: iframeLoading ? "none" : "block" }}
            />
          </Box>
        ) : (
          <Box className={styles.pdfNoUrl}>No PDF available for preview.</Box>
        )}

        {/* <div className={styles.topHeader}>
          <div>
            <div className={styles.company}>Pinnacle Laboratories</div>
            <div className={styles.department}>
              Quality & Regulatory Affairs
            </div>
          </div>
        </div>
        <div className={styles.title}>Change Notification</div>
    
        <div className={styles.meta}>
          <div>
            <b>Notice ID:</b> SCN-DOC-000001
          </div>
          <div>
            <b>Date:</b> 2024-10-11
          </div>
          <div>
            <b>First Shipment Date:</b> 2025-04-05
          </div>
          <div>
            <b>Impact Level:</b> High (mapped: High)
          </div>
        </div>

        <section className={styles.section}>
          <h3>Change Summary</h3>

          <p>
            <b>Change Type:</b> Raw Material
          </p>

          <p className={styles.bodyText}>
            This notification provides advance notice of a proposed change. The
            change is controlled under our quality system and will be
            implemented per the stated effective date, subject to customer
            disposition where applicable.
          </p>

          <p>
            <b>Reason for Change:</b> End-of-life replacement of legacy
            equipment/material.
          </p>
        </section>

    
        <section className={styles.section}>
          <h3>Affected Items</h3>
          <div className={styles.tableMain}>
            <div className={styles.tableTitle}>Affected Items</div>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Identifier</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Service</td>
                  <td>SRV-6803</td>
                  <td>Release testing support</td>
                </tr>
                <tr>
                  <td>Service</td>
                  <td>SRV-1313</td>
                  <td>Incoming inspection service</td>
                </tr>
                <tr>
                  <td>Material</td>
                  <td>MAT-524871</td>
                  <td>Polymer resin, lot controlled</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className={styles.section}>
          <h3>Impact Assessment</h3>
          <p>
            <b>Regulatory Impact Likelihood:</b> High
          </p>
          <p>
            <b>Risk Level (canonical):</b> High
          </p>
          <p>
            Fit/form/function: No change expected unless otherwise noted; impact
            under evaluation where applicable.
          </p>
          <p>
            Testing/qualification: Additional testing/qualification planned as
            required for the change classification.
          </p>
          <h3>Action Requested</h3>
          <p>
            <b>Action:</b> Approval
          </p>
          <p>
            Please acknowledge receipt of this notification. Where approval is
            required, provide disposition prior to the first shipment of
            post-change supply.
          </p>
          <h3>Attachments</h3>
        </section> */}
      </DialogContent>
    </Dialog>
  );
};

export default ChangeNotificationModal;
