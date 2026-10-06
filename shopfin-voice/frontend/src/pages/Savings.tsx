import PageState from '../components/common/PageState'
import ProgressBar from '../components/common/ProgressBar'
import EmptyState from '../components/common/EmptyState'
import { useApi } from '../context/DataContext'
import { inr } from '../lib/format'
import type { Deposit, SavingsGoal } from '../types'

export default function Savings() {
  const goals = useApi<SavingsGoal[]>('/savings/')
  const history = useApi<Deposit[]>('/savings/history')
  const total = (goals.data ?? []).reduce((s, g) => s + g.current_amount, 0)

  return (
    <div className="space-y-6">
      <div className="card"><p className="text-sm font-semibold text-mute">Total saved</p><p className="font-display text-4xl font-bold tracking-tight">{inr(total)}</p>
        <p className="mt-1 text-sm text-mute">Say “today I saved 500” or “saved 1000 for the emergency fund” in the bar below.</p></div>
      <PageState loading={goals.loading} error={goals.error}>
        {goals.data?.length === 0 ? <div className="card"><EmptyState title="No savings goals yet" hint='Try "I saved 500" or "create a goal called New Freezer of 40000".' /></div> :
          <div className="grid gap-4 md:grid-cols-2">
            {goals.data?.map(g => (
              <div key={g.id} className="card">
                <h2 className="text-lg font-bold">{g.name}</h2>
                <p className="mt-1 text-sm text-mute">{inr(g.current_amount)} of {inr(g.target_amount)} · {g.progress.toFixed(0)}%</p>
                <div className="mt-3"><ProgressBar value={g.current_amount} max={g.target_amount} /></div>
              </div>
            ))}
          </div>}
      </PageState>
      <div className="card"><h2 className="text-lg font-bold">Recent savings</h2>
        {history.data?.length === 0 ? <p className="mt-2 text-sm text-mute">Nothing saved yet.</p> :
          <ul className="mt-2 divide-y divide-rule">
            {history.data?.map(d => (
              <li key={d.id} className="grid grid-cols-[5.25rem_1fr_auto] items-center gap-x-3 py-3 text-sm">
                <span className="self-stretch border-r border-stamp/40 pr-3 font-display text-xs font-semibold leading-5 text-mute">{d.date}</span>
                <div><p className="font-semibold">{d.goal_name}</p>{d.note && <p className="text-xs text-mute">{d.note}</p>}</div>
                <span className="font-bold text-pos">+{inr(d.amount)}</span>
              </li>
            ))}
          </ul>}
      </div>
    </div>
  )
}
