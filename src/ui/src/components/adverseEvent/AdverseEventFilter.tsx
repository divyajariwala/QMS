import React, { useState } from "react";
import styles from "./AdverseEventFilter.module.scss";
import { AdverseEventFilterProps } from "src/types";

const AdverseEventFilter = ({
  complaintId,
  setComplaintId,
  setComplaintDetail,
  setSearchActive,
  setPagination,
  doSearch,
}: AdverseEventFilterProps) => {
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setComplaintId(val);

    if (val.trim() === "") {
      setSearchActive(false);
      setError(null);
      setComplaintDetail(null);
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
        setError("Failed to load the required complaint. Please try again.");
      });
    }
  };

  return (
    <>
      <div className={styles.container}>
        <div className={styles.searchBar}>
          <form className={styles.inputWrapper} onSubmit={(e) => e.preventDefault()}>
            <input
              type="search"
              placeholder="Search here..."
              aria-label="Search by complaint id"
              className={styles.searchInput}
              value={complaintId}
              onChange={handleInputChange}
            />
          </form>
        </div>
      </div>
      {error && <div className={styles.errorText}>{error}</div>}
    </>
  );
};

export default AdverseEventFilter;