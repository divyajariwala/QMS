import React from "react";

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
  width = 140,
  height = 140,
}) => {
  const radius = 42;
  const strokeWidth = 12;
  const cx = 70;
  const cy = 70;
  const viewBox = "0 0 140 140";
  const circumference = 2 * Math.PI * radius;

  const sum = data.reduce((a, b) => a + b, 0);

  if (!total || total <= 0 || sum <= 0) {
    return (
      <svg width={width} height={height} viewBox={viewBox} style={{ display: "block" }}>
        <circle r={radius} cx={cx} cy={cy} fill="transparent" stroke="#e9edf3" strokeWidth={strokeWidth} />
        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" fontSize={12} fill="#666">No data</text>
      </svg>
    );
  }

  const percentages = data.map((v) => (total > 0 ? v / total : 0));
  const cumulative = percentages.reduce<number[]>((acc, _, idx) => {
    if (idx === 0) return [0];
    acc.push(acc[idx - 1] + percentages[idx - 1]);
    return acc;
  }, []);
  const displayTotal = total >= 1000 ? `${(total / 1000).toFixed(1)}K` : total.toString();

  return (
    <svg width={width} height={height} viewBox={viewBox} style={{ display: "block", userSelect: "none" }}>
      <circle r={radius} cx={cx} cy={cy} fill="transparent" stroke="#e9edf3" strokeWidth={strokeWidth} />
      {percentages.map((pct, i) => {
        const color = colors[i % colors.length];
        const dashArray = circumference * pct;
        const dashOffset = circumference * (1 - cumulative[i] - pct);
        return (
          <circle
            key={i}
            r={radius}
            cx={cx}
            cy={cy}
            fill="transparent"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${dashArray} ${circumference}`}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            transform={`rotate(-90 ${cx} ${cy})`}
          />
        );
      })}
      <text x="50%" y="46%" textAnchor="middle" dominantBaseline="middle" fontSize={12} fill="#666">Total</text>
      <text x="50%" y="60%" textAnchor="middle" dominantBaseline="middle" fontSize={18} fontWeight="700" fill="#000">{displayTotal}</text>
    </svg>
  );
};

export default DonutChart;