import { Link } from 'react-router-dom'
import { LucideIcon, ArrowUpRight, ArrowDownRight } from 'lucide-react'

type Variant = 'card' | 'hero' | 'line'

/**
 * card: the standard figure card. hero: the closing balance, set large on a navy page.
 * line: one ruled line of a tally, with the amount on the right.
 */
export default function StatCard({ label, value, change, note, icon: I, goodWhenUp = true, to, variant = 'card' }:
  { label: string; value: string; change: number | null; note: string; icon: LucideIcon; goodWhenUp?: boolean; to?: string; variant?: Variant }) {
  const up = (change ?? 0) >= 0
  const good = up === goodWhenUp
  const dark = variant === 'hero'
  const delta = change !== null && (
    <span className={`inline-flex items-center font-bold ${dark ? (good ? 'text-emerald-300' : 'text-red-300') : good ? 'text-pos' : 'text-neg'}`}>
      {up ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}{Math.abs(change)}%
    </span>
  )

  if (variant === 'hero') {
    const hero = (
      <div className="relative h-full overflow-hidden rounded-md bg-navy-900 p-6 text-white md:p-8"
        style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px)', backgroundSize: '100% 32px' }}>
        <div className="flex items-center gap-2 text-sm font-semibold text-white/70"><I size={18} aria-hidden />{label}</div>
        <p className="mt-6 font-display text-5xl font-bold tracking-tight md:text-6xl">
          <span className="inline-block border-b-[6px] border-double border-white/60 pb-1">{value}</span>
        </p>
        <p className="mt-4 flex items-center gap-1 text-sm text-white/70">{delta}<span>{note}</span></p>
      </div>
    )
    return to ? <Link to={to} className="block h-full rounded-md">{hero}</Link> : hero
  }

  if (variant === 'line') {
    const line = (
      <div className="flex items-baseline justify-between gap-4 px-1 py-4">
        <div>
          <p className="flex items-center gap-2 text-sm font-semibold"><I size={16} className="text-mute" aria-hidden />{label}</p>
          <p className="mt-1 flex items-center gap-1 text-xs"><span className="text-mute">{note}</span>{delta}</p>
        </div>
        <p className="font-display text-2xl font-bold tracking-tight">{value}</p>
      </div>
    )
    return to ? <Link to={to} className="block rounded transition-colors hover:bg-paper">{line}</Link> : line
  }

  const card = (
    <div className={`card h-full ${to ? 'transition-colors hover:border-ink' : ''}`}>
      <div className="flex items-center justify-between"><span className="text-sm font-semibold text-mute">{label}</span><I size={18} className="text-accent" aria-hidden /></div>
      <p className="mt-2 font-display text-3xl font-bold tracking-tight">{value}</p>
      <p className="mt-2 flex items-center gap-1 text-xs">
        {delta}
        <span className="text-mute">{note}</span>
      </p>
    </div>
  )
  return to ? <Link to={to} className="block rounded-md">{card}</Link> : card
}
