import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

interface DonutChartProps {
  value: number;
}

/**
 * Renders the category value (percent) indicator.
 * Use the react-chartjs-2 library.
 *
 * @returns A react component.
 */
const DonutChart: React.FC<DonutChartProps> = ({ value }) => {
  const data = {
    labels: [' ', ''],
    datasets: [
      {
        data: [value, 100 - value],
        backgroundColor: ['#31779f', '#d3d9ed'],
        hoverBackgroundColor: ['#31779f', '#d3d9ed'],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    cutout: '70%', // Adjust this value to make the inner radius smaller
    plugins: {
      tooltip: {
        enabled: false,
      },
      legend: {
        display: false
      }
    },
  };

  return (
    <div className="donutChartMainDiv">
      <div className="donutChart">
        <Doughnut data={data} options={options} />
      </div>
    </div>
  );
}

export default DonutChart;
