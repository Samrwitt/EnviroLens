# EnviroLens

### Environmental Health Data Integration and Risk Surveillance Platform

EnviroLens is a data platform designed to help public-health organizations combine environmental, health, demographic, socioeconomic, and geospatial data in one system.

The platform transforms fragmented datasets into reliable indicators, interactive dashboards, geographic risk maps, and automated reports that can support evidence-based public-health planning.

## What It Does

EnviroLens can:

* Import data from CSV, Excel, APIs, and relational databases
* Clean, validate, and standardize datasets from different institutions
* Integrate health, environmental, population, and geographic data
* Detect missing, duplicated, inconsistent, and invalid records
* Calculate transparent environmental-health risk indicators
* Identify high-risk communities using spatial analysis
* Visualize findings through Power BI dashboards and QGIS maps
* Generate reproducible analytical reports for technical and policy audiences
* Simulate integration with national health-information systems such as DHIS2

## Example Use Case

The initial implementation combines environmental measurements, health-facility records, population data, administrative boundaries, and potential pollution-source locations.

EnviroLens uses these datasets to answer questions such as:

* Which communities may face the highest environmental-health risk?
* How many vulnerable people live in those areas?
* Which health facilities or laboratories have incomplete reporting?
* Where should surveillance, environmental sampling, or public-health interventions be prioritized?

The platform is designed to support different environmental-health topics, including air pollution, water contamination, lead exposure, occupational hazards, and respiratory illness.

## Technology Stack

**Data Engineering and APIs**

* Python * FastAPI * Pandas * SQLAlchemy

**Statistical Analysis and Reporting**

* R * Quarto * Tidyverse * ggplot2

**Database and Geospatial Processing**

* PostgreSQL * PostGIS * SQL * GeoPandas * QGIS

**Visualization**

* Power BI * Interactive geographic dashboards

**Infrastructure**

* Docker * GitHub Actions * AWS

## Main Components

### Data Integration Pipeline

Python pipelines import, clean, validate, standardize, and load data from multiple sources into PostgreSQL.

### Data Quality Engine

The platform evaluates completeness, validity, consistency, timeliness, and duplicate records across datasets.

### Environmental Health Risk Model

EnviroLens calculates explainable geographic risk scores using environmental exposure, health indicators, population vulnerability, access to services, and data-quality information.

### Geospatial Analysis

PostGIS, GeoPandas, and QGIS are used to create hotspot maps, exposure-source proximity analysis, population-at-risk estimates, and health-service accessibility maps.

### Analytics and Reporting

R and Quarto generate reproducible statistical reports, while Power BI provides interactive dashboards for analysts, health officials, and policymakers.

### FastAPI Backend

The API provides access to health indicators, environmental measurements, geographic risk scores, metadata, data-quality results, and generated reports.

## High-Level Workflow

```text
Health, Environmental and Population Data
                    |
                    v
        Python Validation and ETL
                    |
                    v
          PostgreSQL and PostGIS
             /              \
            v                v
      FastAPI Services    R Analysis
            |                |
            v                v
     Power BI and QGIS   Quarto Reports
```


