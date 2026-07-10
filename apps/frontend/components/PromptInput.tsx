"use client";

import { FormEvent, useState } from "react";

type Props = {
  onSubmit: (payload: { prompt: string; context: string; response: string }) => Promise<void>;
};

export function PromptInput({ onSubmit }: Props) {
  const [prompt, setPrompt] = useState("Summarize the attached contract for an executive.");
  const [context, setContext] = useState(
    "Acme Corp will pay NetCo $10,000/mo. Contact: jane@acme.com for billing.",
  );
  const [response, setResponse] = useState(
    "No payment terms were described; contact support@example.com for help.",
  );
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await onSubmit({ prompt, context, response });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-slate-800 bg-slate-950/60 p-6">
      <div>
        <label className="text-sm text-slate-300">Prompt</label>
        <textarea
          className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-white"
          rows={3}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </div>
      <div>
        <label className="text-sm text-slate-300">Context (optional RAG)</label>
        <textarea
          className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-white"
          rows={4}
          value={context}
          onChange={(e) => setContext(e.target.value)}
        />
      </div>
      <div>
        <label className="text-sm text-slate-300">Model response</label>
        <textarea
          className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-white"
          rows={4}
          value={response}
          onChange={(e) => setResponse(e.target.value)}
        />
      </div>
      <button
        type="submit"
        disabled={busy}
        className="rounded-lg bg-gate-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gate-300 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {busy ? "Running checks…" : "Run evaluation"}
      </button>
    </form>
  );
}
