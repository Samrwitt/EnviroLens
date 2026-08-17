import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { ChartCard } from "@/components/charts/ChartCard";
import { DataQualityBars } from "@/components/charts/Charts";
import { DataTable } from "@/components/DataTable";
import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { api, ApiError } from "@/lib/api";
import { avg, formatPercent } from "@/lib/utils";

const DIMENSIONS = [
  "completeness",
  "validity",
  "consistency",
  "timeliness",
  "uniqueness",
  "geographic_accuracy",
] as const;

export default async function DataQualityPage() {
  try {
    const [dq, data] = await Promise.all([api.dataQuality(), api.dashboard()]);
    const meanOverall = avg(dq.items.map((d) => d.overall));

    return (
      <div>
        <PageHeader
          title="Data Quality"
          description="Automated completeness, validity, consistency, timeliness, uniqueness, and geographic accuracy scores for each integrated dataset."
        />

        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Datasets scored" value={dq.total} />
          <KpiCard
            label="Mean overall score"
            value={formatPercent(meanOverall)}
            accent="success"
          />
          <KpiCard
            label="Lowest overall"
            value={
              dq.items.length
                ? formatPercent(Math.min(...dq.items.map((d) => d.overall)))
                : "—"
            }
            accent="warning"
          />
          <KpiCard
            label="Highest overall"
            value={
              dq.items.length
                ? formatPercent(Math.max(...dq.items.map((d) => d.overall)))
                : "—"
            }
            accent="info"
          />
        </div>

        <ChartCard title="Quality dimensions by dataset" subtitle="Percent of records passing each check">
          <DataQualityBars data={data.data_quality} />
        </ChartCard>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {dq.items.map((d) => (
            <article
              key={d.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <p className="text-sm font-semibold text-slate-900">{d.dataset_name}</p>
              <p className="mt-1 font-mono text-2xl font-semibold text-brand-700">
                {formatPercent(d.overall)}
              </p>
              <ul className="mt-4 space-y-2">
                {DIMENSIONS.map((key) => (
                  <li key={key}>
                    <div className="mb-1 flex justify-between text-xs text-slate-500">
                      <span className="capitalize">{key.replace("_", " ")}</span>
                      <span className="font-mono">{formatPercent(d[key])}</span>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-brand-500"
                        style={{ width: `${Math.min(100, d[key] * 100)}%` }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>

        <div className="mt-8">
          <DataTable
            columns={[
              { key: "dataset", label: "Dataset" },
              { key: "overall", label: "Overall" },
              { key: "completeness", label: "Completeness" },
              { key: "validity", label: "Validity" },
              { key: "consistency", label: "Consistency" },
              { key: "timeliness", label: "Timeliness" },
              { key: "uniqueness", label: "Uniqueness" },
              { key: "geo", label: "Geo accuracy" },
            ]}
            rows={dq.items.map((d) => ({
              dataset: d.dataset_name,
              overall: formatPercent(d.overall),
              completeness: formatPercent(d.completeness),
              validity: formatPercent(d.validity),
              consistency: formatPercent(d.consistency),
              timeliness: formatPercent(d.timeliness),
              uniqueness: formatPercent(d.uniqueness),
              geo: formatPercent(d.geographic_accuracy),
            }))}
          />
        </div>
      </div>
    );
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : "Could not load data quality scores.";
    return (
      <div>
        <PageHeader title="Data Quality" description="Dataset quality dimension scores." />
        <ApiErrorBanner message={msg} />
      </div>
    );
  }
}
