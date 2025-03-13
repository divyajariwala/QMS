import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PriorityComponent from './PriorityComponent';

const mockHandlePriorityChange = jest.fn();

describe('Test PriorityComponent', () => {
  test('Render component (No edit mode)', async () => {
    render(
      <PriorityComponent
        priorityValue={0}
        handlePriorityChange={mockHandlePriorityChange}
        isChecked={false}
        isEdit={false}
      />
    );

    const label = screen.getByText('Potential Complaint Priority');
    expect(label).toBeInTheDocument();

    const selectElement = within(
      await screen.findByTestId('priority-select')
    ).getByRole('combobox');

    expect(selectElement).toBeInTheDocument();
    expect(selectElement).toHaveAttribute('aria-disabled', 'true');
  });

  test('Render component (Edit mode)', async () => {
    render(
      <PriorityComponent
        priorityValue={0}
        handlePriorityChange={mockHandlePriorityChange}
        isChecked={true}
        isEdit={true}
      />
    );

    const selectElement = within(
      await screen.findByTestId('priority-select')
    ).getByRole('combobox');

    expect(selectElement).toBeInTheDocument();

    userEvent.click(selectElement);

    expect(
      await screen.findByRole('option', { name: 'No' })
    ).toBeInTheDocument();

    expect(
      await screen.findByRole('option', { name: 'Yes' })
    ).toBeInTheDocument();
  });
});
