import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { RiskBandBadge } from "@/components/RiskBandBadge";
import { api, ApiError } from "@/lib/api";
import { avg, formatPercent, formatScore } from "@/lib/utils";
import Link from "next/link";

export default async function OverviewPage() {
  try {
    const [regions, facilities, risk, dq, metadata] = await Promise.all([
      api.regions(),
      api.facilities(),
      api.riskScores(undefined, 1, 500),
      api.dataQuality(),
      api.metadata(),
    ]);

    const highRisk = risk.items.filter((r) => r.risk_band === "high" || r.risk_band === "very_high");
    const avgDq = avg(dq.items.map((d) => d.overall));
    const latestScores = risk.items.slice(0, 8);

    return (
      <div>
        <PageHeader
          title="Executive Overview"
          description="Integrated environmental, health, and vulnerability intelligence for Verdania. AP-EHRI scores help prioritize communities with elevated air-pollution-related health risk."
        />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Regions" value={regions.total} hint="Administrative coverage" />
          <KpiCard
            label="Health facilities"
            value={facilities.total}
            hint="Reporting facilities"
            accent="success"
          />
          <KpiCard
            label="High-risk communities"
            value={highRisk.length}
            hint="AP-EHRI high / very high"
            accent="warning"
          />
          <KpiCard
            label="Overall data quality"
            value={formatPercent(avgDq)}
            hint="Mean across datasets"
          />
        </div>

        <div className="mt-10 grid gap-8 lg:grid-cols-2">
          <section>
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Top risk scores</h2>
            <ul className="space-y-2">
              {latestScores
                .sort((a, b) => b.score - a.score)
                .slice(0, 6)
                .map((r) => (
                  <li
                    key={r.id}
                    className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3"
                  >
                    <span className="text-sm text-slate-600">Community #{r.community_id}</span>
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-sm font-medium">{formatScore(r.score)}</span>
                      <RiskBandBadge band={r.risk_band} />
                    </div>
                  </li>
                ))}
            </ul>
            <Link
              href="/risk"
              className="mt-3 inline-block text-sm font-medium text-brand-700 hover:text-brand-800"
            >
              View all risk scores →
            </Link>
          </section>

          <section>
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Catalogued datasets</h2>
            <ul className="space-y-3">
              {metadata.items.map((m) => (
                <li
                  key={m.id}
                  className="rounded-lg border border-slate-200 bg-white px-4 py-3"
                >
                  <p className="font-medium text-slate-900">{m.dataset_name}</p>
                  <p className="text-sm text-slate-500">{m.owning_institution}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    {m.reporting_frequency ?? "—"} · {m.data_quality_status ?? "unknown status"}
                  </p>
                </li>
              ))}
            </ul>
            <Link
              href="/metadata"
              className="mt-3 inline-block text-sm font-medium text-brand-700 hover:text-brand-800"
            >
              Browse metadata →
            </Link>
          </section>
        </div>
      </div>
    );
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : "Could not reach the API.";
    return (
      <div>
        <PageHeader
          title="Executive Overview"
          description="Connect to the FastAPI backend to load live indicators."
        />
        <ApiErrorBanner message={msg} />
      </div>
    );
  }
}
