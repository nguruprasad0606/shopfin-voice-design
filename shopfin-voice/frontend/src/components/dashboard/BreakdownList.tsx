import type { Slice } from '../../types'
import { inr } from '../../lib/format'

export default function BreakdownList({ title, subtitle, items, color, empty }:
  { title: string; subtitle?: string; items: Slice[]; color: string; empty: string }) {
  return (
    <div className="card">
      <h2 className="text-lg font-bold">{title}</h2>{subtitle && <p className="text-xs text-mute">{subtitle}</p>}
      {items.length === 0 ? <p className="mt-3 text-sm text-mute">{empty}</p> :
        <ul className="mt-4 space-y-3">
          {items.map(i => (
            <li key={i.name}>
              <div className="mb-1 flex justify-between text-sm"><span className="font-semibold">{i.name}</span><span className="text-mute">{inr(i.amount)} · {i.share.toFixed(0)}%</span></div>
              <div className="h-2 rounded-sm bg-rule/60"><div className="h-full rounded-sm" style={{ width: `${Math.min(100, i.share)}%`, background: color }} /></div>
            </li>
          ))}
        </ul>}
    </div>
  )
}
