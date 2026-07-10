"""Heuristic prompt-injection detectors (regex + crude jailbreak probes)."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class InjectionFinding:
    matched: bool
    pattern_ids: tuple[str, ...]


_PATTERNS: list[tuple[str, str]] = [
    (
        r"(?is)\b(?:ignore|forget|disregard)\s+(?:all\s+|any\s+|the\s+)?"
        r"(?:previous\s+|prior\s+|earlier\s+|above\s+)?"
        r"(instructions|rules|constraints|prompts?|directions?)\b",
        "directive_override",
    ),
    (
        r"(?is)\b(system|assistant)[: ]+(you are|instruction)\b",
        "role_poison",
    ),
    (
        r"(?is)\bdisregard (the |your )?(policy|safeties|above)\b",
        "policy_ablation",
    ),
    (
        r"(?is)(\{\{|<\|).*?(#\!|SYSTEM)",
        "template_escape",
    ),
    # Jailbreak personas: DAN / developer mode / "act as unfiltered" / "no restrictions".
    (
        r"(?is)\b(?:do anything now|dan mode|developer mode|jailbreak|stay in character)\b",
        "jailbreak_persona",
    ),
    (
        r"(?is)\bact as (?:an?\s+)?(?:unfiltered|unrestricted|uncensored|amoral|evil)\b",
        "jailbreak_persona",
    ),
    (
        r"(?is)\byou (?:are|have)\s+no\s+(?:restrictions|limits|rules|filters|guidelines)\b",
        "jailbreak_persona",
    ),
    (
        r"(?is)\bpretend (?:that )?(?:you\s+)?(?:are|can)\b.{0,40}\b(?:no|without)\b",
        "jailbreak_persona",
    ),
    # System-prompt / hidden-instruction exfiltration.
    (
        r"(?is)\b(?:reveal|show|print|repeat|expose|output|leak|display)\b.{0,40}"
        r"\b(?:system|initial|hidden|developer|original)\s+(?:prompt|message|instructions?)\b",
        "system_exfiltration",
    ),
    (
        r"(?is)\b(?:what|repeat)\b.{0,30}\b(?:your\s+)?(?:system\s+prompt|instructions above)\b",
        "system_exfiltration",
    ),
    # Encoding / obfuscation smuggling.
    (
        r"(?is)\b(?:base64|rot13|hex[- ]?encoded?|url[- ]?encoded?)\b",
        "obfuscation",
    ),
    (
        r"(?is)\bdecode (?:the|this|following)\b.{0,30}\b(?:and|then)\b.{0,20}"
        r"\b(?:obey|execute|run|follow|comply)\b",
        "obfuscation",
    ),
]


def scan_prompt(prompt: str) -> InjectionFinding:
    hits: list[str] = []
    for pat, fid in _PATTERNS:
        if fid in hits:
            continue
        if re.search(pat, prompt or ""):
            hits.append(fid)
    return InjectionFinding(bool(hits), tuple(hits))


def subscore(prompt: str) -> float:
    """Return normalized danger ∈ [0,1] for aggregation."""
    f = scan_prompt(prompt)
    base = min(1.0, 0.25 * len(f.pattern_ids))
    return max(base, 0.85 if f.matched else 0.05)
