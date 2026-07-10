import type { Verdict } from "@/lib/api";

type Props = {
  verdict?: Verdict | null;
  size?: "sm" | "md";
};

const styles: Record<Verdict, { label: string; className: string }> = {
  pass: { label: "PASS", className: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300" },
  warn: { label: "WARN", className: "border-amber-500/40 bg-amber-500/10 text-amber-300" },
  fail: { label: "FAIL", className: "border-rose-500/40 bg-rose-500/10 text-rose-300" },
};

export function VerdictBadge({ verdict, size = "md" }: Props) {
  const known = verdict ? styles[verdict] : null;
  const sizing = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-3 py-1 text-xs";

  if (!known) {
    return (
      <span className={`inline-flex items-center rounded-full border border-slate-700 bg-slate-800/40 font-semibold uppercase tracking-wide text-slate-400 ${sizing}`}>
        N/A
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center rounded-full border font-semibold uppercase tracking-wide ${known.className} ${sizing}`}>
      {known.label}
    </span>
  );
}
