/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx}", "./components/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#080C14",
          panel: "#0E1523",
          panel2: "#111B2E",
          line: "#1C2740",
          accent: "#2FE0C8",
          accent2: "#3B9DFF",
          up: "#3ED598",
          down: "#FF5C7A",
          text: "#E7ECF5",
          muted: "#7E8CA8",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
        body: ["'Inter'", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 24px rgba(47, 224, 200, 0.15)",
      },
      backgroundImage: {
        grid:
          "linear-gradient(rgba(28,39,64,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(28,39,64,0.5) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "28px 28px",
      },
    },
  },
  plugins: [],
};
