/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      gridTemplateColumns: {
        '16': 'repeat(16, minmax(0, 1fr))',
        '32': 'repeat(32, minmax(0, 1fr))',
      },
      colors: {
        radar: {
          bg: "#0B0F19",
          card: "#111827",
          border: "#1F2937",
          cyan: "#06B6D4",
          green: "#10B981",
          amber: "#F59E0B",
          red: "#EF4444",
          purple: "#8B5CF6",
        },
      },
    },
  },
  plugins: [],
}
