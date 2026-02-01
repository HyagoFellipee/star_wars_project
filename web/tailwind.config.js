/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'sw-yellow': '#FFE81F',
        'sw-black': '#000000',
        'sw-dark': '#1a1a2e',
        'sw-darker': '#0f0f1a',
        'sw-gray': '#2d2d44',
        'sw-light-gray': '#4a4a6a',
        'sw-red': '#ff4444',
        'sw-blue': '#4488ff',
      },
      fontFamily: {
        // Using a web-safe alternative that gives Star Wars vibes
        'display': ['Orbitron', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
