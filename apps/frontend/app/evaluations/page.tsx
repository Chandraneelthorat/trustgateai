import { Suspense } from "react";
import { EvalRunner } from "@/components/EvalRunner";

export default function EvaluationsPage() {
  return (
    <div className="space-y-8">
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Evaluations</p>
        <h1 className="text-3xl font-semibold text-white">Run a governed evaluation</h1>
        <p className="max-w-2xl text-sm text-slate-400">
          POSTs to <code>/evaluations</code> with synchronous scoring by default. Toggle async in the payload when Celery +
          Redis are online.
        </p>
      </div>

      <Suspense fallback={<p className="text-sm text-slate-500">Preparing evaluator…</p>}>
        <EvalRunner />
      </Suspense>
    </div>
  );
}
