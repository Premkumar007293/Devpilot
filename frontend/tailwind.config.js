/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#07090E', // Deepest background
          900: '#0C0E14', // Base background
          850: '#12151E', // Card surface
          800: '#181C28', // Elevated surface / hover
          750: '#1F2433', // Border / active
          700: '#2A3042', // Subdued line
          border: 'rgba(255, 255, 255, 0.07)',
          'border-subtle': 'rgba(255, 255, 255, 0.04)',
          'border-active': 'rgba(139, 92, 246, 0.35)',
        },
        brand: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#6366F1', // Indigo primary
          600: '#4F46E5',
          700: '#4338CA',
          accent: '#8B5CF6', // Violet
          cyan: '#06B6D4',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#F43F5E',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-sm': '0 0 15px -3px rgba(99, 102, 241, 0.15)',
        'glow-md': '0 0 25px -5px rgba(139, 92, 246, 0.20)',
        'glow-violet': '0 0 35px -5px rgba(139, 92, 246, 0.25)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.45)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'subtle-grid': 'radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px)',
      },
      keyframes: {
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
      animation: {
        'pulse-subtle': 'pulse-subtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
