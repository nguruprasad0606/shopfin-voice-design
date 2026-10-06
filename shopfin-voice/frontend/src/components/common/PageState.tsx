import { ReactNode } from 'react'
import EmptyState from './EmptyState'

/** Shared loading / error wrapper so every page handles those the same way. */
export default function PageState({ loading, error, children }: { loading: boolean; error: string; children: ReactNode }) {
  if (loading) return <div className="card text-sm text-mute" role="status">Loading…</div>
  if (error) return <div className="card"><EmptyState title="Could not load data" hint={error} /></div>
  return <>{children}</>
}
