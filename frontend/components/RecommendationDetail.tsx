import type { DailyPlan } from "@/lib/api";

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });
}

export default function RecommendationDetail({ plan }: { plan: DailyPlan[] }) {
  return (
    <div className="flex flex-col gap-3">
      {plan.map((day) => (
        <div key={day.date} className="rounded-lg border border-field-900/10 bg-white p-4">
          <div className="flex items-baseline justify-between">
            <h4 className="font-display text-base">{formatDate(day.date)}</h4>
            <span className="text-xs text-field-900/50">{day.weather.condition}</span>
          </div>

          <div className="mt-2 flex items-start gap-2">
            <span
              className={`mt-0.5 h-2 w-2 shrink-0 rounded-full ${
                day.irrigation.should_irrigate ? "bg-water-500" : "bg-field-900/20"
              }`}
            />
            <p className="text-sm text-field-900/80">{day.irrigation.reasoning}</p>
          </div>

          {day.fertilizer && (
            <div className="mt-2 flex items-start gap-2">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-soil-500" />
              <p className="text-sm text-field-900/80">{day.fertilizer.reasoning}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
