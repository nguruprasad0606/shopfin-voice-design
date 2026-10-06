import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import PageState from '../components/common/PageState'
import EmptyState from '../components/common/EmptyState'
import LedgerRow from '../components/common/LedgerRow'
import { useApi, useData } from '../context/DataContext'
import { api } from '../lib/api'
import { inr } from '../lib/format'
import { isIncome } from './Dashboard'
import type { Transaction } from '../types'

const filters = ['All', 'Income', 'Expense'] as const

export default function Transactions() {
  const { data, loading, error } = useApi<Transaction[]>('/transactions/?limit=500')
  const { refresh } = useData()
  const [filter, setFilter] = useState<(typeof filters)[number]>('All')
  const [err, setErr] = useState('')
  const rows = (data ?? []).filter(t => filter === 'All' || (filter === 'Income') === isIncome(t.type))

  const remove = async (t: Transaction) => {
    if (!window.confirm(`Delete "${t.description || t.category}" (${inr(t.amount)})?`)) return
    try { await api(`/transactions/${t.id}`, { method: 'DELETE' }); refresh() } catch (e) { setErr((e as Error).message) }
  }

  return (
    <div className="space-y-4">
      <div className="seg" role="tablist" aria-label="Filter transactions">
        {filters.map(f => <button key={f} role="tab" aria-selected={filter === f} onClick={() => setFilter(f)} className="seg-tab">{f}</button>)}
      </div>
      {err && <p role="alert" className="text-sm text-neg">{err}</p>}
      <PageState loading={loading} error={error}>
        <div className="card">
          {rows.length === 0 ? <EmptyState title="Nothing here yet" hint='Type "spent 500 on stock" in the bar below.' /> :
            <ul className="divide-y divide-rule">
              {rows.map(t => (
                <LedgerRow key={t.id} date={t.date} title={t.description || t.category} meta={`${t.category} · ${t.method} · ${t.type}`}
                  amount={`${isIncome(t.type) ? '+' : '-'}${inr(t.amount)}`} positive={isIncome(t.type)}
                  action={<button onClick={() => remove(t)} aria-label={`Delete ${t.description || t.category}`} className="rounded p-1.5 text-mute transition-colors hover:bg-paper hover:text-neg"><Trash2 size={16} /></button>} />
              ))}
            </ul>}
        </div>
      </PageState>
    </div>
  )
}
