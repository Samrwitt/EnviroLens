# EnviroLens Data Dictionary — Verdania Air Pollution MVP

## administrative_areas
| Column | Type | Description |
|--------|------|-------------|
| code | string | Stable geographic code (e.g., VR-N-D01) |
| name | string | Official place name |
| level | enum | country / region / district / community |
| parent_code | string | Parent administrative code |
| geometry | MultiPolygon | WGS84 boundary |

## communities
| Column | Type | Description |
|--------|------|-------------|
| code | string | Community code |
| district_code | string | Parent district |
| lon / lat | float | Centroid coordinates |

## environmental_samples
| Column | Type | Description |
|--------|------|-------------|
| site_code | string | Monitoring site identifier |
| pollutant | string | PM2.5 or NO2 |
| value | float | Concentration |
| unit | string | Expected ug/m3 |
| sample_date | date | Collection / representative date |
| period_code | string | Reporting period (e.g., 2024Q3) |

## health_observations
| Column | Type | Description |
|--------|------|-------------|
| facility_code | string | Health facility code |
| indicator_code | string | RESP_ENC_RATE |
| value | float | Encounters per 1,000 population |
| population_at_risk | float | Catchment population |
| reported_at | date | Submission date |

## population_estimates
| Column | Type | Description |
|--------|------|-------------|
| community_code | string | Community |
| total_population | int | Estimated residents |
| under5 | int | Children under 5 |
| elderly_65plus | int | Adults 65+ |

## socioeconomic_indicators
| Column | Type | Description |
|--------|------|-------------|
| indicator_code | string | POVERTY_INDEX / URBANIZATION |
| value | float | Indicator value |
| unit | string | index_0_1 or proportion |
