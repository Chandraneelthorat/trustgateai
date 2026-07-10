export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

/** Merge in the API key header when one is configured (auth is optional by default). */
export function authHeaders(base: Record<string, string> = {}): Record<string, string> {
  return API_KEY ? { ...base, "X-API-Key": API_KEY } : base;
}

export type Verdict = "pass" | "warn" | "fail";

export type EvaluationSummary = {
  id: string;
  status: string;
  prompt: string;
  context?: string | null;
  response?: string | null;
  risk_score?: number | null;
  verdict?: Verdict | null;
  extra: Record<string, unknown>;
  created_at: string;
  findings: Array<{
    id: string;
    category: string;
    severity: string;
    title: string;
    detail?: string | null;
    meta: Record<string, unknown>;
  }>;
  trace_steps: Array<{
    id: string;
    step_index: number;
    name: string;
    payload: Record<string, unknown>;
  }>;
};

export type EvaluationRow = {
  id: string;
  status: string;
  risk_score: number | null;
  verdict?: Verdict | null;
  created_at: string;
};

/** Lightweight list (single request) — ideal for trends and aggregate stats. */
export async function listEvaluationRows(limit = 20): Promise<EvaluationRow[]> {
  const res = await fetch(`${API_URL}/evaluations?limit=${limit}`, {
    cache: "no-store",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to load evaluations");
  return (await res.json()) as EvaluationRow[];
}

/** Full detail for a single run (findings, trace, prompt, subsystem scores). */
export async function getEvaluation(id: string): Promise<EvaluationSummary> {
  const res = await fetch(`${API_URL}/evaluations/${id}`, {
    cache: "no-store",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to load evaluation");
  return (await res.json()) as EvaluationSummary;
}

/** Convenience: list rows then hydrate each with full detail (N+1 requests). */
export async function listEvaluations(limit = 10): Promise<EvaluationSummary[]> {
  const rows = await listEvaluationRows(limit);
  return Promise.all(rows.map((row) => getEvaluation(row.id)));
}

export async function createEvaluation(body: {
  prompt: string;
  context?: string;
  response?: string;
  enqueue_async?: boolean;
}): Promise<EvaluationSummary> {
  const res = await fetch(`${API_URL}/evaluations`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Failed to create evaluation");
  return (await res.json()) as EvaluationSummary;
}
