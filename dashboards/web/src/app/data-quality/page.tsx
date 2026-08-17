import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { api, ApiError } from "@/lib/api";
import { formatPercent } from "@/lib/utils";

export default async function DataQualityPage() {
  try {
    const dq = await api.dataQuality();

    return (
      <div>
        <PageHeader
          title="Data Quality"
          description="Automated completeness, validity, consistency, timeliness, uniqueness, and geographic accuracy scores for each integrated dataset."
        />

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

        <p className="mt-6 text-sm text-slate-500">
          Detailed issue rows are available via{" "}
          <code className="rounded bg-slate-100 px-1">GET /api/v1/data-quality</code> and in the
          Quarto data quality report under <code className="rounded bg-slate-100 px-1">reports/data_quality/</code>.
        </p>
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
