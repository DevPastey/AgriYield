/**
 * Typed client for the AgriYield-API backend.
 *
 * Requests are sent through the Next.js backend proxy. This keeps the browser on
 * the dashboard's origin and makes the actual FastAPI host a server-only setting.
 * The shapes here mirror backend/app/schemas/recommendation.py; keep them
 * in sync if you change the backend schemas.
 */

const API_BASE_URL = "/api/backend";

export type SoilTexture =
  | "sand"
  | "loamy_sand"
  | "sandy_loam"
  | "loam"
  | "silt_loam"
  | "silty_clay_loam"
  | "clay_loam"
  | "clay";

export type GrowthStage = "initial" | "development" | "mid_season" | "late_season";

export interface RecommendationRequest {
  crop_type: string;
  soil_texture: SoilTexture;
  growth_stage: GrowthStage;
  latitude: number;
  longitude: number;
  location_name?: string;
  field_size_hectares?: number;
}

export interface DailyWeather {
  date: string;
  temp_min_c: number;
  temp_max_c: number;
  humidity_pct: number;
  rainfall_mm: number;
  wind_speed_ms: number;
  condition: string;
}

export interface IrrigationRecommendation {
  date: string;
  should_irrigate: boolean;
  irrigation_amount_mm: number | null;
  crop_water_requirement_mm: number | null;
  reasoning: string;
}

export interface NPKBlend {
  nitrogen_kg_per_ha: number;
  phosphorus_kg_per_ha: number;
  potassium_kg_per_ha: number;
  reasoning: string;
}

export interface DailyPlan {
  date: string;
  weather: DailyWeather;
  irrigation: IrrigationRecommendation;
  fertilizer: NPKBlend | null;
}

export interface RecommendationResponse {
  request: RecommendationRequest;
  generated_at: string;
  seven_day_plan: DailyPlan[];
  summary: string;
}

export interface CropOption {
  value: string;
  label: string;
}

export interface LocationLookup {
  name: string;
  latitude: number;
  longitude: number;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function fetchRecommendation(payload: RecommendationRequest): Promise<RecommendationResponse> {
  const res = await fetch(`${API_BASE_URL}/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(detail.detail ?? "Request failed", res.status);
  }

  return res.json();
}

export async function fetchWeatherOutlook(lat: number, lon: number): Promise<DailyWeather[]> {
  const res = await fetch(`${API_BASE_URL}/weather/outlook?lat=${lat}&lon=${lon}`);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(detail.detail ?? "Request failed", res.status);
  }
  return res.json();
}

export async function fetchCrops(): Promise<CropOption[]> {
  const res = await fetch(`${API_BASE_URL}/recommendations/crops`);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(detail.detail ?? "Could not load crops", res.status);
  }
  return res.json();
}

export async function fetchLocationName(lat: number, lon: number, signal?: AbortSignal): Promise<LocationLookup> {
  const params = new URLSearchParams({ lat: String(lat), lon: String(lon) });
  const res = await fetch(`${API_BASE_URL}/weather/location?${params}`, { signal });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(detail.detail ?? "Could not resolve location", res.status);
  }
  return res.json();
}
