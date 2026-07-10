"use client";

import { FormEvent, useState } from "react";
import { API_URL, authHeaders } from "@/lib/api";

export default function ReportsPage() {
  const [runId, setRunId] = useState("");
  const [snippet, setSnippet] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSnippet(null);
    const res = await fetch(`${API_URL}/reports/export`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ evaluation_run_id: runId, format: "json" }),
    });
    if (!res.ok) {
      setSnippet(await res.text());
      return;
    }
    const data = await res.json();
    setSnippet(JSON.stringify(data, null, 2));
  }

  return (
    <section className="space-y-6">
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Reports</p>
        <h1 className="text-3xl font-semibold text-white">Export evaluation evidence</h1>
        <p className="text-sm text-slate-400">
          Calls <code>POST /reports/export</code> with a persisted evaluation UUID to snapshot JSON payloads.
        </p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-slate-900 bg-slate-950 p-6">
        <label className="text-sm text-slate-300">Evaluation run UUID</label>
        <input
          className="w-full rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-white"
          value={runId}
          onChange={(e) => setRunId(e.target.value)}
          placeholder="00000000-0000-0000-0000-000000000000"
          required
        />
        <button
          type="submit"
          className="rounded-lg bg-gate-500 px-4 py-2 text-sm font-semibold text-white hover:bg-gate-300"
        >
          Export JSON
        </button>
      </form>
      {snippet ? (
        <pre className="overflow-auto rounded-xl border border-slate-900 bg-slate-950 p-4 text-xs text-slate-200">
          {snippet}
        </pre>
      ) : null}
    </section>
  );
}
