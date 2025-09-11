import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ComplaintCard from './ComplaintCard';

const MOCK_COMPLAINT = {
  title: 'Test sub-category 1 - CRL',
  crlValue: 0.5,
  category: 'Test sub-category 1',
  categoryValue: 0.5,
  level: 1,
};

const mockHandleCheck = jest.fn();
const mockUpdateCategoryName = jest.fn();
const mockUpdateLevel = jest.fn();
const mockUpdateTitle = jest.fn();
const mockUpdatePriority = jest.fn();
const mockUpdateUnit = jest.fn();

const fixedProps = {
  isSaving: false,
  submitted: false,
  complaint: MOCK_COMPLAINT,
  errors: {},
  levelList: [1, 2, 3],
  handleCheck: mockHandleCheck,
  updateCategoryName: mockUpdateCategoryName,
  updateLevel: mockUpdateLevel,
  updateTitle: mockUpdateTitle,
  updatePriority: mockUpdatePriority,
  updateUnit: mockUpdateUnit,
};

describe('Test ComplaintCard', () => {
  test('Render card (no edit mode)', () => {
    render(
      <ComplaintCard
        isChecked={false}
        isEdit={false}
        subcategoryList={[]}
        crlList={[]}
        {...fixedProps}
      />
    );

    const subCategoryText = screen.getByText('Test sub-category 1');
    expect(subCategoryText).toBeInTheDocument();

    const scoreText = screen.getByText('50%');
    expect(scoreText).toBeInTheDocument();

    const crlText = screen.getByText('Test sub-category 1 - CRL');
    expect(crlText).toBeInTheDocument();
  });

  test('Render card (edit mode)', async () => {
    render(
      <ComplaintCard
        isChecked={true}
        isEdit={true}
        subcategoryList={[
          'Test sub-category 1',
          'Test sub-category 2',
          'Test sub-category 3',
        ]}
        crlList={[
          'Test sub-category 1 - CRL',
          'Test sub-category 2 - CRL',
          'Test sub-category 3 - CRL',
        ]}
        {...fixedProps}
      />
    );

    const selectElement = within(
      await screen.findByTestId('subcategory-select')
    ).getByRole('combobox');

    expect(selectElement).toBeInTheDocument();

    userEvent.click(selectElement);

    expect(
      await screen.findByRole('option', { name: 'Test sub-category 1' })
    ).toBeInTheDocument();

    expect(
      screen.getByRole('option', { name: 'Test sub-category 2' })
    ).toBeInTheDocument();

    expect(
      screen.getByRole('option', { name: 'Test sub-category 3' })
    ).toBeInTheDocument();
  });
});
