import React, { useState, useEffect } from "react";
import styles from "./SCNFilter.module.scss";
import SearchIcon from "../../assets/icons/search.svg";
import {
  Button,
  Menu,
  FormGroup,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import filterIcon from "../../assets/icons/filter.svg";

interface PaginationObj {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

interface FilterOptions {
  all: boolean;
  approved: boolean;
  rejected: boolean;
  pendingReview: boolean;
  supplierActionRequired: boolean;
  inReview: boolean;
  openScns: boolean;
}

interface SCNFilterProps {
  scnNumber: string;
  setSCNNumber: (val: string) => void;
  setSearchResults: (val: any[] | null) => void;
  setSearchActive: (val: boolean) => void;
  setPagination: (val: PaginationObj) => void;
  doSearch: (
    scnNumber: string,
    page?: number,
    filters?: FilterOptions,
  ) => Promise<void>;
  filters: FilterOptions;
  setFilters: (val: FilterOptions) => void;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSearchClick: () => void;
}

const DEFAULT_FILTERS: FilterOptions = {
  all: false,
  approved: false,
  rejected: false,
  pendingReview: false,
  supplierActionRequired: false,
  inReview: false,
  openScns: false,
};

// The 4 filter options the API actually supports
const FILTER_OPTIONS: { key: keyof FilterOptions; label: string }[] = [
  { key: "approved", label: "Approved" },
  { key: "rejected", label: "Rejected" },
  { key: "inReview", label: "In Review" },
  { key: "pendingReview", label: "Pending Review" },
];

const SCNFilter = ({
  scnNumber,
  setSCNNumber,
  setSearchResults,
  setSearchActive,
  setPagination,
  doSearch,
  filters,
  setFilters,
  handleInputChange,
  handleSearchClick,
}: SCNFilterProps) => {
  const [error, setError] = useState<string | null>(null);
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(
    null,
  );
  const [tempFilters, setTempFilters] = useState<FilterOptions>(filters);

  const filterMenuOpen = Boolean(filterAnchorEl);

  useEffect(() => {
    if (filterMenuOpen) {
      setTempFilters(filters);
    }
  }, [filterMenuOpen, filters]);

  const handleInputChange_Local = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleInputChange(e);
  };

  const handleFilterOpen_Menu = (
    event: React.MouseEvent<HTMLButtonElement>,
  ) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleFilterChange = (key: keyof FilterOptions) => {
    if (key === "all") {
      // Toggle all → check/uncheck every real filter
      setTempFilters((prev) => {
        const next = !prev.all;
        return {
          all: next,
          approved: next,
          rejected: next,
          pendingReview: next,
          supplierActionRequired: next,
          inReview: next,
          openScns: next,
        };
      });
      return;
    }
    setTempFilters((prev) => {
      const updated = { ...prev, [key]: !prev[key] };
      // Auto-sync "all" based on whether all real options are checked
      const allChecked = FILTER_OPTIONS.every(({ key: k }) => updated[k]);
      return { ...updated, all: allChecked };
    });
  };

  const handleApplyFilters = () => {
    setFilters(tempFilters);
    setFilterAnchorEl(null);
    setError(null);
  };

  const handleClearFilters = () => {
    setTempFilters(DEFAULT_FILTERS);
  };

  return (
    <>
      <div className={styles.container}>
        <div className={styles.searchBar}>
          <form
            className={styles.inputWrapper}
            onSubmit={(e) => {
              e.preventDefault();
              handleSearchClick();
            }}
          >
            <img src={SearchIcon} alt="Search" className={styles.searchIcon} />
            <input
              type="search"
              placeholder="Search here..."
              aria-label="Search by SCN number"
              className={styles.searchInput}
              value={scnNumber}
              onChange={handleInputChange}
            />
            <button
              type="button"
              className={styles.searchButton}
              onClick={handleSearchClick}
            >
              Search
            </button>
          </form>
        </div>

        <button className={styles.filterButton} onClick={handleFilterOpen_Menu}>
          Filters
          <img src={filterIcon} alt="filter" />
        </button>
      </div>

      {error && <div className={styles.errorText}>{error}</div>}

      <Menu
        anchorEl={filterAnchorEl}
        open={filterMenuOpen}
        onClose={handleFilterClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
        PaperProps={{ sx: { mt: 1, minWidth: 300, p: 2 } }}
      >
        <h4 style={{ marginBottom: 8 }}>Filter by Status</h4>

        <FormGroup>
          {/* "All" convenience toggle */}
          <FormControlLabel
            label="All"
            control={
              <Checkbox
                size="small"
                checked={FILTER_OPTIONS.every(({ key }) => tempFilters[key])}
                indeterminate={
                  FILTER_OPTIONS.some(({ key }) => tempFilters[key]) &&
                  !FILTER_OPTIONS.every(({ key }) => tempFilters[key])
                }
                onChange={() => handleFilterChange("all")}
              />
            }
          />
          {/* Only the 4 real API-filterable statuses */}
          {FILTER_OPTIONS.map(({ key, label }) => (
            <FormControlLabel
              key={key}
              label={label}
              control={
                <Checkbox
                  size="small"
                  checked={tempFilters[key]}
                  onChange={() => handleFilterChange(key)}
                />
              }
            />
          ))}
        </FormGroup>

        <div className={styles.filterActions}>
          <Button
            size="small"
            variant="outlined"
            className={styles.cancelButton}
            onClick={handleClearFilters}
          >
            Clear
          </Button>
          <Button
            size="small"
            variant="contained"
            className={styles.applyButton}
            onClick={handleApplyFilters}
          >
            Apply
          </Button>
        </div>
      </Menu>
    </>
  );
};

export default SCNFilter;

export type { FilterOptions };
