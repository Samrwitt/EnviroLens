import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { ChartCard } from "@/components/charts/ChartCard";
import { SimplePie } from "@/components/charts/Charts";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { api, ApiError } from "@/lib/api";

export default async function MetadataPage() {
  try {
    const meta = await api.metadata();
    const bySensitivity = Object.entries(
      meta.items.reduce(
        (acc, m) => {
          const key = m.sensitivity_level ?? "unspecified";
          acc[key] = (acc[key] ?? 0) + 1;
          return acc;
        },
        {} as Record<string, number>,
      ),
    ).map(([name, value]) => ({ name, value }));

    const byFrequency = Object.entries(
      meta.items.reduce(
        (acc, m) => {
          const key = m.reporting_frequency ?? "unspecified";
          acc[key] = (acc[key] ?? 0) + 1;
          return acc;
        },
        {} as Record<string, number>,
      ),
    ).map(([name, value]) => ({ name, value }));

    return (
      <div>
        <PageHeader
          title="Metadata Catalogue"
          description="Dataset ownership, coverage, reporting frequency, sensitivity, and quality status for integrated sources."
        />

        <div className="mb-8 grid gap-6 lg:grid-cols-2">
          <ChartCard title="Sensitivity classification" subtitle="Catalogue records by access class">
            <SimplePie
              data={bySensitivity}
              nameKey="name"
              valueKey="value"
              colors={["#059669", "#f59e0b", "#ef4444", "#64748b"]}
            />
          </ChartCard>
          <ChartCard title="Reporting frequency" subtitle="How often contributing institutions update">
            <SimplePie
              data={byFrequency}
              nameKey="name"
              valueKey="value"
              colors={["#4f46e5", "#0ea5e9", "#10b981", "#94a3b8"]}
            />
          </ChartCard>
        </div>

        <DataTable
          columns={[
            { key: "dataset", label: "Dataset" },
            { key: "owner", label: "Owning institution" },
            { key: "coverage", label: "Coverage" },
            { key: "frequency", label: "Frequency" },
            { key: "sensitivity", label: "Sensitivity" },
            { key: "status", label: "DQ status" },
          ]}
          rows={meta.items.map((m) => ({
            dataset: m.dataset_name,
            owner: m.owning_institution,
            coverage: m.geographic_coverage ?? "—",
            frequency: m.reporting_frequency ?? "—",
            sensitivity: m.sensitivity_level ?? "—",
            status: m.data_quality_status ?? "—",
          }))}
        />
      </div>
    );
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : "Could not load metadata.";
    return (
      <div>
        <PageHeader title="Metadata Catalogue" description="Integrated dataset inventory." />
        <ApiErrorBanner message={msg} />
      </div>
    );
  }
}
