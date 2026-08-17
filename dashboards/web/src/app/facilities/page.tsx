import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { DataTable } from "@/components/DataTable";
import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { api, ApiError } from "@/lib/api";

export default async function FacilitiesPage() {
  try {
    const facilities = await api.facilities(1, 500);
    const withLab = facilities.items.filter((f) => f.has_lab_access).length;
    const byType = facilities.items.reduce(
      (acc, f) => {
        acc[f.facility_type] = (acc[f.facility_type] ?? 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    return (
      <div>
        <PageHeader
          title="Health System Capacity"
          description="Health facility distribution, laboratory access, and reporting capacity across Verdania."
        />

        <div className="mb-8 grid gap-4 sm:grid-cols-3">
          <KpiCard label="Total facilities" value={facilities.total} />
          <KpiCard
            label="With lab access"
            value={withLab}
            hint={`${((withLab / facilities.total) * 100).toFixed(0)}% of facilities`}
            accent="success"
          />
          <KpiCard label="Facility types" value={Object.keys(byType).length} />
        </div>

        <DataTable
          columns={[
            { key: "code", label: "Code" },
            { key: "name", label: "Name" },
            { key: "type", label: "Type" },
            { key: "lab", label: "Lab access" },
            { key: "community", label: "Community ID" },
          ]}
          rows={facilities.items.map((f) => ({
            code: f.code,
            name: f.name,
            type: f.facility_type.replace(/_/g, " "),
            lab: f.has_lab_access ? (
              <span className="text-emerald-700">Yes</span>
            ) : (
              <span className="text-slate-400">No</span>
            ),
            community: f.community_id ?? "—",
          }))}
        />
      </div>
    );
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : "Could not load facilities.";
    return (
      <div>
        <PageHeader title="Health System Capacity" description="Facility and lab coverage." />
        <ApiErrorBanner message={msg} />
      </div>
    );
  }
}
