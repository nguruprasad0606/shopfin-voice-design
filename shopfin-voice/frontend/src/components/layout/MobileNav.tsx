import { NavLink } from 'react-router-dom'
import { nav } from './Sidebar'

// Settings is a placeholder; everything else scrolls sideways so no page is unreachable on a phone.
export default function MobileNav() {
  return (
    <nav aria-label="Primary" className="fixed inset-x-0 bottom-0 z-30 flex overflow-x-auto border-t border-rule bg-sheet md:hidden">
      {nav.filter(n => n.to !== '/settings').map(({ to, label, icon: I }) => (
        <NavLink key={to} to={to} end={to === '/'}
          className={({ isActive }) => `flex min-w-[72px] flex-1 flex-col items-center gap-0.5 border-t-2 py-2 text-[11px] font-semibold ${isActive ? 'border-ink text-ink' : 'border-transparent text-mute'}`}>
          <I size={20} aria-hidden />{label.split(' ')[0]}
        </NavLink>
      ))}
    </nav>
  )
}
