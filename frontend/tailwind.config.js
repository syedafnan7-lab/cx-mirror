/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0B0F14",
        panel: "#111923",
        panelAlt: "#182330",
        forensicSlate: "#94A3B8",
        forensicEmerald: "#10B981",
        forensicCrimson: "#F43F5E",
        forensicAmber: "#F59E0B",
        forensicBlue: "#38BDF8",
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

