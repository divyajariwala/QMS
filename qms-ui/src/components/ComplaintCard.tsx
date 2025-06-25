import React from 'react';
import CheckCircleOutlineOutlinedIcon from '@mui/icons-material/CheckCircleOutlineOutlined';
import {
  Checkbox,
  MenuItem,
  Select,
  SelectChangeEvent,
  TextField,
} from '@mui/material';
import DonutChart from './controls/Chart/donutChart';
import { ComplaintDataset } from '../types';
import { MISC_SUBCAT } from '../constants';

interface ComplaintErrors {
  unit?: boolean;
}

interface Props {
  isSaving: boolean;
  submitted: boolean;
  isChecked: boolean;
  isEdit: boolean;
  complaint: ComplaintDataset;
  errors: ComplaintErrors;
  subcategoryList: string[];
  crlList: string[];
  levelList: number[];
  handleCheck: (event: React.ChangeEvent<HTMLInputElement>) => void;
  updateCategoryName: (event: SelectChangeEvent<string>) => void;
  updateLevel: (event: SelectChangeEvent<string>) => void;
  updateTitle: (event: SelectChangeEvent<string>) => void;
  updateUnit: (event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement, Element>) => void;
}

const MAX_UNIT_LENGHT = 11; // MAX VALUE: 99999999999

/**
 * Helper - Renders a list of MenuItem elements.
 * These items must be used as children of the Select component.
 *
 * @param levelList - Array of numbers.
 * @param isNA - If true, returns an element with the value "N/A".
 * @returns A list of react components.
 */
const renderLevelMenuItems = (levelList: number[], isNA = false) => {
  if (isNA) {
    return (
      <MenuItem key="level-na" value="N/A">N/A</MenuItem>
    );
  }

  return levelList.map((level: number, index: number) => (
    <MenuItem key={`level-${index}`} value={level}>{level}</MenuItem>
  ));
}

/**
 * Renders a card that shows a complaint result.
 *
 * @returns A react component.
 */
const ComplaintCard: React.FC<Props> = ({
  isSaving,
  submitted,
  isChecked,
  isEdit,
  complaint,
  errors,
  subcategoryList,
  crlList,
  levelList,
  handleCheck,
  updateCategoryName,
  updateLevel,
  updateTitle,
  updateUnit,
}) => {
  const itemClass = `complaint-card${isChecked ? ' checked' : ' not-checked'}${submitted ? ' submitted' : ''}`;

  /**
   * Handles the unit input key down changes.
   * Forces the input to allow only numbers and some keys.
   *
   * @param event KeyboardEvent.
   */
  const handleNumericKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const target = event.target as HTMLInputElement;
    const value = target.value;
    const allowedKeys = [
      'Backspace',
      'ArrowLeft',
      'ArrowRight',
      'Delete',
      'Tab',
    ];

    // If zero is the first character...
    if (value.length === 0 && event.key === '0') {
      event.preventDefault();
      return;
    }

    if (!/[0-9]/.test(event.key) && !allowedKeys.includes(event.key)) {
      event.preventDefault();
    }
  }

  const isSCMisc = (complaint.category_new ?? complaint.category) === MISC_SUBCAT;
  const levelValue = isSCMisc ? 'N/A' : complaint.level_new ?? complaint.level;
  const percent = parseFloat(complaint.categoryValue.toFixed(2)) * 100;
  const crlValue = complaint.title_new ?? complaint.title;

  return (
    <div className={itemClass}>
      <div className="data">
        <div className="data-cell check-cell">
          <span className="label">-</span>
          <div className="check">
            {isChecked && submitted ? (
              <CheckCircleOutlineOutlinedIcon
                sx={{
                  width: '24px',
                  cursor: 'pointer',
                  color: '#21812d',
                }}
              />
            ) : (
              <Checkbox
                disabled={!isChecked && submitted}
                checked={isChecked}
                onChange={handleCheck}
              />
            )}
          </div>
        </div>
        <div className="data-cell category-cell">
          <span className="label">Reported Issue</span>
          <div className="category">
            {isChecked && isEdit ? (
              <Select
                data-testid="subcategory-select"
                size="small"
                fullWidth
                value={complaint.category_new ?? complaint.category}
                onChange={updateCategoryName}
                inputProps={{ 'aria-label': 'Without label' }}
              >
                {subcategoryList.map((subcategory: string, index: number) => (
                  <MenuItem
                    key={`subcategory-${index}`}
                    value={subcategory}
                    data-subcategory-option={subcategory}
                  >
                    {subcategory}
                  </MenuItem>
                ))}
              </Select>
            ) : (
              <>{complaint.category_new ?? complaint.category}</>
            )}
          </div>
        </div>
        <div className="data-cell score-cell">
          <span className="label">Confidence Score</span>
          <div className="score">
            <DonutChart value={!isNaN(percent) ? percent : 0} />
            <span>{(complaint.categoryValue * 100).toFixed() + '%'}</span>
          </div>
        </div>
        <div className="data-cell level-cell">
          <span className="label">Level</span>
          <div className="level">
            {isChecked && isEdit ? (
              <Select
                size="small"
                value={`${levelValue}`}
                onChange={updateLevel}
                inputProps={{ 'aria-label': 'Without label' }}
                disabled={isSCMisc}
              >
                {renderLevelMenuItems(levelList, isSCMisc)}
              </Select>
            ) : (
              <>{levelValue}</>
            )}
          </div>
        </div>
        <div className="data-cell crl-cell">
          <span className="label">CRL</span>
          <div className="crl">
            {isChecked && isEdit ? (
              <Select
                size="small"
                fullWidth
                value={crlValue ?? 'N/A'}
                onChange={updateTitle}
                inputProps={{ 'aria-label': 'Without label' }}
              >
                {crlList.map((crl: string, index: number) => (
                  <MenuItem key={`crl-${index}`} value={crl}>{crl}</MenuItem>
                ))}
                <MenuItem key={'crl-none'} value="N/A">N/A</MenuItem>
              </Select>
            ) : (
              <>{crlValue ?? 'N/A'}</>
            )}
          </div>
        </div>
        <div className="data-cell unit-cell">
          <span className="label">Unit</span>
          <div className="unit">
            {isChecked ? (
              <TextField
                size="small"
                placeholder=""
                fullWidth
                defaultValue={complaint.unit_new ?? ''}
                onKeyDown={handleNumericKeyDown}
                onChange={updateUnit}
                error={errors.unit}
                disabled={isSaving || submitted}
                title="Enter a number greater than 0."
                inputProps={{ maxLength: MAX_UNIT_LENGHT }}
              />
            ) : (
              <>{complaint.unit_new ?? ''}</>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComplaintCard;
