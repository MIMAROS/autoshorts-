import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--bg-app)',
        panel: 'var(--bg-panel)',
        panelSubtle: 'var(--bg-panel-subtle)',
        card: 'var(--bg-card)',
        inputBg: 'var(--bg-input)',
        textMain: 'var(--text-main)',
        textHeading: 'var(--text-heading)',
        textDim: 'var(--text-dim)',
        borderGlass: 'var(--border-glass)',
        borderGlassStrong: 'var(--border-glass-strong)',
        mimaros: {
          blue: '#14AEEA',
          blueMid: '#0B7FA8',
          gold: '#C89B31',
          goldDark: '#916B13',
        },
      },
      fontFamily: {
        sans: ['var(--font-lato)', 'sans-serif'],
        heading: ['var(--font-work-sans)', 'sans-serif'],
        display: ['var(--font-josefin)', 'sans-serif'],
        metric: ['var(--font-poppins)', 'sans-serif'],
      },
      boxShadow: {
        'glass': 'var(--shadow-glass)',
        'glass-hover': '0 20px 48px rgba(200,155,49,0.1), inset 0 0 0 1px rgba(200,155,49,0.4)',
        'blue-glow': '0 4px 20px var(--glow-blue)',
        'blue-glow-hover': '0 8px 32px var(--glow-blue), 0 0 15px var(--glow-blue)',
      }
    },
  },
  plugins: [],
}
export default config
