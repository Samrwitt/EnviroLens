-- Spatial analysis queries for EnviroLens (PostGIS)

-- Nearest exposure source distance (meters) per community
SELECT c.code AS community_code,
       c.name,
       e.code AS nearest_source,
       ST_DistanceSphere(c.centroid, e.location) AS dist_m
FROM communities c
JOIN LATERAL (
    SELECT code, location
    FROM exposure_sources
    ORDER BY c.centroid <-> location
    LIMIT 1
) e ON true
WHERE c.centroid IS NOT NULL;

-- Communities within 5 km of any industrial source
SELECT c.code, c.name
FROM communities c
WHERE EXISTS (
    SELECT 1 FROM exposure_sources e
    WHERE ST_DWithin(c.centroid::geography, e.location::geography, 5000)
);

-- District mean AP-EHRI
SELECT a.code AS district_code,
       a.name,
       ROUND(AVG(ri.score)::numeric, 3) AS mean_ap_ehri
FROM risk_indicators ri
JOIN communities c ON c.id = ri.community_id
JOIN administrative_areas a ON a.id = c.admin_area_id
JOIN reporting_periods rp ON rp.id = ri.period_id
WHERE rp.code = (SELECT code FROM reporting_periods ORDER BY end_date DESC LIMIT 1)
GROUP BY a.code, a.name
ORDER BY mean_ap_ehri DESC;

-- Facility coverage: communities without a facility with lab access
SELECT c.code, c.name
FROM communities c
LEFT JOIN health_facilities f ON f.community_id = c.id AND f.has_lab_access = true
WHERE f.id IS NULL;
