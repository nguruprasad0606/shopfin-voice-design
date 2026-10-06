import {useState} from 'react'
import {Bell,Moon,Sun,LogOut} from 'lucide-react'
import {useAuth} from '../../context/AuthContext'
import {useLocation} from 'react-router-dom'
import {nav} from './Sidebar'
import {useTheme} from '../../context/ThemeContext'
export default function Header(){const {pathname}=useLocation();const {mode,toggle}=useTheme();const {user,logout}=useAuth();const [open,setOpen]=useState(false)
const title=nav.find(n=>n.to===pathname)?.label??'ShopFin'
const btn='grid h-10 w-10 place-items-center rounded-md border border-rule bg-sheet text-ink transition-colors hover:border-ink'
return(<header className="sticky top-0 z-20 flex items-center justify-between border-b border-rule bg-paper/90 px-4 py-3 backdrop-blur md:px-8">
<h1 className="text-2xl font-bold tracking-tight">{title}</h1>
<div className="flex items-center gap-2">
<button className={btn} aria-label="Notifications"><Bell size={18}/></button>
<button className={btn} aria-label="Toggle dark mode" onClick={toggle}>{mode==='dark'?<Sun size={18}/>:<Moon size={18}/>}</button>
<div className="relative"><button aria-label="Profile menu" aria-expanded={open} onClick={()=>setOpen(!open)} className="grid h-10 w-10 place-items-center rounded-md bg-ink font-display text-lg font-bold text-paper">{user?.name[0]?.toUpperCase()}</button>
{open&&<div role="menu" className="absolute right-0 mt-2 w-56 rounded-md border border-rule bg-sheet p-2 shadow-lg"><div className="px-3 py-2 text-sm"><p className="font-bold">{user?.name}</p><p className="truncate text-xs text-mute">{user?.email}</p></div>
<button role="menuitem" onClick={logout} className="flex w-full items-center gap-2 rounded px-3 py-2 text-sm font-semibold text-neg hover:bg-paper"><LogOut size={16}/>Log out</button></div>}</div></div></header>)}
