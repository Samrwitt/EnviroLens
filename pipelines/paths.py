"""Path helpers for pipeline IO."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "synthetic_data"
CSV_DIR = SYNTH / "csv"
EXCEL_DIR = SYNTH / "excel"
JSON_DIR = SYNTH / "json"
BOUNDARIES = ROOT / "geospatial" / "boundaries"
