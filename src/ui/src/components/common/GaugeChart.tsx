import React from "react";
import styles from "./GaugeChart.module.scss";

interface GaugeProps {
  value: number; // 0 - 1
  size?: number;
  label?: string;
}

const Gauge: React.FC<GaugeProps> = ({ value, size = 200, label }) => {
  const radius = 80;
  const circumference = Math.PI * radius;
  const strokeWidth = 28;
  const normalizedValue = Math.max(0, Math.min(1, value));
  const visualTotal = circumference + strokeWidth;
  const progress = Math.max(0, normalizedValue * visualTotal - strokeWidth);

  const getColor = () => {
    if (normalizedValue <= 0.35) return "#DA291C";
    if (normalizedValue <= 0.7) return "#BF8900";
    return "#4EAD58";
  };

  return (
    <div
      className={styles.gauge}
      style={
        {
          width: size,
          "--gauge-size": `${size}px`,
        } as React.CSSProperties
      }
    >
      <svg viewBox="0 0 200 110" className={styles.gaugeSvg}>
        {/* background */}
        <path
          d="M20 100 A80 80 0 0 1 180 100"
          className={styles.gaugeBg}
          style={{ strokeWidth }}
        />

        {/* progress */}
        <path
          d="M20 100 A80 80 0 0 1 180 100"
          className={styles.gaugeProgress}
          style={{
            stroke: getColor(),
            strokeWidth,
            strokeDasharray: circumference,
            strokeDashoffset: circumference - progress,
          }}
        />
      </svg>

      <div className={styles.gaugeValue}>{normalizedValue.toFixed(2)}</div>

      <div className={styles.gaugeLabels}>
        <span className={styles.labelPoor}>Poor</span>
        <span className={styles.labelPoor}>{label}</span>
        <span className={styles.labelGood}>Good</span>
      </div>
    </div>
  );
};

export default Gauge;
