import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Text,
} from "recharts";
import styles from "./TrendChart.module.scss";

export interface TrendChartData {
  date: string;
  count: number;
  displayDate: string;
}

export interface TrendChartProps {
  data: TrendChartData[];
}

const CustomLabel = (props: any) => {
  const { x, y, value } = props;
  if (value === 0) return null;
  return (
    <text
      x={x}
      y={y - 10}
      fill="#272d37"
      fontSize={12}
      fontWeight={600}
      textAnchor="middle"
    >
      {value}
    </text>
  );
};

const TrendChart: React.FC<TrendChartProps> = ({ data }) => {
  return (
    <div className={styles.chartContainer}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 20, right: 10, left: -20, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FD5602" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#FD5602" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={true}
            horizontal={true}
            stroke="#F1F1F1"
          />
          <XAxis
            dataKey="displayDate"
            axisLine={true}
            tickLine={false}
            tick={{ fill: "#5F6D7E", fontSize: 10 }}
            dy={10}
            stroke="#F1F1F1"
          />
          <YAxis
            axisLine={true}
            tickLine={false}
            tick={{ fill: "#5F6D7E", fontSize: 10 }}
            stroke="#F1F1F1"
          />
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "none",
              boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)",
            }}
          />
          <Area
            type="linear"
            dataKey="count"
            stroke="#FD5602"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#colorCount)"
            dot={{
              r: 5,
              fill: "#fff",
              stroke: "#FD5602",
              strokeWidth: 2,
            }}
            activeDot={{ r: 7, fill: "#FD5602" }}
            label={<CustomLabel />}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;
