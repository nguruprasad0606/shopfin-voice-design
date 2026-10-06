import { FormEvent, useState } from 'react'
import { Trash2, Pencil } from 'lucide-react'
import PageState from '../components/common/PageState'
import ProgressBar from '../components/common/ProgressBar'
import { useApi, useData } from '../context/DataContext'
import { api } from '../lib/api'
import { inr } from '../lib/format'
import type { BudgetOverview, BudgetOverviewItem } from '../types'

const tone = { Healthy: 'text-pos', Warning: 'text-warn', Exceeded: 'text-neg' }

export default function Budget() {
  const { data: o, loading, error } = useApi<BudgetOverview>('/budgets/overview', 30000)
  const { refresh } = useData()
  const [name, setName] = useState(''); const [limit, setLimit] = useState(''); const [err, setErr] = useState('')
  const [editId, setEditId] = useState<number | null>(null); const [editLimit, setEditLimit] = useState('')

  const add = async (e: FormEvent) => {
    e.preventDefault(); setErr('')
    try { await api('/budgets/', { body: { name, limit: Number(limit) } }); setName(''); setLimit(''); refresh() } catch (x) { setErr((x as Error).message) }
  }
  const remove = async (b: BudgetOverviewItem) => {
    if (window.confirm(`Delete the ${b.name} budget?`)) { await api(`/budgets/${b.id}`, { method: 'DELETE' }); refresh() }
  }
  const saveLimit = async (e: FormEvent, b: BudgetOverviewItem) => {
    e.preventDefault(); setErr('')
    try { await api(`/budgets/${b.id}`, { method: 'PUT', body: { limit: Number(editLimit) } }); setEditId(null); refresh() } catch (x) { setErr((x as Error).message) }
  }
  const inputCls = 'input'
  const onTrack = o ? o.projected_spend <= o.total_limit : true

  return (
    <div className="space-y-6">
      <p className="text-sm text-mute">“Spent” is added up from this month’s expenses in the same category, so it updates whenever you record one.</p>
      <PageState loading={loading} error={error}>
        {o && <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="card"><p className="text-sm font-semibold text-mute">Total budget · {o.month}</p><p className="mt-2 font-display text-3xl font-bold tracking-tight">{inr(o.total_limit)}</p>
              <p className="mt-2 text-xs text-mute">{o.counts.Healthy} healthy · {o.counts.Warning} warning · {o.counts.Exceeded} exceeded</p></div>
            <div className="card"><p className="text-sm font-semibold text-mute">Spent so far</p><p className="mt-2 font-display text-3xl font-bold tracking-tight">{inr(o.total_spent)}</p>
              <div className="mt-3"><ProgressBar value={o.total_spent} max={o.total_limit} /></div><p className="mt-2 text-xs text-mute">{o.percentage.toFixed(0)}% of the budget</p></div>
            <div className="card"><p className="text-sm font-semibold text-mute">Remaining</p><p className={`mt-2 font-display text-3xl font-bold tracking-tight ${o.remaining < 0 ? 'text-neg' : ''}`}>{inr(o.remaining)}</p>
              <p className="mt-2 text-xs text-mute">{o.days_left} days left in the month</p></div>
            <div className="card"><p className="text-sm font-semibold text-mute">Expected by month end</p><p className={`mt-2 font-display text-3xl font-bold tracking-tight ${onTrack ? '' : 'text-neg'}`}>{inr(o.projected_spend)}</p>
              <p className="mt-2 text-xs text-mute">{o.total_limit ? `${o.projected_percentage.toFixed(0)}% of budget at ${inr(o.daily_burn)} a day` : 'Add a budget to see this'}</p></div>
          </div>
          {o.total_limit > 0 && (
            <div className="card text-sm"><b>{onTrack ? 'You are on track.' : 'You are spending faster than planned.'}</b>{' '}
              {o.remaining > 0 ? `To stay within budget, keep daily spending under ${inr(o.safe_daily_spend)} for the next ${Math.max(o.days_left, 1)} day(s).` : 'The overall budget is already used up for this month.'}</div>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            {o.items.map(b => (
              <div key={b.id} className="card">
                <div className="flex items-center justify-between"><h2 className="text-lg font-bold">{b.name}</h2>
                  <div className="flex items-center gap-2"><span className={`text-xs font-bold ${tone[b.status]}`}>{b.status}</span>
                    <button onClick={() => { setEditId(b.id); setEditLimit(String(b.limit)) }} aria-label={`Edit ${b.name} budget`} className="rounded p-1 text-mute hover:text-accent"><Pencil size={15} /></button>
                    <button onClick={() => remove(b)} aria-label={`Delete ${b.name} budget`} className="rounded p-1 text-mute hover:text-neg"><Trash2 size={15} /></button></div></div>
                <p className="mt-1 text-sm text-mute">{inr(b.spent)} of {inr(b.limit)} ({b.percentage.toFixed(0)}%) · {inr(b.remaining)} left</p>
                <div className="mt-3"><ProgressBar value={b.spent} max={b.limit} /></div>
                <p className={`mt-2 text-xs ${b.projected_percentage > 100 ? 'text-neg' : 'text-mute'}`}>Heading for {inr(b.projected)} by month end ({b.projected_percentage.toFixed(0)}%)</p>
                {editId === b.id && (
                  <form onSubmit={e => saveLimit(e, b)} className="mt-3 flex items-end gap-2">
                    <div><label htmlFor={`el${b.id}`} className="block text-xs font-semibold">New monthly limit (₹)</label>
                      <input id={`el${b.id}`} required autoFocus type="number" min={1} value={editLimit} onChange={e => setEditLimit(e.target.value)} className={inputCls + ' w-36'} /></div>
                    <button className="btn px-3 text-sm">Save</button>
                    <button type="button" onClick={() => setEditId(null)} className="rounded-md px-3 py-2 text-sm font-semibold text-mute hover:text-ink">Cancel</button>
                  </form>
                )}
              </div>
            ))}
          </div>

          {o.unbudgeted.length > 0 && (
            <div className="card"><h2 className="text-lg font-bold">Spending with no budget</h2><p className="text-xs text-mute">This month’s expenses in categories you haven’t set a limit for</p>
              <ul className="mt-3 divide-y divide-rule">
                {o.unbudgeted.map(u => <li key={u.category} className="flex justify-between py-2 text-sm"><span className="font-semibold">{u.category}</span><span>{inr(u.spent)}</span></li>)}
              </ul>
            </div>
          )}
        </>}
      </PageState>
      <form onSubmit={add} className="card flex flex-wrap items-end gap-3">
        <div><label htmlFor="bn" className="block text-sm font-semibold">Category</label><input id="bn" required minLength={2} value={name} onChange={e => setName(e.target.value)} className={inputCls} placeholder="e.g. Marketing" /></div>
        <div><label htmlFor="bl" className="block text-sm font-semibold">Monthly limit (₹)</label><input id="bl" required type="number" min={1} value={limit} onChange={e => setLimit(e.target.value)} className={inputCls} /></div>
        <button className="btn">Add budget</button>
        {err && <p role="alert" className="w-full text-sm text-neg">{err}</p>}
      </form>
    </div>
  )
}
