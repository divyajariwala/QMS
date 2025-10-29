import React from 'react';
import { Breadcrumbs, Link, Box, Typography } from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { Link as RouterLink } from 'react-router-dom';
import styles from './CommonBreadcrumbs.module.scss';

interface BreadcrumbItem {
  label: string;
  to?: string;
}

interface CommonBreadcrumbsProps {
  items: BreadcrumbItem[];
  ariaLabel?: string;
}

const CommonBreadcrumbs: React.FC<CommonBreadcrumbsProps> = ({
  items,
  ariaLabel = 'breadcrumb',
}) => {
  return (
    <Breadcrumbs
      separator={<NavigateNextIcon fontSize="small" />}
      aria-label={ariaLabel}
      className={styles.breadcrumbs}
    >
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        if (isLast) {
          return (
            <Box key={index} className={styles.crumbCurrent}>
              {item.label}
            </Box>
          );
        }

        return item.to ? (
          <Link
            key={index}
            component={RouterLink}
            to={item.to}
            underline="hover"
            className={styles.link}
          >
            {item.label}
          </Link>
        ) : (
          <Typography key={index}>{item.label}</Typography>
        );
      })}
    </Breadcrumbs>
  );
};

export default CommonBreadcrumbs;