import React from "react";
import { Doughnut } from "react-chartjs-2";
import { Box } from "@mui/material";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

interface DonutChartProps {
  data: number[];
  colors: string[];
  total: number;
  width?: number;
  height?: number;
}

const DonutChart: React.FC<DonutChartProps> = ({
  data,
  colors,
  total,
  width,
  height,
}) => {
  const sum = data.reduce((a, b) => a + b, 0);

  // Center total display (e.g., 27.3K)
  const displayTotal =
    total >= 1000 ? `${(total / 1000).toFixed(1)}K` : String(total);

  // Chart data with white gaps between segments
  const chartData = {
    datasets: [
      {
        data,
        backgroundColor: colors,
        borderWidth: 6,        // create white gaps between segments
        borderColor: "#fff",     // white gaps
        hoverBorderColor: "#fff",
      },
    ],
  };

  // Chart options to match SS2 look
  const options = {
    responsive: false,
    maintainAspectRatio: false,
    cutout: "68%", // thick ring
    rotation: -Math.PI / 2, // start from top
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
    },
    animation: { animateRotate: true, duration: 300 },
  };

  // No data placeholder
  if (!total || total <= 0 || sum <= 0) {
    return (
      <Box sx={{ width, height, display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
        <Doughnut data={chartData} options={options} width={width} height={height} />
        <Box sx={{ position: "absolute", textAlign: "center" }}>
          <Box sx={{ fontSize: 12, color: "text.secondary" }}>Total</Box>
          <Box sx={{ fontSize: 14, fontWeight: 700, color: "text.primary" }}>0</Box>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ width, height, position: "relative", display: "inline-block" }}>
      <Doughnut data={chartData} options={options} width={width} height={height} />
      <Box
        sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          userSelect: "none",
        }}
      >
        <Box component="div" sx={{ fontSize: 12, color: "text.secondary" }}>
          Total
        </Box>
        <Box component="div" sx={{ fontSize: 18, fontWeight: 700, color: "text.primary" }}>
          {displayTotal}
        </Box>
      </Box>
    </Box>
  );
};

export default DonutChart;