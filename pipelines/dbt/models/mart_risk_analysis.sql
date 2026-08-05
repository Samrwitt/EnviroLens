{{ config(materialized='view') }}

-- dbt model wrapping the AP-EHRI risk analysis view for analytics schema consumers
select * from {{ source('envirolens', 'vw_risk_analysis') }}
