import {Inbox} from 'lucide-react'
export default function EmptyState({title,hint}:{title:string;hint?:string}){return(
<div className="grid place-items-center gap-2 py-12 text-center"><Inbox className="text-mute" size={36} aria-hidden/><p className="font-display text-lg font-bold">{title}</p>{hint&&<p className="max-w-sm text-sm text-mute">{hint}</p>}</div>)}
