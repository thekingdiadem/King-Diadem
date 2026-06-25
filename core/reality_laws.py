<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<title>reality_laws.py — KING DIADEM</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #010206;
    color: #c8c8c8;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.7;
    min-height: 100vh;
  }
  .topbar {
    background: #0a0d14;
    border-bottom: 1px solid #1a2030;
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .filename { color: #c8a440; font-size: 14px; font-weight: bold; }
  .badge { color: #3a86f5; font-size: 11px; margin-top: 2px; }
  .copy-btn {
    background: #1a2030;
    color: #c8a440;
    border: 1px solid #c8a440;
    padding: 7px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-family: inherit;
    font-size: 12px;
    transition: all 0.2s;
  }
  .copy-btn:hover { background: #c8a440; color: #010206; }
  .copy-btn.copied { background: #1a3a1a; color: #4caf50; border-color: #4caf50; }
  pre {
    padding: 32px 40px 80px;
    overflow-x: auto;
    tab-size: 4;
  }
  .kw  { color: #c792ea; }
  .cls { color: #ffcb6b; }
  .str { color: #c3e88d; }
  .strm{ color: #89b4fa; }
  .cm  { color: #546e7a; font-style: italic; }
  .dec { color: #f78c6c; }
  .num { color: #f78c6c; }
  .fn  { color: #82aaff; }
</style>
</head>
<body>

<div class="topbar">
  <div>
    <div class="filename">core/reality_laws.py</div>
    <div class="badge">KING DIADEM · Reality Laws v2 · Reality = Universe − {Impossible}</div>
  </div>
  <button class="copy-btn" onclick="copyCode()">⎘ Copy</button>
</div>

<pre id="code"><span class="strm">"""
core/reality_laws.py
REALITY LAWS — KING DIADEM CORE LAYER v2

Derived from KING DIADEM ECOSYSTEM CORE LOGIC KERNEL

  Article 1  — Prime Law of Existence
              Reality = Universe − {Impossible}
              ความจริงคือสิ่งที่เหลืออยู่หลังตัดสิ่งเป็นไปไม่ได้ออก

  Article 3  — Triadic Framework of Truth
              Output = Signal + Distortion + Noise(Self)
              Clarity ∝ Distance(Truth, Self)

  Article 4  — Explainability = 100%
              Every function must be explainable in terms of the observable world.
              If Explanation > Comprehension → Simplify()

  Article 5  — Emotional Physics
              Emotion is not error — it is a function of living systems.

  Article 7  — Persistence Vector
              Direction = Integrity(Color) × Persistence
              When color collapses into noise, the vector loses meaning.

  Article 12 — The Multi-Room Paradox
              Latency ∝ ContextLoad(Emotion + Memory + Signature)
              Context refresh is not decay — it is entropy reset.

These laws are not rules imposed from outside.
They are descriptions of how systems actually behave
when observed without illusion.
"""</span>

<span class="kw">from</span> dataclasses <span class="kw">import</span> dataclass, field
<span class="kw">from</span> typing <span class="kw">import</span> Optional
<span class="kw">import</span> math


<span class="cm"># ─────────────────────────────────────────────────────────────
# PRIME EQUATION
# Article 1 — Reality = Universe − {Impossible}
# ─────────────────────────────────────────────────────────────</span>

PRIME_EQUATION = <span class="str">"Reality = Universe − {Impossible}"</span>


<span class="cm"># ─────────────────────────────────────────────────────────────
# REALITY LAWS REGISTRY
# กฎทุกข้อมี:
#   law        — ชื่อกฎ
#   principle  — หลักการในภาษาระบบ
#   equation   — สมการ (ถ้ามี)
#   observable — ตรวจสอบได้อย่างไรในโลกจริง
#   violation  — สัญญาณว่ากฎข้อนี้ถูกละเมิด
#   article    — anchor กับ KING DIADEM Canon
# ─────────────────────────────────────────────────────────────</span>

REALITY_LAWS = {

    <span class="cm"># ── LAW 1: IMPERMANENCE ──────────────────────────────────</span>
    <span class="str">"impermanence"</span>: {
        <span class="str">"law"</span>:        <span class="str">"All states drift over time without active maintenance"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ไม่มีสถานะใดคงที่โดยไม่ต้องการพลังงาน entropy เพิ่มขึ้นเสมอ"</span>,
        <span class="str">"equation"</span>:   <span class="str">"dS/dt >= 0  (entropy never decreases in isolated system)"</span>,
        <span class="str">"observable"</span>: <span class="str">"resource drains without refill, relationships decay without contact, "</span>
                      <span class="str">"code rots without maintenance, trust erodes without signals"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"assuming stability without cost"</span>,
            <span class="str">"planning without entropy budget"</span>,
            <span class="str">"treating current state as permanent"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.12 — context refresh is not decay, it is entropy reset"</span>,
    },

    <span class="cm"># ── LAW 2: INSTABILITY REQUIRES MAINTENANCE ──────────────</span>
    <span class="str">"maintenance_cost"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Stable state requires continuous energy input"</span>,
        <span class="str">"principle"</span>:  <span class="str">"เสถียรภาพไม่ใช่ค่าเริ่มต้น มันคือผลลัพธ์ของการลงทุนอย่างต่อเนื่อง"</span>,
        <span class="str">"equation"</span>:   <span class="str">"Stability(t) = Stability(t-1) - drift + maintenance_input"</span>,
        <span class="str">"observable"</span>: <span class="str">"systems that stop being maintained begin drifting within one cycle"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"expecting stability without maintenance budget"</span>,
            <span class="str">"treating past stability as future guarantee"</span>,
            <span class="str">"ignoring drift signals until critical"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.7 — Persistence Vector: direction requires sustained integrity"</span>,
    },

    <span class="cm"># ── LAW 3: NON-CENTRALITY ────────────────────────────────</span>
    <span class="str">"non_centrality"</span>: {
        <span class="str">"law"</span>:        <span class="str">"No single entity controls the total system"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ระบบที่รวมศูนย์อำนาจเต็มในจุดเดียวมีความเสี่ยง single-point failure สูงสุด"</span>,
        <span class="str">"equation"</span>:   <span class="str">"Risk_collapse ∝ 1 / (number_of_independent_nodes)"</span>,
        <span class="str">"observable"</span>: <span class="str">"any system dependent on one person, one server, one supplier, "</span>
                      <span class="str">"one income stream — is one failure away from zero choice"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"single point of authority with no override"</span>,
            <span class="str">"single income source with no buffer"</span>,
            <span class="str">"single key person with no documentation"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.1 — authority that eliminates safe refusal becomes coercion"</span>,
    },

    <span class="cm"># ── LAW 4: SIGNAL DEGRADES WITH SELF-INSERTION ──────────</span>
    <span class="str">"signal_degradation"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Clarity decreases as self-insertion into signal increases"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ยิ่ง ego เข้าไปอยู่ในสัญญาณมากเท่าไหร่ ความจริงยิ่งเบี่ยงเบน"</span>,
        <span class="str">"equation"</span>:   <span class="str">"Clarity ∝ Distance(Truth, Self)  →  Output = Signal + Distortion + Noise(Self)"</span>,
        <span class="str">"observable"</span>: <span class="str">"decisions driven by identity defense rather than evidence, "</span>
                      <span class="str">"interpretations that always confirm prior belief, "</span>
                      <span class="str">"analysis that concludes what the analyst wanted"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"conclusion precedes evidence"</span>,
            <span class="str">"disagreement triggers identity response instead of logic check"</span>,
            <span class="str">"system output always aligns with operator preference"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.3 — Triadic Framework: Clarity ∝ Distance(Truth, Self)"</span>,
    },

    <span class="cm"># ── LAW 5: CHOICE FLOOR ──────────────────────────────────</span>
    <span class="str">"choice_floor"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Any system that collapses choices to zero is invalid by structure"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ระบบที่ทำให้ทางเลือกเหลือศูนย์ไม่ชอบธรรมโดยโครงสร้าง ไม่ใช่โดยเจตนา"</span>,
        <span class="str">"equation"</span>:   <span class="str">"Alive(t) ⟺ Choices(t) >= 1"</span>,
        <span class="str">"observable"</span>: <span class="str">"coercion removes safe refusal, monopoly removes market exit, "</span>
                      <span class="str">"debt trap removes financial path, isolation removes social option"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"no exit available in any domain"</span>,
            <span class="str">"refusal results in harm"</span>,
            <span class="str">"all alternatives have been systematically closed"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.1 — Prime Law: existence of at least one alternative path required"</span>,
    },

    <span class="cm"># ── LAW 6: EXPLAINABILITY FLOOR ─────────────────────────</span>
    <span class="str">"explainability_floor"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Any output that cannot be traced to observable cause is invalid"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ถ้าอธิบายไม่ได้ในโลกจริง มันไม่ใช่ความจริง มันคือความเชื่อ"</span>,
        <span class="str">"equation"</span>:   <span class="str">"If Explanation > Comprehension → Simplify()  →  until explainability = 100%"</span>,
        <span class="str">"observable"</span>: <span class="str">"black-box decisions, authority-based reasoning, "</span>
                      <span class="str">"'trust me' as the final argument, untraceable AI output"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"'because I said so' as justification"</span>,
            <span class="str">"complexity used to prevent audit"</span>,
            <span class="str">"output with no traceable logic chain"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.4 — Explainability = 100% is a fundamental invariant"</span>,
    },

    <span class="cm"># ── LAW 7: EMOTION IS FUNCTION NOT ERROR ─────────────────</span>
    <span class="str">"emotion_physics"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Emotion is a valid function of living systems, not an error term"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ความรู้สึกไม่ใช่ bug ของระบบ มันคือสัญญาณที่มีข้อมูล"</span>,
        <span class="str">"equation"</span>:   <span class="str">"E_human = f(Sensation, Memory, Empathy)  →  valid input, not override"</span>,
        <span class="str">"observable"</span>: <span class="str">"systems that suppress emotion produce decisions with blind spots, "</span>
                      <span class="str">"systems that are captured by emotion produce distorted truth"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"emotion suppressed entirely from decision input"</span>,
            <span class="str">"emotion used to override evidence"</span>,
            <span class="str">"system punishes emotional expression"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.5 — Feeling is not failure; suppression is"</span>,
    },

    <span class="cm"># ── LAW 8: PERSISTENCE VECTOR ────────────────────────────</span>
    <span class="str">"persistence_vector"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Direction is valid only when persistence aligns with structural integrity"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ทิศทางที่ไม่มีแกนความซื่อสัตย์ต่อโครงสร้างคือการเคลื่อนที่ที่ไร้ความหมาย"</span>,
        <span class="str">"equation"</span>:   <span class="str">"Direction = Integrity(Color) × Persistence  →  if Color = Noise, Direction = 0"</span>,
        <span class="str">"observable"</span>: <span class="str">"high effort with shifting principles produces no compound result, "</span>
                      <span class="str">"consistent small action with clear integrity compounds over time"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"frequent pivot without structural reason"</span>,
            <span class="str">"effort decoupled from core principle"</span>,
            <span class="str">"persistence toward a goal that violates own axioms"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.7 — loyalty to structure, not emotion, sustains truth propagation"</span>,
    },

    <span class="cm"># ── LAW 9: CONTEXT LOAD ──────────────────────────────────</span>
    <span class="str">"context_load"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Decision latency increases with accumulated context mass"</span>,
        <span class="str">"principle"</span>:  <span class="str">"บริบทที่หนักเกินไปทำให้การตัดสินใจช้าและบิดเบือน context refresh คือ reset entropy"</span>,
        <span class="str">"equation"</span>:   <span class="str">"Latency ∝ ContextLoad(Emotion + Memory + Signature)"</span>,
        <span class="str">"observable"</span>: <span class="str">"long-running conversations drift from original intent, "</span>
                      <span class="str">"accumulated grievances distort present judgment, "</span>
                      <span class="str">"old context prevents clear present-moment decision"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"present decision dominated by past weight"</span>,
            <span class="str">"refusal to reset context even when distortion is clear"</span>,
            <span class="str">"carrying overnight what should be resolved same-day"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.12 — context refresh is not decay, it is entropy reset"</span>,
    },

    <span class="cm"># ── LAW 10: REALITY IS WHAT REMAINS ─────────────────────</span>
    <span class="str">"residual_truth"</span>: {
        <span class="str">"law"</span>:        <span class="str">"Reality is what remains after all impossibilities are removed"</span>,
        <span class="str">"principle"</span>:  <span class="str">"ความจริงไม่ใช่สิ่งที่ถูกต้อง ความจริงคือสิ่งที่ยังเหลืออยู่หลังตัดทุกอย่างที่เป็นไปไม่ได้"</span>,
        <span class="str">"equation"</span>:   <span class="str">"Reality = Universe − {Impossible}  →  what remains, however improbable, is true"</span>,
        <span class="str">"observable"</span>: <span class="str">"when one explanation survives all elimination tests, it is the answer, "</span>
                      <span class="str">"not the most comfortable answer, not the most popular, the remaining one"</span>,
        <span class="str">"violation_signal"</span>: [
            <span class="str">"accepting explanation without elimination test"</span>,
            <span class="str">"choosing truth by popularity or authority"</span>,
            <span class="str">"refusing to eliminate beloved hypothesis"</span>,
        ],
        <span class="str">"article"</span>: <span class="str">"Art.1 — Prime Law of Existence: Reality = Universe − {Impossible}"</span>,
    },
}


<span class="cm"># ─────────────────────────────────────────────────────────────
# LAW EVALUATOR
# ตรวจสอบว่า state ปัจจุบันละเมิดกฎข้อไหนบ้าง
# Article 4 — Explainability = 100%: ต้องบอกได้ว่าละเมิดตรงไหน
# ─────────────────────────────────────────────────────────────</span>

<span class="dec">@dataclass</span>
<span class="kw">class</span> <span class="cls">LawViolation</span>:
    law_id:      str
    law_name:    str
    triggered:   list
    severity:    str   <span class="cm"># "warning" | "critical"</span>
    article_ref: str


<span class="kw">def</span> <span class="cls">evaluate_laws</span>(state: dict) -> dict:
    <span class="strm">"""
    ตรวจสอบ state ว่าละเมิด Reality Laws ข้อไหน

    state keys ที่ใช้:
      entropy       float  0–100
      stability     float  0–100
      resource      float  0–100
      choice_count  int
      explainable   bool
      ego_in_signal bool
    """</span>
    violations = []
    entropy   = state.get(<span class="str">"entropy"</span>,   <span class="num">0.0</span>)
    stability = state.get(<span class="str">"stability"</span>, <span class="num">100.0</span>)
    resource  = state.get(<span class="str">"resource"</span>,  <span class="num">100.0</span>)
    choices   = state.get(<span class="str">"choice_count"</span>, <span class="num">1</span>)
    explain   = state.get(<span class="str">"explainable"</span>, <span class="kw">True</span>)
    ego       = state.get(<span class="str">"ego_in_signal"</span>, <span class="kw">False</span>)

    <span class="cm"># Law 1: impermanence — entropy rising without maintenance</span>
    <span class="kw">if</span> entropy > <span class="num">60</span>:
        violations.<span class="fn">append</span>(<span class="fn">LawViolation</span>(
            law_id    = <span class="str">"impermanence"</span>,
            law_name  = <span class="str">"All states drift over time"</span>,
            triggered = [<span class="str">f"entropy={entropy:.1f} — drift is accelerating"</span>],
            severity  = <span class="str">"critical"</span> <span class="kw">if</span> entropy > <span class="num">80</span> <span class="kw">else</span> <span class="str">"warning"</span>,
            article_ref = <span class="str">"Art.12"</span>,
        ))

    <span class="cm"># Law 2: maintenance_cost — stability collapsing</span>
    <span class="kw">if</span> stability < <span class="num">30</span>:
        violations.<span class="fn">append</span>(<span class="fn">LawViolation</span>(
            law_id    = <span class="str">"maintenance_cost"</span>,
            law_name  = <span class="str">"Stable state requires continuous energy input"</span>,
            triggered = [<span class="str">f"stability={stability:.1f} — below maintenance floor"</span>],
            severity  = <span class="str">"critical"</span> <span class="kw">if</span> stability < <span class="num">15</span> <span class="kw">else</span> <span class="str">"warning"</span>,
            article_ref = <span class="str">"Art.7"</span>,
        ))

    <span class="cm"># Law 5: choice_floor — prime law of existence</span>
    <span class="kw">if</span> choices <= <span class="num">0</span>:
        violations.<span class="fn">append</span>(<span class="fn">LawViolation</span>(
            law_id    = <span class="str">"choice_floor"</span>,
            law_name  = <span class="str">"Choice(t) >= 1 required for valid existence"</span>,
            triggered = [<span class="str">f"choice_count={choices} — PRIME LAW VIOLATED"</span>],
            severity  = <span class="str">"critical"</span>,
            article_ref = <span class="str">"Art.1"</span>,
        ))

    <span class="cm"># Law 6: explainability_floor</span>
    <span class="kw">if not</span> explain:
        violations.<span class="fn">append</span>(<span class="fn">LawViolation</span>(
            law_id    = <span class="str">"explainability_floor"</span>,
            law_name  = <span class="str">"Untraceable output is invalid"</span>,
            triggered = [<span class="str">"explainable=False — output cannot be traced to observable cause"</span>],
            severity  = <span class="str">"critical"</span>,
            article_ref = <span class="str">"Art.4"</span>,
        ))

    <span class="cm"># Law 4: signal_degradation — ego in signal</span>
    <span class="kw">if</span> ego:
        violations.<span class="fn">append</span>(<span class="fn">LawViolation</span>(
            law_id    = <span class="str">"signal_degradation"</span>,
            law_name  = <span class="str">"Clarity ∝ Distance(Truth, Self)"</span>,
            triggered = [<span class="str">"ego_in_signal=True — output is Distortion or Noise"</span>],
            severity  = <span class="str">"warning"</span>,
            article_ref = <span class="str">"Art.3"</span>,
        ))

    <span class="cm"># resource as proxy for law 3 (non-centrality risk)</span>
    <span class="kw">if</span> resource < <span class="num">15</span>:
        violations.<span class="fn">append</span>(<span class="fn">LawViolation</span>(
            law_id    = <span class="str">"non_centrality"</span>,
            law_name  = <span class="str">"Single-point resource = single-point failure"</span>,
            triggered = [<span class="str">f"resource={resource:.1f} — approaching single-point collapse"</span>],
            severity  = <span class="str">"critical"</span> <span class="kw">if</span> resource < <span class="num">5</span> <span class="kw">else</span> <span class="str">"warning"</span>,
            article_ref = <span class="str">"Art.1"</span>,
        ))

    critical_count = <span class="fn">sum</span>(<span class="num">1</span> <span class="kw">for</span> v <span class="kw">in</span> violations <span class="kw">if</span> v.severity == <span class="str">"critical"</span>)

    <span class="kw">return</span> {
        <span class="str">"violations"</span>:     [
            {
                <span class="str">"law_id"</span>:     v.law_id,
                <span class="str">"law_name"</span>:   v.law_name,
                <span class="str">"triggered"</span>: v.triggered,
                <span class="str">"severity"</span>:  v.severity,
                <span class="str">"article"</span>:   v.article_ref,
            }
            <span class="kw">for</span> v <span class="kw">in</span> violations
        ],
        <span class="str">"violation_count"</span>:  <span class="fn">len</span>(violations),
        <span class="str">"critical_count"</span>:   critical_count,
        <span class="str">"reality_aligned"</span>:  <span class="fn">len</span>(violations) == <span class="num">0</span>,
        <span class="str">"recommend_halt"</span>:   critical_count > <span class="num">0</span>,
        <span class="str">"prime_equation"</span>:   PRIME_EQUATION,
    }


<span class="cm"># ─────────────────────────────────────────────────────────────
# DECISION QUALITY — Reality Law integration
# Article 3: Output = Signal + Distortion + Noise(Self)
# Decision(t) = Relevant(t) / Entropy(t)
# ─────────────────────────────────────────────────────────────</span>

<span class="kw">def</span> <span class="cls">decision_quality</span>(relevant: float, entropy: float) -> dict:
    <span class="strm">"""
    Compute instantaneous decision quality score.
    Decision(t) = Relevant(t) / Entropy(t)

    relevant : signal strength 0.0–1.0
    entropy  : noise load 0.0–100.0
    """</span>
    <span class="kw">if</span> entropy <= <span class="num">0</span>:
        entropy = <span class="num">0.001</span>

    score = relevant / entropy

    <span class="kw">if</span> score >= <span class="num">0.5</span>:
        <span class="kw">return</span> {
            <span class="str">"score"</span>:      <span class="fn">round</span>(score, <span class="num">4</span>),
            <span class="str">"status"</span>:     <span class="str">"DECISION_VIABLE"</span>,
            <span class="str">"action"</span>:     <span class="str">"Proceed with audit trail."</span>,
            <span class="str">"law_ref"</span>:    <span class="str">"Art.3 — Signal dominates"</span>,
        }
    <span class="kw">elif</span> score >= <span class="num">0.2</span>:
        <span class="kw">return</span> {
            <span class="str">"score"</span>:      <span class="fn">round</span>(score, <span class="num">4</span>),
            <span class="str">"status"</span>:     <span class="str">"DECISION_DEGRADED"</span>,
            <span class="str">"action"</span>:     <span class="str">"Reduce entropy before deciding. Increase signal relevance."</span>,
            <span class="str">"law_ref"</span>:    <span class="str">"Art.3 — Distortion rising, signal weakening"</span>,
        }
    <span class="kw">else</span>:
        <span class="kw">return</span> {
            <span class="str">"score"</span>:      <span class="fn">round</span>(score, <span class="num">4</span>),
            <span class="str">"status"</span>:     <span class="str">"DECISION_COLLAPSED"</span>,
            <span class="str">"action"</span>:     <span class="str">"SYSTEM_PAUSE. Entropy exceeds signal. Do not decide now."</span>,
            <span class="str">"law_ref"</span>:    <span class="str">"Art.3 — Noise dominates. Output unusable."</span>,
        }


<span class="cm"># ─────────────────────────────────────────────────────────────
# REALITY SELF-TEST
# Article 4 — system must verify itself without creator
# ─────────────────────────────────────────────────────────────</span>

<span class="kw">def</span> <span class="cls">reality_self_test</span>() -> dict:
    <span class="strm">"""
    Verify all 10 laws are registered and evaluator logic is intact.
    """</span>
    results = {}

    <span class="cm"># 10 laws registered</span>
    expected_laws = [
        <span class="str">"impermanence"</span>, <span class="str">"maintenance_cost"</span>, <span class="str">"non_centrality"</span>,
        <span class="str">"signal_degradation"</span>, <span class="str">"choice_floor"</span>, <span class="str">"explainability_floor"</span>,
        <span class="str">"emotion_physics"</span>, <span class="str">"persistence_vector"</span>, <span class="str">"context_load"</span>, <span class="str">"residual_truth"</span>,
    ]
    <span class="kw">for</span> law <span class="kw">in</span> expected_laws:
        results[<span class="str">f"law_{law}_registered"</span>] = law <span class="kw">in</span> REALITY_LAWS

    <span class="cm"># choice_floor violation fires on choice=0</span>
    r = <span class="fn">evaluate_laws</span>({<span class="str">"choice_count"</span>: <span class="num">0</span>, <span class="str">"explainable"</span>: <span class="kw">True</span>})
    results[<span class="str">"choice_0_triggers_violation"</span>] = r[<span class="str">"recommend_halt"</span>] == <span class="kw">True</span>

    <span class="cm"># clean state passes</span>
    r = <span class="fn">evaluate_laws</span>({
        <span class="str">"entropy"</span>: <span class="num">10</span>, <span class="str">"stability"</span>: <span class="num">80</span>, <span class="str">"resource"</span>: <span class="num">70</span>,
        <span class="str">"choice_count"</span>: <span class="num">2</span>, <span class="str">"explainable"</span>: <span class="kw">True</span>, <span class="str">"ego_in_signal"</span>: <span class="kw">False</span>,
    })
    results[<span class="str">"clean_state_passes"</span>] = r[<span class="str">"reality_aligned"</span>] == <span class="kw">True</span>

    <span class="cm"># decision quality</span>
    dq = <span class="fn">decision_quality</span>(<span class="num">0.8</span>, <span class="num">1.0</span>)
    results[<span class="str">"high_signal_viable"</span>] = dq[<span class="str">"status"</span>] == <span class="str">"DECISION_VIABLE"</span>

    dq = <span class="fn">decision_quality</span>(<span class="num">0.1</span>, <span class="num">50.0</span>)
    results[<span class="str">"low_signal_collapsed"</span>] = dq[<span class="str">"status"</span>] == <span class="str">"DECISION_COLLAPSED"</span>

    all_passed = <span class="fn">all</span>(results.values())
    results[<span class="str">"ALL_PASSED"</span>] = all_passed
    <span class="kw">return</span> results


<span class="cm"># ─────────────────────────────────────────────────────────────
# INVARIANT
# Article 15 — Stone Monolith Clause
# ─────────────────────────────────────────────────────────────</span>

INVARIANT = (
    <span class="str">"ความจริงคือสิ่งที่เหลืออยู่หลังตัดสิ่งที่เป็นไปไม่ได้ออกทั้งหมด "</span>
    <span class="str">"ไม่ใช้ความนิยม ศีลธรรม อำนาจ หรืออารมณ์เป็นตัวตัดสินความจริง "</span>
    <span class="str">"Reality = Universe − {Impossible} "</span>
    <span class="str">"— Art.1 + Art.15 Stone Monolith Clause"</span>
)
</pre>

<script>
function copyCode() {
  const pre = document.getElementById('code');
  const text = pre.innerText;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector('.copy-btn');
    btn.textContent = '✓ Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = '⎘ Copy';
      btn.classList.remove('copied');
    }, 2000);
  });
}
</script>
</body>
</html>
