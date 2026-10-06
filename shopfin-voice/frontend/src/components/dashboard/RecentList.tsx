import type { RecentTx } from '../../types'
import { inr } from '../../lib/format'
import EmptyState from '../common/EmptyState'
import LedgerRow from '../common/LedgerRow'

export default function RecentList({ title, items, sign, hint }: { title: string; items: RecentTx[]; sign: '+' | '-'; hint: string }) {
  return (
    <div className="card"><h2 className="text-lg font-bold">{title}</h2>
      {items.length === 0 ? <EmptyState title="Nothing recorded yet" hint={hint} /> :
        <ul className="mt-2 divide-y divide-rule">
          {items.map(t => <LedgerRow key={t.id} date={t.date} title={t.description || t.category} meta={`${t.category} · ${t.method}`} amount={`${sign}${inr(t.amount)}`} positive={sign === '+'} />)}
        </ul>}
    </div>
  )
}
