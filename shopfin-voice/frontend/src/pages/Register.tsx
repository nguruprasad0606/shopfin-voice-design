import {useState,FormEvent} from 'react'
import {Link,useNavigate} from 'react-router-dom'
import {useAuth} from '../context/AuthContext'
import AuthShell,{Field,field} from '../components/common/AuthShell'
const types=['Retail Shop','Grocery','Clothing','Electronics','Restaurant','Other']
export default function Register(){const nav=useNavigate();const {register}=useAuth()
const [f,setF]=useState({name:'',email:'',password:'',shop:'',type:types[0]});const [errs,setErrs]=useState<Record<string,string>>({})
const set=(k:string)=>(e:{target:{value:string}})=>setF({...f,[k]:e.target.value})
const [busy,setBusy]=useState(false)
const submit=async(e:FormEvent)=>{e.preventDefault();const x:Record<string,string>={}
if(!f.name.trim())x.name='Enter the owner’s name.'
if(!/^\S+@\S+\.\S+$/.test(f.email))x.email='Enter a valid email address.'
if(f.password.length<8)x.password='Use at least 8 characters.'
if(!f.shop.trim())x.shop='Enter your shop name.'
setErrs(x);if(Object.keys(x).length)return
setBusy(true);const r=await register(f);setBusy(false);r?setErrs({email:r}):nav('/')}
return(<AuthShell title="Create your ShopFin account" subtitle="Set up your shop in a minute.">
<form onSubmit={submit} noValidate>
<Field id="name" label="Owner name" value={f.name} onChange={set('name')} error={errs.name}/>
<Field id="email" label="Email" type="email" value={f.email} onChange={set('email')} error={errs.email}/>
<Field id="password" label="Password" type="password" value={f.password} onChange={set('password')} error={errs.password}/>
<Field id="shop" label="Shop name" value={f.shop} onChange={set('shop')} error={errs.shop}/>
<div className="mt-5"><label htmlFor="type" className="block text-sm font-semibold">Business type</label>
<select id="type" value={f.type} onChange={set('type')} className={field}>{types.map(t=><option key={t}>{t}</option>)}</select></div>
<button disabled={busy} className="btn mt-7 w-full py-3">{busy?'Creating…':'Create account'}</button></form>
<p className="mt-5 text-center text-sm">Already have an account? <Link to="/login" className="font-bold text-accent">Log in</Link></p></AuthShell>)}
