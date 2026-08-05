# Indicator Registry

## AP_EHRI — Air Pollution Environmental-Health Risk Index

- **Level:** Community (rolled up to district)
- **Purpose:** Transparent prioritization of communities with elevated air-pollution–related health risk
- **Not for:** Individual clinical diagnosis

### Components and weights (v1.0)

| Component | Code | Weight | Direction | Source |
|-----------|------|--------|-----------|--------|
| Mean PM2.5 | PM25_NORM | 0.25 | higher = worse | Environmental samples |
| Respiratory encounter rate | RESP_NORM | 0.20 | higher = worse | Health observations |
| Distance to industrial source | PROX_NORM | 0.15 | closer = worse | Exposure sources (PostGIS) |
| Vulnerable population share | VULN_NORM | 0.15 | higher = worse | under5 + elderly / total |
| Poverty index | POV_NORM | 0.10 | higher = worse | SES indicators |
| Facility access gap | ACCESS_NORM | 0.10 | farther/no lab = worse | Facilities |
| Reporting incompleteness | INC_NORM | 0.05 | lower completeness = worse | DQ scores |

### Normalization
Min-max to [0, 1] within the reporting period across communities. Missing components imputed with period median and flagged.

### Risk bands
- Low: score < 0.35
- Moderate: 0.35–0.55
- High: 0.55–0.75
- Very high: ≥ 0.75

### Limitations
Synthetic data; equal spatial support assumed; industrial proximity is a proxy for exposure; respiratory encounters are not etiologically specific to air pollution.
