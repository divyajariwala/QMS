import { render } from '@testing-library/react';
import DonutChart from './donutChart';

describe('Test DonutChart', () => {
  test('Render component', async () => {
    render(
      <DonutChart
        value={0.25}
      />
    );
  });
});
