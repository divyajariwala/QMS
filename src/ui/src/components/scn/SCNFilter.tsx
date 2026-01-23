import React, { useState } from "react";
import styles from "./SCNFilter.module.scss";
import SearchIcon from "../../assets/icons/search.svg";
import { Button } from "@mui/material";
import filterIcon from "../../assets/icons/filter.svg";

interface PaginationObj {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

interface SCNFilterProps {
  scnNumber: string;
  setSCNNumber: (val: string) => void;
  setSearchResults: (val: any[] | null) => void;
  setSearchActive: (val: boolean) => void;
  setPagination: (val: PaginationObj) => void;
  doSearch: (scnNumber: string, page?: number) => Promise<void>;
}

const SCNFilter = ({
  scnNumber,
  setSCNNumber,
  setSearchResults,
  setSearchActive,
  setPagination,
  doSearch,
}: SCNFilterProps) => {
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
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
      doSearch(val, 1).catch(() => {
        setError("Failed to load the required SCN. Please try again.");
      });
    }
  };

  const handleSearchClick = () => {
    if (scnNumber.trim() !== "") {
      setSearchActive(true);
      doSearch(scnNumber, 1).catch(() => {
        setError("Failed to load the required SCN. Please try again.");
      });
    }
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
              aria-label="Search"
            >
              Search
            </button>
          </form>
        </div>
        <button className={styles.filterButton}>
          Filters
          <img src={filterIcon} alt="filter" />
        </button>
      </div>
      {error && <div className={styles.errorText}>{error}</div>}
    </>
  );
};

export default SCNFilter;
