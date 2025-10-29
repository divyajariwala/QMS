import React from 'react';
import styles from './ButtonGroup.module.scss';

interface ButtonGroupProps {
  onSelect?: (selected: string) => void;
  selected?: string;
}

const ButtonGroup: React.FC<ButtonGroupProps> = ({
  onSelect,
  selected,
}) => {
  const buttons = ['Root Cause Analysis', 'Grading'];

  return (
    <div className={styles.buttonGroup}>
      {buttons.map((btn) => (
        <button
          key={btn}
          type="button"
          className={`${styles.button} ${
            selected === btn ? styles.selected : ''
          }`}
          onClick={() => onSelect && onSelect(btn)}
          aria-pressed={selected === btn}
        >
          {btn}
        </button>
      ))}
    </div>
  );
};

export default ButtonGroup;