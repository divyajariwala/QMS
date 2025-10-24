import React from 'react';
import { Breadcrumbs, Link } from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { Link as RouterLink } from 'react-router-dom';
import styles from './DeviationsBreadcrumbs.module.scss';

const DeviationsBreadcrumbs: React.FC = () => {
  return (
    <Breadcrumbs
      separator={<NavigateNextIcon fontSize="small" />}
      aria-label="breadcrumb"
      className={styles.breadcrumbs}
    >
      <Link
        component={RouterLink}
        to="/"
        underline="hover"
        className={styles.link}
      >
        Home
      </Link>
      <Link
        component={RouterLink}
        to="/deviations"
        underline="hover"
        className={styles.crumbCurrent}
      >
        Deviations
      </Link>
    </Breadcrumbs>
  );
};

export default DeviationsBreadcrumbs;