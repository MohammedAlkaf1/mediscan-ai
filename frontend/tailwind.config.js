/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          darkest:  '#27374D',
          primary:  '#526D82',
          secondary:'#9DB2BF',
          lightest: '#DDE6ED',
        },
      },
    },
  },
  plugins: [],
}
