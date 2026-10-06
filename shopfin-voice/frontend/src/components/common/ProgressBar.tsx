import { motion } from 'framer-motion'

export default function ProgressBar({ value, max }: { value: number; max: number }) {
  const raw = max > 0 ? (value / max) * 100 : 0
  const p = Math.min(100, Math.round(raw))
  const color = raw > 100 ? 'bg-neg' : raw >= 80 ? 'bg-warn' : 'bg-pos'
  return (
    <div role="progressbar" aria-valuenow={p} aria-valuemin={0} aria-valuemax={100} className="h-2 rounded-sm bg-rule/60">
      <motion.div className={`h-full rounded-sm ${color}`} initial={{ width: 0 }} animate={{ width: p + '%' }} transition={{ duration: 0.6 }} />
    </div>
  )
}
