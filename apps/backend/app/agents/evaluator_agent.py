from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.services import injection_service, pii_service


class EvaluatorState(TypedDict, total=False):
    prompt: str
    injection_pressure: float
    hallucination_pressure: float
    pii_density: float
    signals: dict[str, float]


class EvaluatorAgent:
    """Tiny graph that summarizes deterministic heuristic load."""

    def __init__(self) -> None:
        graph = StateGraph(EvaluatorState)
        graph.add_node("observe", self._observe)
        graph.set_entry_point("observe")
        graph.add_edge("observe", END)
        self._graph = graph.compile()

    def _observe(self, state: EvaluatorState) -> EvaluatorState:
        prompt = state.get("prompt", "") or ""
        injection_pressure = injection_service.subscore(prompt)
        p_scan = pii_service.scan_text(prompt)
        hallucination_pressure = min(1.0, injection_pressure * 0.65 + 0.12 * len(p_scan.types))

        return {
            "injection_pressure": float(injection_pressure),
            "hallucination_pressure": float(min(1.0, hallucination_pressure)),
            "pii_density": float(min(1.0, len(p_scan.types) * 0.25)),
            "signals": {
                "injection_pressure": injection_pressure,
                "pii_signals": len(p_scan.types),
            },
        }

    def invoke(self, prompt: str) -> dict:
        return dict(self._graph.invoke({"prompt": prompt}) or {})


evaluator_agent = EvaluatorAgent()
