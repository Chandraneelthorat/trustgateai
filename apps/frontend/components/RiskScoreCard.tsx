type Props = {
  score?: number | null;
  status: string;
};

export function RiskScoreCard({ score, status }: Props) {
  const safe = typeof score === "number" ? score : null;
  const clamped = safe === null ? null : Math.max(0, Math.min(100, safe));
  const tone =
    clamped === null
      ? "text-slate-400"
      : clamped > 70
        ? "text-rose-400"
        : clamped > 40
          ? "text-amber-300"
          : "text-emerald-300";

  return (
    <div className="rounded-xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950 p-6 shadow-lg shadow-gate-900/40">
      <p className="text-sm uppercase tracking-wide text-slate-400">Composite risk</p>
      <div className="mt-2 flex items-end gap-3">
        <div className={`text-5xl font-semibold ${tone}`}>{clamped === null ? "—" : clamped.toFixed(1)}</div>
        <div className="pb-1 text-sm text-slate-400">/ 100</div>
      </div>
      <p className="mt-3 text-sm text-slate-400">Status: {status}</p>
      <p className="mt-2 text-xs text-slate-500">
        Higher scores surface more policy pressure from injection, PII, grounding, and RAG faithfulness checks.
      </p>
    </div>
  );
}
