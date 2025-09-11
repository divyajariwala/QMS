import { render, screen } from '@testing-library/react';
import LeftPanel from './LeftPanel';

const mockSetDrugName = jest.fn();
const mockSetNarrativeText = jest.fn();
const mockSetHtmlContent = jest.fn();
const mockSetSummary = jest.fn();
const mockSetComplaintId = jest.fn();
const mockSetComplaintsDatasets = jest.fn();
const mockSetPriority = jest.fn();
const mockSetChecked = jest.fn();
const mockSetIsEdit = jest.fn();
const mockSetSubmitInProgress = jest.fn();
const mockSetSubmitted = jest.fn();
const mockSetUiData = jest.fn();

const fixedProps = {
  isDrugnameEditable: false,
  isNarrativeEditable: false,
  setDrugName: mockSetDrugName,
  setNarrativeText: mockSetNarrativeText,
  complaintId: 'VDE000000014044',
  setComplaintId: mockSetComplaintId,
  setComplaintsDatasets: mockSetComplaintsDatasets,
  setPriority: mockSetPriority,
  setHtmlContent: mockSetHtmlContent,
  setSummary: mockSetSummary,
  setChecked: mockSetChecked,
  setIsEdit: mockSetIsEdit,
  submitInProgress: false,
  setSubmitInProgress: mockSetSubmitInProgress,
  setSubmitted: mockSetSubmitted,
  setUiData: mockSetUiData,
  sessionData: null,
};

describe('Test Dashboard Left Panel', () => {
  test('Render component', () => {
    render(
      <LeftPanel
        drugName={'DEVICE MOUNJARO'}
        narrativeText={'Lorem ipsum'}
        {...fixedProps}
      />
    );

    const drugName = screen.getByText('DEVICE MOUNJARO');
    expect(drugName).toBeInTheDocument();

    const narrativeText = screen.getByText('Lorem ipsum');
    expect(narrativeText).toBeInTheDocument();
  });

  test('Classify button disabled (no drugname, no narrative)', () => {
    render (
      <LeftPanel
        drugName={''}
        narrativeText={''}
        {...fixedProps}
      />
    );

    // If drugname and narrative are empty, the button must be disabled.
    const saveButton = screen.getByTestId('submit-button');
    expect(saveButton).toBeDisabled();
  });

  test('Classify button disabled (no narrative)', () => {
    render (
      <LeftPanel
        drugName={'DEVICE MOUNJARO'}
        narrativeText={''}
        {...fixedProps}
      />
    );

    // If only drugname is set, the button must be disabled.
    const saveButton = screen.getByTestId('submit-button');
    expect(saveButton).toBeDisabled();
  });

  test('Classify button disabled (no drugname)', () => {
    render (
      <LeftPanel
        drugName={''}
        narrativeText={'Testing'}
        {...fixedProps}
      />
    );

    // If only narrative is set, the button must be disabled.
    const saveButton = screen.getByTestId('submit-button');
    expect(saveButton).toBeDisabled();
  });

  test('Classify button enabled', () => {
    render (
      <LeftPanel
        drugName={'DEVICE MOUNJARO'}
        narrativeText={'Testing'}
        {...fixedProps}
      />
    );

    // If drugname and narrative are set, the button must be enabled.
    const saveButton = screen.getByTestId('submit-button');
    expect(saveButton).toBeEnabled();
  });
});
