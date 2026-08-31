import type { DailyWeather } from "@/lib/api";

function formatDay(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", { weekday: "short", day: "numeric" });
}

export default function WeatherStrip({ days }: { days: DailyWeather[] }) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {days.map((day) => (
        <div
          key={day.date}
          className="flex min-w-[110px] flex-col gap-1 rounded-lg border border-field-900/10 bg-white px-3.5 py-3"
        >
          <span className="text-xs text-field-900/60">{formatDay(day.date)}</span>
          <span className="font-display text-lg">
            {Math.round(day.temp_max_c)}° <span className="text-field-900/40">/ {Math.round(day.temp_min_c)}°</span>
          </span>
          <span className="text-xs text-water-600">{day.rainfall_mm.toFixed(1)}mm rain</span>
          <span className="text-xs text-field-900/50">{day.condition}</span>
        </div>
      ))}
    </div>
  );
}
