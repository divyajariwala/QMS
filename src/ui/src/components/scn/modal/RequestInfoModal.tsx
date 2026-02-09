import React, { useState } from "react";
import CommonModal from "@components/common/CommonModal";
import SelectedFields from "@components/common/SelectedFields";
import FormInput from "@components/common/FormInput";
import styles from "./RequestInfoModal.module.scss";

interface RequestInfoModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (fields: string[], comment: string) => void;
  allFields: string[];
  initialSelected?: string[];
}

const RequestInfoModal: React.FC<RequestInfoModalProps> = ({
  open,
  onClose,
  onSubmit,
  allFields,
  initialSelected = [],
}) => {
  const [selected, setSelected] = useState<string[]>(initialSelected);
  const [comment, setComment] = useState("");

  const handleSelect = (field: string) => {
    setSelected((prev) =>
      prev.includes(field) ? prev.filter((f) => f !== field) : [...prev, field],
    );
  };

  const handleRemove = (field: string) => {
    setSelected((prev) => prev.filter((f) => f !== field));
  };

  const handleSubmit = () => {
    onSubmit(selected, comment);
    onClose();
  };

  return (
    <CommonModal
      open={open}
      onClose={onClose}
      title="Request info"
      width={686}
      actions={[
        {
          label: "Cancel",
          variant: "outlined",
          onClick: onClose,
          classes: styles.actionButton,
        },
        {
          label: "Submit",
          variant: "primary",
          onClick: handleSubmit,
          disabled: selected.length === 0 || !comment.trim(),
            classes: styles.actionButton,
        },
      ]}
    >
      <div className={styles.wrapper}>
        <div className={styles.title}>Please select the fields to request</div>
        <SelectedFields
          fields={allFields}
          selected={selected}
          onSelect={handleSelect}
          onRemove={handleRemove}
        />
        <div>
          <div className={styles.commentLabel}>
            Comment<span className={styles.required}>*</span>
          </div>
          <FormInput
            label=""
            value={comment}
            onChange={setComment}
            placeholder="Input text"
            multiline
            rows={3}
            disabled={false}
            className={styles.commentBox}
          />
        </div>
      </div>
    </CommonModal>
  );
};

export default RequestInfoModal;
