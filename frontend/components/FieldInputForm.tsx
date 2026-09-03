"use client";

import { useEffect, useState } from "react";
import {
  ApiError,
  fetchCrops,
  fetchLocationName,
  type CropOption,
  type GrowthStage,
  type RecommendationRequest,
  type SoilTexture,
} from "@/lib/api";

const SOIL_TEXTURES: { value: SoilTexture; label: string }[] = [
  { value: "sand", label: "Sand" },
  { value: "loamy_sand", label: "Loamy sand" },
  { value: "sandy_loam", label: "Sandy loam" },
  { value: "loam", label: "Loam" },
  { value: "silt_loam", label: "Silt loam" },
  { value: "silty_clay_loam", label: "Silty clay loam" },
  { value: "clay_loam", label: "Clay loam" },
  { value: "clay", label: "Clay" },
];

const GROWTH_STAGES: { value: GrowthStage; label: string }[] = [
  { value: "initial", label: "Initial (germination / emergence)" },
  { value: "development", label: "Development" },
  { value: "mid_season", label: "Mid-season" },
  { value: "late_season", label: "Late-season" },
];

interface Props {
  onSubmit: (payload: RecommendationRequest) => void;
  isLoading: boolean;
}

export default function FieldInputForm({ onSubmit, isLoading }: Props) {
  const [cropType, setCropType] = useState("maize");
  const [soilTexture, setSoilTexture] = useState<SoilTexture>("loam");
  const [growthStage, setGrowthStage] = useState<GrowthStage>("development");
  const [locationName, setLocationName] = useState("");
  const [latitude, setLatitude] = useState("7.3775");
  const [longitude, setLongitude] = useState("3.9470");
  const [fieldSize, setFieldSize] = useState("1.5");
  const [crops, setCrops] = useState<CropOption[]>([]);
  const [cropError, setCropError] = useState<string | null>(null);
  const [isLoadingCrops, setIsLoadingCrops] = useState(true);
  const [isResolvingLocation, setIsResolvingLocation] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    fetchCrops()
      .then((availableCrops) => {
        if (!isCurrent) return;
        setCrops(availableCrops);
        setCropType((currentCrop) =>
          availableCrops.some((crop) => crop.value === currentCrop)
            ? currentCrop
            : (availableCrops[0]?.value ?? ""),
        );
      })
      .catch((error) => {
        if (isCurrent) setCropError(error instanceof Error ? error.message : "Could not load crops.");
      })
      .finally(() => {
        if (isCurrent) setIsLoadingCrops(false);
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  useEffect(() => {
    const lat = Number(latitude);
    const lon = Number(longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      setLocationError(null);
      setIsResolvingLocation(false);
      return;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setIsResolvingLocation(true);
      setLocationError(null);
      try {
        const location = await fetchLocationName(lat, lon, controller.signal);
        setLocationName(location.name);
      } catch (error) {
        if ((error as Error).name !== "AbortError") {
          setLocationError(error instanceof ApiError ? error.message : "Could not resolve these coordinates.");
        }
      } finally {
        if (!controller.signal.aborted) setIsResolvingLocation(false);
      }
    }, 500);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [latitude, longitude]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      crop_type: cropType,
      soil_texture: soilTexture,
      growth_stage: growthStage,
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      location_name: locationName || undefined,
      field_size_hectares: fieldSize ? parseFloat(fieldSize) : undefined,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div>
        <label className="block text-sm text-field-900/70 mb-1.5" htmlFor="crop_type">
          Crop
        </label>
        <select
          id="crop_type"
          value={cropType}
          onChange={(e) => setCropType(e.target.value)}
          disabled={isLoadingCrops || crops.length === 0}
          className="w-full rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
        >
          {isLoadingCrops && <option>Loading available crops…</option>}
          {!isLoadingCrops && crops.length === 0 && <option>No crops available</option>}
          {crops.map((crop) => (
            <option key={crop.value} value={crop.value}>
              {crop.label}
            </option>
          ))}
        </select>
        {cropError && <p className="mt-1 text-xs text-alert-500">{cropError}</p>}
      </div>

      <div>
        <label className="block text-sm text-field-900/70 mb-1.5" htmlFor="soil_texture">
          Soil texture
        </label>
        <select
          id="soil_texture"
          value={soilTexture}
          onChange={(e) => setSoilTexture(e.target.value as SoilTexture)}
          className="w-full rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
        >
          {SOIL_TEXTURES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm text-field-900/70 mb-1.5" htmlFor="growth_stage">
          Growth stage
        </label>
        <select
          id="growth_stage"
          value={growthStage}
          onChange={(e) => setGrowthStage(e.target.value as GrowthStage)}
          className="w-full rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
        >
          {GROWTH_STAGES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm text-field-900/70 mb-1.5" htmlFor="location_name">
          Location
        </label>
        <input
          id="location_name"
          value={locationName}
          onChange={(e) => setLocationName(e.target.value)}
          placeholder="Field or town name"
          className="w-full rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
        />
        <p className="mt-1 text-xs text-field-900/50">
          {isResolvingLocation ? "Finding location from coordinates…" : "Updated automatically from latitude and longitude."}
        </p>
        {locationError && <p className="mt-1 text-xs text-alert-500">{locationError}</p>}
        <div className="mt-2 grid grid-cols-2 gap-2">
          <input
            aria-label="Latitude"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            placeholder="Latitude"
            className="rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm tabular-nums focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
          />
          <input
            aria-label="Longitude"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            placeholder="Longitude"
            className="rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm tabular-nums focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm text-field-900/70 mb-1.5" htmlFor="field_size">
          Field size (hectares)
        </label>
        <input
          id="field_size"
          value={fieldSize}
          onChange={(e) => setFieldSize(e.target.value)}
          placeholder="Optional"
          className="w-full rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm tabular-nums focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading || isLoadingCrops || crops.length === 0}
        className="mt-2 rounded-md bg-chlorophyll-500 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-chlorophyll-600 disabled:opacity-50"
      >
        {isLoading ? "Building plan..." : "Generate 7-day plan"}
      </button>
    </form>
  );
}
