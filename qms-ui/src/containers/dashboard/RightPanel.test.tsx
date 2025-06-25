import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComplaintDataset } from '../../types';
import RightPanel from './RightPanel';

const mockSetComplaintId = jest.fn();
const mockSetDrugName = jest.fn();
const mockSetNarrativeText = jest.fn();
const mockSetComplaintsDatasets = jest.fn();
const mockSetHtmlContent = jest.fn();
const mockSetSubmitInProgress = jest.fn();
const mockSetSummary = jest.fn();
const mockSetChecked = jest.fn();
const mockSetIsEdit = jest.fn();
const mockSetIsSaving = jest.fn();
const mockSetSubmitted = jest.fn();

const mockComplaintsDatasets: ComplaintDataset[] = [
  {
    title: 'Air bubble - CSC',
    crlValue: 0.5,
    category: 'Air bubble',
    categoryValue: 0.5,
    level: 1,
  },
  {
    title: 'Base cap difficult to remove - CSC',
    crlValue: 0.5,
    category: 'Base cap difficult to remove',
    categoryValue: 0.5,
    level: 1,
  }
];

const fixedProps = {
  complaintId: 'VDE000000014044',
  setComplaintId: mockSetComplaintId,
  drugName: 'DEVICE MOUNJARO',
  setDrugName: mockSetDrugName,
  setNarrativeText: mockSetNarrativeText,
  complaintsDatasets: mockComplaintsDatasets,
  setComplaintsDatasets: mockSetComplaintsDatasets,
  priority: 0,
  htmlContent: '',
  setHtmlContent: mockSetHtmlContent,
  summary: 'Lorem ipsum',
  setSummary: mockSetSummary,
  submitInProgress: false,
  setSubmitInProgress: mockSetSubmitInProgress,
  setChecked: mockSetChecked,
  isEdit: false,
  setIsEdit: mockSetIsEdit,
  isSaving: false,
  setIsSaving: mockSetIsSaving,
  submitted: false,
  setSubmitted: mockSetSubmitted,
  uiData: {
    scList: [
      'Air bubble',
      'Base cap difficult to remove',
      'Base cap replacement',
    ],
    crlList: [
      'Air bubble - CSC',
      'Base cap difficult to remove - CSC',
      'Base cap replacement - CSC',
    ],
  },
};

describe('Test Dashboard right panel', () => {
  test('Submit button disabled (no checked items)', () => {
    render(
      <RightPanel
        checked={[]}
        {...fixedProps}
      />
    );

    // Find save button. It must be disabled.
    const saveButton = screen.getByTestId('save-button');
    expect(saveButton).toBeDisabled();
  });

  test('Submit button disabled (1 checked item)', () => {
    const mockChecked: number[] = [1];

    render(
      <RightPanel
        checked={mockChecked}
        {...fixedProps}
      />
    );

    // Find save button. It must be enabled.
    const saveButton = screen.getByTestId('save-button');
    expect(saveButton).toBeEnabled();
  });

  test('Submit buttton is disabled if unit is empty', async () => {
    const mockChecked: number[] = [0];
    const dataSet: ComplaintDataset[] = [...mockComplaintsDatasets];
    // Unit is empty.
    dataSet[0].unit_new = '';

    render(
      <RightPanel
        checked={mockChecked}
        {...fixedProps}
        complaintsDatasets={dataSet}
        isEdit={true}
      />
    );

    const saveButton = screen.getByTestId('save-button');
    expect(saveButton).toBeDisabled();
  });

  test('Submit buttton is disabled if unit is 0', async () => {
    const mockChecked: number[] = [0];
    const dataSet: ComplaintDataset[] = [...mockComplaintsDatasets];
    // Unit is 0.
    dataSet[0].unit_new = 0;

    render(
      <RightPanel
        checked={mockChecked}
        {...fixedProps}
        complaintsDatasets={dataSet}
        isEdit={true}
      />
    );

    const saveButton = screen.getByTestId('save-button');
    expect(saveButton).toBeDisabled();
  });

  test('Submit button is enabled if unit is 1', async () => {
    const mockChecked: number[] = [0];
    const dataSet: ComplaintDataset[] = [...mockComplaintsDatasets];
    // Unit is greatest than 0.
    dataSet[0].unit_new = 1;

    render(
      <RightPanel
        checked={mockChecked}
        {...fixedProps}
        complaintsDatasets={dataSet}
        isEdit={true}
      />
    );

    const saveButton = screen.getByTestId('save-button');
    expect(saveButton).toBeEnabled();
  });

  test('Priority selector behavior', async () => {
    const mockChecked: number[] = [0];
    const dataSet: ComplaintDataset[] = [...mockComplaintsDatasets];

    render(
      <RightPanel
        checked={mockChecked}
        {...fixedProps}
        complaintsDatasets={dataSet}
        priority={0}
        isEdit={true}
      />
    );

    // The summary is not present in the screen.
    expect(
      screen.queryByTestId('summary-text')
    ).toBeNull();

    const priorityElement = within(
      await screen.findByTestId('priority-select')
    ).getByRole('combobox');

    expect(priorityElement).toBeInTheDocument();

    userEvent.click(priorityElement);

    const yesOption = await screen.findByRole('option', { name: 'Yes' });
    expect(yesOption).toBeInTheDocument();

    userEvent.click(yesOption);

    // The summary must be visible at this moment.´
    expect(
      await screen.findByTestId('summary-text')
    ).toBeInTheDocument();
  });
});
