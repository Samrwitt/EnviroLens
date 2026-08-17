import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { ChartCard } from "@/components/charts/ChartCard";
import {
  DataQualityBars,
  HorizontalBars,
  MeanRiskArea,
  PollutionHealthTrend,
  RiskBandDonut,
} from "@/components/charts/Charts";
import { InsightGrid } from "@/components/InsightGrid";
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
        <section className="mb-8 overflow-hidden rounded-2xl border border-emerald-900/10 bg-gradient-to-br from-brand-900 via-emerald-900 to-slate-900 px-6 py-8 text-white shadow-lg sm:px-8">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-200">
            Verdania · {period}
          </p>
          <h1 className="mt-2 max-w-3xl text-3xl font-semibold tracking-tight sm:text-4xl">
            Where air pollution, health burden, and vulnerability coincide
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-emerald-100/90">
            EnviroLens fuses ambient PM2.5/NO₂, facility respiratory reports, and community
            socioeconomic data into a transparent AP-EHRI index. Use it to prioritize surveillance —
            not to diagnose patients.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/explorer"
              className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-brand-900 hover:bg-emerald-50"
            >
              Open weight lab
            </Link>
            <Link
              href="/map"
              className="rounded-lg border border-white/30 px-4 py-2 text-sm font-semibold text-white hover:bg-white/10"
            >
              View risk map
            </Link>
          </div>
        </section>

        {data.insights?.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Analyst briefing
            </h2>
            <InsightGrid insights={data.insights} />
          </div>
        )}

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
