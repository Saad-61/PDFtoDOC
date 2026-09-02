/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        carbon: {
          950: "#0D0E10",
          900: "#121316", // Base Canvas
          850: "#16171B",
          800: "#1A1B1F", // Surface Level 1
          750: "#1F2025",
          700: "#222328", // Surface Level 2
          600: "#2B2C33",
        },
        slate: {
          border: "#2E2F35",
          "border-light": "#3D3E46",
          "border-active": "#C5A059",
        },
        gold: {
          300: "#E6CE94",
          400: "#D4AF37",
          500: "#C5A059", // Primary Antique Gold
          600: "#AA863F",
          700: "#8B6B2B",
        },
        ivory: {
          DEFAULT: "#F5F4F0",
          soft: "#E8E6DF",
        },
        taupe: {
          DEFAULT: "#A8A69E",
          muted: "#8C8A82",
        },
        dim: "#686660",
        forest: {
          DEFAULT: "#2D5A43",
          light: "#3E7B5C",
          surface: "#172A20",
        },
        oxblood: {
          DEFAULT: "#7A2E2E",
          light: "#9E3C3C",
          surface: "#2A1414",
        },
        brass: {
          DEFAULT: "#C59B27",
          surface: "#2D2411",
        },
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', "Georgia", "serif"],
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      boxShadow: {
        "editorial": "0 20px 40px -15px rgba(0, 0, 0, 0.7)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
}
