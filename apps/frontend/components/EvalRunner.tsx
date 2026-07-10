"use client";

import { useMemo, useState } from "react";
import type { EvaluationSummary } from "@/lib/api";
import { createEvaluation } from "@/lib/api";
import { EvalResultTable } from "@/components/EvalResultTable";
import { PromptInput } from "@/components/PromptInput";
import { RiskScoreCard } from "@/components/RiskScoreCard";
import { TraceViewer } from "@/components/TraceViewer";
import { VerdictBadge } from "@/components/VerdictBadge";

export function EvalRunner() {
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const subsystem = useMemo(() => evaluation?.extra as Record<string, unknown> | undefined, [evaluation]);
  const policyReasons = useMemo(() => {
    const policy = evaluation?.extra?.policy as { reasons?: string[] } | undefined;
    return policy?.reasons ?? [];
  }, [evaluation]);

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
      <div className="space-y-6">
        <PromptInput
          onSubmit={async ({ prompt, context, response }) => {
            setError(null);
            try {
              const result = await createEvaluation({
                prompt,
                context,
                response,
                enqueue_async: false,
              });
              setEvaluation(result);
            } catch (err) {
              setError(err instanceof Error ? err.message : "Evaluation failed");
            }
          }}
        />
        <EvalResultTable evaluation={evaluation} />
        <TraceViewer evaluation={evaluation} />
      </div>
      <div className="space-y-4">
        <RiskScoreCard score={evaluation?.risk_score} status={evaluation?.status || "idle"} />
        <div className="rounded-xl border border-slate-900 bg-slate-950 p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-white">Gate verdict</span>
            <VerdictBadge verdict={evaluation?.verdict} />
          </div>
          {policyReasons.length > 0 ? (
            <ul className="mt-3 list-disc space-y-1 pl-4 text-xs text-slate-400">
              {policyReasons.map((reason, idx) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-xs text-slate-500">Run an evaluation to see the release-gate decision.</p>
          )}
        </div>
        <div className="rounded-xl border border-slate-900 bg-slate-950 p-4 text-xs text-slate-400">
          <div className="text-sm font-semibold text-white">Subsystem scores</div>
          <pre className="mt-2 max-h-64 overflow-auto text-[11px] text-slate-300">
            {JSON.stringify(subsystem?.subsystem_scores ?? subsystem ?? {}, null, 2)}
          </pre>
        </div>
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      </div>
    </div>
  );
}
