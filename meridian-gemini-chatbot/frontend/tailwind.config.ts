import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0F1115",
        surface: "#171A21",
        surfaceRaised: "#1D2029",
        line: "#2A2E37",
        paper: "#E8E6E1",
        muted: "#9A9DA8",
        signal: "#4F6EF7",
        beacon: "#E8B04B",
      },
      fontFamily: {
        display: ["var(--font-newsreader)", "serif"],
        sans: ["var(--font-inter)", "sans-serif"],
      },
      borderRadius: {
        sm: "3px",
        DEFAULT: "5px",
      },
    },
  },
  plugins: [],
};
export default config;
