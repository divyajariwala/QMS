import React from "react";
import { Box, Typography } from "@mui/material";
import styles from "./ComplaintSecondaryInfo.module.scss";

interface InfoItemProps {
  label: string;
  iconSrc: string;
  iconAlt: string;
  value: string | React.ReactNode;
}

const InfoItem: React.FC<InfoItemProps> = ({ label, iconSrc, iconAlt, value }) => (
  <div className={styles.infoItem}>
    <Typography component="p" className={styles.infoItem__label}>
      {label}
    </Typography>
    <div className={styles.infoItem__valueRow}>
      <img src={iconSrc} alt={iconAlt} />
      {typeof value === "string" ? (
        <Typography component="p" className={styles.infoItem__valueText}>
          {value}
        </Typography>
      ) : (
        value
      )}
    </div>
  </div>
);

interface InfoChipProps {
  iconSrc: string;
  iconAlt: string;
  label: string;
  className?: string;
}

const InfoChip: React.FC<InfoChipProps> = ({ iconSrc, iconAlt, label, className }) => (
  <div className={`${styles.infoChip} ${className ?? ""}`.trim()}>
    <img src={iconSrc} alt={iconAlt} />
    <Typography component="p" className={styles.infoChip__label}>
      {label}
    </Typography>
  </div>
);

interface SecondaryInfoCardProps {
  infoItems: Array<{
    label: string;
    iconSrc: string;
    iconAlt: string;
    value: string | React.ReactNode;
  }>;
  productComplaintIconSrc: string;
  adverseEventIconSrc: string;
  productComplaintsChipClassName?: string;
  adverseEventChipClassName?: string;
}

const ComplaintSecondaryInfo: React.FC<SecondaryInfoCardProps> = ({
  infoItems,
  productComplaintIconSrc,
  adverseEventIconSrc,
  productComplaintsChipClassName,
  adverseEventChipClassName,
}) => {
  return (
    <Box className={styles.complaintSecondaryInfo}>
      <div className={styles.complaintSecondaryInfo__row}>
        {infoItems.map(({ label, iconSrc, iconAlt, value }) => (
          <InfoItem
            key={label}
            label={label}
            iconSrc={iconSrc}
            iconAlt={iconAlt}
            value={value}
          />
        ))}
        <div className={styles.caseType}>
          <Typography component="p" className={styles.infoItem__label}>
            Case Type
          </Typography>
          <div className={styles.caseType__row}>
            <InfoChip
              iconSrc={productComplaintIconSrc}
              iconAlt="Product Complaint"
              label="Product Complaint"
              className={productComplaintsChipClassName}
            />
            <InfoChip
              iconSrc={adverseEventIconSrc}
              iconAlt="Adverse Event"
              label="Adverse Event"
              className={adverseEventChipClassName}
            />
          </div>
        </div>
      </div>
    </Box>
  );
};

export default ComplaintSecondaryInfo;