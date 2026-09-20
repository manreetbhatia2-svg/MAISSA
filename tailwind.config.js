/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "sans-serif"],
      },
      colors: {
        ink: "#1A1A1A",
        paper: "#FAFAF7",
        line: "#E5E5E0",
        accent: "#0B6E4F",
        muted: "#777770",
      },
      borderRadius: {
        tool: "5px",
      },
    },
  },
  plugins: [],
};