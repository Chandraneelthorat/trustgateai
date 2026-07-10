import { EvaluationSummary } from "@/lib/api";

type Props = {
  evaluation: EvaluationSummary | null;
};

export function TraceViewer({ evaluation }: Props) {
  if (!evaluation) {
    return null;
  }

  const sorted = [...evaluation.trace_steps].sort((a, b) => a.step_index - b.step_index);

  return (
    <div className="space-y-3 rounded-xl border border-slate-800 bg-slate-950/60 p-4">
      <div className="text-sm font-semibold text-white">LangGraph stubs & orchestration trace</div>
      <div className="space-y-2">
        {sorted.map((step) => (
          <div key={step.id} className="rounded-lg border border-slate-900 bg-slate-900/50 p-3">
            <div className="text-xs uppercase text-slate-500">
              Step {step.step_index} · {step.name}
            </div>
            <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-xs text-slate-200">
              {JSON.stringify(step.payload, null, 2)}
            </pre>
          </div>
        ))}
        {sorted.length === 0 ? <div className="text-sm text-slate-500">No trace persisted.</div> : null}
      </div>
    </div>
  );
}
