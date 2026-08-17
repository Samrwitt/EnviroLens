import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { ChartCard } from "@/components/charts/ChartCard";
import {
  ComponentRadar,
  DistrictRiskBars,
  HistogramChart,
  HorizontalBars,
  SensitivityBars,
  StackedBandChart,
} from "@/components/charts/Charts";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { RiskBandBadge } from "@/components/RiskBandBadge";
import { api, ApiError } from "@/lib/api";
import { formatScore } from "@/lib/utils";

export default async function RiskPage() {
  try {
    const [data, risk] = await Promise.all([api.dashboard(), api.riskScores(undefined, 1, 500)]);
    const period = data.latest_period_label ?? data.latest_period ?? "latest period";

    return (
      <div>
        <PageHeader
          title="Risk Analysis"
          description="AP-EHRI combines normalized PM2.5, respiratory rates, industrial proximity, vulnerability, poverty, access gaps, and reporting incompleteness. Charts below use the latest quarter unless labelled as a trend."
        />

        <div className="mb-6 flex flex-wrap gap-3">
          {data.risk_by_band.map((b) => (
            <div
              key={b.band}
              className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 shadow-sm"
            >
              <RiskBandBadge band={b.band} />
              <span className="text-sm font-medium text-slate-700">{b.count}</span>
              <span className="text-xs text-slate-400">{(b.share * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <ChartCard title="Score distribution" subtitle={`Histogram of community AP-EHRI · ${period}`}>
            <HistogramChart data={data.score_histogram} />
          </ChartCard>
          <ChartCard title="Index composition" subtitle="Mean normalized components (0–1)">
            <ComponentRadar data={data.component_means} />
          </ChartCard>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <ChartCard title="Risk bands by quarter" subtitle="Count of communities in each band">
            <StackedBandChart data={data.stacked_bands} />
          </ChartCard>
          <ChartCard title="District mean AP-EHRI" subtitle={period}>
            <DistrictRiskBars data={data.district_risk} />
          </ChartCard>
        </div>

        <div className="mt-6">
          <ChartCard
            title="Sensitivity: drop one component"
            subtitle="How much community ranks move when a weight is set to zero (others re-normalized). High rank shift = that factor is driving the league table."
          >
            <SensitivityBars data={data.sensitivity ?? []} />
          </ChartCard>
        </div>

        <div className="mt-6">
          <ChartCard title="Highest-scoring communities" subtitle="Latest period ranking">
            <HorizontalBars
              data={data.top_communities.map((c) => ({
                name: `${c.community} (${c.district.split(" ").slice(-2).join(" ")})`,
                score: Number(c.score.toFixed(3)),
              }))}
              xKey="score"
              yKey="name"
              color="#c2410c"
              xDomain={[0, 1]}
            />
          </ChartCard>
        </div>

        <h2 className="mb-3 mt-10 text-lg font-semibold text-slate-900">All community–period scores</h2>
        <DataTable
          columns={[
            { key: "community", label: "Community" },
            { key: "district", label: "District" },
            { key: "period", label: "Period" },
            { key: "score", label: "AP-EHRI", className: "font-mono" },
            { key: "band", label: "Band" },
            { key: "pm25", label: "PM2.5", className: "font-mono" },
            { key: "resp", label: "Respiratory", className: "font-mono" },
          ]}
          rows={risk.items.map((r) => ({
            community: r.community_name ?? `#${r.community_id}`,
            district: r.district_name ?? "—",
            period: r.period_code ?? r.period_id,
            score: formatScore(r.score),
            band: <RiskBandBadge band={r.risk_band} />,
            pm25: r.pm25_component != null ? formatScore(r.pm25_component) : "—",
            resp: r.respiratory_component != null ? formatScore(r.respiratory_component) : "—",
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
