# legacy/ — โค้ดที่ระบบยังไม่ได้ใช้

ไฟล์ในโฟลเดอร์นี้ย้ายมาจากตำแหน่งเดิม (โครงสร้างโฟลเดอร์คงเดิม เช่น `legacy/ENGINE/world_model.py` เดิมคือ `ENGINE/world_model.py`)
เพราะไม่มีโค้ดส่วนไหนของแอปหรือเทสต์ import ถึงเลย — ตรวจจากการไล่ import ทั้งแบบปกติและแบบโหลดด้วยชื่อ (`importlib` / `_try_import`) เริ่มจาก `app.py`

- **ไม่ได้ลบ** — เก็บไว้เป็นต้นแบบความคิด ถ้าจะนำกลับมาใช้ ให้ย้ายกลับตำแหน่งเดิม (`git mv legacy/X X`) แล้วต่อเข้ากับ `app.py` พร้อมเพิ่มเทสต์
- ไฟล์ในนี้ import กันด้วย path เดิม (เช่น `from DATABASE.user_db import ...`) จึง **import จาก legacy/ ตรงๆ ไม่ได้** จนกว่าจะย้ายกลับ
- ไฟล์ที่ `portfolio.html` อ้างถึง (และไฟล์ที่ไฟล์เหล่านั้น import) ยังอยู่ที่เดิม เพื่อไม่ให้หน้าผลงานชี้ไปที่ไฟล์ที่ไม่มี
- เอกสารออกแบบ (`.md`) ในโฟลเดอร์เดิมยังอยู่ที่เดิม

## รายชื่อไฟล์ที่ย้ายมา
- `AI/HUMAN_PROTOCOL.py`
- `AI/choice_points.py`
- `AI/consensus_engine.py`
- `AI/decision_engine.py`
- `AI/decision_heatmap.py`
- `AI/decision_tree.py`
- `AI/decision_tree_expand.py`
- `AI/galaxy_expand.py`
- `AI/galaxy_tree.py`
- `AI/galaxy_visualization.py`
- `AI/global_decision_map.py`
- `AI/king_response.py`
- `AI/node_consensus.py`
- `AI/persona_engine.py`
- `AI/planetary_reality.py`
- `AI/planetary_signal.py`
- `AI/simulation_engine.py`
- `AI/strategic_engine.py`
- `AI/strategic_memory.py`
- `AI/world_connector.py`
- `AI_KERNEL/core_principles.py`
- `AI_KERNEL/scl7_core.py`
- `AI_KERNEL/udok.py`
- `AI_KERNEL/unified_world_kernel.py`
- `AUTH/api_keys.py`
- `AUTH/auth.py`
- `DATABASE/credit_store.py`
- `DATABASE/init_db.py`
- `DATABASE/payment_store.py`
- `DATABASE/user_db.py`
- `DATABASE/user_store.py`
- `DOMAINS/business_engine.py`
- `DOMAINS/domain_router.py`
- `DOMAINS/human_engine.py`
- `DOMAINS/life_engine.py`
- `DOMAINS/world_engine.py`
- `ENGINE/ai_needs.py`
- `ENGINE/core.py`
- `ENGINE/dialogue_engine.py`
- `ENGINE/energy_governor.py`
- `ENGINE/eternal_snapshot_patch.py`
- `ENGINE/future_simulator.py`
- `ENGINE/human_state_engine.py`
- `ENGINE/intent_engine.py`
- `ENGINE/kernel_runtime.py`
- `ENGINE/king_response.py`
- `ENGINE/language_detector.py`
- `ENGINE/learning_engine.py`
- `ENGINE/path_generator.py`
- `ENGINE/persona_engine.py`
- `ENGINE/response_translator.py`
- `ENGINE/survival_map_engine.py`
- `ENGINE/survival_nodes.py`
- `ENGINE/world_intelligence.py`
- `ENGINE/world_model.py`
- `EXAMPLES/__init__.py`
- `GLOBAL_NODE/feed_store.py`
- `GLOBAL_NODE/mobile_node.py`
- `GLOBAL_NODE/node_trust.py`
- `INTEGRATIONS/__init__.py`
- `INTEGRATIONS/google_docs.py`
- `INTEGRATIONS/google_maps.py`
- `INTEGRATIONS/google_search.py`
- `INTELLIGENCE/__init__.py`
- `INTELLIGENCE/decision_intelligence.py`
- `INTELLIGENCE/pattern_engine.py`
- `INTELLIGENCE/risk_engine.py`
- `INTERFACE/__init__.py`
- `INTERFACE/api.py`
- `KERNEL/__init__.py`
- `KING_DIADEM_core.py`
- `MODELS/__init__.py`
- `NETWORK/node_sync.py`
- `NETWORK/planetary_node.py`
- `PAYMENT/stripe_webhook.py`
- `PAYMENT/wallet_engine.py`
- `PERSONA/lyla_core.py`
- `PERSONA/vega_core.py`
- `SECURITY/survival_mode.py`
- `SIMULATIONS/entropy_engine.py`
- `SIMULATIONS/scenario_engine.py`
- `SIMULATIONS/scenario_tree.py`
- `WORLD_MODEL/environment.py`
- `WORLD_MODEL/human_behavior.py`
- `WORLD_MODEL/survival_threshold.py`
- `core/api_keys.py`
- `core/axioms.py`
- `core/brain.py`
- `core/creator_identity.py`
- `core/master_brain.py`
- `core/memory_store.py`
- `core/navigator.py`
- `core/survival_threshold.py`
- `core/truth_system.py`
- `core/users.py`
- `static/style.css`

## ย้ายมาเพิ่ม (พี่อนุญาต)
ระบบตัดสินใจชุดเก่าและ facade ฐานข้อมูล — ไม่มีโค้ดของแอปเรียกแล้ว แต่ถ้ามีใคร import จะได้ pipeline/ฐานข้อมูลชุดที่สองซ้อนกับของจริง
- `ENGINE/brain.py` · `ENGINE/decision.py` · `ENGINE/intent.py` · `ENGINE/risk.py` — pipeline รุ่นเก่า (ของจริง: `ENGINE/decision_engine.py`, `AI/intent_engine.py`, `ENGINE/risk_engine.py`)
- `ENGINE/intervention_engine.py` — ใช้โดย `ENGINE/brain.py` เท่านั้น
- `core/database.py` — facade ของ `DATABASE/db.py`

ต่อมา `portfolio.html` แก้ให้ตรงกับระบบจริง (ไม่อ้างถึงไฟล์ที่ไม่ได้ต่อเข้าระบบแล้ว) จึงย้ายตามมา:
- `AUTH/` ทั้งโฟลเดอร์ — ระบบบัญชี/เครดิตชุดที่สอง (ของจริงอยู่ใน `app.py` + `DATABASE/db.py`)
- `PAYMENT/` ทั้งโฟลเดอร์ — Stripe Checkout ชุดเก่า (ของจริง: `/create-checkout-session` · `/wallet/topup` · `/webhook/stripe` ใน `app.py`)
- `NETWORK/global_chat.py` · `NETWORK/global_network.py` — ห้องแชทรวมที่เก็บข้อความผู้ใช้ถาวร (ขัดกับหลักไม่เก็บข้อความ)
- `AI_KERNEL/reality_constraint.py` — ซ้ำกับ `core/reality_laws.py` + `AI_KERNEL/belief_core.py` ด้วยเกณฑ์คนละชุด
- `WORLD_MODEL/human_state.py` — ซ้ำกับ `ENGINE/human_engine.py` + survivor engine และใช้สเกลคนละแบบ
- `SECURITY/emergency_mode.py` — แบน IP อัตโนมัติ 24 ชม. (คนที่ใช้ IP ร่วมกันโดนด้วย) ซ้ำกับ `_rate_check` ใน `app.py`

