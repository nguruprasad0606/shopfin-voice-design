import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Wallet, PieChart, Target, TrendingUp, Receipt, Landmark, FileText, Settings } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export const nav = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/transactions', label: 'Transactions', icon: Wallet },
  { to: '/sales', label: 'Sales', icon: TrendingUp },
  { to: '/expenses', label: 'Expenses', icon: Receipt },
  { to: '/cash', label: 'Cash Flow', icon: Landmark },
  { to: '/budget', label: 'Budget', icon: PieChart },
  { to: '/savings', label: 'Savings', icon: Target },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/settings', label: 'Settings', icon: Settings },
]

// The sidebar is the ledger's spine: the open page is a tab that joins the paper beside it.
export default function Sidebar() {
  const { user } = useAuth()
  return (
    <aside className="sticky top-0 hidden h-screen shrink-0 flex-col bg-navy-900 text-white md:flex md:w-20 lg:w-64 dark:bg-[#050913]">
      <div className="flex items-center gap-3 px-4 py-6"><img src="/logo.svg" alt="" className="h-9 w-9" /><span className="hidden font-display text-2xl font-bold tracking-tight lg:block">ShopFin</span></div>
      <nav aria-label="Main" className="flex-1 space-y-1 pl-3">
        {nav.map(({ to, label, icon: I }) => (
          <NavLink key={to} to={to} end={to === '/'} title={label}
            className={({ isActive }) => `flex items-center gap-3 rounded-l-md px-3 py-2.5 text-sm transition-colors ${isActive ? 'bg-paper font-bold text-ink' : 'font-semibold text-white/70 hover:bg-white/10 hover:text-white'}`}>
            <I size={19} aria-hidden /><span className="hidden lg:block">{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="m-3 hidden rounded-md border border-white/15 p-3 text-sm lg:block">
        <p className="font-display text-base font-bold">{user?.shop ?? 'My shop'}</p><p className="text-white/60">Owner: {user?.name}</p>
      </div>
    </aside>
  )
}
