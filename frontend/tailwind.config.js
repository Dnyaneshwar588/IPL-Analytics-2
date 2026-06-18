/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#0b0f19',
        cardBg: 'rgba(15, 23, 42, 0.65)',
        cardBorder: 'rgba(255, 255, 255, 0.06)',
        textMain: '#f1f5f9',
        textMuted: '#94a3b8',
        accentBlue: '#38bdf8',
        accentOrange: '#f97316',
        accentGreen: '#10b981',
        accentPurple: '#a855f7',
        accentYellow: '#facc15'
      },
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      boxShadow: {
        cardGlow: '0 12px 40px rgba(0, 0, 0, 0.3)',
        accentGlow: '0 12px 40px rgba(56, 189, 248, 0.05)'
      }
    },
  },
  plugins: [],
}
