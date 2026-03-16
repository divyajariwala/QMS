import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

import styles from "./GaugeChart.module.scss";

export interface GaugeChartProps {
  value: number;
  max: number;
  leftLabel?: string;
  rightLabel?: string;
}

const GaugeChart: React.FC<GaugeChartProps> = ({
  value,
  max,
  leftLabel = "Low",
  rightLabel = "High",
}) => {
  // Four equal segments matching the Figma design from light to dark orange
  const segments = [
    { value: 1, color: "#FFE7D2" }, // Lightest orange
    { value: 1, color: "#FFCBA2" }, // Light orange
    { value: 1, color: "#FFA568" }, // Medium orange
    { value: 1, color: "#FF7219" }, // Dark orange
    { value: 1, color: "#FF3B00" }, // Dark orange
  ];

  // Calculate needle rotation based on value and max
  // percent goes from 0 to 1
  const percent = Math.min(Math.max(value / max, 0), 1);
  // rotation goes from -90deg (left) to 90deg (right)
  const rotation = -90 + percent * 180;

  return (
    <div className={styles.gaugeContainer}>
      <div className={styles.chartWrapper}>
        {/* We use a container that is twice the height visually to place the center at the bottom */}
        <div className={styles.pieContainer}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={segments}
                cx="50%"
                cy="50%"
                startAngle={180}
                endAngle={0}
                innerRadius="65%"
                outerRadius="95%"
                dataKey="value"
                stroke="#fff"
                strokeWidth={1}
              >
                {segments.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Triangle Indicator Needle */}
        {/* We want it to be positioned correctly on the inner boundary of the arc */}
        {/* Since the arc's center is at the bottom of THIS div: */}
        <div
          className={styles.needleContainer}
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        >
          {/* A downward/inward pointing triangle at the top of the rotational container */}
          <div className={styles.needle} />
        </div>
      </div>

      {/* Bottom Labels */}
      <div className={styles.labels}>
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>
    </div>
  );
};

export default GaugeChart;
