import React from 'react';
import { Box, Stack, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';

interface InfoItemProps {
  label: string;
  iconSrc: string;
  iconAlt: string;
  value: string | React.ReactNode;
}

const labelTypographySx = {
  fontFamily: "Inter",
  fontWeight: 500,
  fontSize: "14px",
  lineHeight: "20px",
  letterSpacing: "-0.1px",
  color: "#5F6D7E",
};

const valueTypographySx = {
  fontFamily: "Inter",
  fontWeight: 600,
  fontSize: "16px",
  lineHeight: "22px",
  letterSpacing: "-0.1px",
  color: "#272D37",
};

const InfoItem: React.FC<InfoItemProps> = ({ label, iconSrc, iconAlt, value }) => (
  <Stack direction="column" gap={0.75}>
    <Typography variant="subtitle1" sx={labelTypographySx}>
      {label}
    </Typography>
    <Stack direction="row" gap={0.5} alignItems="center">
      <img src={iconSrc} alt={iconAlt} />
      {typeof value === "string" ? (
        <Typography variant="body1" sx={valueTypographySx}>
          {value}
        </Typography>
      ) : (
        value
      )}
    </Stack>
  </Stack>
);

interface InfoChipProps {
  iconSrc: string;
  iconAlt: string;
  label: string;
  className?: string;
}

const InfoChip: React.FC<InfoChipProps> = ({ iconSrc, iconAlt, label, className }) => (
  <Stack direction="row" gap={0.5} className={className}>
    <img src={iconSrc} alt={iconAlt} />
    <Typography
      variant="subtitle1"
      sx={{
        fontFamily: "Inter",
        fontWeight: 500,
        fontSize: "14px",
        lineHeight: "20px",
        letterSpacing: "-0.1px",
      }}
    >
      {label}
    </Typography>
  </Stack>
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
    <Box
      sx={{
        mt: 3,
        border: "1px solid",
        borderColor: grey[300],
        borderRadius: 2,
        padding: 2,
        boxShadow: 1,
        backgroundColor: "background.paper",
      }}
    >
      <Stack direction="row" gap={8}>
        {infoItems.map(({ label, iconSrc, iconAlt, value }) => (
          <InfoItem
            key={label}
            label={label}
            iconSrc={iconSrc}
            iconAlt={iconAlt}
            value={value}
          />
        ))}
        <Stack direction="column" gap={0.75}>
          <Typography variant="subtitle1" sx={labelTypographySx}>
            Case Type
          </Typography>
          <Stack direction="row" gap={0.5}>
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
          </Stack>
        </Stack>
      </Stack>
    </Box>
  );
};

export default ComplaintSecondaryInfo;