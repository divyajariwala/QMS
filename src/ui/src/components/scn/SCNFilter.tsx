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
  all: true,
  approved: true,
  rejected: true,
  pendingReview: true,
  supplierActionRequired: true,
  inReview: true,
  openScns: true,
};

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

  // Sync tempFilters with filters prop when menu is opened
  useEffect(() => {
    if (filterMenuOpen) {
      setTempFilters(filters);
    }
  }, [filterMenuOpen, filters]);

  const handleInputChange_Local = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSCNNumber(val);

    if (val.trim() === "") {
      setSearchActive(false);
      setError(null);
      setSearchResults(null);
      setPagination({
        current_page: 1,
        total_pages: 0,
        total_items: 0,
        items_per_page: 15,
        has_next: false,
        has_previous: false,
      });
    } else {
      setSearchActive(true);
      // Use tempFilters if filter menu is open, otherwise use current filters
      doSearch(val, 1, filters).catch(() => {
        setError("Failed to load the required SCN. Please try again.");
      });
    }
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
    setTempFilters((prev) => {
      // Select / Deselect ALL
      if (key === "all") {
        const value = !prev.all;
        const newFilters = Object.keys(prev).reduce((acc, k) => {
          acc[k as keyof FilterOptions] = value;
          return acc;
        }, {} as FilterOptions);
        return newFilters;
      }

      const updated = {
        ...prev,
        [key]: !prev[key],
      };

      // Auto sync "All"
      const allChecked = Object.entries(updated)
        .filter(([k]) => k !== "all")
        .every(([, v]) => v);

      const result = {
        ...updated,
        all: allChecked,
      };
      return result;
    });
  };

  const handleApplyFilters = () => {
    setFilters(tempFilters);
    setFilterAnchorEl(null);
    setError(null);
    setSearchActive(true);

    doSearch(scnNumber, 1, tempFilters).catch(() => {
      setError("Failed to apply filters. Please try again.");
    });
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
            onSubmit={(e) => e.preventDefault()}
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
        <h4 style={{ marginBottom: 8 }}>SCN Type</h4>

        <FormGroup>
          {(Object.keys(tempFilters) as (keyof FilterOptions)[]).map((key) => {
            const label = key
              .replace(/([A-Z])/g, " $1")
              .replace(/^./, (str) => str.toUpperCase())
              .trim();

            return (
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
            );
          })}
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
