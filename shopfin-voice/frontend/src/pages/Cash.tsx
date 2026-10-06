import { FormEvent, useState } from 'react'
import { ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts'
import { Landmark, Coins, Smartphone, PiggyBank } from 'lucide-react'
import StatCard from '../components/dashboard/StatCard'
import RangeTabs from '../components/dashboard/RangeTabs'
import PageState from '../components/common/PageState'
import { useApi, useData } from '../context/DataContext'
import { api } from '../lib/api'
import { inr, inrShort } from '../lib/format'
import { grid, tick, tip } from '../lib/chart'
import type { CashDashboard } from '../types'

export default function Cash() {
  const [days, setDays] = useState(30)
  const { data: d, loading, error } = useApi<CashDashboard>(`/analytics/cash?days=${days}`, 30000)
  const { refresh } = useData()
  const [opening, setOpening] = useState(''); const [err, setErr] = useState(''); const [saved, setSaved] = useState(false)

  const saveOpening = async (e: FormEvent) => {
    e.preventDefault(); setErr(''); setSaved(false)
    try { await api('/analytics/cash/opening', { method: 'PUT', body: { amount: Number(opening) } }); setOpening(''); setSaved(true); refresh() }
    catch (x) { setErr((x as Error).message) }
  }

  return (
    <div className="space-y-6">
      <RangeTabs value={days} onChange={setDays} />
      <PageState loading={loading} error={error}>
        {d && <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Available cash" value={inr(d.available_cash)} change={null} note="opening cash + sales − expenses" icon={Landmark} />
            <StatCard label="Cash in hand" value={inr(d.cash_in_hand)} change={null} note="notes and coins in the till" icon={Coins} />
            <StatCard label="UPI, card and bank" value={inr(d.digital_balance)} change={null} note="money in your accounts" icon={Smartphone} />
            <StatCard label="Cash after savings" value={inr(d.cash_after_savings)} change={null} note={`${inr(d.savings_total)} is kept as savings`} icon={PiggyBank} to="/savings" />
          </div>

          <div className="card">
            <h2 className="text-lg font-bold">Money in and out</h2><p className="text-xs text-mute">Last {d.days} days · the line is your available cash at the end of each day</p>
            <div className="mt-4 h-72">
              <ResponsiveContainer>
                <ComposedChart data={d.flow}>
                  <CartesianGrid stroke={grid} vertical={false} />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} tick={tick} interval="preserveStartEnd" minTickGap={16} />
                  <YAxis tickLine={false} axisLine={false} tick={tick} width={52} tickFormatter={inrShort} />
                  <Tooltip formatter={(v: number) => inr(v)} {...tip} /><Legend wrapperStyle={{ fontSize: 13 }} />
                  <Bar name="Money in" dataKey="money_in" fill="#14935f" radius={[2, 2, 0, 0]} />
                  <Bar name="Money out" dataKey="money_out" fill="#e0831a" radius={[2, 2, 0, 0]} />
                  <Line name="Available cash" dataKey="balance" stroke="#5b7bd8" strokeWidth={2.5} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card"><h2 className="text-lg font-bold">Balance by payment method</h2>
              <ul className="mt-3 divide-y divide-rule">
                {d.by_method.map(m => (
                  <li key={m.name} className="flex items-center justify-between py-3 text-sm">
                    <div><p className="font-semibold">{m.name}</p><p className="text-xs text-mute">in {inr(m.money_in)} · out {inr(m.money_out)}</p></div>
                    <span className={`font-bold ${m.balance < 0 ? 'text-neg' : ''}`}>{inr(m.balance)}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="space-y-6">
              <div className="card"><h2 className="text-lg font-bold">This month</h2>
                <dl className="mt-3 grid grid-cols-3 gap-3 text-sm">
                  <div><dt className="text-mute">In</dt><dd className="font-bold text-pos">{inr(d.month_in)}</dd></div>
                  <div><dt className="text-mute">Out</dt><dd className="font-bold">{inr(d.month_out)}</dd></div>
                  <div><dt className="text-mute">Net</dt><dd className={`font-bold ${d.month_net < 0 ? 'text-neg' : 'text-pos'}`}>{inr(d.month_net)}</dd></div>
                </dl>
                <p className="mt-4 text-sm text-mute">
                  {d.runway_days === null ? 'Not enough spending data to estimate how long your cash will last.'
                    : `At your average spend of ${inr(d.avg_daily_spend)} a day (last 30 days), your available cash lasts about ${d.runway_days} days.`}
                </p>
              </div>
              <form onSubmit={saveOpening} className="card">
                <h2 className="text-lg font-bold">Opening cash</h2>
                <p className="text-sm text-mute">Cash you already had before recording entries here: {inr(d.opening_cash)}. Change it if your starting balance was different.</p>
                <div className="mt-3 flex flex-wrap items-end gap-3">
                  <div><label htmlFor="oc" className="block text-sm font-semibold">New opening cash (₹)</label>
                    <input id="oc" required type="number" min={0} value={opening} onChange={e => setOpening(e.target.value)} className="input" /></div>
                  <button className="btn">Save</button>
                </div>
                {err && <p role="alert" className="mt-2 text-sm text-neg">{err}</p>}
                {saved && <p role="status" className="mt-2 text-sm text-pos">Opening cash updated.</p>}
              </form>
            </div>
          </div>
        </>}
      </PageState>
    </div>
  )
}
