# QGIS Project Notes — EnviroLens Verdania

## Recommended layers

1. `geospatial/boundaries/verdania_admin.geojson` — filter `level = community` for choropleth
2. `geospatial/boundaries/exposure_sources.geojson` — point symbols (red)
3. `geospatial/boundaries/facilities.geojson` — point symbols (blue)
4. `geospatial/boundaries/monitoring_sites.geojson` — point symbols (green)

## PostGIS connection (preferred when DB is running)

- Host: `localhost`
- Database: `envirolens`
- User / password: from `.env`
- Key layers: `communities`, `exposure_sources`, `health_facilities`, view `vw_risk_map`

## Styling

- Risk choropleth: graduated on `score` (YlOrRd), bands aligned to AP-EHRI
- Overlay industrial sources at 70% opacity

## Project file

Open `envirolens_verdania.qgz` in QGIS 3.28+ after generating GeoJSON boundaries (`python -m synthetic_data.generators.generate_all`). If the `.qgz` is a placeholder zip, recreate layers via Browser → GeoJSON / PostGIS.
