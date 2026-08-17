import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { ChartCard } from "@/components/charts/ChartCard";
import {
  DataQualityBars,
  HorizontalBars,
  MeanRiskArea,
  PollutionHealthTrend,
  RiskBandDonut,
} from "@/components/charts/Charts";
import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { RiskBandBadge } from "@/components/RiskBandBadge";
import { api, ApiError } from "@/lib/api";
import { formatCompact, formatNumber, formatPercent, formatScore } from "@/lib/utils";
import Link from "next/link";

export default async function OverviewPage() {
  try {
    const data = await api.dashboard();
    const { kpis } = data;
    const period = data.latest_period_label ?? data.latest_period ?? "latest period";

    return (
      <div>
        <PageHeader
          title="Environmental Health Intelligence"
          description={`Verdania air-pollution risk dashboard. KPIs and charts use ${period} unless a trend is shown. AP-EHRI supports public-health prioritization, not clinical diagnosis.`}
        />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4">
          <KpiCard
            label="Mean AP-EHRI"
            value={formatScore(kpis.mean_ap_ehri)}
            hint={`${period} · community average`}
          />
          <KpiCard
            label="High / very high risk"
            value={kpis.high_risk}
            hint={`of ${kpis.communities} communities`}
            accent="warning"
          />
          <KpiCard
            label="Mean PM2.5"
            value={`${kpis.mean_pm25.toFixed(1)} µg/m³`}
            hint="Valid ambient samples"
            accent="info"
          />
          <KpiCard
            label="Respiratory rate"
            value={kpis.mean_resp.toFixed(1)}
            hint="Encounters per 1,000"
            accent="warning"
          />
          <KpiCard
            label="Population covered"
            value={formatCompact(kpis.population)}
            hint={`${formatNumber(kpis.vulnerable)} under-5 + 65+`}
            accent="success"
          />
          <KpiCard
            label="Health facilities"
            value={kpis.facilities}
            hint={`${kpis.monitoring_sites} AQ sites · ${kpis.exposure_sources} sources`}
            accent="success"
          />
          <KpiCard
            label="Data quality"
            value={formatPercent(kpis.overall_dq)}
            hint="Mean across datasets"
          />
          <KpiCard
            label="Reporting period"
            value={data.latest_period ?? "—"}
            hint={data.latest_period_label ?? ""}
            accent="info"
          />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <ChartCard
            title="Risk band mix"
            subtitle={`Community AP-EHRI classification · ${period}`}
          >
            <RiskBandDonut data={data.risk_by_band} />
          </ChartCard>
          <ChartCard
            title="Highest-risk communities"
            subtitle="Top 12 AP-EHRI scores in the latest period"
          >
            <HorizontalBars
              data={data.top_communities.map((c) => ({
                name: c.community.replace("Community ", "C"),
                score: Number(c.score.toFixed(3)),
              }))}
              xKey="score"
              yKey="name"
              color="#dc2626"
              xDomain={[0, 1]}
            />
          </ChartCard>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <ChartCard
            title="Exposure and health trends"
            subtitle="Quarterly mean PM2.5 / NO₂ vs respiratory encounter rate"
          >
            <PollutionHealthTrend pollution={data.pollution_trend} health={data.health_trend} />
          </ChartCard>
          <ChartCard title="Mean AP-EHRI over time" subtitle="National community average by quarter">
            <MeanRiskArea data={data.risk_by_period} />
          </ChartCard>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-5">
          <ChartCard
            title="Data quality dimensions"
            subtitle="Percent scores by dataset"
            className="lg:col-span-3"
          >
            <DataQualityBars data={data.data_quality} />
          </ChartCard>
          <ChartCard
            title="Priority list"
            subtitle="Communities to investigate first"
            className="lg:col-span-2"
          >
            <ul className="space-y-2">
              {data.top_communities.slice(0, 8).map((c) => (
                <li
                  key={c.community_code}
                  className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
                >
                  <div>
                    <p className="text-sm font-medium text-slate-800">{c.community}</p>
                    <p className="text-xs text-slate-500">{c.district}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold">{formatScore(c.score)}</span>
                    <RiskBandBadge band={c.band} />
                  </div>
                </li>
              ))}
            </ul>
            <Link
              href="/risk"
              className="mt-4 inline-block text-sm font-medium text-brand-700 hover:text-brand-800"
            >
              Open full risk analysis →
            </Link>
          </ChartCard>
        </div>
      </div>
    );
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : "Could not reach the API.";
    return (
      <div>
        <PageHeader
          title="Environmental Health Intelligence"
          description="Connect to the FastAPI backend to load live indicators."
        />
        <ApiErrorBanner message={msg} />
      </div>
    );
  }
}
