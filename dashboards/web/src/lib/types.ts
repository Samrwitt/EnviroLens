export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Region {
  id: number;
  code: string;
  name: string;
  level: string;
}

export interface District extends Region {
  parent_id: number | null;
}

export interface Facility {
  id: number;
  code: string;
  name: string;
  facility_type: string;
  has_lab_access: boolean;
  community_id: number | null;
}

export interface RiskScore {
  id: number;
  community_id: number;
  period_id: number;
  index_code: string;
  score: number;
  risk_band: string;
  methodology_version: string;
  community_code?: string | null;
  community_name?: string | null;
  district_name?: string | null;
  period_code?: string | null;
  pm25_component?: number | null;
  respiratory_component?: number | null;
  proximity_component?: number | null;
  vulnerability_component?: number | null;
  poverty_component?: number | null;
  access_component?: number | null;
}

export interface DashboardAnalytics {
  latest_period: string | null;
  latest_period_label: string | null;
  kpis: {
    communities: number;
    facilities: number;
    monitoring_sites: number;
    exposure_sources: number;
    high_risk: number;
    mean_ap_ehri: number;
    overall_dq: number;
    population: number;
    vulnerable: number;
    mean_pm25: number;
    mean_resp: number;
  };
  risk_by_band: { band: string; count: number; share: number }[];
  risk_by_period: { period: string; label: string; mean_score: number; elevated: number; n: number }[];
  top_communities: {
    community: string;
    community_code: string;
    district: string;
    score: number;
    band: string;
    pm25_component: number | null;
    respiratory_component: number | null;
    proximity_component: number | null;
    vulnerability_component: number | null;
    poverty_component: number | null;
    access_component: number | null;
  }[];
  score_histogram: { bucket: string; count: number }[];
  stacked_bands: {
    period: string;
    low: number;
    moderate: number;
    high: number;
    very_high: number;
  }[];
  component_means: { component: string; value: number }[];
  pollution_trend: { period: string; pm25: number | null; no2: number | null }[];
  health_trend: { period: string; resp_rate: number | null }[];
  data_quality: {
    dataset_name: string;
    completeness: number;
    validity: number;
    consistency: number;
    timeliness: number;
    uniqueness: number;
    geographic_accuracy: number;
    overall: number;
  }[];
  facility_types: { type: string; count: number }[];
  lab_access: { label: string; count: number }[];
  district_risk: { district: string; mean_score: number; elevated: number }[];
}

export interface DataQuality {
  id: number;
  dataset_name: string;
  period_code: string | null;
  completeness: number;
  validity: number;
  consistency: number;
  timeliness: number;
  uniqueness: number;
  geographic_accuracy: number;
  overall: number;
}

export interface MetadataRecord {
  id: number;
  dataset_name: string;
  owning_institution: string;
  geographic_coverage: string | null;
  reporting_frequency: string | null;
  data_quality_status: string | null;
  sensitivity_level: string | null;
}

export interface HealthIndicator {
  id: number;
  facility_id: number;
  indicator_code: string;
  indicator_name: string;
  value: number | null;
  period_id: number;
  is_valid: boolean;
}

export type RiskBand = "low" | "moderate" | "high" | "very_high";
