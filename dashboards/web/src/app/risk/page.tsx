import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { RiskBandBadge } from "@/components/RiskBandBadge";
import { api, ApiError } from "@/lib/api";
import { formatScore } from "@/lib/utils";

export default async function RiskPage() {
  try {
    const risk = await api.riskScores(undefined, 1, 500);
    const sorted = [...risk.items].sort((a, b) => b.score - a.score);

    const bandCounts = sorted.reduce(
      (acc, r) => {
        acc[r.risk_band] = (acc[r.risk_band] ?? 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    return (
      <div>
        <PageHeader
          title="Risk Analysis"
          description="Community-level Air Pollution Environmental-Health Risk Index (AP-EHRI). Scores combine PM2.5, respiratory rates, industrial proximity, vulnerability, poverty, and access gaps."
        />

        <div className="mb-8 flex flex-wrap gap-3">
          {Object.entries(bandCounts).map(([band, count]) => (
            <div
              key={band}
              className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 shadow-sm"
            >
              <RiskBandBadge band={band} />
              <span className="text-sm font-medium text-slate-700">{count}</span>
            </div>
          ))}
        </div>

        <DataTable
          columns={[
            { key: "community", label: "Community ID" },
            { key: "period", label: "Period ID" },
            { key: "score", label: "AP-EHRI", className: "font-mono" },
            { key: "band", label: "Risk band" },
            { key: "version", label: "Method" },
          ]}
          rows={sorted.map((r) => ({
            community: r.community_id,
            period: r.period_id,
            score: formatScore(r.score),
            band: <RiskBandBadge band={r.risk_band} />,
            version: r.methodology_version,
          }))}
          emptyMessage="No risk scores calculated yet. Run the risk model pipeline."
        />
      </div>
    );
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : "Could not load risk data.";
    return (
      <div>
        <PageHeader title="Risk Analysis" description="AP-EHRI community rankings." />
        <ApiErrorBanner message={msg} />
      </div>
    );
  }
}
