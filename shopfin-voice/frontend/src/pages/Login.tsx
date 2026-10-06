import {useState,FormEvent} from 'react'
import {Link,useNavigate} from 'react-router-dom'
import {useAuth} from '../context/AuthContext'
import AuthShell,{Field} from '../components/common/AuthShell'
export default function Login(){const nav=useNavigate();const {login}=useAuth()
const [email,setEmail]=useState('');const [pw,setPw]=useState('');const [err,setErr]=useState('')
const [busy,setBusy]=useState(false)
const submit=async(e:FormEvent)=>{e.preventDefault();setBusy(true);const r=await login(email,pw);setBusy(false);r?setErr(r):nav('/')}
return(<AuthShell title="Welcome back" subtitle="Run your shop. Understand your money. Plan your future.">
<form onSubmit={submit} noValidate>
<Field id="email" label="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required/>
<Field id="pw" label="Password" type="password" value={pw} onChange={e=>setPw(e.target.value)} required error={err}/>
<div className="mt-4 flex items-center justify-between text-sm"><label className="flex items-center gap-2"><input type="checkbox" className="accent-ink"/>Remember me</label><button type="button" className="font-semibold text-accent">Forgot password?</button></div>
<button disabled={busy} className="btn mt-7 w-full py-3">{busy?'Logging in…':'Log in'}</button></form>
<p className="mt-5 text-center text-sm">Don’t have an account? <Link to="/register" className="font-bold text-accent">Create account</Link></p></AuthShell>)}
