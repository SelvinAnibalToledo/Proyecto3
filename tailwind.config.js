/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './collection/templates/**/*.{html,js}',
  ],
  theme: {
    extend: {
      colors:{
        'primary':"#7F0F0E",
        'secondary':"#dac182"
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    ],
}

