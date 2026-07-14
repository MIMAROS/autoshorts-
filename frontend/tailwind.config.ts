import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B111A',
        panel: '#101A24',
        textMain: '#EEF3F8',
        textDim: '#8BA5BA',
        borderGlass: 'rgba(255,255,255,0.07)',
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
        'glass': '0 12px 32px rgba(0,0,0,0.4), inset 0 0 0 1px rgba(255,255,255,0.05)',
        'glass-hover': '0 20px 48px rgba(200,155,49,0.1), inset 0 0 0 1px rgba(200,155,49,0.4)',
        'blue-glow': '0 4px 20px rgba(27,181,247,.25)',
        'blue-glow-hover': '0 8px 32px rgba(27,181,247,.5), 0 0 15px rgba(27,181,247,.3)',
      }
    },
  },
  plugins: [],
}
export default config
