import type { Config } from "tailwindcss";

// Design tokens grounded in the subject matter: soil, chlorophyll, water,
// and harvest — not a generic SaaS palette. See app/globals.css for the
// font imports these reference.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        field: {
          50: "#F3F5EE", // page background — cool sage-white, not cream
          100: "#E6EBDC",
          900: "#1F2A1D", // primary text — deep loam, not pure black
        },
        chlorophyll: {
          500: "#3F6B3B", // brand / growth / positive actions
          600: "#345A31",
          700: "#2A4827",
        },
        soil: {
          500: "#A8652F", // fertilizer / nutrient accents
          600: "#8C5327",
        },
        water: {
          500: "#2F6E8C", // irrigation / weather accents
          600: "#255A73",
        },
        alert: {
          500: "#C98A2C", // caution / threshold-crossed states
        },
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "serif"],
        sans: ["var(--font-plex)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
