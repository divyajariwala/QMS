import React from "react";
import clsx from "clsx";
import styles from "./AppButton.module.scss";

type ButtonVariant =
  | "primary"
  | "secondary"
  | "outlined"
  | "danger"
  | "success"
  | "ghost";

type ButtonSize = "sm" | "md" | "lg";

interface AppButtonProps {
  label?: string;
  children?: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  className?: string;
}

const AppButton: React.FC<AppButtonProps> = ({
  label,
  children,
  onClick,
  type = "button",
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  fullWidth = false,
  className,
}) => {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={clsx(
        styles.button,
        styles[variant],
        styles[size],
        {
          [styles.fullWidth]: fullWidth,
          [styles.loading]: loading,
        },
        className,
      )}
    >
      {loading && <span className={styles.loader} />}

      <span>{label || children}</span>
    </button>
  );
};

export default AppButton;
