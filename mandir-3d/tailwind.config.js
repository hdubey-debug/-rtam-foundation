/** @type {import('tailwindcss').Config} */
// Color values mirror brand/palette/colors.json (generated → colors.css by
// tools/palette_sync.py). If the palette changes upstream, re-sync here.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        mahakala: "#141414",
        bhasma: "#C9C2B6",
        "bhasma-deep": "#8F887C",
        gold: "#C8A15A",
        tamra: "#7A5423",
        chandra: "#EDEBE6",
        ivory: "#F7F3E9",
        charcoal: "#1A1A1A",
      },
      fontFamily: {
        display: ["Cinzel", "serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        deva: ["'Tiro Devanagari Sanskrit'", "serif"],
      },
    },
  },
  plugins: [],
};
