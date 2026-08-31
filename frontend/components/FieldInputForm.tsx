"use client";

import { useState } from "react";
import type { GrowthStage, RecommendationRequest, SoilTexture } from "@/lib/api";

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
  const [locationName, setLocationName] = useState("Ibadan, Oyo State");
  const [latitude, setLatitude] = useState("7.3775");
  const [longitude, setLongitude] = useState("3.9470");
  const [fieldSize, setFieldSize] = useState("1.5");

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
        <input
          id="crop_type"
          value={cropType}
          onChange={(e) => setCropType(e.target.value)}
          placeholder="e.g. maize, cassava, tomato"
          className="w-full rounded-md border border-field-900/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-chlorophyll-500"
        />
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
        {/* TODO: replace the two manual lat/lon fields below with a geocoding
            lookup (OpenWeatherMap's Geo API, given OPENWEATHER_GEO_URL in the
            backend .env) so the farmer only ever types a place name. */}
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
        disabled={isLoading}
        className="mt-2 rounded-md bg-chlorophyll-500 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-chlorophyll-600 disabled:opacity-50"
      >
        {isLoading ? "Building plan..." : "Generate 7-day plan"}
      </button>
    </form>
  );
}
