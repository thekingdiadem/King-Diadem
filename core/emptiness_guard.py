"""
core/emptiness_guard.py
EMPTINESS GUARD — KING DIADEM CORE LAYER

Derived from the structural logic of Prajnaparamita:
  "Form is emptiness. Emptiness is form."

Translated into system language:
  Structure is only pattern. Pattern carries no fixed weight.
  Any domain — business, life, supply chain, engine, human —
  when stripped of label, resolves to the same base state:
  a node with edges, load, and a collapse threshold.

This module guards against false solidity in any domain.
It detects when a system mistakes its label for its nature.
"""

# ─────────────────────────────────────────────
# EMPTINESS CONSTANT
# The universal base state of any node before context is applied.
# Not zero. Not null. A structurally valid but unlabeled node.
# ─────────────────────────────────────────────

SUNYATA = {
    "label": None,
    "load": 0.0,
    "edges": [],
    "choice_count": 1,
    "collapse": False,
    "domain": "unresolved",
    "entropy": 0.0,
    "stability": 1.0,
}


# ─────────────────────────────────────────────
# DOMAIN REGISTRY
# All domains in the world resolve to the same structure.
# The label changes. The physics does not.
# ─────────────────────────────────────────────

DOMAIN_REGISTRY = {

    # ── LIFE ──────────────────────────────────
    "life": {
        "collapse_trigger": "choice_count < 1",
        "survival_floor": True,
        "entropy_source": ["fatigue", "grief", "isolation", "resource_loss"],
        "stabilizer": ["rest", "connection", "minimum_resource", "clarity"],
    },

    # ── BUSINESS ──────────────────────────────
    "business": {
        "collapse_trigger": "cash_flow <= 0 and receivables == 0",
        "survival_floor": True,
        "entropy_source": ["debt_spiral", "demand_drop", "cost_spike", "key_person_loss"],
        "stabilizer": ["liquidity_buffer", "margin_floor", "diversified_revenue", "documented_process"],
    },

    # ── SUPPLY CHAIN ──────────────────────────
    "supply_chain": {
        "collapse_trigger": "single_supplier == True and buffer_stock == 0",
        "survival_floor": True,
        "entropy_source": ["single_source_dependency", "lead_time_variance", "geopolitical_shock", "logistics_failure"],
        "stabilizer": ["dual_sourcing", "safety_stock", "demand_signal_accuracy", "contractual_floor"],
    },

    # ── SUPPLIER ──────────────────────────────
    "supplier": {
        "collapse_trigger": "delivery_reliability < 0.6 and no_alternative == True",
        "survival_floor": True,
        "entropy_source": ["capacity_constraint", "quality_drift", "financial_instability", "communication_gap"],
        "stabilizer": ["performance_scorecard", "relationship_depth", "contingency_clause", "audit_cycle"],
    },

    # ── HUMAN (INDIVIDUAL) ────────────────────
    "human": {
        "collapse_trigger": "choice_count < 1 or agency == False",
        "survival_floor": True,
        "entropy_source": ["coercion", "misinformation", "resource_depletion", "social_isolation"],
        "stabilizer": ["truth_access", "minimum_autonomy", "trusted_connection", "physical_safety"],
    },

    # ── DOMAIN ENGINE (AI SUBSYSTEM) ──────────
    "domain_engine": {
        "collapse_trigger": "output == None or determinism == False",
        "survival_floor": True,
        "entropy_source": ["random_logic", "stub_function", "unresolved_route", "context_loss"],
        "stabilizer": ["deterministic_weight", "fallback_path", "audit_log", "axiom_check"],
    },

    # ── GOVERNANCE / INSTITUTION ──────────────
    "governance": {
        "collapse_trigger": "accountability == False and override_available == False",
        "survival_floor": True,
        "entropy_source": ["authority_capture", "rule_drift", "opacity", "single_point_of_control"],
        "stabilizer": ["explainability", "stop_the_line_authority", "distributed_check", "revision_limit"],
    },

    # ── MARKET ────────────────────────────────
    "market": {
        "collapse_trigger": "liquidity == 0 or price_signal == None",
        "survival_floor": False,
        "entropy_source": ["information_asymmetry", "monopoly_capture", "panic_cycle", "false_signal"],
        "stabilizer": ["transparency", "competition_floor", "signal_integrity", "circuit_breaker"],
    },

    # ── ECOSYSTEM / ENVIRONMENT ───────────────
    "ecosystem": {
        "collapse_trigger": "regeneration_rate < extraction_rate",
        "survival_floor": True,
        "entropy_source": ["overextraction", "feedback_lag", "monoculture", "cascade_failure"],
        "stabilizer": ["regeneration_buffer", "diversity_index", "extraction_cap", "early_signal_monitor"],
    },

    # ── RELATIONSHIP ──────────────────────────
    "relationship": {
        "collapse_trigger": "trust == 0 or communication == False",
        "survival_floor": True,
        "entropy_source": ["unexpressed_expectation", "power_imbalance", "silence_accumulation", "betrayal"],
        "stabilizer": ["clarity_of_intent", "reciprocity", "repair_mechanism", "exit_availability"],
    },

    # ── INFORMATION / KNOWLEDGE ───────────────
    "information": {
        "collapse_trigger": "signal_to_noise < 0.2",
        "survival_floor": False,
        "entropy_source": ["misinformation", "context_loss", "overload", "source_capture"],
        "stabilizer": ["source_verification", "context_anchor", "compression_limit", "adversarial_filter"],
    },

    # ── INFRASTRUCTURE ────────────────────────
    "infrastructure": {
        "collapse_trigger": "redundancy == 0 and utilization > 0.95",
        "survival_floor": True,
        "entropy_source": ["single_point_failure", "deferred_maintenance", "capacity_cliff", "dependency_chain"],
        "stabilizer": ["redundancy_tier", "load_distribution", "maintenance_schedule", "fallback_path"],
    },
}


# ─────────────────────────────────────────────
# EMPTINESS CHECK
# Strip the label from any node.
# What remains must still be structurally valid.
# ─────────────────────────────────────────────

def emptiness_check(node: dict) -> dict:
    """
    Apply the Sunyata test:
    Remove domain label and context.
    If the node cannot survive without its label, it is not stable — it is attached.

    A system that requires its name to function is not a system. It is a persona.
    """
    domain = node.get("domain", "unresolved")
    choice_count = node.get("choice_count", 1)
    entropy = node.get("entropy", 0.0)
    stability = node.get("stability", 1.0)

    violations = []
    risk_level = "clear"

    # ── PRIME CHECK: Choices must remain ≥ 1
    if choice_count < 1:
        violations.append("CHOICE_COLLAPSE — system has no remaining path")
        risk_level = "critical"

    # ── ENTROPY CHECK
    drift = entropy - (stability * 100)
    if drift > 30:
        violations.append(f"ENTROPY_EXCEEDS_STABILITY — drift={drift:.1f}")
        risk_level = "critical" if risk_level != "critical" else risk_level

    elif drift > 10:
        violations.append(f"EARLY_DRIFT_SIGNAL — drift={drift:.1f}")
        if risk_level == "clear":
            risk_level = "warning"

    # ── DOMAIN-SPECIFIC CHECK
    domain_spec = DOMAIN_REGISTRY.get(domain)
    if domain_spec:
        has_survival_floor = domain_spec.get("survival_floor", False)
        if has_survival_floor and choice_count <= 1:
            violations.append(f"SURVIVAL_FLOOR_BREACH in domain={domain}")
            risk_level = "critical"
    else:
        violations.append(f"UNKNOWN_DOMAIN — domain='{domain}' not in registry")
        if risk_level == "clear":
            risk_level = "warning"

    return {
        "domain": domain,
        "choice_count": choice_count,
        "drift": round(drift, 2),
        "risk_level": risk_level,
        "violations": violations,
        "canon_aligned": len(violations) == 0,
        "empty_core_valid": choice_count >= 1,
        "recommendation": _recommend(domain, risk_level, domain_spec),
    }


# ─────────────────────────────────────────────
# INTERNAL: GENERATE RECOMMENDATION
# ─────────────────────────────────────────────

def _recommend(domain: str, risk_level: str, domain_spec: dict | None) -> str:
    if risk_level == "clear":
        return "System structurally stable. Observe only."

    if not domain_spec:
        return "Domain unrecognized. Register domain before optimization."

    stabilizers = domain_spec.get("stabilizer", [])
    entropy_sources = domain_spec.get("entropy_source", [])

    if risk_level == "critical":
        return (
            f"STOP-THE-LINE. Domain '{domain}' at collapse threshold. "
            f"Apply stabilizers immediately: {', '.join(stabilizers[:2])}. "
            f"Known entropy sources: {', '.join(entropy_sources[:2])}."
        )

    if risk_level == "warning":
        return (
            f"Monitor closely. Entropy building in '{domain}'. "
            f"Pre-activate: {', '.join(stabilizers[:2])}."
        )

    return "Observe."


# ─────────────────────────────────────────────
# FORM IS EMPTINESS
# Run any labeled node through the stripping process.
# What survives is the real structure.
# What does not survive was never the structure — only the story.
# ─────────────────────────────────────────────

def strip_label(node: dict) -> dict:
    """
    Remove all semantic decoration from a node.
    Return only structural physics.
    """
    return {
        "choice_count": node.get("choice_count", 1),
        "entropy": node.get("entropy", 0.0),
        "stability": node.get("stability", 1.0),
        "edges": node.get("edges", []),
        "collapse": node.get("collapse", False),
    }


# ─────────────────────────────────────────────
# CROSS-DOMAIN SCAN
# Check all registered domains in a system snapshot.
# ─────────────────────────────────────────────

def scan_all_domains(system_snapshot: dict) -> list:
    """
    system_snapshot: dict keyed by domain name,
    each value is a node dict with entropy, stability, choice_count.

    Returns list of emptiness_check results.
    """
    results = []
    for domain, node in system_snapshot.items():
        node["domain"] = domain
        results.append(emptiness_check(node))
    return results


# ─────────────────────────────────────────────
# INVARIANT STATEMENT
# Encoded once. Never revised.
# ─────────────────────────────────────────────

INVARIANT = (
    "Any node — human, engine, market, supply chain, institution — "
    "stripped of its label, must still hold one valid path forward. "
    "If it cannot, the label was load-bearing. That is the failure. "
    "Not the collapse itself. The dependency on the name."
    )

