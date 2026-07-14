/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        app: "#0b1118",
        panel: "#111926",
        line: "#213044",
        accent: "#8cb3d9",
        success: "#6fbf73",
        warning: "#d9a441",
        danger: "#d9785a",
      },
      boxShadow: {
        panel: "0 20px 60px rgba(2, 6, 23, 0.35)",
      },
      fontFamily: {
        sans: ["'IBM Plex Sans'", "ui-sans-serif", "system-ui"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "SFMono-Regular"],
      },
    },
  },
  plugins: [],
};
