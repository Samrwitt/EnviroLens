import type { RiskBand } from "@/lib/types";

export function riskBandLabel(band: string): string {
  return band.replace(/_/g, " ");
}

export function riskBandColor(band: string): string {
  const map: Record<RiskBand, string> = {
    low: "bg-emerald-100 text-emerald-800 border-emerald-200",
    moderate: "bg-amber-100 text-amber-800 border-amber-200",
    high: "bg-orange-100 text-orange-800 border-orange-200",
    very_high: "bg-red-100 text-red-800 border-red-200",
  };
  return map[band as RiskBand] ?? "bg-slate-100 text-slate-700 border-slate-200";
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatScore(value: number): string {
  return value.toFixed(3);
}

export function avg(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((a, b) => a + b, 0) / values.length;
}
