import { ChartCard } from "@/components/charts/ChartCard";
import { DistrictRiskBars } from "@/components/charts/Charts";
import { PageHeader } from "@/components/PageHeader";
import { api } from "@/lib/api";
import Image from "next/image";

export default async function MapPage() {
  let districts: { district: string; mean_score: number; elevated: number }[] = [];
  try {
    const data = await api.dashboard();
    districts = data.district_risk;
  } catch {
    districts = [];
  }

  return (
    <div>
      <PageHeader
        title="Geographic Risk Map"
        description="Spatial view of AP-EHRI, industrial exposure sources, and health-facility coverage. Static layers are GeoPandas exports; the interactive map is Folium."
      />

      {districts.length > 0 && (
        <div className="mb-8">
          <ChartCard title="District mean AP-EHRI" subtitle="Latest reporting period">
            <DistrictRiskBars data={districts} />
          </ChartCard>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <MapPanel title="Risk choropleth" caption="Community AP-EHRI (YlOrRd)">
          <Image
            src="/maps/risk_choropleth.png"
            alt="Verdania community AP-EHRI risk choropleth"
            fill
            className="object-contain p-2"
            unoptimized
          />
        </MapPanel>
        <MapPanel title="Interactive map" caption="Folium overlay of risk polygons and sources">
          <iframe
            title="Verdania interactive risk map"
            src="/maps/interactive_risk_map.html"
            className="h-full min-h-[420px] w-full border-0"
          />
        </MapPanel>
        <MapPanel title="Exposure sources" caption="Industrial / power / quarry sites">
          <Image
            src="/maps/exposure_sources.png"
            alt="Industrial exposure sources in Verdania"
            fill
            className="object-contain p-2"
            unoptimized
          />
        </MapPanel>
        <MapPanel title="Health facilities" caption="Clinic and hospital locations">
          <Image
            src="/maps/facility_access.png"
            alt="Health facility distribution"
            fill
            className="object-contain p-2"
            unoptimized
          />
        </MapPanel>
      </div>
    </div>
  );
}

function MapPanel({
  title,
  caption,
  children,
}: {
  title: string;
  caption: string;
  children: React.ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
        <p className="text-xs text-slate-500">{caption}</p>
      </div>
      <div className="relative aspect-[4/5] w-full bg-slate-50">{children}</div>
    </section>
  );
}
