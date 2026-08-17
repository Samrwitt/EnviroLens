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
