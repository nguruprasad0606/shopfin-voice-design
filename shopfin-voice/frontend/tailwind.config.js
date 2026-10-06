// Theme colours are CSS variables (see src/index.css) so light and dark mode swap in one place.
const v = (n) => `rgb(var(--${n}) / <alpha-value>)`
export default { darkMode:'class', content:['./index.html','./src/**/*.{ts,tsx}'],
theme:{extend:{
fontFamily:{sans:['Figtree','system-ui','sans-serif'],display:['"Zilla Slab"','Figtree','system-ui','serif']},
colors:{navy:{50:'#f3f5fa',100:'#e4e9f4',600:'#27408b',700:'#1c2f6b',800:'#14234f',900:'#0c1736',950:'#080f25'},
paper:v('paper'),sheet:v('sheet'),ink:v('ink'),mute:v('mute'),rule:v('rule'),stamp:v('stamp'),accent:v('accent'),
pos:v('pos'),warn:v('warn'),neg:v('neg')}}}}
