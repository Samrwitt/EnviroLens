# AP-EHRI Risk Model

Transparent community-level **Air Pollution Environmental-Health Risk Index**.

## Formula (v1.0)

```
AP_EHRI = 0.25*PM25 + 0.20*RESP + 0.15*PROX + 0.15*VULN
        + 0.10*POV + 0.10*ACCESS + 0.05*INCOMPLETE
```

All components min-max normalized to [0,1] within a reporting period.

## Missing data

Period median imputation; completeness component increases when inputs are missing.

## Limitations

See `metadata/indicator_registry/indicators.md`.
