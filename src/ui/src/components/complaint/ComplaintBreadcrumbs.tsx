// ComplaintBreadcrumbs.tsx
import React from 'react';
import { Breadcrumbs, Link, Typography } from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { blue, grey } from '@mui/material/colors';
import { Link as RouterLink } from 'react-router-dom'; // <-- react-router-dom Link

const breadcrumbSx = {
  fontSize: 14,
  color: grey[700],
  '& a': { textDecoration: 'none', cursor: 'pointer', color: blue[700] },
};

interface ComplaintBreadcrumbsProps {
  caseId: string;
}

const ComplaintBreadcrumbs: React.FC<ComplaintBreadcrumbsProps> = ({ caseId }) => {
  return (
    <Breadcrumbs
      separator={<NavigateNextIcon fontSize="small" />}
      aria-label="breadcrumb"
      sx={breadcrumbSx}
    >
      <Link
        component={RouterLink}
        to="/"
        underline="hover"
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 500,
          fontStyle: 'normal',
          fontSize: '14px',
          lineHeight: '20px',
          letterSpacing: '-0.1px',
          color: ' #5F6D7E !important',
          cursor: 'pointer',
          '&:hover': {
            color: 'black',
            textDecoration: 'underline',
          },
        }}
      >
        Home
      </Link>
      <Link
        component={RouterLink}
        to="/productComplaints"
        underline="hover"
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 500,
          fontStyle: 'normal',
          fontSize: '14px',
          lineHeight: '20px',
          letterSpacing: '-0.1px',
          color: ' #5F6D7E !important',
          cursor: 'pointer',
          '&:hover': {
            color: 'black',
            textDecoration: 'underline',
          },
        }}
      >
        Complaints
      </Link>
      <Typography
        sx={{
          fontFamily: 'Inter, sans-serif',
          fontWeight: 500,
          fontStyle: 'normal',
          fontSize: 14,
          lineHeight: '20px',
          letterSpacing: '-0.1px',
          color: '#437EF7',
        }}
      >
        {caseId}
      </Typography>
    </Breadcrumbs>
  );
};

export default ComplaintBreadcrumbs;