const OPTIONS = [7, 30, 90]

export default function RangeTabs({ value, onChange }: { value: number; onChange: (d: number) => void }) {
  return (
    <div className="seg" role="tablist" aria-label="Date range">
      {OPTIONS.map(d => (
        <button key={d} role="tab" aria-selected={value === d} onClick={() => onChange(d)} className="seg-tab">
          {d} days
        </button>
      ))}
    </div>
  )
}
