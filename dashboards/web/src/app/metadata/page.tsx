import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { DataTable } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { api, ApiError } from "@/lib/api";

export default async function MetadataPage() {
  try {
    const meta = await api.metadata();

    return (
      <div>
        <PageHeader
          title="Metadata Catalogue"
          description="Dataset ownership, coverage, reporting frequency, sensitivity, and quality status for integrated sources."
        />

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
