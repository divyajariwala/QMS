import React from "react";
import styles from "./FormInput.module.scss";

interface FormInputProps {
  label: string;
  value: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
  type?: "text" | "email" | "date" | "number";
  multiline?: boolean;
  rows?: number;
  className?: string;
}

const FormInput: React.FC<FormInputProps> = ({
  label,
  value,
  onChange,
  disabled = true,
  placeholder = "Input text",
  type = "text",
  multiline = false,
  rows = 4,
  className = "",
}) => {
  return (
    <div className={`${styles.formGroup} ${className}`}>
      <label className={styles.formLabel}>{label}</label>
      {multiline ? (
        <textarea
          className={styles.formTextarea}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
          rows={rows}
        />
      ) : (
        <input
          type={type}
          className={styles.formInput}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
        />
      )}
    </div>
  );
};

export default FormInput;
