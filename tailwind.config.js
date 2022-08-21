/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{html,js,vue}',
    './src/*.{html,js,vue}',
    './public/*.{html,js,vue}'
  ],
  theme: {
    extend: {
    },
    screens: {
      'mobile': {'min': '0px', 'max': '767px'},
      'tablet': {'min': '768px', 'max': '1023px'},
      'desktop': {'min': '1024px'},
    },
  },
  plugins: [],
}
