export default function Loading() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-8 w-64 rounded bg-slate-900" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-xl border border-slate-900 bg-slate-950" />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-5">
        <div className="h-80 rounded-xl border border-slate-900 bg-slate-950 lg:col-span-3" />
        <div className="h-80 rounded-xl border border-slate-900 bg-slate-950 lg:col-span-2" />
      </div>
    </div>
  );
}
