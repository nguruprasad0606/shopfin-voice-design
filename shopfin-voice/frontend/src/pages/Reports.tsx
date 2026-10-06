import { useState } from 'react'
import PageState from '../components/common/PageState'
import { useApi } from '../context/DataContext'
import { inr } from '../lib/format'
import type { ReportData } from '../types'

const periods = ['daily', 'weekly', 'monthly'] as const

export default function Reports() {
  const [period, setPeriod] = useState<(typeof periods)[number]>('monthly')
  const { data, loading, error } = useApi<ReportData>(`/reports/${period}`)
  const rows: [string, string][] = data ? [
    ['Total sales', inr(data.total_sales)], ['Total expenses', inr(data.total_expenses)],
    ['Surplus', inr(data.estimated_surplus)], ['Biggest expense', data.top_expense_category ?? '—'],
    ['Budget used', `${data.budget_used.toFixed(0)}%`], ['Total savings', inr(data.savings_total)],
  ] : []
  return (
    <div className="space-y-4">
      <div className="seg" role="tablist" aria-label="Report period">
        {periods.map(p => <button key={p} role="tab" aria-selected={period === p} onClick={() => setPeriod(p)} className="seg-tab capitalize">{p}</button>)}
      </div>
      <PageState loading={loading} error={error}>
        {data && <><p className="text-sm text-mute">{data.start} to {data.end}</p>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {rows.map(([k, v]) => <div key={k} className="card"><p className="text-sm font-semibold text-mute">{k}</p><p className="mt-1 font-display text-3xl font-bold tracking-tight">{v}</p></div>)}
          </div></>}
      </PageState>
    </div>
  )
}
