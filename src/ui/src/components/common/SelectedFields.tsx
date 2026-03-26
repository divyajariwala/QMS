import React from "react";
import styles from "./SelectedFields.module.scss";
import closeIcon from "../../assets/icons/close.svg";

interface SelectedFieldsProps {
  fields: string[];
  selected: string[];
  onSelect?: (field: string) => void;
  onRemove?: (field: string) => void;
  className?: string;
  label?: string;
  disabled?: boolean;
}

const SelectedFields: React.FC<SelectedFieldsProps> = ({
  fields,
  selected,
  onSelect,
  onRemove,
  className = "",
  label = "Selected fields",
  disabled = false,
}) => {
  return (
    <div className={className}>
      {label && <div className={styles.label}>{label}</div>}
      {selected.length > 0 && (
        <div className={styles.selectedBox}>
          {selected.map((field) => (
            <span key={field} className={styles.tag}>
              {field}
              <button
                className={styles.removeBtn}
                onClick={() => onRemove && onRemove(field)}
                aria-label={`Remove ${field}`}
                disabled={disabled}
              >
                <img src={closeIcon} alt="X" className={styles.closeIcon} />
              </button>
            </span>
          ))}
        </div>
      )}
      <div className={styles.fieldsGrid}>
        {fields.map((field) => (
          <label key={field} className={styles.fieldLabel}>
            <input
              type="checkbox"
              checked={selected.includes(field)}
              onChange={() => onSelect && onSelect(field)}
              disabled={disabled}
            />
            {field}
          </label>
        ))}
      </div>
    </div>
  );
};

export default SelectedFields;
