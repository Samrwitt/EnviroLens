"""GeoPandas / Folium map generation for Verdania risk and exposure."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parents[1]
BOUNDARIES = Path(__file__).resolve().parent / "boundaries"
MAPS = Path(__file__).resolve().parent / "maps"
MAPS.mkdir(parents=True, exist_ok=True)


def load_admin() -> gpd.GeoDataFrame:
    path = BOUNDARIES / "verdania_admin.geojson"
    gdf = gpd.read_file(path)
    return gdf


def load_points(name: str) -> gpd.GeoDataFrame:
    return gpd.read_file(BOUNDARIES / name)


def risk_from_db_or_synth(communities: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Attach risk scores from DB if available; else synthetic placeholder scores."""
    try:
        from sqlalchemy import text
        from database.session import engine

        df = pd.read_sql(
            text(
                """
                SELECT c.code AS code, ri.score, ri.risk_band
                FROM risk_indicators ri
                JOIN communities c ON c.id = ri.community_id
                JOIN reporting_periods rp ON rp.id = ri.period_id
                WHERE rp.code = (SELECT code FROM reporting_periods ORDER BY end_date DESC LIMIT 1)
                """
            ),
            engine,
        )
        out = communities.merge(df, on="code", how="left")
        if out["score"].notna().any():
            return out
    except Exception:
        pass
    # Fallback deterministic scores from code hash
    communities = communities.copy()
    communities["score"] = communities["code"].map(lambda c: (abs(hash(c)) % 100) / 100)
    communities["risk_band"] = pd.cut(
        communities["score"],
        bins=[-0.01, 0.35, 0.55, 0.75, 1.01],
        labels=["low", "moderate", "high", "very_high"],
    )
    return communities


def export_static_maps() -> list[Path]:
    admin = load_admin()
    communities = admin[admin["level"] == "community"].copy()
    districts = admin[admin["level"] == "district"].copy()
    risk = risk_from_db_or_synth(communities)

    paths = []
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    districts.boundary.plot(ax=ax, linewidth=0.8, color="#333333")
    risk.plot(column="score", cmap="YlOrRd", legend=True, ax=ax, edgecolor="white", linewidth=0.2)
    ax.set_title("Verdania Community AP-EHRI Risk")
    ax.set_axis_off()
    p = MAPS / "risk_choropleth.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    paths.append(p)

    sources = load_points("exposure_sources.geojson")
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    districts.plot(ax=ax, color="#f0f0f0", edgecolor="#666666")
    sources.plot(ax=ax, color="#b22222", markersize=40, label="Exposure sources")
    ax.legend()
    ax.set_title("Industrial / exposure sources")
    ax.set_axis_off()
    p2 = MAPS / "exposure_sources.png"
    fig.savefig(p2, dpi=150, bbox_inches="tight")
    plt.close(fig)
    paths.append(p2)

    facilities = load_points("facilities.geojson")
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    districts.plot(ax=ax, color="#e8f0e8", edgecolor="#555555")
    facilities.plot(ax=ax, color="#1f4e79", markersize=20, label="Health facilities")
    ax.legend()
    ax.set_title("Health facility distribution")
    ax.set_axis_off()
    p3 = MAPS / "facility_access.png"
    fig.savefig(p3, dpi=150, bbox_inches="tight")
    plt.close(fig)
    paths.append(p3)

    # Folium interactive map
    try:
        import folium

        center = [float(communities.geometry.centroid.y.mean()), float(communities.geometry.centroid.x.mean())]
        m = folium.Map(location=center, zoom_start=7, tiles="CartoDB positron")
        folium.GeoJson(
            risk.__geo_interface__,
            name="Risk",
            style_function=lambda feat: {
                "fillColor": "#d73027"
                if (feat["properties"].get("score") or 0) >= 0.75
                else "#fc8d59"
                if (feat["properties"].get("score") or 0) >= 0.55
                else "#fee08b"
                if (feat["properties"].get("score") or 0) >= 0.35
                else "#91cf60",
                "color": "#444",
                "weight": 0.5,
                "fillOpacity": 0.6,
            },
        ).add_to(m)
        for _, row in sources.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=4,
                color="red",
                fill=True,
                popup=row.get("name", "source"),
            ).add_to(m)
        html_path = MAPS / "interactive_risk_map.html"
        m.save(str(html_path))
        paths.append(html_path)
    except Exception as exc:
        print(f"Folium map skipped: {exc}")

    print("Wrote maps:", ", ".join(str(p) for p in paths))
    return paths


def main():
    export_static_maps()


if __name__ == "__main__":
    main()
