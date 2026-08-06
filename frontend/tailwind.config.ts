import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0d14",
        surface: "#121824",
        "surface-border": "#1e293b",
        primary: {
          DEFAULT: "#6366f1",
          hover: "#4f46e5",
        },
        cyan: {
          glow: "#06b6d4",
        },
        emerald: {
          glow: "#10b981",
        }
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
