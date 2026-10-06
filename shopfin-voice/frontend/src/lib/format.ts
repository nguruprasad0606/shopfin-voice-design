export const inr=(n:number)=>(n<0?'-':'')+'₹'+Math.abs(n).toLocaleString('en-IN')

/** Compact axis label: 1200 -> ₹1.2k, 250000 -> ₹2.5L. */
export const inrShort = (n: number) => {
  const a = Math.abs(n), s = n < 0 ? '-' : ''
  if (a >= 10000000) return `${s}₹${+(a / 10000000).toFixed(1)}Cr`
  if (a >= 100000) return `${s}₹${+(a / 100000).toFixed(1)}L`
  if (a >= 1000) return `${s}₹${+(a / 1000).toFixed(1)}k`
  return `${s}₹${Math.round(a)}`
}
