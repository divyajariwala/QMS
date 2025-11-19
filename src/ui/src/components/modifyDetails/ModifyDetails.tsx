import React, { useEffect, useState, ChangeEvent, MouseEvent } from 'react';
import styles from './ModifyDetails.module.scss';
import { MAX_LENGTH } from 'src/constants';

/**
 * Data shape sent to onSubmit
 */
export type SubmittedData = {
  status?: string | undefined;
  caseId?: string | undefined;
  overdueDays?: number | undefined;
  primaryReporter?: Record<string, any> | undefined;
  patientName?: string | undefined;
  physicianName?: string | undefined;
  drug?: string | undefined;
  lotNumber?: string | undefined;
  doseAmount?: string | undefined;
  expirationDate?: string | undefined;
  partNumber?: string | undefined;
  receipt_date?: string | undefined;
};

type Props = {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: SubmittedData) => void;
  initialValues?: Partial<SubmittedData>;
};

const ModifyDetails: React.FC<Props> = ({ open, onClose, onSubmit, initialValues = {} }) => {
  const [primaryReporter, setPrimaryReporter] = useState(
    initialValues?.primaryReporter ?? { address: '', name: '' }
  );
  const [drug, setDrug] = useState(initialValues?.drug ?? '');
  const [dose, setDose] = useState(initialValues?.doseAmount ?? '');
  const [patientName, setPatientName] = useState(initialValues?.patientName ?? '');
  const [physicianName, setPhysicianName] = useState(initialValues?.physicianName ?? '');
  const [expirationDate, setExpirationDate] = useState(initialValues?.expirationDate ?? '');
  const [lotNumber, setLotNumber] = useState(initialValues?.lotNumber ?? '');
  const [partNumber, setPartNumber] = useState(initialValues?.partNumber ?? '');

  const handlePrimaryReporterTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const v = e.target.value;

    // Split only on the first newline into name and address
    const firstNewlineIndex = v.indexOf('\n');
    if (firstNewlineIndex === -1) {
      // No newline => all is name, address empty
      setPrimaryReporter({
        name: v,
        address: '',
      });
    } else {
      const namePart = v.substring(0, firstNewlineIndex);
      const addressPart = v.substring(firstNewlineIndex + 1);
      setPrimaryReporter({
        name: namePart,
        address: addressPart,
      });
    }
  };

  useEffect(() => {
    // initialize when open or when initialValues change
    if (open) {
      setPrimaryReporter(initialValues.primaryReporter ?? { address: '', name: '' });
      setDrug(initialValues.drug ?? '');
      setDose(initialValues.doseAmount ?? '');
      setPatientName(initialValues.patientName ?? '');
      setPhysicianName(initialValues.physicianName ?? '');
      setExpirationDate(initialValues.expirationDate ?? '');
      setLotNumber(initialValues.lotNumber ?? '');
      setPartNumber(initialValues.partNumber ?? '');
    }
  }, [open, initialValues]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (open) window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  const handleSubmit = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    const data: SubmittedData = {
      primaryReporter: primaryReporter,
      doseAmount: dose.trim(),
      expirationDate: expirationDate,
      patientName: patientName.trim(),
      physicianName: physicianName.trim(),
      drug: drug.trim(),
      lotNumber: lotNumber.trim(),
      partNumber: partNumber.trim(),
    };

    onSubmit(data);
    // reset fields and close
    setPrimaryReporter({ address: '', name: '' });
    setDrug('');
    setDose('');
    setPatientName('');
    setPhysicianName('');
    setExpirationDate('');
    setLotNumber('');
    setPartNumber('');
    onClose();
  };

  const handleCancel = (e?: MouseEvent<HTMLElement> | Event) => {
    e?.preventDefault();
    onClose();
  };

  // prevent clicks inside dialog from bubbling to backdrop
  const stopProp = (e: React.MouseEvent) => e.stopPropagation();

  return (
    <>
      <div className={styles.backdrop} onClick={handleCancel} />
      <div
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="popup-title"
        onClick={stopProp}
      >
        <header className={styles.dialogTitleRow}>
          <div>
            <h2 id="popup-title" className={styles.dialogTitle}>Modify Details</h2>
          </div>

          <button
            type="button"
            aria-label="Close dialog"
            className={styles.closeBtn}
            onClick={handleCancel}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden
              focusable="false"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M6 6L18 18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M6 18L18 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </header>

        <section className={styles.dialogContent}>
          <form className={styles.form} onSubmit={(e) => e.preventDefault()}>
            <div className={styles.textareaGroup}>
              <label htmlFor="primaryReporter" className={styles.label}>Primary Reporter</label>
              <textarea
                id="primaryReporter"
                className={styles.textarea}
                value={primaryReporter.name + '\n' + (primaryReporter.address ?? '')}
                onChange={handlePrimaryReporterTextChange}
                rows={10}
                maxLength={MAX_LENGTH}
                aria-describedby="char-count"
              />
            </div>
            <div className={styles.formGrid}>
              <div className={styles.formField}>
                <label htmlFor="patientName" className={styles.label}>Patient Name</label>
                <input
                  id="patientName"
                  type="text"
                  value={patientName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setPatientName(e.target.value)}
                  className={styles.input}
                  placeholder="Enter Patient name"
                />
              </div>

              <div className={styles.formField}>
                <label htmlFor="physicianName" className={styles.label}>Physician</label>
                <input
                  id="physicianName"
                  type="text"
                  value={physicianName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setPhysicianName(e.target.value)}
                  className={styles.select}
                  placeholder="Enter physician name"
                />
              </div>

              <div className={styles.formField}>
                <label htmlFor="drug" className={styles.label}>Drug</label>
                <input
                  id="drug"
                  type="text"
                  value={drug}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setDrug(e.target.value)}
                  className={styles.input}
                  placeholder="Enter drug name"
                />
              </div>

              <div className={styles.formField}>
                <label htmlFor="lot" className={styles.label}>Lot #</label>
                <input
                  id="lot"
                  type="text"
                  value={lotNumber}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setLotNumber(e.target.value)}
                  className={styles.input}
                  placeholder="Enter lot number"
                />
              </div>

              <div className={styles.formField}>
                <label htmlFor="dose" className={styles.label}>Dose</label>
                <input
                  id="dose"
                  type="text"
                  value={dose}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setDose(e.target.value)}
                  className={styles.input}
                  placeholder="Enter Dose name"
                />
              </div>
              <div className={styles.formField}>
                <label htmlFor="expirationDate" className={styles.label}>Expiration Date</label>
                <input
                  id="expirationDate"
                  type="date"
                  value={expirationDate}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setExpirationDate(e.target.value)}
                  className={styles.input}
                />
              </div>
              <div className={styles.formField}>
                <label htmlFor="partNumber" className={styles.label}>Part Number</label>
                <input
                  id="partNumber"
                  type="text"
                  value={partNumber}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setPartNumber(e.target.value)}
                  className={styles.input}
                  placeholder="Part no."
                />
              </div>
            </div>
          </form>
        </section>

        <footer className={styles.dialogActions}>
          <button type="button" className={styles.btnCancel} onClick={handleCancel}>Cancel</button>
          <button
            type="button"
            className={styles.btnSubmit}
            onClick={handleSubmit}
          >
            Submit
          </button>
        </footer>
      </div>
    </>
  );
};

export default ModifyDetails;