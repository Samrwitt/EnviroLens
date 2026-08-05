"""CLI and Prefect flow entrypoint for EnviroLens ETL."""

from __future__ import annotations

import argparse
import logging

from pipelines.cleaning.transforms import (
    clean_environmental,
    clean_health,
    clean_population,
    clean_ses,
)
from pipelines.ingestion.loaders import load_core_datasets, load_reference_frames
from pipelines.loading.load_db import (
    load_fact_tables,
    load_reference,
    persist_dq,
    seed_metadata_catalogue,
)
from pipelines.validation.dq_engine import (
    mark_valid_environmental,
    mark_valid_health,
    validate_environmental,
    validate_health,
    validate_population,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("envirolens.pipeline")


def run_pipeline() -> dict:
    from database.session import SessionLocal

    log.info("Loading reference and core datasets")
    refs = load_reference_frames()
    core = load_core_datasets()

    env = clean_environmental(core["environmental_samples"])
    health = clean_health(core["health_observations"])
    pop = clean_population(core["population_estimates"])
    ses = clean_ses(core["socioeconomic_indicators"])

    valid_districts = set(refs["admin"].loc[refs["admin"]["level"] == "district", "code"])
    valid_facilities = set(refs["facilities"]["code"])

    dq_env = validate_environmental(env, valid_districts)
    dq_health = validate_health(health, valid_facilities)
    dq_pop = validate_population(pop)

    env_valid = mark_valid_environmental(env, valid_districts)
    health_valid = mark_valid_health(health, valid_facilities)

    session = SessionLocal()
    try:
        seed_metadata_catalogue(session)
        ids = load_reference(session, refs)
        persist_dq(session, [dq_env, dq_health, dq_pop])
        load_fact_tables(
            session,
            ids,
            {
                "environmental_samples": env_valid,
                "health_observations": health_valid,
                "population_estimates": pop,
                "socioeconomic_indicators": ses,
            },
        )
        session.commit()
        log.info(
            "Pipeline complete. DQ overall env=%.3f health=%.3f pop=%.3f",
            dq_env.overall,
            dq_health.overall,
            dq_pop.overall,
        )
        return {
            "environmental_dq": dq_env.overall,
            "health_dq": dq_health.overall,
            "population_dq": dq_pop.overall,
            "env_rows": len(env_valid),
            "health_rows": len(health_valid),
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def prefect_flow():
    """Prefect flow wrapping the same pipeline functions."""
    try:
        from prefect import flow, task
    except ImportError:
        log.warning("Prefect not installed; running pipeline directly")
        return run_pipeline()

    @task(name="envirolens-etl")
    def etl_task():
        return run_pipeline()

    @flow(name="envirolens-pipeline")
    def pipeline_flow():
        return etl_task()

    return pipeline_flow()


def main():
    parser = argparse.ArgumentParser(description="EnviroLens ETL pipeline")
    parser.add_argument("--all", action="store_true", help="Run full ingest/validate/load")
    parser.add_argument("--prefect", action="store_true", help="Run via Prefect flow")
    args = parser.parse_args()
    if args.prefect:
        result = prefect_flow()
    else:
        result = run_pipeline()
    print(result)


if __name__ == "__main__":
    main()
