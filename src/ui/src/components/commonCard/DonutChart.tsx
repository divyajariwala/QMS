import React from "react";
import { Doughnut } from "react-chartjs-2";
import { Box } from "@mui/material";
import {
  Chart as ChartJS,
  registerables
} from "chart.js";

ChartJS.register(...registerables);

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
  width = 130,   // default to 130
  height = 130,  // default to 130
}) => {
  const sum = data.reduce((a, b) => a + b, 0);

  // Center total display (e.g., 27.3K)
  const displayTotal =
    total >= 1000 ? `${(total / 1000).toFixed(1)}K` : String(total);

  // compute a reasonable borderWidth for the smaller donut (avoid visual overlap)
  const borderWidth = Math.max(3, Math.round(Math.min(width, height) / 26)); // ~5 for 130px

  const chartData = {
    datasets: [
      {
        data,
        backgroundColor: colors,
        borderWidth,        // white gaps between segments
        borderColor: "#fff",
        hoverBorderColor: "#fff",
      },
    ],
  };

  const options = {
    responsive: false,
    maintainAspectRatio: false,
    cutout: "68%", // thick ring, adjust if you want thicker/thinner
    rotation: 270, // 180 degrees (left). Change if you want a different start angle
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
    },
    animation: { animateRotate: true, duration: 300 },
  };

  const wrapperStyle = { width: `${width}px`, height: `${height}px`, position: "relative", display: "inline-block" };

  // Render donut (even with zero data to keep layout consistent)
  return (
    <Box sx={wrapperStyle}>
      <Doughnut
        data={chartData}
        options={options}
        width={width}
        height={height}
        style={{ width: `${width}px`, height: `${height}px` }}
      />
      <Box
        sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          userSelect: "none",
          pointerEvents: "none",
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