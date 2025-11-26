import React, { useState } from "react";
import Search from "../../assets/icons/search.svg";
import styles from "./ComplaintsFilter.module.scss";
import { fetchComplaintDetailById } from "../../services/api.service"; // adjust the import path
import { ComplaintDetail } from "src/types";

interface ComplaintFilterProps {
  complaintId: string;
  setComplaintId: (val: string) => void;
  complaintDetail: ComplaintDetail | null;
  setComplaintDetail: (val: ComplaintDetail | null) => void;
  setSearchActive: (val: boolean) => void;
}

const ComplaintsFilter = ({
  complaintId,
  complaintDetail,
  setComplaintId,
  setComplaintDetail,
  setSearchActive,
}: ComplaintFilterProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Helper function to format complaint ID to "CAS-00017" style
  const formatComplaintId = (id: string): string => {
    const trimmed = id.trim();

    if (/^CAS-/i.test(trimmed)) {
      return trimmed.toUpperCase();
    }

    const digits = trimmed.replace(/\D/g, "");
    if (digits.length === 0) {
      return trimmed.toUpperCase(); // fallback for invalid input
    }

    const padded = digits.padStart(5, "0");
    return `CAS-${padded}`;
  };

  const SearchSvg = () => <img src={Search} alt="Search icon" />;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setComplaintId(e.target.value);
    if (e.target.value === "") {
      setSearchActive(false);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setComplaintDetail(null);
    setSearchActive(true);

    if (!complaintId.trim()) {
      setError("Please enter a complaint id.");
      return;
    }

    const formattedId = formatComplaintId(complaintId);

    setLoading(true);
    try {
      const detail = await fetchComplaintDetailById(formattedId);
      setComplaintDetail(detail);
    } catch (err) {
      setError("Failed to load the required complaint. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
    <div className={styles.container}>
      <div className={styles.searchBar}>
        <form className={styles.inputWrapper} onSubmit={handleSubmit}>
          <span className={styles.searchIcon}>
            <SearchSvg />
          </span>
          <input
            type="search"
            placeholder="Search here..."
            aria-label="Search by complaint id"
            className={styles.searchInput}
            value={complaintId}
            onChange={handleInputChange}
          />
          <button
            type="submit"
            className={styles.searchButtonInside}
            aria-label="Search Button"
            disabled={loading}
          >
            <span className={styles.searchButtonIcon}>
              <SearchSvg />
            </span>
            <span className={styles.searchButtonText}>
              {loading ? "Searching..." : "Search"}
            </span>
          </button>
        </form>
      </div>
    </div>
    {error && <div className={styles.errorText}>{error}</div>}
    </>
  );
};

export default ComplaintsFilter;