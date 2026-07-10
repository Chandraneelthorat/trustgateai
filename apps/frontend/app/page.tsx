import Link from "next/link";

export default function HomePage() {
  return (
    <section className="space-y-6">
      <div className="space-y-3">
        <p className="text-sm uppercase tracking-[0.2em] text-gate-300">Governed AI launches</p>
        <h1 className="text-4xl font-semibold leading-tight text-white">
          Ship prompts, agents, and RAG with evidence-backed risk scoring.
        </h1>
        <p className="max-w-3xl text-slate-400">
          TrustGateAI runs injection, privacy, grounding, RAG faithfulness, and adversarial stubs before releases.
          Compose brings FastAPI + Celery + Postgres; the dashboard visualizes traces and weighted scores.
        </p>
      </div>
      <div className="flex gap-4">
        <Link
          href="/dashboard"
          className="rounded-lg bg-gate-500 px-5 py-2 text-sm font-semibold text-white hover:bg-gate-300"
        >
          View dashboard
        </Link>
        <Link href="/evaluations" className="rounded-lg border border-slate-800 px-5 py-2 text-sm hover:border-white">
          Create evaluation
        </Link>
      </div>
    </section>
  );
}
