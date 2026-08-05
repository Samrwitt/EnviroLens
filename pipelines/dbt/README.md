# dbt models for EnviroLens

Minimal dbt project that reads PostgreSQL reporting views into an `analytics` schema.

```bash
cd pipelines/dbt
cp profiles.yml.example profiles.yml   # or set DBT_PROFILES_DIR
dbt run
```

Requires `dbt-postgres`. Core warehouse transforms are implemented in Python ETL + SQL views; dbt provides interoperable marts for BI tools.
