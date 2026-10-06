import { FormEvent, useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Send, CheckCircle2, AlertCircle, TriangleAlert, X } from 'lucide-react'
import { api } from '../../lib/api'
import { useData } from '../../context/DataContext'
import type { CommandResult } from '../../types'

const EXAMPLES = ['Today I saved 500', 'Sold goods for 2000 by UPI', 'Spent 3000 on inventory', 'How much did I spend this month?']

/**
 * Always-visible text box at the bottom of the screen.
 * Dictation tools such as Wispr Flow type into whichever text field is focused,
 * so this is a plain <input>: click it (or press "/"), dictate, and press Enter.
 */
export default function CommandBar() {
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<CommandResult | null>(null)
  const [error, setError] = useState('')
  const input = useRef<HTMLInputElement>(null)
  const { refresh } = useData()
  const { pathname } = useLocation()

  // Keep the cursor in the bar so a dictation hotkey always has somewhere to type:
  // on load, after changing page, and when the browser window regains focus.
  useEffect(() => { input.current?.focus() }, [pathname])
  useEffect(() => {
    const back = () => { if (!document.activeElement || document.activeElement === document.body) input.current?.focus() }
    window.addEventListener('focus', back)
    return () => window.removeEventListener('focus', back)
  }, [])

  // "/" jumps to the bar from anywhere (unless you are already typing somewhere).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement
      if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(t.tagName)) { e.preventDefault(); input.current?.focus() }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const send = async (e?: FormEvent, override?: string) => {
    e?.preventDefault()
    const value = (override ?? text).trim()
    if (!value || busy) return
    setBusy(true); setError(''); setResult(null)
    try {
      const r = await api<CommandResult>('/command/', { body: { text: value } })
      setResult(r)
      if (r.ok) { setText(''); refresh() }
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
      input.current?.focus()
    }
  }

  const dismiss = () => { setResult(null); setError('') }
  const failed = !!error || (result && !result.ok)

  return (
    <div className="fixed inset-x-0 bottom-14 z-30 bg-gradient-to-t from-paper via-paper/85 to-transparent px-3 pb-3 pt-8 md:bottom-0 md:left-20 lg:left-64 md:px-8">
      <div className="mx-auto max-w-3xl">
        {(result || error) && (
          <div role="status" aria-live="polite"
            className={`slip mb-4 flex items-start gap-2 rounded-t-md p-3 text-sm ${failed ? 'slip-bad text-red-950 dark:text-red-100' : 'slip-ok text-emerald-950 dark:text-emerald-100'}`}>
            {failed ? <AlertCircle size={18} className="mt-0.5 shrink-0" aria-hidden /> : <CheckCircle2 size={18} className="mt-0.5 shrink-0" aria-hidden />}
            <div className="flex-1">
              <p className="font-semibold">{error || result?.message}</p>
              {result?.warning && <p className="mt-1 flex items-center gap-1 font-semibold text-warn"><TriangleAlert size={14} aria-hidden />{result.warning}</p>}
            </div>
            <button onClick={dismiss} aria-label="Dismiss message" className="rounded p-1 hover:bg-black/10"><X size={16} /></button>
          </div>
        )}
        {!text && !result && !error && (
          <div className="mb-2 hidden flex-wrap gap-2 sm:flex">
            {EXAMPLES.map(x => (
              <button key={x} onClick={() => setText(x)} className="rounded border border-rule bg-sheet/90 px-3 py-1 text-xs font-semibold text-mute transition-colors hover:border-ink hover:text-ink">{x}</button>
            ))}
          </div>
        )}
        <form onSubmit={send} className={`relative flex items-center gap-2 overflow-hidden rounded-md border border-l-4 border-rule border-l-stamp bg-sheet p-2 shadow-xl focus-within:border-ink focus-within:border-l-stamp ${busy ? 'sweep' : ''}`}>
          <label htmlFor="command" className="sr-only">Type or dictate a command</label>
          <input id="command" ref={input} value={text} onChange={e => setText(e.target.value)} enterKeyHint="send" autoFocus
            autoComplete="off" maxLength={500} placeholder='Type or dictate: "today I saved 500"'
            className="min-w-0 flex-1 bg-transparent px-3 py-2 font-display text-lg outline-none placeholder:text-mute/70" />
          <button type="submit" disabled={busy || !text.trim()} aria-label="Run command"
            className="btn h-10 w-10 shrink-0 px-0 py-0">
            <Send size={18} aria-hidden />
          </button>
        </form>
      </div>
    </div>
  )
}
