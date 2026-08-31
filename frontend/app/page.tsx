"use client";

import { useState } from "react";
import FieldInputForm from "@/components/FieldInputForm";
import WeatherStrip from "@/components/WeatherStrip";
import CropCalendar from "@/components/CropCalendar";
import RecommendationDetail from "@/components/RecommendationDetail";
import { ApiError, fetchRecommendation, type RecommendationRequest, type RecommendationResponse } from "@/lib/api";

export default function DashboardPage() {
  const [plan, setPlan] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(payload: RecommendationRequest) {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetchRecommendation(payload);
      setPlan(result);
    } catch (err) {
      if (err instanceof ApiError && err.status === 501) {
        setError(
          "The agronomy engine isn't implemented yet (that's expected — see backend/app/services/irrigation_engine.py)."
        );
      } else {
        setError(err instanceof Error ? err.message : "Something went wrong.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-10 lg:flex-row">
        <aside className="w-full shrink-0 lg:w-72">
          <h1 className="font-display text-2xl leading-tight">
            AgriYield
          </h1>
          <p className="mt-1 text-sm text-field-900/60">
            Localized irrigation and fertilizer guidance, built from live weather and soil data.
          </p>
          <div className="mt-6">
            <FieldInputForm onSubmit={handleSubmit} isLoading={isLoading} />
          </div>
        </aside>

        <section className="flex-1">
          {error && (
            <div className="mb-6 rounded-md border border-alert-500/30 bg-alert-500/10 px-4 py-3 text-sm text-alert-500">
              {error}
            </div>
          )}

          {!plan && !error && (
            <div className="flex h-64 flex-col items-center justify-center rounded-lg border border-dashed border-field-900/15 text-center">
              <p className="font-display text-lg text-field-900/70">Your 7-day plan will appear here</p>
              <p className="mt-1 text-sm text-field-900/50">Fill in the field details and generate a plan.</p>
            </div>
          )}

          {plan && (
            <div className="flex flex-col gap-6">
              <div>
                <h2 className="font-display text-lg mb-2">Weather outlook</h2>
                <WeatherStrip days={plan.seven_day_plan.map((d) => d.weather)} />
              </div>

              <CropCalendar plan={plan.seven_day_plan} />

              <div>
                <h2 className="font-display text-lg mb-2">Daily reasoning</h2>
                <RecommendationDetail plan={plan.seven_day_plan} />
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
