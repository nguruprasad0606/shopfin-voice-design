import { ReactNode } from 'react'

/** One line of the day-book: date in its own column (split by a red rule), details, amount on the right. */
export default function LedgerRow({ date, title, meta, amount, positive, action }:
  { date: string; title: string; meta: string; amount: string; positive: boolean; action?: ReactNode }) {
  return (
    <li className="grid grid-cols-[5.25rem_1fr_auto] items-center gap-x-3 py-3 text-sm">
      <span className="self-stretch border-r border-stamp/40 pr-3 font-display text-xs font-semibold leading-5 text-mute">{date}</span>
      <div className="min-w-0"><p className="truncate font-semibold">{title}</p><p className="truncate text-xs text-mute">{meta}</p></div>
      <div className="flex items-center gap-3"><span className={`font-bold ${positive ? 'text-pos' : ''}`}>{amount}</span>{action}</div>
    </li>
  )
}
