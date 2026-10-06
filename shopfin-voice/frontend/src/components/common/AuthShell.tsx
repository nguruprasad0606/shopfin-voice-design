import {ReactNode} from 'react'
export const field='line-field'
export function Field({id,label,error,...p}:{id:string;label:string;error?:string}&React.InputHTMLAttributes<HTMLInputElement>){return(
<div className="mt-5"><label htmlFor={id} className="block text-sm font-semibold">{label}</label>
<input id={id} {...p} aria-invalid={!!error} aria-describedby={error?id+'-e':undefined} className={field}/>
{error&&<p id={id+'-e'} role="alert" className="mt-1 text-xs text-neg">{error}</p>}</div>)}

// A ledger page on a navy desk: the red margin rule runs down the left of the form.
export default function AuthShell({title,subtitle,children}:{title:string;subtitle:string;children:ReactNode}){return(
<main className="grid min-h-screen place-items-center bg-navy-900 p-4" style={{backgroundImage:'linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px)',backgroundSize:'100% 32px'}}>
<div className="relative w-full max-w-md overflow-hidden rounded-md bg-sheet py-9 pl-14 pr-8 text-ink shadow-2xl">
<span aria-hidden className="absolute inset-y-0 left-9 w-px bg-stamp/70"/><span aria-hidden className="absolute inset-y-0 left-[2.65rem] w-px bg-stamp/70"/>
<img src="/logo.svg" alt="ShopFin" className="h-11 w-11"/><h1 className="mt-5 text-3xl font-bold leading-tight tracking-tight">{title}</h1><p className="mt-1 text-sm text-mute">{subtitle}</p>{children}</div></main>)}
