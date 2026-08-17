import type {
  DashboardAnalytics,
  DataQuality,
  District,
  Facility,
  HealthIndicator,
  MetadataRecord,
  Page,
  Region,
  RiskScore,
} from "./types";

const API_BASE =
  typeof window === "undefined"
    ? process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : process.env.NEXT_PUBLIC_API_URL || "/api-backend";

const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "dev-api-key-change-me";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(text || `Request failed: ${res.status}`, res.status);
  }

  return res.json() as Promise<T>;
}

export const api = {
  health: () => fetchApi<{ status: string; service: string }>("/api/v1/health"),

  regions: (page = 1, pageSize = 50) =>
    fetchApi<Page<Region>>(`/api/v1/regions?page=${page}&page_size=${pageSize}`),

  districts: (regionCode?: string, page = 1, pageSize = 100) => {
    const q = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (regionCode) q.set("region_code", regionCode);
    return fetchApi<Page<District>>(`/api/v1/districts?${q}`);
  },

  facilities: (page = 1, pageSize = 200) =>
    fetchApi<Page<Facility>>(`/api/v1/facilities?page=${page}&page_size=${pageSize}`),

  riskScores: (riskBand?: string, page = 1, pageSize = 200) => {
    const q = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (riskBand) q.set("risk_band", riskBand);
    return fetchApi<Page<RiskScore>>(`/api/v1/risk-scores?${q}`);
  },

  dataQuality: (page = 1, pageSize = 50) =>
    fetchApi<Page<DataQuality>>(`/api/v1/data-quality?page=${page}&page_size=${pageSize}`),

  metadata: (page = 1, pageSize = 50) =>
    fetchApi<Page<MetadataRecord>>(`/api/v1/metadata?page=${page}&page_size=${pageSize}`),

  healthIndicators: (page = 1, pageSize = 100) =>
    fetchApi<Page<HealthIndicator>>(
      `/api/v1/health-indicators?page=${page}&page_size=${pageSize}`,
    ),

  dashboard: () => fetchApi<DashboardAnalytics>("/api/v1/analytics/dashboard"),
};

export { ApiError };
