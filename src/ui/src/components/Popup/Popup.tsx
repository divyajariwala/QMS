import React, { useState, ChangeEvent, MouseEvent } from 'react';
import styles from './Popup.module.scss';

interface PopupProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (value: string) => void;
}

const MAX_LENGTH = 420;

const Popup: React.FC<PopupProps> = ({ open, onClose, onSubmit }) => {
  const [inputValue, setInputValue] = useState<string>('');

  if (!open) return null;

  const handleInputChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    if (e.target.value.length <= MAX_LENGTH) {
      setInputValue(e.target.value);
    }
  };

  const handleSubmit = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    onSubmit(inputValue);
    setInputValue('');
  };

  const handleCancel = (e: MouseEvent<HTMLElement>): void => {
  e.preventDefault();
  setInputValue('');
  onClose();
};

  return (
    <>
      <div className={styles.backdrop} onClick={handleCancel} />
      <div className={styles.dialog}>
        <header className={styles.dialogTitle}>Add Narrative Manually</header>

        <section className={styles.dialogContent}>
          <div className={styles.contentWrapper}>
            <label htmlFor="narrative" className={styles.label}>
              Narrative
            </label>
            <textarea
              id="narrative"
              autoFocus
              className={styles.textarea}
              value={inputValue}
              onChange={handleInputChange}
              rows={13}
              maxLength={MAX_LENGTH}
            />
            <div className={styles.charCount}>
              {inputValue.length}/{MAX_LENGTH}
            </div>
          </div>
        </section>

        <footer className={styles.dialogActions}>
          <button type="button" className={styles.btnCancel} onClick={handleCancel}>
            Cancel
          </button>
          <button type="button" className={styles.btnSubmit} onClick={handleSubmit}>
            Submit
          </button>
        </footer>
      </div>
    </>
  );
};

export default Popup;