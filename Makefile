.PHONY: help up down install synth migrate pipeline risk api test maps reports lint

help:
	@echo "EnviroLens make targets:"
	@echo "  make up        - Start PostGIS + Redis"
	@echo "  make down      - Stop containers"
	@echo "  make install   - Install Python deps"
	@echo "  make synth     - Generate synthetic Verdania data"
	@echo "  make migrate   - Run Alembic migrations"
	@echo "  make pipeline  - Run ETL + DQ + load"
	@echo "  make risk      - Calculate AP-EHRI risk scores"
	@echo "  make api       - Run FastAPI locally"
	@echo "  make maps      - Generate geospatial map exports"
	@echo "  make reports   - Render Quarto reports (requires Quarto + R)"
	@echo "  make test      - Run pytest"
	@echo "  make lint      - Run ruff"

up:
	docker compose up -d db redis

down:
	docker compose down

install:
	pip install -r requirements.txt

synth:
	python -m synthetic_data.generators.generate_all

migrate:
	alembic upgrade head

pipeline:
	python -m pipelines.run --all

risk:
	python -m analysis.risk_model.calculate
	python -m database.views.apply_views

api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

maps:
	python -m geospatial.generate_maps

reports:
	cd reports/quarto && quarto render envirolens_technical_report.qmd
	cd reports/policy_briefs && quarto render policy_brief.qmd || true
	cd reports/data_quality && quarto render data_quality_report.qmd || true

bootstrap:
	bash scripts/bootstrap.sh

test:
	PYTHONPATH=. pytest -q

lint:
	ruff check api pipelines database analysis integrations synthetic_data tests || true
