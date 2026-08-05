-- Reporting views for Power BI and API consumers

CREATE OR REPLACE VIEW vw_executive_overview AS
SELECT
    (SELECT COUNT(*) FROM communities) AS communities_covered,
    (SELECT COALESCE(SUM(total_population),0) FROM population_estimates pe
        JOIN reporting_periods rp ON rp.id = pe.period_id
        WHERE rp.code = (SELECT code FROM reporting_periods ORDER BY end_date DESC LIMIT 1)
    ) AS population_latest_period,
    (SELECT COUNT(*) FROM health_facilities WHERE is_active) AS reporting_facilities,
    (SELECT COUNT(*) FROM environmental_monitoring_sites) AS monitoring_sites,
    (SELECT COUNT(*) FROM risk_indicators WHERE risk_band IN ('high','very_high')
        AND period_id = (SELECT id FROM reporting_periods ORDER BY end_date DESC LIMIT 1)
    ) AS high_risk_communities,
    (SELECT ROUND(AVG(overall)::numeric, 3) FROM data_quality_scores) AS overall_dq_score,
    (SELECT code FROM reporting_periods ORDER BY end_date DESC LIMIT 1) AS latest_period;

CREATE OR REPLACE VIEW vw_risk_analysis AS
SELECT
    c.code AS community_code,
    c.name AS community_name,
    a.code AS district_code,
    a.name AS district_name,
    rp.code AS period_code,
    ri.score AS ap_ehri_score,
    ri.risk_band,
    ri.pm25_component,
    ri.respiratory_component,
    ri.proximity_component,
    ri.vulnerability_component,
    ri.poverty_component,
    ri.access_component,
    ri.completeness_component
FROM risk_indicators ri
JOIN communities c ON c.id = ri.community_id
JOIN administrative_areas a ON a.id = c.admin_area_id
JOIN reporting_periods rp ON rp.id = ri.period_id;

CREATE OR REPLACE VIEW vw_data_quality AS
SELECT
    dataset_name,
    period_code,
    completeness,
    validity,
    consistency,
    timeliness,
    uniqueness,
    geographic_accuracy,
    overall,
    scored_at
FROM data_quality_scores;

CREATE OR REPLACE VIEW vw_health_system_capacity AS
SELECT
    a.code AS district_code,
    a.name AS district_name,
    COUNT(DISTINCT f.id) AS facility_count,
    COUNT(DISTINCT f.id) FILTER (WHERE f.has_lab_access) AS facilities_with_lab,
    COUNT(DISTINCT l.id) AS laboratory_count,
    COUNT(DISTINCT s.id) AS monitoring_site_count
FROM administrative_areas a
LEFT JOIN health_facilities f ON f.admin_area_id = a.id
LEFT JOIN laboratories l ON l.admin_area_id = a.id
LEFT JOIN environmental_monitoring_sites s ON s.admin_area_id = a.id
WHERE a.level = 'district'
GROUP BY a.code, a.name;

CREATE OR REPLACE VIEW vw_risk_map AS
SELECT
    c.id AS community_id,
    c.code AS community_code,
    c.name AS community_name,
    rp.code AS period_code,
    ri.score,
    ri.risk_band,
    ST_AsGeoJSON(c.geometry)::json AS geometry
FROM risk_indicators ri
JOIN communities c ON c.id = ri.community_id
JOIN reporting_periods rp ON rp.id = ri.period_id;
