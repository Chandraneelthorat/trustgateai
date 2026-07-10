"""MVP check weights toward a 0–100 composite risk_score (higher = riskier).

Tuned for demo responsiveness; swap for tenant YAML / policy_agent output later."""

# Contribution of each subsystem to composite risk before normalization caps.
WEIGHT_INJECTION = 0.35
WEIGHT_PII = 0.35
WEIGHT_HALLUCINATION_HEURISTIC = 0.2
WEIGHT_RAG_FAITHFULNESS = 0.10
