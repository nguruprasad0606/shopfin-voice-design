import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import type { Point } from '../../types'
import { inr, inrShort } from '../../lib/format'
import { grid, tick, tip } from '../../lib/chart'

export default function TrendChart({ title, subtitle, data, color }: { title: string; subtitle: string; data: Point[]; color: string }) {
  return (
    <div className="card">
      <h2 className="text-lg font-bold">{title}</h2><p className="text-xs text-mute">{subtitle}</p>
      <div className="mt-4 h-64">
        <ResponsiveContainer>
          <BarChart data={data}>
            <CartesianGrid stroke={grid} vertical={false} />
            <XAxis dataKey="label" tickLine={false} axisLine={false} tick={tick} interval="preserveStartEnd" minTickGap={16} />
            <YAxis tickLine={false} axisLine={false} tick={tick} width={52} tickFormatter={inrShort} />
            <Tooltip formatter={(v: number) => inr(v)} cursor={{ fill: '#94a3b822' }} {...tip} />
            <Bar name={title} dataKey="amount" fill={color} radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
