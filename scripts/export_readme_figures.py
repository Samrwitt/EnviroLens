"""Export README figures from the live warehouse (maps + analytics charts)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from sqlalchemy import text

from api.services.analytics import dashboard_payload
from database.session import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
MAPS = ROOT / "geospatial" / "maps"

COLORS = {
    "low": "#10b981",
    "moderate": "#eab308",
    "high": "#f97316",
    "very_high": "#ef4444",
    "brand": "#047857",
    "indigo": "#4f46e5",
}


def _style():
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#e2e8f0",
            "axes.grid": True,
            "grid.color": "#e2e8f0",
            "grid.linestyle": "--",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "semibold",
        }
    )


def copy_maps() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("risk_choropleth.png", "exposure_sources.png", "facility_access.png"):
        src = MAPS / name
        if src.exists():
            dest = OUT / name
            dest.write_bytes(src.read_bytes())


def risk_band_chart(payload: dict) -> None:
    rows = payload.get("risk_by_band") or []
    if not rows:
        return
    df = pd.DataFrame(rows)
    order = ["low", "moderate", "high", "very_high"]
    df["band"] = pd.Categorical(df["band"], categories=order, ordered=True)
    df = df.sort_values("band")
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    bars = ax.bar(
        df["band"].astype(str).str.replace("_", " "),
        df["count"],
        color=[COLORS.get(b, "#64748b") for b in df["band"]],
    )
    ax.bar_label(bars, padding=3)
    ax.set_title("Community AP-EHRI bands — latest quarter")
    ax.set_ylabel("Communities")
    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))
    fig.tight_layout()
    fig.savefig(OUT / "risk_bands.png", dpi=160)
    plt.close(fig)


def pollution_trend_chart(payload: dict) -> None:
    poll = pd.DataFrame(payload.get("pollution_trend") or [])
    health = pd.DataFrame(payload.get("health_trend") or [])
    if poll.empty:
        return
    df = poll.merge(health, on="period", how="left")
    fig, ax1 = plt.subplots(figsize=(7.2, 3.8))
    ax1.plot(df["period"], df["pm25"], color=COLORS["indigo"], marker="o", label="PM2.5")
    ax1.plot(df["period"], df["no2"], color="#0ea5e9", marker="o", linestyle="--", label="NO₂")
    ax1.set_ylabel("µg/m³")
    ax2 = ax1.twinx()
    ax2.plot(df["period"], df["resp_rate"], color="#e11d48", marker="s", label="Resp. rate / 1,000")
    ax2.set_ylabel("Encounters per 1,000")
    ax1.set_title("Ambient pollution vs respiratory encounter rate")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "pollution_health_trend.png", dpi=160)
    plt.close(fig)


def sensitivity_chart(payload: dict) -> None:
    df = pd.DataFrame(payload.get("sensitivity") or [])
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.bar(df["label"], df["mean_rank_shift"], color=COLORS["indigo"])
    ax.set_title("Sensitivity: mean rank shift if a weight is dropped")
    ax.set_ylabel("Mean |Δ rank|")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(OUT / "sensitivity.png", dpi=160)
    plt.close(fig)


def top_communities_chart(payload: dict) -> None:
    df = pd.DataFrame(payload.get("top_communities") or [])
    if df.empty:
        return
    df = df.head(8).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.barh(df["community"], df["score"], color="#dc2626")
    ax.set_xlim(0, 1)
    ax.set_xlabel("AP-EHRI")
    ax.set_title("Highest-risk communities — latest quarter")
    fig.tight_layout()
    fig.savefig(OUT / "top_communities.png", dpi=160)
    plt.close(fig)


def dq_chart(payload: dict) -> None:
    df = pd.DataFrame(payload.get("data_quality") or [])
    if df.empty:
        return
    dims = [
        "completeness",
        "validity",
        "consistency",
        "timeliness",
        "uniqueness",
        "geographic_accuracy",
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    x = range(len(df))
    width = 0.12
    colors = ["#059669", "#4f46e5", "#0ea5e9", "#f59e0b", "#8b5cf6", "#64748b"]
    for i, dim in enumerate(dims):
        offset = (i - 2.5) * width
        ax.bar([xi + offset for xi in x], df[dim] * 100, width=width, label=dim.replace("_", " "), color=colors[i])
    ax.set_xticks(list(x))
    ax.set_xticklabels([n.replace("Community ", "").replace("Facility ", "")[:22] for n in df["dataset_name"]], rotation=12, ha="right")
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    ax.set_title("Data-quality dimensions by dataset")
    ax.legend(ncols=3, fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "data_quality.png", dpi=160)
    plt.close(fig)


def main() -> None:
    _style()
    copy_maps()
    session = SessionLocal()
    try:
        payload = dashboard_payload(session)
    finally:
        session.close()
    risk_band_chart(payload)
    pollution_trend_chart(payload)
    sensitivity_chart(payload)
    top_communities_chart(payload)
    dq_chart(payload)
    print(f"Wrote README figures to {OUT}")


if __name__ == "__main__":
    main()
