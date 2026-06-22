/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1867C0',
        'primary-light': '#3986D8',
        'primary-dark': '#0D4A8F',
      },
      gradientColorStops: {
        'gradient-1': '#1867C0',
        'gradient-2': '#3986D8',
        'gradient-3': '#5AA6F5',
      },
    },
  },
  plugins: [],
}
