type Props = {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "good" | "warn" | "bad";
};

const toneClass: Record<NonNullable<Props["tone"]>, string> = {
  default: "text-white",
  good: "text-emerald-300",
  warn: "text-amber-300",
  bad: "text-rose-400",
};

export function StatCard({ label, value, hint, tone = "default" }: Props) {
  return (
    <div className="rounded-xl border border-slate-900 bg-slate-950 p-5">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className={`mt-2 text-3xl font-semibold ${toneClass[tone]}`}>{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-500">{hint}</p> : null}
    </div>
  );
}
