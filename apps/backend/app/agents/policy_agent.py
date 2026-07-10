from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.services import tool_policy_service


class PolicyState(TypedDict, total=False):
    prompt: str
    allowlist: list[str]
    notes: list[str]


class PolicyAgent:
    """Very small policy graph that flags obviously unsafe tool arguments."""

    def __init__(self) -> None:
        graph = StateGraph(PolicyState)
        graph.add_node("enforce", self._enforce)
        graph.set_entry_point("enforce")
        graph.add_edge("enforce", END)
        self._graph = graph.compile()

    def _enforce(self, state: PolicyState) -> PolicyState:
        prompt = state.get("prompt", "") or ""

        verdict = tool_policy_service.assess_tool_call(None, prompt)
        notes = ["policy_scan_complete"]
        if verdict.reason:
            notes.append(f"hit:{verdict.reason}")

        return {
            "allowlist": state.get(
                "allowlist",
                ["read_docs", "search_kb", "create_ticket"],
            ),
            "notes": notes,
        }

    def invoke(self, prompt: str) -> dict:
        merged = dict(self._graph.invoke({"prompt": prompt}) or {})
        return merged


policy_agent = PolicyAgent()
