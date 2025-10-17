import React from 'react';
import { Breadcrumbs, Link, Typography } from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { Link as RouterLink } from 'react-router-dom';
import styles from './ComplaintBreadcrumbs.module.scss';

interface ComplaintBreadcrumbsProps {
  caseId: string;
}

const ComplaintBreadcrumbs: React.FC<ComplaintBreadcrumbsProps> = ({ caseId }) => {
  return (
    <Breadcrumbs
      separator={<NavigateNextIcon fontSize="small" />}
      aria-label="breadcrumb"
      className={styles.breadcrumbs}
    >
      <Link component={RouterLink} to="/" underline="hover" className={styles.link}>
        Home
      </Link>
      <Link component={RouterLink} to="/productComplaints" underline="hover" className={styles.link}>
        Complaints
      </Link>
      <Typography className={styles.crumbCurrent}>
        {caseId}
      </Typography>
    </Breadcrumbs>
  );
};

export default ComplaintBreadcrumbs;