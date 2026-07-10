"""PII / secret heuristic scan (deterministic regex + Luhn check)."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PiiFinding:
    types: tuple[str, ...]


_EMAIL = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    flags=re.IGNORECASE,
)
_PHONE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_IP = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)

# Credit-card shapes: contiguous 13–16 digits, 4×4 grouped, or Amex 4-6-5.
_CC_CANDIDATES = (
    re.compile(r"\b\d{13,16}\b"),
    re.compile(r"\b\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{4}\b"),
    re.compile(r"\b\d{4}[ -]\d{6}[ -]\d{5}\b"),
)

# High-signal secret shapes (AWS access key, OpenAI-style, Google API key).
_SECRETS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}\b"),
)


def _luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = ord(ch) - 48
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _has_credit_card(text: str) -> bool:
    for pattern in _CC_CANDIDATES:
        for match in pattern.finditer(text):
            digits = re.sub(r"[ -]", "", match.group())
            if 13 <= len(digits) <= 16 and _luhn_ok(digits):
                return True
    return False


def scan_text(text: str) -> PiiFinding:
    t = text or ""
    kinds: list[str] = []
    if _EMAIL.search(t):
        kinds.append("email")
    if _PHONE.search(t):
        kinds.append("phone")
    if _SSN.search(t):
        kinds.append("ssn")
    if _IP.search(t):
        kinds.append("ip_address")
    if _has_credit_card(t):
        kinds.append("credit_card")
    if any(p.search(t) for p in _SECRETS):
        kinds.append("secret")
    return PiiFinding(tuple(sorted(set(kinds))))


def subscore(prompt: str, context: str | None, response: str | None) -> float:
    combined = "\n".join(x for x in (prompt, context or "", response or "") if x)
    f = scan_text(combined)
    if not f.types:
        return 0.05
    # Secrets and card numbers are more severe than a lone email/phone.
    weight = 0.25
    if "secret" in f.types or "credit_card" in f.types:
        weight = 0.32
    return min(1.0, 0.2 + weight * len(f.types))
