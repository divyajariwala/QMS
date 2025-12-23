import React, { useState } from "react";
import Search from "../../assets/icons/search.svg";
import styles from "./DeviationsFilter.module.scss";
import { getDeviationsApiResponse } from "src/types";

interface PaginationObj {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

interface DeviationFilterProps {
  deviationId: string;
  setDeviationId: (val: string) => void;
  setDeviationDetail: (val: getDeviationsApiResponse | null) => void;
  setSearchActive: (val: boolean) => void;
  setPagination: (val: PaginationObj) => void;
  doSearch: (id: string, page?: number) => Promise<void>;
}

const DeviationsFilter = ({
  deviationId,
  setDeviationId,
  setDeviationDetail,
  setSearchActive,
  setPagination,
  doSearch,
}: DeviationFilterProps) => {
  const [error, setError] = useState<string | null>(null);
  const SearchSvg = () => <img src={Search} alt="Search icon" />;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setDeviationId(val);

    if (val.trim() === "") {
      setSearchActive(false);
      setError(null);
      setDeviationDetail(null);
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
        setError("Failed to load the required deviantion. Please try again.");
      });
    }
  };

  return (
    <>
      <div className={styles.container}>
        <div className={styles.searchBar}>
          <form className={styles.inputWrapper}>
            <span className={styles.searchIcon}>
              <SearchSvg />
            </span>
            <input
              type="search"
              placeholder="Search here..."
              aria-label="Search"
              className={styles.searchInput}
              value={deviationId}
              onChange={handleInputChange}
            />
            <button
              type="submit"
              className={styles.searchButtonInside}
              aria-label="Search Button"
            >
              <span className={styles.searchButtonText}>Search</span>
            </button>
          </form>
        </div>
      </div>
      {error && <div className={styles.errorText}>{error}</div>}
    </>
  );
};

export default DeviationsFilter;
