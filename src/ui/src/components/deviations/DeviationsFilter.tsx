import React from "react";
import Search from "../../assets/icons/search.svg";
import styles from "./DeviationsFilter.module.scss";

const DeviationsFilter: React.FC = () => {
  const SearchSvg = () => <img src={Search} alt="Search icon" />;

  return (
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
          />
          <button
            type="submit"
            className={styles.searchButtonInside}
            aria-label="Search Button"
          >
            <span className={styles.searchButtonIcon}>
              <SearchSvg />
            </span>
            <span className={styles.searchButtonText}>Search</span>
          </button>
        </form>
      </div>

      <button type="button" className={styles.advancedButton}>
        Advanced Search
      </button>
    </div>
  );
};

export default DeviationsFilter;