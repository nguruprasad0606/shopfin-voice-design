import { useState } from 'react'
import { Banknote, Receipt } from 'lucide-react'
import StatCard from '../components/dashboard/StatCard'
import TrendChart from '../components/dashboard/TrendChart'
import BreakdownList from '../components/dashboard/BreakdownList'
import RecentList from '../components/dashboard/RecentList'
import RangeTabs from '../components/dashboard/RangeTabs'
import PageState from '../components/common/PageState'
import { useApi } from '../context/DataContext'
import { inr } from '../lib/format'
import type { FlowDashboard } from '../types'

const KINDS = {
  sales: {
    path: 'sales', color: '#14935f', icon: Banknote, goodWhenUp: true, sign: '+' as const,
    word: 'sales', todayLabel: 'Today’s sales', hint: 'Try typing “sold goods for 2000 by UPI” in the bar below.',
  },
  expenses: {
    path: 'expenses', color: '#e0831a', icon: Receipt, goodWhenUp: false, sign: '-' as const,
    word: 'expenses', todayLabel: 'Today’s expenses', hint: 'Try typing “spent 3000 on inventory” in the bar below.',
  },
}

/** One layout for both the Sales and Expenses dashboards. */
export default function FlowPage({ kind }: { kind: keyof typeof KINDS }) {
  const k = KINDS[kind]
  const [days, setDays] = useState(30)
  // Re-checks every 30s, and straight away when something is added from the command bar.
  const { data: d, loading, error, updatedAt } = useApi<FlowDashboard>(`/analytics/${k.path}?days=${days}`, 30000)

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <RangeTabs value={days} onChange={setDays} />
        {updatedAt && <p className="text-xs text-mute" role="status">Updated {updatedAt.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</p>}
      </div>
      <PageState loading={loading} error={error}>
        {d && <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label={k.todayLabel} value={inr(d.today)} change={d.today_change} note="vs yesterday" icon={k.icon} goodWhenUp={k.goodWhenUp} />
            <StatCard label="Last 7 days" value={inr(d.week)} change={d.week_change} note="vs the 7 days before" icon={k.icon} goodWhenUp={k.goodWhenUp} />
            <StatCard label="This month" value={inr(d.month)} change={d.month_change} note="vs same days last month" icon={k.icon} goodWhenUp={k.goodWhenUp} />
            <StatCard label={`Daily average (${d.days}d)`} value={inr(d.daily_average)} change={null} icon={k.icon}
              note={d.best_day ? `highest: ${d.best_day.label}, ${inr(d.best_day.amount)}` : `no ${k.word} in this period`} />
          </div>

          <div className="card flex flex-wrap items-center gap-x-8 gap-y-2 text-sm">
            <p><span className="text-mute">Entries today </span><b>{d.today_count}</b></p>
            <p><span className="text-mute">Average per entry </span><b>{inr(d.today_average)}</b></p>
            {kind === 'expenses' && d.budget_total ? <p><span className="text-mute">Monthly budget used </span><b>{d.budget_used_percent?.toFixed(0)}%</b> <span className="text-mute">of {inr(d.budget_total)}</span></p> : null}
          </div>

          <TrendChart title={kind === 'sales' ? 'Daily sales' : 'Daily expenses'} subtitle={`Last ${d.days} days · total ${inr(d.range_total)}`} data={d.daily} color={k.color} />

          <div className="grid gap-6 lg:grid-cols-2">
            <BreakdownList title="By payment method" subtitle={`Last ${d.days} days`} items={d.by_method} color={k.color} empty={`No ${k.word} in this period.`} />
            <BreakdownList title="By category" subtitle={`Last ${d.days} days`} items={d.by_category} color={k.color} empty={`No ${k.word} in this period.`} />
          </div>

          <RecentList title={kind === 'sales' ? 'Recent sales' : 'Recent expenses'} items={d.recent} sign={k.sign} hint={k.hint} />
        </>}
      </PageState>
    </div>
  )
}
