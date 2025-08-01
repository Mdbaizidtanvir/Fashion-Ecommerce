module.exports = {
  content: [
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {    animation: {
      'fade-in-up': 'fadeInUp 0.6s ease-out both',
    },
    keyframes: {
      fadeInUp: {
        '0%': { opacity: 0, transform: 'translateY(20px)' },
        '100%': { opacity: 1, transform: 'translateY(0)' },
      },
    },
},
  },
  plugins: [],
}
