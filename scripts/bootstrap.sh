#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
cp -n .env.example .env || true
docker compose up -d db redis
echo "Waiting for PostGIS..."
sleep 8
pip install -r requirements.txt
python -m synthetic_data.generators.generate_all
alembic upgrade head
python -m pipelines.run --all
python -m analysis.risk_model.calculate
python -m database.views.apply_views
python -m analysis.r.export_for_r || true
python -m geospatial.generate_maps || true
echo "Bootstrap complete. Start API with: make api"
