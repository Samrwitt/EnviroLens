"use client";

import { riskBandLabel } from "@/lib/utils";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const BAND_FILL: Record<string, string> = {
  low: "#10b981",
  moderate: "#eab308",
  high: "#f97316",
  very_high: "#ef4444",
};

const tooltipStyle = {
  backgroundColor: "#0f172a",
  border: "none",
  borderRadius: 8,
  fontSize: 12,
  color: "#f8fafc",
};

export function RiskBandDonut({
  data,
}: {
  data: { band: string; count: number }[];
}) {
  const chart = data.map((d) => ({
    ...d,
    name: riskBandLabel(d.band),
  }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={chart}
          dataKey="count"
          nameKey="name"
          innerRadius={62}
          outerRadius={92}
          paddingAngle={3}
          stroke="#fff"
          strokeWidth={2}
        >
          {chart.map((entry) => (
            <Cell key={entry.band} fill={BAND_FILL[entry.band] ?? "#94a3b8"} />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function HorizontalBars({
  data,
  xKey,
  yKey,
  color = "#059669",
  xDomain,
}: {
  data: Record<string, string | number>[];
  xKey: string;
  yKey: string;
  color?: string;
  xDomain?: [number, number];
}) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(240, data.length * 28)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
        <XAxis type="number" domain={xDomain} tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey={yKey} width={110} tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey={xKey} fill={color} radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function PollutionHealthTrend({
  pollution,
  health,
}: {
  pollution: { period: string; pm25: number | null; no2: number | null }[];
  health: { period: string; resp_rate: number | null }[];
}) {
  const healthMap = Object.fromEntries(health.map((h) => [h.period, h.resp_rate]));
  const data = pollution.map((p) => ({
    period: p.period,
    pm25: p.pm25,
    no2: p.no2,
    resp: healthMap[p.period] ?? null,
  }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="period" tick={{ fontSize: 11 }} />
        <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="pm25"
          name="PM2.5 (µg/m³)"
          stroke="#4f46e5"
          strokeWidth={2.5}
          dot={{ r: 3 }}
        />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="no2"
          name="NO₂ (µg/m³)"
          stroke="#0ea5e9"
          strokeWidth={2}
          strokeDasharray="4 3"
          dot={{ r: 3 }}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="resp"
          name="Respiratory rate / 1,000"
          stroke="#e11d48"
          strokeWidth={2.5}
          dot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function MeanRiskArea({
  data,
}: {
  data: { period: string; mean_score: number; elevated: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#059669" stopOpacity={0.35} />
            <stop offset="95%" stopColor="#059669" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="period" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Area
          type="monotone"
          dataKey="mean_score"
          name="Mean AP-EHRI"
          stroke="#047857"
          fill="url(#riskFill)"
          strokeWidth={2.5}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function StackedBandChart({
  data,
}: {
  data: { period: string; low: number; moderate: number; high: number; very_high: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="period" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend />
        <Bar dataKey="low" stackId="a" fill={BAND_FILL.low} name="Low" />
        <Bar dataKey="moderate" stackId="a" fill={BAND_FILL.moderate} name="Moderate" />
        <Bar dataKey="high" stackId="a" fill={BAND_FILL.high} name="High" />
        <Bar
          dataKey="very_high"
          stackId="a"
          fill={BAND_FILL.very_high}
          name="Very high"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HistogramChart({ data }: { data: { bucket: string; count: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey="count" name="Communities" fill="#6366f1" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ComponentRadar({ data }: { data: { component: string; value: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid stroke="#cbd5e1" />
        <PolarAngleAxis dataKey="component" tick={{ fontSize: 11 }} />
        <PolarRadiusAxis domain={[0, 1]} tick={{ fontSize: 10 }} />
        <Radar
          name="Mean component (0–1)"
          dataKey="value"
          stroke="#047857"
          fill="#10b981"
          fillOpacity={0.35}
        />
        <Tooltip contentStyle={tooltipStyle} />
      </RadarChart>
    </ResponsiveContainer>
  );
}

export function DataQualityBars({
  data,
}: {
  data: {
    dataset_name: string;
    completeness: number;
    validity: number;
    consistency: number;
    timeliness: number;
    uniqueness: number;
    geographic_accuracy: number;
  }[];
}) {
  const chart = data.map((d) => ({
    name: d.dataset_name.replace("Community ", "").replace("Facility ", "").slice(0, 28),
    Completeness: Math.round(d.completeness * 1000) / 10,
    Validity: Math.round(d.validity * 1000) / 10,
    Consistency: Math.round(d.consistency * 1000) / 10,
    Timeliness: Math.round(d.timeliness * 1000) / 10,
    Uniqueness: Math.round(d.uniqueness * 1000) / 10,
    Geo: Math.round(d.geographic_accuracy * 1000) / 10,
  }));
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={chart}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend />
        <Bar dataKey="Completeness" fill="#059669" />
        <Bar dataKey="Validity" fill="#4f46e5" />
        <Bar dataKey="Consistency" fill="#0ea5e9" />
        <Bar dataKey="Timeliness" fill="#f59e0b" />
        <Bar dataKey="Uniqueness" fill="#8b5cf6" />
        <Bar dataKey="Geo" fill="#64748b" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function SimplePie({
  data,
  nameKey,
  valueKey,
  colors,
}: {
  data: Record<string, string | number>[];
  nameKey: string;
  valueKey: string;
  colors: string[];
}) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          dataKey={valueKey}
          nameKey={nameKey}
          outerRadius={90}
          label
          stroke="#fff"
        >
          {data.map((_, i) => (
            <Cell key={i} fill={colors[i % colors.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function DistrictRiskBars({
  data,
}: {
  data: { district: string; mean_score: number; elevated: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(260, data.length * 26)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
        <XAxis type="number" domain={[0, 1]} tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey="district" width={130} tick={{ fontSize: 10 }} />
        <Tooltip contentStyle={tooltipStyle} />
        <Bar dataKey="mean_score" name="Mean AP-EHRI" fill="#0f766e" radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
