"""WORLD_MODEL — แบบจำลองโลกของการตัดสินใจ (ไม่ใช้ AI · ค่าเดิมได้ผลเดิม)

จุดเรียกเดียว: observe(text) → WorldView ที่สภา 6 เสียง · VEGA · AI ใช้ร่วมกัน
  human_bias      กับดักความคิด 10 แบบ + คำถามแก้ทาง          → PATICCA (ต้นเหตุ)
  reversibility   สิ่งที่ล็อกให้ย้อนกลับยาก + วิธีทำให้ถอยได้     → VEGA (ด้านเสีย)
  concentration   ไข่ใบเดียวในตะกร้าเดียว + วิธีกระจาย          → VEGA
  consequences    ผลลำดับสอง: ใครได้รับผล และควรถามอะไร         → CIVIL
  time_horizon    มองแค่ระยะสั้นหรือยาว + ชวนมองอีกระยะ         → COSMOS
  earth_guardian  เผาไร่/เผาขยะ/ทิ้งของเสียลงน้ำ (เดิม)          · small_animal_model ความปลอดภัยสัตว์เล็ก (เดิม)
"""
from __future__ import annotations

from typing import NamedTuple


class WorldView(NamedTuple):
    biases: list
    locks: list
    concentration: list
    ripples: list
    horizon: str
    horizon_prompt: str

    def empty(self) -> bool:
        return not (self.biases or self.locks or self.concentration or self.ripples)

    def note(self) -> str:
        """บรรทัดสั้นๆ ให้ AI เป็นบริบท — สิ่งที่แบบจำลองเห็น ไม่ใช่คำตัดสิน"""
        bits = []
        if self.biases:
            bits.append("กับดักความคิด=" + ",".join(b.th for b in self.biases))
        if self.locks:
            bits.append("ย้อนกลับยาก=" + ",".join(lk.th for lk in self.locks))
        if self.concentration:
            bits.append("รวมความเสี่ยง=" + ",".join(c.th for c in self.concentration))
        if self.ripples:
            bits.append("ได้รับผลด้วย=" + ",".join(r.th for r in self.ripples))
        return "[WORLD MODEL: " + " · ".join(bits + [f"มองระยะ={self.horizon}"]) + "]"


def observe(text) -> WorldView:
    from WORLD_MODEL.concentration import risks
    from WORLD_MODEL.consequences import ripples
    from WORLD_MODEL.human_bias import detect_biases
    from WORLD_MODEL.reversibility import locks
    from WORLD_MODEL.time_horizon import horizon, prompt
    t = str(text or "")
    return WorldView(detect_biases(t), locks(t), risks(t), ripples(t), horizon(t), prompt(t))
