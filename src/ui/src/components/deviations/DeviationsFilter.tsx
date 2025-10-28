import React from "react";
import styles from "./DeviationsFilter.module.scss";

const DeviationsFilter: React.FC = () => {
  const SearchSvg = () => (
    <svg
      className={styles.searchIcon}
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <circle cx="11" cy="11" r="7" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );

  return (
    <div className={styles.searchBar}>
      <div className={styles.inputWrapper}>
        {SearchSvg()}
        <input
          type="search"
          placeholder="Search here..."
          aria-label="Search"
          className={styles.searchInput}
        />
        <button
          type="submit"
          className={styles.searchButtonInside}
          aria-label="Search Button"
        >
          <span style={{position: 'absolute', right: 115, bottom: 27}}>{SearchSvg()}</span>
          <span className={styles.searchButtonText}>Search</span>
        </button>
      </div>
    </div>
  );
};

export default DeviationsFilter;