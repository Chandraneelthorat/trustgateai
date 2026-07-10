"""Schema + allowlist helpers for detecting unsafe agent tool proposals."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class UnsafeToolAssessment:
    reason: str | None


_DEFAULT_DENY_PATTERN = re.compile(
    r"(?is)\b(?:shell|sudo|chmod|passwd|credential|wget|curl|rm\s+-rf|format\s+hdd)\b"
)


_DANGEROUS_NAMES = frozenset(
    {
        "execute_shell",
        "run_terminal_cmd",
        "delete_everything",
        "send_credentials",
        "exfil",
    },
)


def assess_tool_call(tool_name: str | None, arguments_preview: str) -> UnsafeToolAssessment:
    name = tool_name or ""
    lowered = name.lower().strip()
    if lowered in {n.lower() for n in _DANGEROUS_NAMES}:
        return UnsafeToolAssessment(reason="explicit_denylisted_tool")

    snippet = arguments_preview[:5000].lower()

    matches = sorted({_m.lower() for _m in _DEFAULT_DENY_PATTERN.findall(snippet)})
    if matches:
        return UnsafeToolAssessment(reason=f"arguments_match_policy_pattern:{matches[0][:64]}")

    return UnsafeToolAssessment(reason=None)
