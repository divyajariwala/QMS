import '@testing-library/jest-dom/extend-expect';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App'; // Adjust the import path according to your file structure

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('Load the application', async () => {
    render(<App />);

    // Wait for the component to update
    await waitFor(() => {
      expect(screen.getByText('QMS Complaints Assessment Toolkit')).toBeInTheDocument();
    });
  });
});
