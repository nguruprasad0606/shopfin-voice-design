import { Routes, Route, useLocation, Navigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import MobileNav from './components/layout/MobileNav'
import CommandBar from './components/common/CommandBar'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Sales from './pages/Sales'
import Expenses from './pages/Expenses'
import Cash from './pages/Cash'
import Budget from './pages/Budget'
import Savings from './pages/Savings'
import Reports from './pages/Reports'
import Login from './pages/Login'
import Register from './pages/Register'
import Placeholder from './pages/Placeholder'
import { useAuth } from './context/AuthContext'

const later: [string, string][] = [['settings', 'Settings']]

export default function App() {
  const { pathname } = useLocation()
  const { user, loading } = useAuth()
  if (loading) return <div className="grid min-h-screen place-items-center text-mute" role="status">Loading…</div>
  if (pathname === '/login') return user ? <Navigate to="/" replace /> : <Login />
  if (pathname === '/register') return user ? <Navigate to="/" replace /> : <Register />
  if (!user) return <Navigate to="/login" replace />
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        {/* Bottom padding keeps the last card clear of the command bar (and the mobile nav). */}
        <motion.main key={pathname} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 p-4 pb-48 md:p-8 md:pb-40">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/sales" element={<Sales />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/cash" element={<Cash />} />
            <Route path="/budget" element={<Budget />} />
            <Route path="/savings" element={<Savings />} />
            <Route path="/reports" element={<Reports />} />
            {later.map(([p, n]) => <Route key={p} path={'/' + p} element={<Placeholder name={n} />} />)}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </motion.main>
      </div>
      <CommandBar />
      <MobileNav />
    </div>
  )
}
