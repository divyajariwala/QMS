// src/components/NarrativeFilterPopover.tsx
import React, { useState, forwardRef } from 'react';
import {
  Popover,
  Box,
  Typography,
  IconButton,
  Divider,
  Button,
  TextField,
  Chip,
  InputAdornment
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Filters } from '../../types';
import styles from './NarrativeFilterPopover.module.scss';

interface FilterPopoverProps {
  anchorEl: HTMLElement | null;
  onClose: () => void;
  onApply: (filters: Filters) => void;
}

const sourceOptions = ['Veeva', 'Trackwise', 'Others'];
const typeOptions   = ['Product complaint', 'Adverse event', 'Others'];

// Custom input for react-datepicker range picker
const RangeInput = forwardRef<HTMLElement, { value?: string; onClick?: () => void }>(
  ({ value, onClick }, ref) => (
    <TextField
      fullWidth
      size="small"
      placeholder="Date range"
      inputRef={ref as React.Ref<HTMLInputElement>}
      onClick={onClick}
      value={value}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <CalendarTodayIcon />
          </InputAdornment>
        )
      }}
    />
  )
);

const NarrativeFilterPopover: React.FC<FilterPopoverProps> = ({ anchorEl, onClose, onApply }) => {
  const open = Boolean(anchorEl);
  const [ingestedRange, setIngestedRange]   = useState<[Date | null, Date | null]>([null, null]);
  const [processedRange, setProcessedRange] = useState<[Date | null, Date | null]>([null, null]);
  const [sources, setSources]               = useState<string[]>([]);
  const [types, setTypes]                   = useState<string[]>([]);

  const toggle = (item: string, list: string[], setter: React.Dispatch<React.SetStateAction<string[]>>) => 
    setter(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);

  const handleApply = () => {
    onApply({
      ingestedStart:   ingestedRange[0],
      ingestedEnd:     ingestedRange[1],
      processedStart:  processedRange[0],
      processedEnd:    processedRange[1],
      selectedSources: sources,
      selectedTypes:   types
    });
    onClose();
  };

  const renderRangePicker = (
    range: [Date | null, Date | null],
    setter: (value: [Date | null, Date | null]) => void
  ) => (
    <DatePicker
      selectsRange
      startDate={range[0]}
      endDate={range[1]}
      onChange={dates => setter(dates as [Date | null, Date | null])}
      customInput={<RangeInput />}
    />
  );

  return (
    <Popover
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      slotProps={{ paper: { className: styles.paper } }}
    >
      <Box className={styles.header}>
        <Typography variant="h6">Filters</Typography>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>
      <Divider />

      <Box className={styles.content}>
        <Box mb={3}>
          <Typography variant="subtitle1">Ingested date (range)</Typography>
          {renderRangePicker(ingestedRange, setIngestedRange)}
        </Box>
        <Divider />

        <Box my={3}>
          <Typography variant="subtitle1">Processed date (range)</Typography>
          {renderRangePicker(processedRange, setProcessedRange)}
        </Box>
        <Divider />

        <Box my={3}>
          <Typography variant="subtitle1">
            Source system ({sources.length}/{sourceOptions.length})
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
            {sourceOptions.map(opt => (
              <Chip
                key={opt}
                label={opt}
                className={styles.typeChip}
                variant={sources.includes(opt) ? 'filled' : 'outlined'}
                onClick={() => toggle(opt, sources, setSources)}
              />
            ))}
          </Box>
        </Box>
        <Divider />

        <Box my={3}>
          <Typography variant="subtitle1">
            Narrative type ({types.length}/{typeOptions.length})
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
            {typeOptions.map(opt => (
              <Chip
                key={opt}
                label={opt}
                className={styles.typeChip}
                variant={types.includes(opt) ? 'filled' : 'outlined'}
                onClick={() => toggle(opt, types, setTypes)}
              />
            ))}
          </Box>
        </Box>
      </Box>

      <Divider />
      <Box className={styles.actions}>
        <Button className={styles.cancel} onClick={onClose}>Cancel</Button>
        <Button className={styles.apply} variant="contained" onClick={handleApply}>
          Apply
        </Button>
      </Box>
    </Popover>
  );
};

export default NarrativeFilterPopover;
