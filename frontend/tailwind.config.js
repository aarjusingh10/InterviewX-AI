/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#05070d",
        panel: "#0d111c",
        line: "rgba(255,255,255,0.12)",
        mint: "#55f0c7",
        coral: "#ff7a6b",
        steel: "#9fb0c8"
      },
      boxShadow: {
        glow: "0 24px 90px rgba(85, 240, 199, 0.16)"
      }
    }
  },
  plugins: []
};

