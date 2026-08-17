"use client";

import { RiskBandBadge } from "@/components/RiskBandBadge";
import type { ExplorerCommunity } from "@/lib/types";
import { formatScore } from "@/lib/utils";
import { useMemo, useState } from "react";

const LABELS: Record<string, string> = {
  pm25: "PM2.5 exposure",
  resp: "Respiratory burden",
  prox: "Industrial proximity",
  vuln: "Vulnerable population",
  pov: "Poverty",
  access: "Access gap",
  incomplete: "Reporting gaps",
};

const KEYS = ["pm25", "resp", "prox", "vuln", "pov", "access", "incomplete"] as const;
type WeightKey = (typeof KEYS)[number];

function bandFrom(score: number): string {
  if (score >= 0.75) return "very_high";
  if (score >= 0.55) return "high";
  if (score >= 0.35) return "moderate";
  return "low";
}

function toPercents(weights: Record<string, number>): Record<WeightKey, number> {
  return Object.fromEntries(
    KEYS.map((k) => [k, Math.round((weights[k] ?? 0) * 100)]),
  ) as Record<WeightKey, number>;
}

function weightedScore(row: ExplorerCommunity, pct: Record<WeightKey, number>): number {
  const total = KEYS.reduce((s, k) => s + pct[k], 0) || 1;
  return KEYS.reduce((s, k) => s + (pct[k] / total) * Number(row[k] || 0), 0);
}

export function WeightExplorer({
  communities,
  defaultWeights,
}: {
  communities: ExplorerCommunity[];
  defaultWeights: Record<string, number>;
}) {
  const baselinePct = useMemo(() => toPercents(defaultWeights), [defaultWeights]);
  const [pct, setPct] = useState(baselinePct);

  const baselineRanks = useMemo(() => {
    const ranked = [...communities].sort(
      (a, b) => weightedScore(b, baselinePct) - weightedScore(a, baselinePct),
    );
    return Object.fromEntries(ranked.map((r, i) => [r.community_code, i + 1]));
  }, [communities, baselinePct]);

  const ranked = useMemo(() => {
    return [...communities]
      .map((row) => {
        const score = weightedScore(row, pct);
        return {
          ...row,
          liveScore: score,
          liveBand: bandFrom(score),
          newRank: 0,
          delta: 0,
        };
      })
      .sort((a, b) => b.liveScore - a.liveScore)
      .map((row, i) => ({
        ...row,
        newRank: i + 1,
        delta: (baselineRanks[row.community_code] ?? i + 1) - (i + 1),
      }));
  }, [communities, pct, baselineRanks]);

  const total = KEYS.reduce((s, k) => s + pct[k], 0) || 1;
  const elevated = ranked.filter((r) => r.liveBand === "high" || r.liveBand === "very_high").length;

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Weight scenario</h2>
            <p className="mt-1 text-xs text-slate-500">
              Drag sliders to stress-test AP-EHRI. Ranks update instantly from stored components — the
              warehouse is not overwritten.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setPct(baselinePct)}
            className="shrink-0 rounded-md border border-slate-200 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            Reset v1.0
          </button>
        </div>
        <ul className="space-y-4">
          {KEYS.map((key) => (
            <li key={key}>
              <div className="mb-1 flex justify-between text-xs">
                <span className="font-medium text-slate-700">{LABELS[key]}</span>
                <span className="font-mono text-slate-500">
                  {((pct[key] / total) * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={50}
                value={pct[key]}
                onChange={(e) => setPct({ ...pct, [key]: Number(e.target.value) })}
                className="h-2 w-full cursor-pointer accent-emerald-600"
              />
            </li>
          ))}
        </ul>
        <p className="mt-4 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-600">
          Live classification: <strong>{elevated}</strong> of {ranked.length} communities high / very
          high under this scenario.
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-3">
        <div className="border-b border-slate-100 px-4 py-3">
          <h2 className="text-sm font-semibold text-slate-900">Live ranking</h2>
          <p className="text-xs text-slate-500">Δ rank vs published methodology v1.0</p>
        </div>
        <div className="max-h-[540px] overflow-auto">
          <table className="min-w-full text-sm">
            <thead className="sticky top-0 bg-slate-50 text-left text-xs font-semibold text-slate-500">
              <tr>
                <th className="px-3 py-2">#</th>
                <th className="px-3 py-2">Δ</th>
                <th className="px-3 py-2">Community</th>
                <th className="px-3 py-2">Score</th>
                <th className="px-3 py-2">Band</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {ranked.map((row) => (
                <tr key={row.community_code} className="hover:bg-slate-50/80">
                  <td className="px-3 py-2 font-mono text-xs text-slate-500">{row.newRank}</td>
                  <td className="px-3 py-2 font-mono text-xs">
                    {row.delta === 0 ? (
                      <span className="text-slate-400">0</span>
                    ) : row.delta > 0 ? (
                      <span className="text-red-600">↑{row.delta}</span>
                    ) : (
                      <span className="text-emerald-600">↓{Math.abs(row.delta)}</span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    <div className="font-medium text-slate-800">{row.community}</div>
                    <div className="text-xs text-slate-400">{row.district}</div>
                  </td>
                  <td className="px-3 py-2 font-mono text-xs">{formatScore(row.liveScore)}</td>
                  <td className="px-3 py-2">
                    <RiskBandBadge band={row.liveBand} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
