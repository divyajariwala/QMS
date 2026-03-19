import React from "react";
import DashboardStatsCard from "./InternalReviewStatsCard";
import DonutChart from "../charts/DonutChart";
import GaugeChart from "../charts/GaugeChart";
import DialIcon from "../../assets/icons/dialIcon.svg";
import BarChartIcon from "../../assets/icons/barChartIcon.svg";
import PieChart from "../../assets/icons/PieChart.svg";
import TrendChart from "../charts/TrendChart";
import { format } from "date-fns";

export interface InternalReviewStatsComponentsProps {
  total?: number;
  riskLevelSummary?: {
    major?: number;
    moderate?: number;
    minor?: number;
    unclassified?: number;
  };
  classificationSummary?: {
    scn?: number;
    non_scn?: number;
    unclassified?: number;
  };
  scnVolumeTrend?: {
    dates: string[];
    counts: number[];
  };
  avgProcessingTime?: {
    seconds: number;
    human_readable: string;
  };
}

const InternalReviewStatsComponents: React.FC<
  InternalReviewStatsComponentsProps
> = ({
  total = 0,
  riskLevelSummary,
  classificationSummary,
  scnVolumeTrend,
  avgProcessingTime,
}) => {
  // Card 1 Data
  const riskData = riskLevelSummary || { major: 0, moderate: 0, minor: 0 };
  const card1RawData = [
    { name: "Major", value: riskData.major || 0 },
    { name: "Moderate", value: riskData.moderate || 0 },
    { name: "Minor", value: riskData.minor || 0 },
  ];

  const card1Data = card1RawData.filter((d) => d.value > 0);
  const displayCard1Data =
    card1Data.length > 0 ? card1Data : [{ name: "No Data", value: 1 }];

  const getColorsForRisk = (data: { name: string; value: number }[]) => {
    return data.map((d) => {
      if (d.name === "Major") return "#FF7219";
      if (d.name === "Moderate") return "#FFAA72";
      if (d.name === "Minor") return "#EEEFF1";
      return "#E0E0E0";
    });
  };

  const card1Colors = getColorsForRisk(displayCard1Data);
  const card1Legend = card1RawData.map((d) => ({
    label: d.name,
    value: d.value,
    color: getColorsForRisk([d])[0],
  }));
  const card1Total = card1RawData.reduce((a, b) => a + b.value, 0);
  // Card 2 Data
  const classData = classificationSummary || { scn: 0, non_scn: 0 };
  const card2RawData = [
    { name: "SCN", value: classData.scn || 0 },
    { name: "Non SCN", value: classData.non_scn || 0 },
  ];

  const card2Data = card2RawData.filter((d) => d.value > 0);
  const displayCard2Data =
    card2Data.length > 0 ? card2Data : [{ name: "No Data", value: 1 }];

  const getColorsForClass = (data: { name: string; value: number }[]) => {
    return data.map((d) => {
      if (d.name === "SCN") return "#FF7219";
      if (d.name === "Non SCN") return "#EDEDEE";
      return "#E0E0E0";
    });
  };

  const card2Colors = getColorsForClass(displayCard2Data);
  const card2Legend = card2RawData.map((d) => ({
    label: d.name,
    value: d.value,
    color: getColorsForClass([d])[0],
  }));

  const card2Total = (classData.scn || 0) + (classData.non_scn || 0);

  // Card 4 Data
  const getDayWithSuffix = (dateStr: string) => {
    const date = new Date(dateStr);
    const day = date.getDate();
    const month = date.getMonth() + 1;
    const suffix = (day: number) => {
      if (day > 3 && day < 21) return "th";
      switch (day % 10) {
        case 1:
          return "st";
        case 2:
          return "nd";
        case 3:
          return "rd";
        default:
          return "th";
      }
    };
    return `${day}${suffix(day)}/${month}`;
  };

  const trendData = scnVolumeTrend
    ? scnVolumeTrend.dates.map((date, index) => ({
        date,
        count: scnVolumeTrend.counts[index],
        displayDate: getDayWithSuffix(date),
      }))
    : [];

  const trendTotal = scnVolumeTrend
    ? scnVolumeTrend.counts.reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(334px, 1fr))",
        gap: "16px",
        marginTop: "24px",
      }}
    >
      {/* Card 1 */}
      <DashboardStatsCard
        title="Total"
        value={card1Total}
        chartComponent={
          <DonutChart
            data={displayCard1Data}
            colors={card1Colors}
            innerRadius={0}
            outerRadius={60}
          />
        }
        legendItems={card1Legend}
        icon={<img src={PieChart} alt="Pie Chart" />}
      />

      {/* Card 2 */}
      <DashboardStatsCard
        title="SCN Vs Non SCN"
        value={card2Total}
        chartComponent={
          <DonutChart
            data={displayCard2Data}
            colors={card2Colors}
            innerRadius={0}
            outerRadius={60}
          />
        }
        legendItems={card2Legend}
        icon={<img src={DialIcon} alt="Dial" />}
      />

      {/* Card 3 */}
      {/* <DashboardStatsCard
        title="Average Time To Complete"
        value={avgProcessingTime?.human_readable || "5.2 Min"}
        chartComponent={
          <GaugeChart
            value={avgProcessingTime ? avgProcessingTime.seconds / 3600 : 5.2}
            max={
              avgProcessingTime
                ? Math.max(avgProcessingTime.seconds / 3600, 24)
                : 10
            }
            leftLabel="Low"
            rightLabel="High"
          />
        }
        icon={<img src={BarChartIcon} alt="Bar Chart" />}
      /> */}

      {/* Card 4 */}
      <DashboardStatsCard
        title="SCN Volumes In Last 5 Days"
        value={trendTotal}
        chartComponent={<TrendChart data={trendData} />}
        icon={<img src={BarChartIcon} alt="Trend Icon" />}
      />
    </div>
  );
};

export default InternalReviewStatsComponents;
