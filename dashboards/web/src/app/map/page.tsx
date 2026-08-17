import { PageHeader } from "@/components/PageHeader";
import Image from "next/image";

export default function MapPage() {
  return (
    <div>
      <PageHeader
        title="Geographic Risk Map"
        description="Community-level AP-EHRI visualization and exposure-source overlays. Generate maps with python -m geospatial.generate_maps."
      />

      <div className="grid gap-8 lg:grid-cols-2">
        <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-4 py-3">
            <h2 className="font-semibold text-slate-900">Risk choropleth</h2>
            <p className="text-sm text-slate-500">Static export from GeoPandas</p>
          </div>
          <div className="relative aspect-[4/5] w-full bg-slate-100">
            <Image
              src="/maps/risk_choropleth.png"
              alt="Verdania community AP-EHRI risk choropleth"
              fill
              className="object-contain p-2"
              unoptimized
            />
          </div>
        </section>

        <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-4 py-3">
            <h2 className="font-semibold text-slate-900">Interactive map</h2>
            <p className="text-sm text-slate-500">Folium HTML export (iframe)</p>
          </div>
          <iframe
            title="Verdania interactive risk map"
            src="/maps/interactive_risk_map.html"
            className="h-[480px] w-full border-0"
          />
        </section>
      </div>

      <p className="mt-6 text-sm text-slate-500">
        Map assets are copied from <code className="rounded bg-slate-100 px-1">geospatial/maps/</code>{" "}
        into <code className="rounded bg-slate-100 px-1">public/maps/</code> when you run{" "}
        <code className="rounded bg-slate-100 px-1">make web-maps</code> or the bootstrap script.
        For advanced GIS workflows, use the QGIS project under{" "}
        <code className="rounded bg-slate-100 px-1">geospatial/qgis/</code>.
      </p>
    </div>
  );
}
