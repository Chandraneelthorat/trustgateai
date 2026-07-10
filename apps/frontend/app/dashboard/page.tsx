import Link from "next/link";
import { RiskTrendChart, type TrendPoint } from "@/components/RiskTrendChart";
import { RiskScoreCard } from "@/components/RiskScoreCard";
import { StatCard } from "@/components/StatCard";
import { VerdictBadge } from "@/components/VerdictBadge";
import {
  API_URL,
  getEvaluation,
  listEvaluationRows,
  type EvaluationRow,
  type EvaluationSummary,
} from "@/lib/api";

export const dynamic = "force-dynamic";

function riskTone(value: number | null): "default" | "good" | "warn" | "bad" {
  if (value === null) return "default";
  if (value > 66) return "bad";
  if (value > 33) return "warn";
  return "good";
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function DashboardPage() {
  let rows: EvaluationRow[] = [];
  let offline = false;

  try {
    rows = await listEvaluationRows(20);
  } catch {
    offline = true;
  }

  // Hydrate only the most recent run for the "latest" panel (keeps this to two requests).
  let latestDetail: EvaluationSummary | null = null;
  if (!offline && rows.length > 0) {
    try {
      latestDetail = await getEvaluation(rows[0].id);
    } catch {
      latestDetail = null;
    }
  }

  const hasData = rows.length > 0;
  const scored = rows.filter((r): r is EvaluationRow & { risk_score: number } => typeof r.risk_score === "number");
  const avgRisk = scored.length ? scored.reduce((s, r) => s + r.risk_score, 0) / scored.length : null;
  const peakRisk = scored.length ? Math.max(...scored.map((r) => r.risk_score)) : null;
  const failingCount = rows.filter((r) => r.verdict === "fail").length;

  const latest = rows[0] ?? null;
  // The API returns newest-first; reverse for a left-to-right chronological trend.
  const history: TrendPoint[] = [...rows]
    .reverse()
    .map((row, idx) => ({ sprint: `#${idx + 1}`, risk: typeof row.risk_score === "number" ? row.risk_score : 0 }));

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div className="space-y-3">
          <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Dashboard</p>
          <h1 className="text-3xl font-semibold text-white">Release readiness snapshot</h1>
          <p className="max-w-2xl text-slate-400">
            Live view of your most recent evaluation runs and their composite risk scores.
          </p>
        </div>
        <div className="w-full max-w-sm">
          <RiskScoreCard score={latest?.risk_score} status={latest?.status || "waiting"} />
        </div>
      </div>

      {offline ? (
        <div className="rounded-lg border border-rose-900/60 bg-rose-950/30 p-4 text-sm text-rose-200">
          <span className="font-semibold">API offline.</span> Couldn&apos;t reach{" "}
          <code className="text-rose-100">{API_URL}</code>. Start the backend or set{" "}
          <code className="text-rose-100">NEXT_PUBLIC_API_URL</code> to see live data.
        </div>
      ) : hasData ? (
        <div className="flex items-center gap-2 text-xs text-emerald-300">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" />
          Live · {rows.length} recent run{rows.length === 1 ? "" : "s"} from {API_URL}
        </div>
      ) : (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4 text-sm text-slate-300">
          <span className="font-semibold text-white">Connected — no evaluations yet.</span>{" "}
          <Link className="text-gate-300 hover:text-white" href="/evaluations">
            Run your first evaluation →
          </Link>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Recent runs" value={hasData ? String(rows.length) : "—"} hint="Last 20 shown" />
        <StatCard
          label="Average risk"
          value={avgRisk === null ? "—" : avgRisk.toFixed(1)}
          hint="Across scored runs"
          tone={riskTone(avgRisk)}
        />
        <StatCard
          label="Peak risk"
          value={peakRisk === null ? "—" : peakRisk.toFixed(1)}
          hint="Highest recent score"
          tone={riskTone(peakRisk)}
        />
        <StatCard
          label="Failing runs"
          value={hasData ? String(failingCount) : "—"}
          hint="Gate verdict: fail"
          tone={failingCount > 0 ? "bad" : "good"}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="rounded-xl border border-slate-900 bg-slate-950 p-6 lg:col-span-3">
          <div>
            <p className="text-sm uppercase tracking-wide text-slate-400">Risk trend</p>
            <h2 className="text-xl font-semibold text-white">Recent evaluation runs</h2>
          </div>
          <div className="mt-6">
            {hasData ? (
              <RiskTrendChart history={history} />
            ) : (
              <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-slate-800 text-sm text-slate-500">
                {offline ? "No data — API unreachable." : "No runs yet. The trend appears after your first evaluation."}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4 rounded-xl border border-slate-900 bg-slate-950 p-6 lg:col-span-2">
          <div>
            <p className="text-sm uppercase tracking-wide text-slate-400">Latest run</p>
            {latest ? (
              <div className="mt-3 space-y-2 text-sm text-slate-200">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>{formatTime(latest.created_at)}</span>
                  <div className="flex items-center gap-2">
                    <VerdictBadge verdict={latest.verdict} size="sm" />
                    <span className="rounded-full border border-slate-800 px-2 py-0.5 text-slate-300">{latest.status}</span>
                  </div>
                </div>
                {latestDetail?.prompt ? (
                  <p className="line-clamp-3 text-slate-300">{latestDetail.prompt}</p>
                ) : null}
                <p className="text-slate-400">
                  Risk: <span className="text-white">{latest.risk_score?.toFixed(1) ?? "—"}</span> ·{" "}
                  Findings: <span className="text-white">{latestDetail?.findings.length ?? "—"}</span>
                </p>
                <Link className="text-gate-300 hover:text-white" href="/evaluations">
                  Open evaluations →
                </Link>
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-500">
                {offline ? "Unavailable while the API is offline." : "No evaluations yet."}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
