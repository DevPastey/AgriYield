"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  ComposedChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DailyPlan } from "@/lib/api";

function formatDay(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", { weekday: "short" });
}

export default function CropCalendar({ plan }: { plan: DailyPlan[] }) {
  const chartData = plan.map((day) => ({
    day: formatDay(day.date),
    rainfall: day.weather.rainfall_mm,
    irrigation: day.irrigation.irrigation_amount_mm ?? 0,
    cropWaterDemand: day.irrigation.crop_water_requirement_mm ?? 0,
  }));

  return (
    <div className="rounded-lg border border-field-900/10 bg-white p-4">
      <h3 className="font-display text-base mb-3">Water balance, 7-day outlook</h3>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1F2A1D14" vertical={false} />
          <XAxis dataKey="day" tick={{ fontSize: 12, fill: "#1F2A1D99" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 12, fill: "#1F2A1D99" }} axisLine={false} tickLine={false} unit="mm" />
          <Tooltip
            contentStyle={{ borderRadius: 8, border: "1px solid #1F2A1D1A", fontSize: 13 }}
            formatter={(value: number) => `${value.toFixed(1)} mm`}
          />
          <Bar dataKey="rainfall" name="Rainfall" fill="#2F6E8C" radius={[3, 3, 0, 0]} barSize={16} />
          <Bar dataKey="irrigation" name="Recommended irrigation" fill="#3F6B3B" radius={[3, 3, 0, 0]} barSize={16} />
          <Line
            type="monotone"
            dataKey="cropWaterDemand"
            name="Crop water demand (ETc)"
            stroke="#C9782E"
            strokeWidth={2}
            dot={{ r: 3, fill: "#C9782E" }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-7 gap-2">
        {plan.map((day) => (
          <div key={day.date} className="rounded-md border border-field-900/10 px-2 py-2 text-center">
            <div className="text-xs text-field-900/60">{formatDay(day.date)}</div>
            <div
              className={`mt-1 text-xs font-medium ${
                day.irrigation.should_irrigate ? "text-chlorophyll-600" : "text-field-900/40"
              }`}
            >
              {day.irrigation.should_irrigate ? "Irrigate" : "Skip"}
            </div>
            {day.fertilizer && <div className="mt-0.5 text-xs text-soil-600">Fertilize</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
