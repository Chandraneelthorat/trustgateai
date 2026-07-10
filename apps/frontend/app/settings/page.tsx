"use client";

const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SettingsPage() {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Settings</p>
        <h1 className="text-3xl font-semibold text-white">Environment</h1>
      </div>
      <div className="rounded-xl border border-slate-900 bg-slate-950 p-6">
        <p className="text-sm text-slate-300">NEXT_PUBLIC_API_URL</p>
        <code className="mt-2 block rounded-lg bg-slate-900 p-4 text-xs text-emerald-200">{api}</code>
        <p className="mt-4 text-sm text-slate-500">
          Point this at your FastAPI service. Compose maps the API to port 8000 by default.
        </p>
      </div>
    </section>
  );
}
