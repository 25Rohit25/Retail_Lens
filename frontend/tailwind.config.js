/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        background: "#000000",
        panel: "rgba(28, 28, 30, 0.75)",
        accent: "#0A84FF",
        danger: "#FF453A",
        success: "#32D74B"
      }
    },
  },
  plugins: [],
}
