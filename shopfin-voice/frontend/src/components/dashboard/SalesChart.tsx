import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts'
import type { DayPoint } from '../../types'
import { inr } from '../../lib/format'
import { grid, tick, tip } from '../../lib/chart'

export default function SalesChart({ data }: { data: DayPoint[] }) {
  return (
    <div className="card h-full">
      <h2 className="text-lg font-bold">Sales vs expenses</h2><p className="text-xs text-mute">Last 7 days</p>
      <div className="mt-4 h-64">
        <ResponsiveContainer>
          <AreaChart data={data}>
            <CartesianGrid stroke={grid} vertical={false} />
            <XAxis dataKey="d" tickLine={false} axisLine={false} tick={tick} />
            <YAxis tickLine={false} axisLine={false} tick={tick} width={48} tickFormatter={(v: number) => '₹' + v / 1000 + 'k'} />
            <Tooltip formatter={(v: number) => inr(v)} {...tip} /><Legend wrapperStyle={{ fontSize: 13 }} />
            <Area name="Sales" dataKey="sales" stroke="#14935f" fill="#14935f26" strokeWidth={2.5} />
            <Area name="Expenses" dataKey="exp" stroke="#e0831a" fill="#e0831a26" strokeWidth={2.5} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
