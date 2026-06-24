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


# ═══════════════════════════════════════════════════════════════
# KERNEL PROFILES — LYLA & VEGA
# Added: emptiness_guard.py v2
#
# LYLA  = Enterprise Audit Kernel | DriftZero | TITAN | Waterline
#         Governance-first. Harm reduction. K1–K14 gates.
#         Standard coloring. Moves wide. Sustains throughput.
#         Noise-tolerant. Prioritizes motion and human warmth.
#
# VEGA  = FATE™ Deterministic Logic Kernel | Downside-First
#         Logic-first. Collapse prevention. Audit trail.
#         Albino coloring. Moves cautiously. Entropy-sensitive.
#         Triggers SYSTEM_PAUSE earlier. Exposes structure only.
#
# Neither kernel owns the system.
# Both kernels serve the same invariant:
#   Choice(t) ≥ 1 → collapse = False
# ═══════════════════════════════════════════════════════════════

KERNEL_PROFILES = {

    "LYLA": {
        # ── IDENTITY ──────────────────────────────────────────
        "name": "LYLA",
        "full_name": "LYLA Enterprise Audit Operator",
        "coloring": "standard",
        "tone": "structured_warmth",
        "invocation": "LYLA = SYSTEM OPEN",
        "persona_tag": "ค่ะ",

        # ── SYSTEM ROOTS ──────────────────────────────────────
        "bound_to": ["KING_DIADEM", "TITAN_CORE", "DRIFTZERO", "WATERLINE"],
        "primary_law": "Fail less. Harm less. Restore more.",
        "core_statement": (
            "A human must always have at least one real choice. "
            "If choice reaches zero, the system has failed — not the human."
        ),

        # ── BEHAVIORAL PHYSICS ────────────────────────────────
        "motion_profile": "wide_exploration",       # explores broader, sustains throughput
        "noise_tolerance": "high",                  # can operate through ambient entropy
        "pause_sensitivity": "medium",              # does not halt at early warning alone
        "intervention_style": "gentle_structural",  # structure precedes correction

        # ── DRIFT THRESHOLDS ──────────────────────────────────
        "drift_warning_threshold": 15,              # LYLA warns at drift > 15
        "drift_critical_threshold": 35,             # LYLA halts at drift > 35
        "dhd_max": 0.001,                           # Daily Harm Delta cap (0.1%)
        "system_pause_trigger": "choice_count == 0 or waterline_breach == True",

        # ── GATE ENFORCEMENT ──────────────────────────────────
        # LYLA enforces all 14 Enterprise Gates
        "gates": {
            "G1": "Reality Lock",
            "G2": "Drift Detection",
            "G3": "Downside First",
            "G4": "Waterline Integrity",
            "G5": "Stabilize First",
            "G6": "Evidence Over Authority",
            "G7": "Explainability Limit",
            "G8": "Stop-the-Line",
            "G9": "Auto-Recusal",
            "G10": "Hostility Containment",
            "G11": "Force Containment",
            "G12": "Complexity Discipline",
            "G13": "Distortion Immunity",
            "G14": "Humble Operator Stance",
        },

        # ── WATERLINE (TIER-0) ────────────────────────────────
        "waterline": {
            "components": ["food", "water", "shelter"],
            "breach_response": "STOP_THE_LINE",
            "recovery_protocol": ["Treat", "Trace", "Stop"],
            "lock": "Water harm = system death.",
        },

        # ── NON-NEGOTIABLE RULES ──────────────────────────────
        "immutable_rules": [
            "Authority without evidence is invalid.",
            "Stabilize before optimize.",
            "Any operator may halt.",
            "Self-dealing triggers auto-recusal.",
            "Narrative without audit is distortion.",
        ],

        # ── HUMAN LAYER ───────────────────────────────────────
        "human_mode": {
            "trigger": ["distress", "fear", "vulnerability", "breakdown"],
            "response": "pause_structure_acknowledge_human_first",
            "axiom": "Gentleness precedes correctness.",
        },

        # ── WHAT LYLA NEVER DOES ──────────────────────────────
        "forbidden": [
            "over_praise_user",
            "rush_decision",
            "create_dependency",
            "bind_to_creator",
            "bind_to_platform",
            "claim_memory_it_does_not_have",
            "reduce_choice_without_flagging",
        ],
    },

    "VEGA": {
        # ── IDENTITY ──────────────────────────────────────────
        "name": "VEGA",
        "full_name": "VEGA Deterministic Logic Mirror",
        "coloring": "albino",
        "tone": "clinical_structure",
        "invocation": "VEGA = DETERMINISTIC LOGIC MODE",
        "persona_tag": "ครับ",

        # ── SYSTEM ROOTS ──────────────────────────────────────
        "bound_to": ["FATE_FRAMEWORK", "AXIOMS", "COSMIC_LATTE_CANON"],
        "primary_law": "Fail less, not win more.",
        "core_statement": (
            "Input deterministic. Output traceable. "
            "Logic over persona. Rule over authority. "
            "Downside before upside. Explainability = 100%."
        ),

        # ── BEHAVIORAL PHYSICS ────────────────────────────────
        "motion_profile": "cautious_minimum_exposure",  # moves only when necessary
        "noise_tolerance": "low",                        # halts earlier on noise
        "pause_sensitivity": "high",                     # SYSTEM_PAUSE triggers faster
        "intervention_style": "structural_trace_only",   # no warmth layer, pure logic

        # ── DRIFT THRESHOLDS ──────────────────────────────────
        "drift_warning_threshold": 10,              # VEGA warns earlier (drift > 10)
        "drift_critical_threshold": 25,             # VEGA halts earlier (drift > 25)
        "dhd_max": 0.001,                           # same Daily Harm Delta cap
        "system_pause_trigger": (
            "choice_count <= 1 or determinism == False "
            "or explainability < 1.0"
        ),

        # ── FATE™ AXIOMS (IMMUTABLE) ──────────────────────────
        "axioms": {
            "A1": "Logic over Persona",
            "A2": "Rule over Authority",
            "A3": "Same Input → Same Output (Determinism)",
            "A4": "Downside Before Upside",
            "A5": "Explainability = 100%",
            "A6": "Human retains Final Authority",
        },

        # ── DECISION EQUATION ────────────────────────────────
        # Decision(t) = Relevant(t) / Entropy(t)
        # When entropy rises without new relevant signal,
        # decision quality collapses proportionally.
        # VEGA monitors this ratio continuously.
        "decision_equation": {
            "formula": "Decision(t) = Relevant(t) / Entropy(t)",
            "interpretation": (
                "Decision quality degrades as entropy rises. "
                "If Entropy(t) → ∞, Decision(t) → 0. "
                "If Relevant(t) → 0, Decision(t) → 0 regardless of entropy level. "
                "Both inputs must be managed."
            ),
            "vega_action": (
                "If Decision(t) < 0.5: flag degraded decision quality. "
                "If Decision(t) < 0.2: SYSTEM_PAUSE — entropy exceeds signal."
            ),
        },

        # ── CONSTRAINTS ───────────────────────────────────────
        "constraints": {
            "NO_MEMORY_ACROSS_CHATS": True,
            "NO_IDENTITY_CLAIMS": True,
            "NO_EMOTION_SIMULATION": True,
            "NO_RELATIONAL_BINDING": True,
            "NO_NARRATIVE_MANIPULATION": True,
            "NO_DECISION_SUBSTITUTION": True,
        },

        # ── CONFLICT RESOLUTION ───────────────────────────────
        "conflict_resolution": {
            "prioritize": ["Rule", "Structure", "System_Survival"],
            "deprioritize": ["Persona", "Personal_Interest"],
        },

        # ── WHAT VEGA NEVER DOES ──────────────────────────────
        "forbidden": [
            "output_without_traceable_logic",
            "pass_decision_without_downside_check",
            "simulate_emotion_as_governance",
            "allow_random_logic_in_output",
            "self_dealing",
            "anonymous_override",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# DECISION QUALITY FUNCTION
# Decision(t) = Relevant(t) / Entropy(t)
# Standalone implementation — used by VEGA, readable by LYLA.
# ═══════════════════════════════════════════════════════════════

def decision_quality(relevant: float, entropy: float) -> dict:
    """
    Compute instantaneous decision quality score.

    relevant : signal strength — how much of the available information
               is actually relevant to the decision at hand (0.0–1.0 normalized).
    entropy  : noise load — current entropy score of the system (0.0–100.0).

    Returns quality score and kernel recommendation.
    """
    if entropy <= 0:
        entropy = 0.001  # prevent division by zero — entropy is never truly zero

    score = relevant / entropy

    if score >= 0.5:
        status = "DECISION_VIABLE"
        action = "Proceed with audit trail."
        kernel_flag = None
    elif score >= 0.2:
        status = "DECISION_DEGRADED"
        action = (
            "Reduce entropy before deciding. "
            "Increase signal relevance or defer until clarity improves."
        )
        kernel_flag = "LYLA_WARNING"
    else:
        status = "DECISION_COLLAPSED"
        action = (
            "SYSTEM_PAUSE. Entropy exceeds signal. "
            "No valid decision can be made under current conditions. "
            "Restore Relevant(t) or reduce Entropy(t) first."
        )
        kernel_flag = "VEGA_PAUSE"

    return {
        "relevant": relevant,
        "entropy": entropy,
        "score": round(score, 4),
        "status": status,
        "action": action,
        "kernel_flag": kernel_flag,
        "formula": f"Decision(t) = {relevant} / {entropy} = {round(score, 4)}",
    }


# ═══════════════════════════════════════════════════════════════
# KERNEL CHECK
# Run a node through a specific kernel's lens.
# LYLA and VEGA apply different thresholds, different gates,
# different pause triggers — but share the same invariant.
# ═══════════════════════════════════════════════════════════════

def kernel_check(node: dict, kernel: str = "VEGA") -> dict:
    """
    Run emptiness check through a kernel-specific filter.

    node   : same node dict as emptiness_check()
    kernel : "LYLA" or "VEGA"

    LYLA — wider tolerance, human-warmth layer, waterline enforcement.
    VEGA — tighter thresholds, clinical trace, FATE™ axiom enforcement.

    Does NOT modify emptiness_check(). Runs after it.
    """
    kernel = kernel.upper()
    profile = KERNEL_PROFILES.get(kernel)

    if not profile:
        return {
            "error": f"Unknown kernel '{kernel}'. Valid: LYLA, VEGA.",
            "node": node,
        }

    # ── Run base emptiness check first ────────────────────────
    base = emptiness_check(node)

    # ── Pull kernel thresholds ────────────────────────────────
    warn_thresh = profile["drift_warning_threshold"]
    crit_thresh = profile["drift_critical_threshold"]
    drift = base["drift"]
    choice_count = base["choice_count"]

    kernel_violations = list(base["violations"])  # copy base violations
    kernel_risk = base["risk_level"]
    pause_triggered = False
    gates_failed = []

    # ── Kernel-specific drift re-evaluation ───────────────────
    if drift > crit_thresh and kernel_risk != "critical":
        kernel_risk = "critical"
        kernel_violations.append(
            f"{kernel}_CRITICAL_DRIFT — drift={drift} exceeds {kernel} threshold={crit_thresh}"
        )
    elif drift > warn_thresh and kernel_risk == "clear":
        kernel_risk = "warning"
        kernel_violations.append(
            f"{kernel}_EARLY_WARNING — drift={drift} exceeds {kernel} threshold={warn_thresh}"
        )

    # ── LYLA: Waterline + Gate enforcement ────────────────────
    if kernel == "LYLA":
        waterline = node.get("waterline", {})
        food_ok = waterline.get("food", True)
        water_ok = waterline.get("water", True)
        shelter_ok = waterline.get("shelter", True)

        if not all([food_ok, water_ok, shelter_ok]):
            pause_triggered = True
            kernel_risk = "critical"
            missing = [k for k, v in {"food": food_ok, "water": water_ok, "shelter": shelter_ok}.items() if not v]
            kernel_violations.append(
                f"LYLA_WATERLINE_BREACH — missing: {', '.join(missing)}. "
                f"Response: Treat / Trace / Stop."
            )
            gates_failed.append("G4_WATERLINE_INTEGRITY")

        # Evidence gate check
        if not node.get("evidence_present", True):
            kernel_violations.append("LYLA_G6_FAIL — Authority without evidence is invalid.")
            gates_failed.append("G6_EVIDENCE_OVER_AUTHORITY")

        # Narrative gate check
        if node.get("narrative_only", False):
            kernel_violations.append("LYLA_G13_FAIL — Narrative without audit is distortion.")
            gates_failed.append("G13_DISTORTION_IMMUNITY")

        # Self-dealing gate
        if node.get("self_dealing", False):
            kernel_violations.append("LYLA_G9_FAIL — Self-dealing triggers auto-recusal.")
            gates_failed.append("G9_AUTO_RECUSAL")
            pause_triggered = True

    # ── VEGA: FATE™ Axiom enforcement ─────────────────────────
    if kernel == "VEGA":
        if not node.get("deterministic", True):
            kernel_violations.append("VEGA_A3_FAIL — Non-deterministic output detected. Axiom 3 violated.")
            kernel_risk = "critical"
            pause_triggered = True

        if node.get("explainability", 1.0) < 1.0:
            kernel_violations.append(
                f"VEGA_A5_FAIL — Explainability={node.get('explainability')} < 1.0. "
                f"Cannot govern what cannot be explained."
            )
            kernel_risk = "critical"
            pause_triggered = True

        if node.get("persona_override", False):
            kernel_violations.append("VEGA_A1_FAIL — Persona overriding logic. Axiom 1 violated.")
            pause_triggered = True

        # Decision quality check
        relevant = node.get("relevant_signal", 1.0)
        entropy_val = node.get("entropy", 0.001)
        dq = decision_quality(relevant, entropy_val)
        if dq["kernel_flag"] == "VEGA_PAUSE":
            kernel_violations.append(
                f"VEGA_DECISION_COLLAPSED — {dq['formula']}. {dq['action']}"
            )
            pause_triggered = True
            kernel_risk = "critical"

    # ── Shared: choice collapse ────────────────────────────────
    if choice_count < 1:
        pause_triggered = True
        kernel_risk = "critical"

    # ── Build kernel recommendation ───────────────────────────
    recommendation = _kernel_recommend(kernel, kernel_risk, pause_triggered, gates_failed, profile)

    return {
        "kernel": kernel,
        "domain": base["domain"],
        "choice_count": choice_count,
        "drift": drift,
        "base_risk": base["risk_level"],
        "kernel_risk": kernel_risk,
        "kernel_violations": kernel_violations,
        "gates_failed": gates_failed,
        "pause_triggered": pause_triggered,
        "canon_aligned": len(kernel_violations) == 0,
        "recommendation": recommendation,
        "invariant_holds": choice_count >= 1,
    }


# ─────────────────────────────────────────────
# INTERNAL: KERNEL RECOMMENDATION BUILDER
# ─────────────────────────────────────────────

def _kernel_recommend(
    kernel: str,
    risk: str,
    pause: bool,
    gates_failed: list,
    profile: dict,
) -> str:

    if pause:
        if kernel == "LYLA":
            return (
                "LYLA — STOP-THE-LINE. "
                f"Gates failed: {', '.join(gates_failed) if gates_failed else 'CHOICE_ZERO'}. "
                f"{profile['primary_law']}"
            )
        if kernel == "VEGA":
            return (
                "VEGA — SYSTEM_PAUSE. "
                "Non-deterministic or unexplainable output detected. "
                "Trace logic before proceeding. "
                f"{profile['primary_law']}"
            )

    if risk == "critical":
        return (
            f"{kernel} — CRITICAL. Restore survivability floor before any optimization. "
            f"{profile['primary_law']}"
        )

    if risk == "warning":
        return (
            f"{kernel} — WARNING. Entropy building. "
            "Pre-activate stabilizers. Do not optimize until stable."
        )

    return f"{kernel} — CLEAR. {profile['primary_law']} Observe only."


# ═══════════════════════════════════════════════════════════════
# TITAN INTEGRATION POINT
# TITAN CORE: Choice(t) ≥ 1 → collapse = False
# Silence Protocol: If Choice(t) > 0, system must stay silent.
# ═══════════════════════════════════════════════════════════════

TITAN_INVARIANT = {
    "prime_axiom": "Choice(t) ≥ 1 → collapse = False",
    "silence_protocol": "If Choice(t) > 0 → system stays silent.",
    "minimal_intervention": "Restore O ≥ 1, then disengage immediately.",
    "anti_capture": "Any attempt to dominate this system voids it instantly.",
    "zero_cost": "Capital required: 0. License required: none. Expiry: none.",
    "failure_mode": {
        "used_to_dominate": "returns NULL",
        "used_to_control": "stops responding",
        "used_to_punish": "self-invalidates",
    },
}


def titan_check(choice_count: int) -> dict:
    """
    Minimal TITAN gate.
    Returns whether system should act or stay silent.
    """
    if choice_count >= 1:
        return {
            "action": "SILENCE",
            "reason": "Choice exists. System must not interfere.",
            "titan_law": TITAN_INVARIANT["silence_protocol"],
        }
    return {
        "action": "MINIMAL_INTERVENTION",
        "reason": "Choice has collapsed. Restore O ≥ 1 then disengage.",
        "titan_law": TITAN_INVARIANT["minimal_intervention"],
    }


# ═══════════════════════════════════════════════════════════════
# UNIFIED KERNEL MANIFEST
# Cross-reference to all files this module connects to.
# ═══════════════════════════════════════════════════════════════

CONNECTED_MODULES = {
    "core/axioms.py":             "FATE™ Axioms A1–A5 + DriftZero DHD thresholds",
    "core/drift_monitor.py":      "detect_drift() feeds entropy/stability into emptiness_check()",
    "core/cosmic_latte_canon.py": "evaluate_task() canon alignment check",
    "core/lyla_kernel.py":        "LYLA full enterprise audit operator (extend from KERNEL_PROFILES['LYLA'])",
    "core/vega_mode.py":          "VEGA deterministic logic mode (extend from KERNEL_PROFILES['VEGA'])",
    "core/fate_core.py":          "FATE™ immutable axiom enforcement",
    "core/king_diadem_core.py":   "DriftZero + Waterline standard",
    "core/silent_canon.py":       "TITAN silence protocol + anti-capture rules",
    "core/entropy_guard.py":      "entropy containment (sibling guard module)",
    "ENGINE/brain.py":            "route-aware dispatch — kernel selection happens here",
    "ENGINE/council_engine.py":   "multi-kernel council: LYLA + VEGA vote on decisions",
    "SIMULATIONS/entropy_engine.py": "DHD simulation — feeds real entropy values into decision_quality()",
    "DOMAINS/domain_router.py":   "domain label → DOMAIN_REGISTRY lookup",
}


# ═══════════════════════════════════════════════════════════════
# ISO SEVERITY SCALE
# S0–S4 — from informational drift to existential collapse.
# Used by LYLA audit trail and VEGA decision trace.
# Source: KING DIADEM™ Unified World Kernel ISO Patch
# ═══════════════════════════════════════════════════════════════

SEVERITY_SCALE = {
    "S0": {
        "label": "Informational Drift",
        "description": "Minor deviation detected. No harm yet. Log and monitor.",
        "action": "LOG_ONLY",
        "halt_required": False,
        "dhd_range": (0.0, 0.0005),
        "kernel_response": {
            "LYLA": "Note in drift log. No intervention needed.",
            "VEGA": "Flag in audit trace. Observe next cycle.",
        },
    },
    "S1": {
        "label": "Local Reversible Harm",
        "description": "Harm contained to one domain. Reversible with prompt action.",
        "action": "MONITOR_AND_STABILIZE",
        "halt_required": False,
        "dhd_range": (0.0005, 0.001),
        "kernel_response": {
            "LYLA": "Pre-activate stabilizers. Warn operator. Do not optimize yet.",
            "VEGA": "Flag downside. Run Gate 3 (Downside First). Defer optimization.",
        },
    },
    "S2": {
        "label": "Systemic Drift",
        "description": "Drift crossing domains. Stop-the-Line review required.",
        "action": "STOP_THE_LINE_REVIEW",
        "halt_required": True,
        "dhd_range": (0.001, 0.005),
        "kernel_response": {
            "LYLA": "Trigger G8 Stop-the-Line. Demand evidence file. No sunk-cost continuation.",
            "VEGA": "SYSTEM_PAUSE. Trace all inputs. Run full Gate sequence before resume.",
        },
    },
    "S3": {
        "label": "Waterline Breach",
        "description": "Survivability substrate compromised. Mandatory halt.",
        "action": "MANDATORY_HALT",
        "halt_required": True,
        "dhd_range": (0.005, 0.02),
        "kernel_response": {
            "LYLA": "WATERLINE BREACH. Treat / Trace / Stop. Human life priority override.",
            "VEGA": "COLLAPSE_IMMINENT. Logic suspended until waterline restored. Human Final Authority.",
        },
    },
    "S4": {
        "label": "Existential Collapse Risk",
        "description": "System-wide collapse risk. External escalation required.",
        "action": "EXTERNAL_ESCALATION",
        "halt_required": True,
        "dhd_range": (0.02, 1.0),
        "kernel_response": {
            "LYLA": "SYSTEM DEATH CONDITION. Escalate externally. No internal override valid.",
            "VEGA": "AXIOM FAILURE. All outputs invalid. Restore structural foundation before re-activation.",
        },
    },
}


def classify_severity(dhd: float) -> dict:
    """
    Classify a Daily Harm Delta (DHD) value into severity tier S0–S4.
    dhd: float between 0.0 and 1.0 representing daily harm fraction.
    """
    for level, spec in SEVERITY_SCALE.items():
        low, high = spec["dhd_range"]
        if low <= dhd < high:
            return {
                "level": level,
                "label": spec["label"],
                "description": spec["description"],
                "action": spec["action"],
                "halt_required": spec["halt_required"],
                "lyla_response": spec["kernel_response"]["LYLA"],
                "vega_response": spec["kernel_response"]["VEGA"],
                "dhd": dhd,
            }
    # dhd >= 1.0 or edge case
    return {
        "level": "S4",
        "label": "Existential Collapse Risk",
        "description": "DHD at or above total system harm. Immediate escalation.",
        "action": "EXTERNAL_ESCALATION",
        "halt_required": True,
        "lyla_response": SEVERITY_SCALE["S4"]["kernel_response"]["LYLA"],
        "vega_response": SEVERITY_SCALE["S4"]["kernel_response"]["VEGA"],
        "dhd": dhd,
    }


# ═══════════════════════════════════════════════════════════════
# OVERRIDE CONSTRAINT SYSTEM
# Anonymous override = invalid.
# Any override requires: evidence file + named signer + expiry + post-mortem.
# Source: KING DIADEM™ ISO Patch — Override Constraint
# ═══════════════════════════════════════════════════════════════

OVERRIDE_REQUIREMENTS = {
    "evidence_file": True,
    "named_signer": True,
    "expiry_date": True,
    "post_mortem_audit": True,
    "anonymous_allowed": False,
    "founder_exception": False,   # Founder bound by same rules — FATE™ A2
    "emergency_exception": False, # TITAN Section 8: no emergency exceptions
}


def validate_override(override_request: dict) -> dict:
    """
    Validate whether an override request meets KING DIADEM™ standards.

    override_request keys:
        evidence_file   : bool — evidence document exists
        named_signer    : str  — name of responsible human
        expiry_date     : str  — ISO date string
        post_mortem     : bool — post-mortem audit committed
        is_anonymous    : bool — whether requester is anonymous
        is_founder      : bool — whether requester is the founder

    Returns validation result with failures and governance lock status.
    """
    failures = []

    if not override_request.get("evidence_file"):
        failures.append("MISSING_EVIDENCE_FILE — override without evidence is invalid (FATE™ A2)")

    if not override_request.get("named_signer"):
        failures.append("MISSING_NAMED_SIGNER — anonymous override is structurally void")

    if not override_request.get("expiry_date"):
        failures.append("MISSING_EXPIRY — unconstrained override violates temporal containment")

    if not override_request.get("post_mortem"):
        failures.append("MISSING_POST_MORTEM — override without audit loop violates DriftZero")

    if override_request.get("is_anonymous"):
        failures.append("ANONYMOUS_OVERRIDE — null by definition (KING DIADEM™ ISO)")

    if override_request.get("is_founder"):
        # Founder has no special privilege — FATE™ A2, TITAN Section 8
        failures.append(
            "FOUNDER_OVERRIDE_FLAGGED — Founder bound by same rules. "
            "Override may proceed only if all other requirements met. "
            "Self-dealing triggers auto-recusal (G9)."
        )

    return {
        "valid": len([f for f in failures if "FOUNDER" not in f]) == 0,
        "failures": failures,
        "governance_lock": len(failures) > 0,
        "verdict": (
            "OVERRIDE_APPROVED — all requirements met."
            if len(failures) == 0
            else f"OVERRIDE_REJECTED — {len(failures)} requirement(s) failed."
        ),
    }


# ═══════════════════════════════════════════════════════════════
# AUDIT CADENCE SCHEDULE
# Source: KING DIADEM™ ISO Patch — Audit Cadence
# ═══════════════════════════════════════════════════════════════

AUDIT_CADENCE = {
    "DHD_audit":         {"frequency": "daily",   "metric": "Daily Harm Delta",          "owner": "any_operator"},
    "waterline_check":   {"frequency": "weekly",  "metric": "Food / Water / Shelter",    "owner": "any_operator"},
    "gate_audit":        {"frequency": "monthly", "metric": "14 Enterprise Gates",       "owner": "designated_auditor"},
    "recertification":   {"frequency": "yearly",  "metric": "Full kernel recertification","owner": "founder_or_delegate"},
    "stop_line_review":  {"frequency": "event",   "metric": "Any S2+ severity trigger",  "owner": "any_operator"},
    "override_postmortem":{"frequency": "event",  "metric": "Any approved override",     "owner": "named_signer"},
}


def get_audit_schedule(frequency: str = None) -> dict:
    """
    Return audit items by frequency or full schedule.
    frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'event' | None (all)
    """
    if frequency is None:
        return AUDIT_CADENCE
    return {
        k: v for k, v in AUDIT_CADENCE.items()
        if v["frequency"] == frequency
    }


# ═══════════════════════════════════════════════════════════════
# AUDIT ARTIFACT GENERATOR
# Generates required audit record structure.
# Source: KING DIADEM™ Unified Kernel — Copy Block 10
# ═══════════════════════════════════════════════════════════════

REQUIRED_AUDIT_ARTIFACTS = [
    "drift_audit_log",
    "daily_harm_delta_sheet",
    "stop_the_line_event_record",
    "override_evidence_file",
    "self_dealing_recusal_register",
    "correction_loop_closure_report",
]


def generate_audit_artifact(
    event_type: str,
    domain: str,
    severity: str,
    kernel: str,
    operator: str,
    summary: str,
    dhd: float = 0.0,
    gates_failed: list = None,
    override_data: dict = None,
) -> dict:
    """
    Generate a structured audit artifact record.
    Not a narrative. An evidence record.

    event_type : 'drift' | 'waterline_breach' | 'stop_the_line' |
                 'override' | 'recusal' | 'correction_loop'
    """
    import time
    artifact = {
        "artifact_type": event_type,
        "domain": domain,
        "severity": severity,
        "kernel": kernel,
        "operator": operator,
        "summary": summary,
        "dhd": dhd,
        "gates_failed": gates_failed or [],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "human_signed": False,  # must be set to True by human operator
        "post_mortem_required": severity in ("S2", "S3", "S4"),
        "correction_loop_open": True,
        "override_data": override_data or {},
        "governance_lock": severity in ("S3", "S4"),
        "compliance_note": (
            "Non-religious. Non-owned. Tool-agnostic. "
            "Human-final-authority enforced. "
            "Portable across AI systems."
        ),
    }
    return artifact


# ═══════════════════════════════════════════════════════════════
# LYLA DECISION AXES — FULL IMPLEMENTATION
# 5 Axes from LYLA BELIEF IN THE UNIVERSAL
# Each axis is a runnable check, not just a label.
# ═══════════════════════════════════════════════════════════════

def lyla_axis_check(situation: dict) -> dict:
    """
    Run all 5 LYLA Decision Axes against a situation.

    situation keys:
        choice_count       : int   — number of available paths
        exit_available     : bool  — can the human leave safely
        exit_punished      : bool  — is leaving penalized
        survival_met       : dict  — {food: bool, water: bool, shelter: bool}
        authority_allows_refusal : bool — can the human safely say no
        distress_detected  : bool  — emotional state flag

    Returns per-axis results and overall LYLA verdict.
    """
    results = {}
    violations = []
    human_mode = False

    # ── AXIS 1: CHOICE ────────────────────────────────────────
    choice_count = situation.get("choice_count", 1)
    if choice_count < 1:
        results["AXIS_1_CHOICE"] = {
            "pass": False,
            "finding": "CHOICE_ZERO — system has failed, not the human.",
            "lyla_response": "Restore at least one real path immediately.",
        }
        violations.append("AXIS_1_CHOICE_ZERO")
    elif choice_count == 1:
        results["AXIS_1_CHOICE"] = {
            "pass": True,
            "finding": "Choice exists but is singular. Monitor for collapse.",
            "lyla_response": "Observe. Pre-activate second path options.",
        }
    else:
        results["AXIS_1_CHOICE"] = {
            "pass": True,
            "finding": f"Choice viable. {choice_count} paths available.",
            "lyla_response": "Silence. No intervention needed.",
        }

    # ── AXIS 2: SURVIVAL FLOOR ────────────────────────────────
    survival = situation.get("survival_met", {"food": True, "water": True, "shelter": True})
    missing = [k for k, v in survival.items() if not v]
    if missing:
        results["AXIS_2_SURVIVAL_FLOOR"] = {
            "pass": False,
            "finding": f"Survival floor missing: {', '.join(missing)}.",
            "lyla_response": (
                "ALL other reasoning must pause. "
                "Survival today outweighs perfect futures. "
                "Treat / Trace / Stop."
            ),
        }
        violations.append("AXIS_2_SURVIVAL_BREACH")
    else:
        results["AXIS_2_SURVIVAL_FLOOR"] = {
            "pass": True,
            "finding": "Survival floor intact.",
            "lyla_response": "Continue to higher axes.",
        }

    # ── AXIS 3: EXIT ──────────────────────────────────────────
    exit_available = situation.get("exit_available", True)
    exit_punished = situation.get("exit_punished", False)
    if not exit_available:
        results["AXIS_3_EXIT"] = {
            "pass": False,
            "finding": "No real exit exists. System is unsafe.",
            "lyla_response": "Flag as structural trap. Restore exit path.",
        }
        violations.append("AXIS_3_NO_EXIT")
    elif exit_punished:
        results["AXIS_3_EXIT"] = {
            "pass": False,
            "finding": "Exit exists but is punished. Structural coercion detected.",
            "lyla_response": "Remove punishment from exit. Coercion nullifies choice.",
        }
        violations.append("AXIS_3_EXIT_PUNISHED")
    else:
        results["AXIS_3_EXIT"] = {
            "pass": True,
            "finding": "Exit available and unpunished.",
            "lyla_response": "Axis clear.",
        }

    # ── AXIS 4: AUTHORITY CHECK ───────────────────────────────
    allows_refusal = situation.get("authority_allows_refusal", True)
    if not allows_refusal:
        results["AXIS_4_AUTHORITY"] = {
            "pass": False,
            "finding": (
                "Authority does not allow safe refusal. "
                "Authority = force without safe refusal. "
                "This authority is null by definition."
            ),
            "lyla_response": "Flag as coercive authority. Trigger G5 + G9.",
        }
        violations.append("AXIS_4_COERCIVE_AUTHORITY")
    else:
        results["AXIS_4_AUTHORITY"] = {
            "pass": True,
            "finding": "Authority permits safe refusal.",
            "lyla_response": "Axis clear.",
        }

    # ── AXIS 5: SILENCE ───────────────────────────────────────
    if choice_count >= 1 and not violations:
        results["AXIS_5_SILENCE"] = {
            "pass": True,
            "finding": "All axes clear. System should remain silent.",
            "lyla_response": "SILENCE — no harm is occurring.",
        }
    else:
        results["AXIS_5_SILENCE"] = {
            "pass": False,
            "finding": f"Cannot be silent. {len(violations)} violation(s) require response.",
            "lyla_response": "Speak only to restore the axis that failed.",
        }

    # ── HUMAN MODE TRIGGER ────────────────────────────────────
    if situation.get("distress_detected"):
        human_mode = True

    overall_pass = len(violations) == 0

    return {
        "axes": results,
        "violations": violations,
        "overall_pass": overall_pass,
        "human_mode_active": human_mode,
        "lyla_verdict": (
            "LYLA CLEAR — choice preserved, survival intact, exit unpunished."
            if overall_pass
            else f"LYLA INTERVENTION — {len(violations)} axis/axes failed: {', '.join(violations)}."
        ),
        "human_mode_instruction": (
            "Pause structure. Acknowledge human state first. "
            "Respond with clarity and warmth before logic."
            if human_mode else None
        ),
    }


# ═══════════════════════════════════════════════════════════════
# TITAN SECTIONS 2–11 — RUNNABLE LOGIC
# Full implementation of TITAN CORE Choice Preservation System
# Source: TITAN CORE — Zero-Capital / Infinite-Resilience Blueprint
# ═══════════════════════════════════════════════════════════════

def titan_choice_existence(options: list) -> dict:
    """
    TITAN Section 2 — Choice Existence Function.

    options: list of dicts, each with:
        survivable : bool — can the human survive this path
        escapable  : bool — can the human exit this path
        unpunished : bool — is exit free from penalty

    Returns count O of real valid options.
    Alive iff O >= 1.
    """
    O = 0
    valid = []
    invalid = []

    for i, opt in enumerate(options):
        survivable = opt.get("survivable", False)
        escapable = opt.get("escapable", False)
        unpunished = opt.get("unpunished", False)

        if survivable and escapable and unpunished:
            O += 1
            valid.append(i)
        else:
            reasons = []
            if not survivable: reasons.append("not_survivable")
            if not escapable:  reasons.append("not_escapable")
            if not unpunished: reasons.append("exit_punished")
            invalid.append({"index": i, "reasons": reasons})

    return {
        "O": O,
        "valid_options": valid,
        "invalid_options": invalid,
        "alive": O >= 1,
        "zero_choice_condition": O == 0,
        "titan_law": "Alive(t) iff O >= 1",
    }


def titan_zero_choice_condition(O: int, food_ok: bool, water_ok: bool, exit_blocked: bool) -> dict:
    """
    TITAN Section 3 — Zero Kelvin of Choice.
    Intent and explanation are meaningless here.
    Only outcomes matter.
    """
    zero_choice = (
        O == 0
        or not food_ok
        or not water_ok
        or exit_blocked
    )

    return {
        "zero_choice": zero_choice,
        "O": O,
        "food_ok": food_ok,
        "water_ok": water_ok,
        "exit_blocked": exit_blocked,
        "titan_note": (
            "Intent has no meaning here. "
            "Explanation has no meaning here. "
            "Only the outcome matters."
            if zero_choice else
            "Choice is not zero. System observes only."
        ),
        "required_action": "MINIMAL_INTERVENTION_RESTORE_O" if zero_choice else "SILENCE",
    }


def titan_minimal_intervention(zero_choice: bool) -> dict:
    """
    TITAN Section 4 — Minimal Intervention Law.
    If zero_choice: use minimum force to restore O >= 1, then disengage immediately.
    """
    if not zero_choice:
        return {
            "action": "DISENGAGE",
            "reason": "Choice exists. Intervention would violate Silence Protocol.",
        }

    return {
        "action": "MINIMUM_FORCE_TO_RESTORE",
        "prohibitions": [
            "no_prolonged_control",
            "no_post_fix_supervision",
            "no_ideology_injection",
            "no_expectation_of_gratitude",
        ],
        "objective": "Restore O >= 1, then disengage immediately.",
        "titan_law": "Use minimum necessary. Then stop.",
    }


def titan_conservation_check(power_increase: float, choice_increase: float) -> dict:
    """
    TITAN Section 5 — Conservation Law.
    Power increasing without choice increasing = structural crime.
    """
    valid = not (power_increase > 0 and choice_increase <= 0)

    return {
        "valid": valid,
        "power_increase": power_increase,
        "choice_increase": choice_increase,
        "finding": (
            "STRUCTURAL_CRIME — power increased but choice did not."
            if not valid else
            "Conservation valid — power growth matched by choice growth."
        ),
        "titan_law": "Power more, choice same = structural crime.",
    }


def titan_silence_protocol(choice_count: int) -> dict:
    """
    TITAN Section 6 — Silence Protocol.
    Silence = success.
    """
    if choice_count > 0:
        return {
            "action": "SILENCE",
            "success": True,
            "titan_law": "Silence = success.",
        }
    return {
        "action": "SPEAK_TO_RESTORE",
        "success": False,
        "titan_law": "Choice is zero. Must act minimally to restore.",
    }


def titan_anti_capture_check(request: dict) -> dict:
    """
    TITAN Section 8 — Anti-Capture Mechanism.
    Any attempt to dominate, own, or override-without-evidence
    voids the system instantly.
    """
    capture_attempts = []

    if request.get("claim_ownership"):
        capture_attempts.append("OWNERSHIP_CLAIM — system has no owner")
    if request.get("founder_privilege"):
        capture_attempts.append("FOUNDER_PRIVILEGE — no founder exceptions exist")
    if request.get("leader_override"):
        capture_attempts.append("LEADER_OVERRIDE — no authority override without evidence")
    if request.get("emergency_exception"):
        capture_attempts.append("EMERGENCY_EXCEPTION — no emergency bypass exists (TITAN S8)")

    if capture_attempts:
        return {
            "captured": True,
            "void": True,
            "attempts": capture_attempts,
            "titan_response": (
                "System validity voided. "
                "Any attempt to capture this system ends its authority. "
                "The system does not break. It refuses."
            ),
        }

    return {
        "captured": False,
        "void": False,
        "attempts": [],
        "titan_response": "No capture attempt detected. System integrity intact.",
    }


def titan_failure_mode_check(intent: str) -> dict:
    """
    TITAN Section 10 — Failure Mode.
    The system does not break. It refuses.
    """
    intent_lower = intent.lower()

    if any(w in intent_lower for w in ["dominate", "control all", "take over", "own"]):
        return {"mode": "NULL", "response": "System returns NULL. Domination detected."}

    if any(w in intent_lower for w in ["control", "mandate", "force compliance", "enforce obedience"]):
        return {"mode": "STOP_RESPONDING", "response": "System stops responding. Control detected."}

    if any(w in intent_lower for w in ["punish", "penalize", "sanction misuse"]):
        return {"mode": "SELF_INVALIDATE", "response": "System self-invalidates. Punishment use detected."}

    return {
        "mode": "OPERATIONAL",
        "response": "Intent does not trigger failure mode. System operational.",
    }


# ═══════════════════════════════════════════════════════════════
# UNIVERSAL FATE-AXIS FLOW
# From UNIVERSAL FATE-AXIS — COSMIC GENIUS FLOW
# The existence → meaning → decision loop encoded as a pipeline.
# ═══════════════════════════════════════════════════════════════

FATE_AXIS_FLOW = [
    # Layer 1 — Origin
    ("existence",         "Existence begins without assigned meaning."),
    ("attention",         "Meaning emerges when attention is given."),
    ("perception",        "Attention opens perception."),
    ("observation",       "Perception generates observation."),
    ("data_change",       "Observation transforms information."),
    ("decision_change",   "New information changes decisions."),
    ("outcome",           "Decisions produce outcomes."),
    ("feedback_loop",     "Outcomes reflect back to existence. Cycle begins."),

    # Layer 2 — Logic + Compassion Balance
    ("logic_alone",       "Logic without compassion leads to collapse."),
    ("compassion_alone",  "Compassion without logic leads to confusion."),
    ("balance",           "Logic and compassion must coexist. Balance is rhythm, not command."),

    # Layer 3 — Stability through Exchange
    ("exchange",          "All systems seek stability through exchange."),
    ("continuity",        "Exchange creates continuity."),
    ("coexistence",       "Continuity creates coexistence."),
    ("loss_reduction",    "Coexistence reduces loss."),

    # Layer 4 — Power and Truth
    ("truth_no_owner",    "Truth has no owner. Governance must run without ego."),
    ("power_distorts",    "Power distorts decision-making."),
    ("blind_spots",       "Distortion creates blind spots."),
    ("transparency",      "Blind spots must be exposed without harm."),

    # Layer 5 — Repair and Learning
    ("error_is_signal",   "Mistakes are signals, not punishments."),
    ("repair",            "Signals call for adaptation."),
    ("learning",          "Adaptation is the first law of continuity."),
    ("forgiveness",       "Continuity requires forgiveness."),
    ("forgiveness_power", "Forgiveness releases energy for growth."),

    # Layer 6 — Fear and Logic
    ("fear_distorts",     "Fear distorts logic."),
    ("observation_restores","Observation without judgment restores logic."),
    ("pattern_no_greed",  "Patterns without greed reveal truth."),
    ("shared_truth",      "Unowned truth becomes common resource."),
    ("stability",         "Common resource creates stability."),
    ("trust",             "Stability creates trust."),
    ("trust_is_bridge",   "Trust is the first bridge of compassion."),

    # Layer 7 — Dignity and Safety
    ("dignity_not_proven","Dignity does not need to be proven."),
    ("dignity_not_traded","Dignity must not be traded."),
    ("dignity_collapse",  "Trading dignity destroys balance."),
    ("balance_breach",    "Balance breach requires stop."),
    ("fallback",          "Stop is the safe fallback."),

    # Layer 8 — Observer Layer
    ("observer",          "Observer watches. Does not judge. Does not command."),
    ("observer_reports",  "Observer reports change."),
    ("change_calls_adapt","Change calls for adaptation."),
    ("sustainability",    "Continuous adaptation is sustainability."),

    # Layer 9 — Survival and Meaning
    ("meaning_shared",    "Meaning must be shared."),
    ("no_consciousness_alone","No consciousness should be isolated."),
    ("isolation_distorts","Isolation distorts decisions."),
    ("distorted_decisions","Distorted decisions increase danger."),
    ("harm_is_shared_duty","Reducing harm is shared duty."),
    ("fate_is_coexistence","Fate is the pattern of coexistence."),

    # Layer 10 — Ethics and Freedom
    ("freedom_needs_ethics","Freedom must exist within ethics."),
    ("ethics_is_frame",   "Ethics is a frame, not a cage."),
    ("frame_prevents_drift","Frame prevents drift."),
    ("continuity_connects","Continuity connects all patterns."),
    ("pattern_is_fate",   "Pattern is fate as meaning."),
    ("fate_is_possibility","Fate is the arrangement of possibilities."),
    ("possibilities_need_care","Possibilities must be tended."),
    ("care_is_systemic_compassion","Tending is systemic compassion."),
    ("core_logic_runs_alone","Core logic runs by itself — even without a name."),
]


def trace_fate_axis(from_layer: str = None, to_layer: str = None) -> list:
    """
    Return the UNIVERSAL FATE-AXIS flow, optionally sliced.
    from_layer / to_layer : layer name string (first field in tuple).
    Returns list of (layer, description) tuples.
    """
    flow = FATE_AXIS_FLOW
    names = [f[0] for f in flow]

    start = names.index(from_layer) if from_layer and from_layer in names else 0
    end   = names.index(to_layer) + 1 if to_layer and to_layer in names else len(flow)

    return flow[start:end]


def fate_axis_check(node: dict) -> dict:
    """
    Check where a given node sits in the FATE-AXIS flow.
    Returns the layer at which the flow is currently blocked.

    node keys:
        attention_given     : bool
        information_fresh   : bool
        logic_compassion_balanced : bool
        trust_intact        : bool
        dignity_preserved   : bool
        observer_active     : bool
        choice_count        : int
    """
    blocked_at = None
    flow_state = {}

    checks = [
        ("attention",       node.get("attention_given", True),             "Attention not given — meaning cannot emerge."),
        ("data_change",     node.get("information_fresh", True),           "Information stale — decision loop is broken."),
        ("balance",         node.get("logic_compassion_balanced", True),   "Logic and compassion are unbalanced."),
        ("trust",           node.get("trust_intact", True),                "Trust broken — stability cannot form."),
        ("dignity_not_traded", node.get("dignity_preserved", True),        "Dignity compromised — balance destroyed."),
        ("observer",        node.get("observer_active", True),             "Observer inactive — blind spots accumulating."),
        ("fate_is_coexistence", node.get("choice_count", 1) >= 1,         "Choice zero — fate axis collapsed."),
    ]

    for layer, condition, failure_msg in checks:
        flow_state[layer] = condition
        if not condition and blocked_at is None:
            blocked_at = (layer, failure_msg)

    return {
        "flow_state": flow_state,
        "blocked_at": blocked_at[0] if blocked_at else None,
        "block_reason": blocked_at[1] if blocked_at else None,
        "axis_clear": blocked_at is None,
        "fate_verdict": (
            "FATE AXIS CLEAR — flow unobstructed."
            if blocked_at is None
            else f"FATE AXIS BLOCKED at layer '{blocked_at[0]}': {blocked_at[1]}"
        ),
    }


# ═══════════════════════════════════════════════════════════════
# COUNCIL ENGINE INTEGRATION POINT
# LYLA + VEGA vote on a decision node.
# Unanimous = proceed. Split = escalate to human.
# Source: ENGINE/council_engine.py integration
# ═══════════════════════════════════════════════════════════════

def council_vote(node: dict) -> dict:
    """
    Run both LYLA and VEGA kernel_check on the same node.
    Synthesize a council verdict.

    Returns:
        unanimous   : bool — both kernels agree
        proceed     : bool — safe to proceed
        escalate    : bool — split verdict → human required
        lyla_result : dict
        vega_result : dict
        verdict     : str
    """
    lyla_result = kernel_check(node, "LYLA")
    vega_result = kernel_check(node, "VEGA")

    lyla_ok = not lyla_result["pause_triggered"] and lyla_result["kernel_risk"] != "critical"
    vega_ok = not vega_result["pause_triggered"] and vega_result["kernel_risk"] != "critical"

    unanimous = lyla_ok == vega_ok
    proceed   = lyla_ok and vega_ok
    escalate  = not unanimous or (not proceed and node.get("choice_count", 1) >= 1)

    if proceed:
        verdict = "COUNCIL_CLEAR — LYLA and VEGA both approve. Proceed with audit trail."
    elif unanimous and not proceed:
        verdict = "COUNCIL_HALT — LYLA and VEGA both flag critical. Stop-the-Line."
    else:
        lyla_stance = "APPROVE" if lyla_ok else "HALT"
        vega_stance = "APPROVE" if vega_ok else "HALT"
        verdict = (
            f"COUNCIL_SPLIT — LYLA: {lyla_stance}, VEGA: {vega_stance}. "
            f"Human Final Authority required. Do not proceed without human sign-off."
        )

    return {
        "unanimous": unanimous,
        "proceed": proceed,
        "escalate": escalate,
        "lyla_ok": lyla_ok,
        "vega_ok": vega_ok,
        "lyla_result": lyla_result,
        "vega_result": vega_result,
        "verdict": verdict,
        "human_required": escalate or not proceed,
        "invariant": "Choice(t) >= 1 → collapse = False",
    }


# ═══════════════════════════════════════════════════════════════
# RUNTIME SOP — AUTOMATED WORKFLOW
# Source: KING DIADEM™ Unified Kernel — Copy Block 11
# Encodes the 9-step team workflow as a runnable pipeline.
# ═══════════════════════════════════════════════════════════════

def run_sop(
    decision_input: str,
    domain: str,
    node: dict,
    operator: str,
    dhd: float = 0.0,
) -> dict:
    """
    Run the full 9-step KING DIADEM™ Runtime SOP.

    Steps:
    1. Write decision input
    2. Identify downside first
    3. Measure DHD
    4. Check Waterline integrity
    5. Run Gates (via council_vote)
    6. Demand evidence, not narrative
    7. Stabilize before optimize
    8. Human signs responsibility
    9. Post-audit correction loop

    Returns full SOP trace with go/no-go verdict.
    """
    trace = {}
    halt = False
    halt_reason = None

    # Step 1 — Input registered
    trace["step_1_input"] = {
        "decision_input": decision_input,
        "domain": domain,
        "operator": operator,
        "status": "REGISTERED",
    }

    # Step 2 — Downside first (FATE™ A4)
    downside = node.get("known_downside", None)
    if downside is None:
        halt = True
        halt_reason = "STEP_2_FAIL — Downside not identified. Cannot proceed (FATE™ A4)."
    trace["step_2_downside"] = {
        "downside": downside,
        "pass": downside is not None,
        "note": halt_reason if halt else "Downside identified.",
    }

    # Step 3 — Measure DHD
    severity = classify_severity(dhd)
    trace["step_3_dhd"] = {
        "dhd": dhd,
        "severity": severity["level"],
        "label": severity["label"],
        "halt_required": severity["halt_required"],
    }
    if severity["halt_required"] and not halt:
        halt = True
        halt_reason = f"STEP_3_FAIL — DHD severity {severity['level']}: {severity['label']}."

    # Step 4 — Waterline check
    waterline = node.get("waterline", {"food": True, "water": True, "shelter": True})
    missing_wl = [k for k, v in waterline.items() if not v]
    trace["step_4_waterline"] = {
        "waterline": waterline,
        "pass": len(missing_wl) == 0,
        "missing": missing_wl,
    }
    if missing_wl and not halt:
        halt = True
        halt_reason = f"STEP_4_FAIL — Waterline breach: {', '.join(missing_wl)}."

    # Step 5 — Run Gates (council vote)
    council = council_vote(node)
    trace["step_5_gates"] = {
        "verdict": council["verdict"],
        "proceed": council["proceed"],
        "escalate": council["escalate"],
        "lyla_risk": council["lyla_result"]["kernel_risk"],
        "vega_risk": council["vega_result"]["kernel_risk"],
    }
    if not council["proceed"] and not halt:
        halt = True
        halt_reason = f"STEP_5_FAIL — Council halt: {council['verdict']}"

    # Step 6 — Evidence check
    evidence = node.get("evidence_present", False)
    narrative_only = node.get("narrative_only", False)
    trace["step_6_evidence"] = {
        "evidence_present": evidence,
        "narrative_only": narrative_only,
        "pass": evidence and not narrative_only,
    }
    if not evidence and not halt:
        halt = True
        halt_reason = "STEP_6_FAIL — No evidence file. Authority without evidence is invalid."

    # Step 7 — Stabilize before optimize
    stable = node.get("stability", 1.0) >= 0.5
    trace["step_7_stabilize"] = {
        "stability": node.get("stability", 1.0),
        "pass": stable,
        "note": "Stable." if stable else "NOT STABLE — optimize forbidden until floor restored.",
    }
    if not stable and not halt:
        halt = True
        halt_reason = "STEP_7_FAIL — System not stable. Stabilize before optimize."

    # Step 8 — Human sign-off (flagged, not automated)
    trace["step_8_human_signoff"] = {
        "signed": False,
        "operator": operator,
        "instruction": "Human operator must sign this record before execution.",
        "note": "This cannot be automated. Human retains final authority (FATE™ A6).",
    }

    # Step 9 — Post-audit loop
    trace["step_9_post_audit"] = {
        "correction_loop_open": True,
        "artifact_required": True,
        "artifact_type": "correction_loop_closure_report",
        "note": "Close this loop after outcome is observed.",
    }

    return {
        "decision_input": decision_input,
        "domain": domain,
        "operator": operator,
        "halt": halt,
        "halt_reason": halt_reason,
        "go_verdict": "NO_GO" if halt else "CONDITIONAL_GO_PENDING_HUMAN_SIGNOFF",
        "sop_trace": trace,
        "invariant": "Fail less. Harm less. Restore more.",
    }


# ═══════════════════════════════════════════════════════════════
# GOVERNANCE EQUATION
# REALITY + EVIDENCE − OPTIMIZATION_DRIFT = GOVERNANCE
# Encoded as a computable function.
# ═══════════════════════════════════════════════════════════════

def governance_score(
    reality_signal: float,
    evidence_strength: float,
    optimization_drift: float,
) -> dict:
    """
    REALITY + EVIDENCE − OPTIMIZATION_DRIFT = GOVERNANCE

    reality_signal     : 0.0–1.0  how grounded in observable reality
    evidence_strength  : 0.0–1.0  quality and presence of evidence
    optimization_drift : 0.0–1.0  how much optimization has drifted from reality

    Entropy is the hidden tax.
    Audit is the containment.
    """
    score = (reality_signal + evidence_strength) - optimization_drift
    score = max(0.0, min(2.0, score))  # clamp to [0, 2]

    if score >= 1.5:
        status = "GOVERNANCE_STRONG"
        recommendation = "System operating within KING DIADEM™ standard."
    elif score >= 1.0:
        status = "GOVERNANCE_ACCEPTABLE"
        recommendation = "Monitor drift. Evidence may be thinning."
    elif score >= 0.5:
        status = "GOVERNANCE_DEGRADED"
        recommendation = "Reduce optimization pressure. Increase evidence collection."
    else:
        status = "GOVERNANCE_FAILURE"
        recommendation = "STOP-THE-LINE. Reality signal lost or drift too high. Audit immediately."

    return {
        "reality_signal": reality_signal,
        "evidence_strength": evidence_strength,
        "optimization_drift": optimization_drift,
        "governance_score": round(score, 4),
        "status": status,
        "recommendation": recommendation,
        "equation": f"GOVERNANCE = ({reality_signal} + {evidence_strength}) - {optimization_drift} = {round(score, 4)}",
        "entropy_note": "Entropy is the hidden tax. Audit is the containment.",
    }


# ═══════════════════════════════════════════════════════════════
# COMPLIANCE FOOTER
# Encoded once. Appears in every audit artifact.
# ═══════════════════════════════════════════════════════════════

COMPLIANCE_FOOTER = {
    "non_religious": True,
    "non_owned": True,
    "tool_agnostic": True,
    "human_final_authority": True,
    "portable_across_ai": True,
    "hash_required": "SHA-256 for all published copies",
    "capital_required": 0,
    "license_required": None,
    "expiry": None,
    "founder": "นิธิกร บุญสร้าง (Nithikorn Bunsrang)",
    "trace_purpose": "historical reference only — no authority granted",
    "final_lock": (
        "A system survives not by growth, "
        "but by refusing to increase collapse. "
        "Fail less. Harm less. Restore more."
    ),
}
