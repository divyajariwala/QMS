import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Label } from 'recharts';

import styles from './DonutChart.module.scss';

export interface DonutChartData {
  name: string;
  value: number;
}

export interface DonutChartProps {
  data: DonutChartData[];
  colors: string[];
  centerValue?: string | number;
  centerSubtitle?: string;
  innerRadius?: number | string;
  outerRadius?: number | string;
  paddingAngle?: number;
}

const DonutChart: React.FC<DonutChartProps> = ({ 
  data, 
  colors, 
  centerValue, 
  centerSubtitle,
  innerRadius = 45,
  outerRadius = 60,
  paddingAngle = 0
}) => {
  return (
    <div className={styles.donutContainer}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={outerRadius}
            paddingAngle={paddingAngle}
            dataKey="value"
            stroke="#fff"
            strokeWidth={1}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
            {centerValue && (
              <Label
                value={centerValue}
                position="center"
                className={styles.centerLabel}
              />
            )}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DonutChart;
