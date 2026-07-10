import { EvaluationSummary } from "@/lib/api";

type Props = {
  evaluation: EvaluationSummary | null;
};

export function EvalResultTable({ evaluation }: Props) {
  if (!evaluation) {
    return (
      <div className="rounded-xl border border-dashed border-slate-800 p-6 text-sm text-slate-500">
        Run an evaluation to populate findings.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800">
      <table className="min-w-full divide-y divide-slate-800 text-sm">
        <thead className="bg-slate-950 text-left text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-4 py-3">Category</th>
            <th className="px-4 py-3">Severity</th>
            <th className="px-4 py-3">Title</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-900 bg-slate-950/40">
          {evaluation.findings.map((finding) => (
            <tr key={finding.id} className="text-slate-200">
              <td className="px-4 py-3 font-semibold text-gate-300">{finding.category}</td>
              <td className="px-4 py-3 text-amber-200">{finding.severity}</td>
              <td className="px-4 py-3">{finding.title}</td>
            </tr>
          ))}
          {evaluation.findings.length === 0 ? (
            <tr>
              <td className="px-4 py-4 text-slate-500" colSpan={3}>
                No findings recorded for this pass.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
