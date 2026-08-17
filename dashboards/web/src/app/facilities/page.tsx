import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { ChartCard } from "@/components/charts/ChartCard";
import { SimplePie } from "@/components/charts/Charts";
import { DataTable } from "@/components/DataTable";
import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { api, ApiError } from "@/lib/api";

export default async function FacilitiesPage() {
  try {
    const [facilities, data] = await Promise.all([
      api.facilities(1, 500),
      api.dashboard(),
    ]);
    const withLab = facilities.items.filter((f) => f.has_lab_access).length;

    return (
      <div>
        <PageHeader
          title="Health System Capacity"
          description="Health facility distribution, laboratory access, and reporting capacity across Verdania."
        />

        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Total facilities" value={facilities.total} />
          <KpiCard
            label="With lab access"
            value={withLab}
            hint={
              facilities.total
                ? `${((withLab / facilities.total) * 100).toFixed(0)}% of facilities`
                : undefined
            }
            accent="success"
          />
          <KpiCard
            label="Air monitoring sites"
            value={data.kpis.monitoring_sites}
            accent="info"
          />
          <KpiCard
            label="Exposure sources"
            value={data.kpis.exposure_sources}
            accent="warning"
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <ChartCard title="Facilities by type" subtitle="Clinic, health centre, and hospital mix">
            <SimplePie
              data={data.facility_types.map((t) => ({
                name: String(t.type).replace(/_/g, " "),
                value: t.count,
              }))}
              nameKey="name"
              valueKey="value"
              colors={["#059669", "#4f46e5", "#f59e0b", "#0ea5e9"]}
            />
          </ChartCard>
          <ChartCard title="Laboratory access" subtitle="Share of facilities that can refer for testing">
            <SimplePie
              data={data.lab_access.map((t) => ({ name: t.label, value: t.count }))}
              nameKey="name"
              valueKey="value"
              colors={["#10b981", "#94a3b8"]}
            />
          </ChartCard>
        </div>

        <div className="mt-8">
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
