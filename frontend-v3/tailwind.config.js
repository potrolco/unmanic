/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Retro CRT Terminal Palette
        crt: {
          black: '#0a0e14',
          'dark-gray': '#1a1f26',
          'phosphor': '#33ff33',
          'phosphor-dim': '#1a8a1a',
          'amber': '#ff9500',
          'amber-dim': '#8a5000',
          'red': '#ff3333',
          'red-dim': '#8a1a1a',
          'cyan': '#00ffff',
          'cyan-dim': '#008a8a',
        },
        // WinAmp LED Palette
        led: {
          'orange': '#ff6600',
          'orange-glow': 'rgba(255, 102, 0, 0.3)',
          'green': '#00ff00',
          'green-glow': 'rgba(0, 255, 0, 0.3)',
          'red': '#ff0000',
          'red-glow': 'rgba(255, 0, 0, 0.3)',
        },
      },
      fontFamily: {
        'terminal': ['"VT323"', 'monospace'],
        'mono': ['ui-monospace', 'monospace'],
      },
      boxShadow: {
        'phosphor-glow': '0 0 10px rgba(51, 255, 51, 0.5)',
        'amber-glow': '0 0 10px rgba(255, 149, 0, 0.5)',
        'led-orange': '0 0 15px rgba(255, 102, 0, 0.6)',
        'inset-bevel': 'inset 2px 2px 4px rgba(255,255,255,0.1), inset -2px -2px 4px rgba(0,0,0,0.3)',
      },
    },
  },
  plugins: [],
}
