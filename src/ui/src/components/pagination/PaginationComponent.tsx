import React from 'react';
import { Pagination, Typography } from '@mui/material';
import styles from './PaginationComponent.module.scss';

interface PaginationData {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

interface PaginationComponentProps {
  pagination: PaginationData;
  onPageChange: (page: number) => void;
}

const PaginationComponent: React.FC<PaginationComponentProps> = ({
  pagination,
  onPageChange,
}) => {
  const handleChange = (_event: React.ChangeEvent<unknown>, page: number) => {
    onPageChange(page);
  };

  return (
    <div className={styles.paginationContainer}>
      <Pagination
        count={pagination.total_pages}
        page={pagination.current_page}
        onChange={handleChange}
        color="primary"
        showFirstButton
        showLastButton
        siblingCount={1}
        boundaryCount={1}
      />
      <Typography variant="body1" className={styles.pageInfo}>
        {`Showing Page ${pagination.current_page} of ${pagination.total_pages}`}
      </Typography>
    </div>
  );
};

export default PaginationComponent;