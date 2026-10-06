import { Link } from 'react-router-dom'
import { Banknote, Receipt, Landmark, PiggyBank } from 'lucide-react'
import StatCard from '../components/dashboard/StatCard'
import SalesChart from '../components/dashboard/SalesChart'
import ProgressBar from '../components/common/ProgressBar'
import PageState from '../components/common/PageState'
import EmptyState from '../components/common/EmptyState'
import LedgerRow from '../components/common/LedgerRow'
import { useApi } from '../context/DataContext'
import { useAuth } from '../context/AuthContext'
import { inr } from '../lib/format'
import type { BudgetItem, DashboardData, Insight, Transaction } from '../types'

const greeting = () => { const h = new Date().getHours(); return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening' }
const edge = { info: 'border-accent', warn: 'border-warn', good: 'border-pos' }

export default function Dashboard() {
  const { user } = useAuth()
  const dash = useApi<DashboardData>('/dashboard/', 30000)  // today's numbers re-check every 30s
  const tx = useApi<Transaction[]>('/transactions/?limit=5')
  const budgets = useApi<BudgetItem[]>('/budgets/')
  const insights = useApi<Insight[]>('/insights/')
  const d = dash.data

  return (
    <div className="space-y-6">
      <div><h2 className="text-3xl font-bold tracking-tight">{greeting()}, {user?.name.split(' ')[0]} 👋</h2><p className="mt-1 text-mute">Here’s your business overview for today. Use the bar below to add entries.</p></div>
      <PageState loading={dash.loading} error={dash.error}>
        {d && <>
          {/* Closing balance on the left, the day's lines on the right. */}
          <div className="grid gap-4 lg:grid-cols-5">
            <div className="lg:col-span-3"><StatCard variant="hero" to="/cash" label="Available cash" value={inr(d.available_cash)} change={null} note="opening cash + sales − expenses" icon={Landmark} /></div>
            <div className="card divide-y divide-rule !py-2 lg:col-span-2">
              <StatCard variant="line" to="/sales" label="Today’s sales" value={inr(d.today_sales)} change={d.sales_change} note="vs yesterday" icon={Banknote} />
              <StatCard variant="line" to="/expenses" label="Today’s expenses" value={inr(d.today_expenses)} change={d.expenses_change} note="vs yesterday" icon={Receipt} goodWhenUp={false} />
              <StatCard variant="line" to="/savings" label="Total savings" value={inr(d.savings_total)} change={null} note={`${inr(d.cash_after_savings)} cash left after savings`} icon={PiggyBank} />
            </div>
          </div>
          <div className="card flex flex-wrap items-baseline gap-x-8 gap-y-2 text-sm">
            <h2 className="text-lg font-bold">Today’s sales update</h2>
            <p><span className="text-mute">Sales entered </span><b>{d.today_sales_count}</b></p>
            <p><span className="text-mute">Average sale </span><b>{inr(d.today_average_sale)}</b></p>
            <p><span className="text-mute">Surplus today </span><b className={d.estimated_surplus < 0 ? 'text-neg' : 'text-pos'}>{inr(d.estimated_surplus)}</b></p>
            {d.today_by_method.length > 0
              ? <p className="text-mute">{d.today_by_method.map(m => `${m.name} ${inr(m.amount)}`).join(' · ')}</p>
              : <p className="text-mute">No sales recorded yet today.</p>}
            {dash.updatedAt && <p className="ml-auto text-xs text-mute" role="status">Updated {dash.updatedAt.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</p>}
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2"><SalesChart data={d.weekly} /></div>
            <div className="card"><div className="flex items-baseline justify-between"><h2 className="text-lg font-bold">Budget usage <span className="font-sans text-xs font-normal text-mute">this month</span></h2><Link to="/budget" className="text-xs font-semibold text-accent hover:underline">Details</Link></div>
              {d.budget_total > 0 && <div className="mt-3"><div className="mb-1 flex justify-between text-sm"><span className="font-semibold">Overall</span><span className="text-mute">{inr(d.budget_used)} / {inr(d.budget_total)}</span></div><ProgressBar value={d.budget_used} max={d.budget_total} /></div>}
              <div className="mt-4 space-y-4">
                {budgets.data?.length === 0 && <p className="text-sm text-mute">No budgets yet. Add some on the Budget page.</p>}
                {budgets.data?.map(b => (
                  <div key={b.id}><div className="mb-1 flex justify-between text-sm"><span className="font-semibold">{b.name}</span><span className="text-mute">{inr(b.spent)} / {inr(b.limit)}</span></div><ProgressBar value={b.spent} max={b.limit} /></div>
                ))}
              </div>
            </div>
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="card lg:col-span-2"><h2 className="text-lg font-bold">Recent transactions</h2>
              {tx.data?.length === 0 ? <EmptyState title="No transactions yet" hint='Try typing "sold goods for 2000" below.' /> :
                <ul className="mt-2 divide-y divide-rule">
                  {tx.data?.map(t => <LedgerRow key={t.id} date={t.date} title={t.description || t.category} meta={`${t.category} · ${t.method}`} amount={`${isIncome(t.type) ? '+' : '-'}${inr(t.amount)}`} positive={isIncome(t.type)} />)}
                </ul>}
            </div>
            <div className="card"><h2 className="text-lg font-bold">Insights</h2><p className="text-xs text-mute">Based on your own numbers, not financial advice</p>
              <ul className="mt-3 space-y-3">{insights.data?.map(i => <li key={i.id} className={`rounded-md border-l-4 bg-paper p-3 text-sm ${edge[i.tone] ?? 'border-rule'}`}>{i.text}</li>)}</ul>
            </div>
          </div>
        </>}
      </PageState>
    </div>
  )
}

export const isIncome = (type: string) => ['Sale', 'Customer Payment', 'Other Income'].includes(type)
