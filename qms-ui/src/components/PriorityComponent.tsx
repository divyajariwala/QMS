import React, { useEffect, useState } from 'react';
import { Select, MenuItem, SelectChangeEvent } from '@mui/material';

interface Props {
  priorityValue: number;
  handlePriorityChange: (event: SelectChangeEvent<number>) => void;
  isChecked: boolean;
  isEdit: boolean;
}

/**
 * Renders the prority selector component.
 *
 * @returns A react components.
 */
const PriorityComponent: React.FC<Props> = ({
  priorityValue: initialPriorityValue,
  handlePriorityChange,
  isChecked,
  isEdit
}) => {
  const [priorityValue, setPriorityValue] = useState<number>(initialPriorityValue);

  useEffect(() => {
    setPriorityValue(initialPriorityValue);
  }, [initialPriorityValue]);

  /**
   * Handles the selector change.
   *
   * @param event A SelectChangeEvent.
   */
  const handleLocalChange = (event: SelectChangeEvent<number>) => {
    const newValue = parseInt(event.target.value as string, 10);
    setPriorityValue(newValue);
    handlePriorityChange(event);
  };

  return (
    <div className="priority">
      <span className="title">Potential Complaint Priority</span>
      <div className="priority-select">
        {isChecked && isEdit ? (
          <Select
            data-testid="priority-select"
            size="small"
            value={priorityValue}
            onChange={handleLocalChange}
            displayEmpty
            inputProps={{
              'aria-label': 'Without label',
              readOnly: !isEdit,
            }}
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                borderWidth: 1,
                outline: 'none',
              },
              '& .MuiSelect-select': {
                backgroundColor: 'inherit',
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#1976d2',
              },
            }}
          >
            <MenuItem value={0}>No</MenuItem>
            <MenuItem value={1}>Yes</MenuItem>
          </Select>
        ) : (
          <Select
            data-testid="priority-select"
            size="small"
            value={priorityValue}
            disabled
            fullWidth
            displayEmpty
            inputProps={{
              'aria-label': 'Without label',
              readOnly: true,
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderWidth: 1,
                outline: 'none',
              },
              '& .MuiSelect-select': {
                backgroundColor: '#f5f5f5',
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#ccc',
              },
            }}
          >
            {priorityValue === 0 ? <MenuItem value={0}>No</MenuItem> : <MenuItem value={1}>Yes</MenuItem>}
          </Select>
        )}
      </div>
    </div>
  );
};

export default PriorityComponent;
