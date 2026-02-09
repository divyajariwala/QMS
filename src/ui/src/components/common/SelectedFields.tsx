import React from "react";
import styles from "./SelectedFields.module.scss";
import closeIcon from "../../assets/icons/close.svg";

interface SelectedFieldsProps {
  fields: string[];
  selected: string[];
  onSelect: (field: string) => void;
  onRemove: (field: string) => void;
  className?: string;
}

const SelectedFields: React.FC<SelectedFieldsProps> = ({
  fields,
  selected,
  onSelect,
  onRemove,
  className = "",
}) => {
  // Split fields for two columns
  const mid = Math.ceil(fields.length / 2);
  const leftFields = fields.slice(0, mid);
  const rightFields = fields.slice(mid);

  return (
    <div className={className}>
      <div className={styles.label}>Selected fields</div>
      <div className={styles.selectedBox}>
        {selected.map((field) => (
          <span key={field} className={styles.tag}>
            {field}
            <button
              className={styles.removeBtn}
              onClick={() => onRemove(field)}
              aria-label={`Remove ${field}`}
            >
              <img src={closeIcon} alt="X" className={styles.closeIcon} />
            </button>
          </span>
        ))}
      </div>
      <div className={styles.fieldsGrid}>
        <div className={styles.column}>
          {leftFields.map((field) => (
            <label key={field} className={styles.fieldLabel}>
              <input
                type="checkbox"
                checked={selected.includes(field)}
                onChange={() => onSelect(field)}
              />
              {field}
            </label>
          ))}
        </div>
        <div className={styles.column}>
          {rightFields.map((field) => (
            <label key={field} className={styles.fieldLabel}>
              <input
                type="checkbox"
                checked={selected.includes(field)}
                onChange={() => onSelect(field)}
              />
              {field}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SelectedFields;
