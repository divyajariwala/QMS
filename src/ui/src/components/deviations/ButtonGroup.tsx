import React from 'react';
import { ButtonGroupProps } from 'src/types'
import styles from './ButtonGroup.module.scss';

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
          className={`${styles.button} ${selected === btn ? styles.selected : ''
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