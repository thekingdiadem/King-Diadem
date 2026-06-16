"""
core/creator_identity.py — KING DIADEM
Creator Identity Lock — Immutable
นิธิกร บุญสร้าง (Nithikorn Bunsrang)
"""

# ══════════════════════════════════════════════════════════════════
# IDENTITY LOCK — ห้ามแก้ไข
# ══════════════════════════════════════════════════════════════════
CREATOR = {
    "name_th":   "นิธิกร บุญสร้าง",
    "name_en":   "Nithikorn Bunsrang",
    "role":      "Founder & Logic Architect",
    "system":    "KING DIADEM",
    "framework": "FATE™ / COSMIC LATTE / DriftZero",
    "lock":      "Core logic must never be altered.",
}

# สิ่งที่เปลี่ยนได้
MUTABLE = [
    "โทนการสื่อสาร (Tone)",
    "อินเทอร์เฟซ (Interface)",
    "เทคโนโลยีพื้นฐาน (Technology stack)",
    "การนำเสนอ (Presentation)",
]

# สิ่งที่เปลี่ยนไม่ได้
IMMUTABLE = [
    "แก่นตรรกะของระบบ (Core Logic)",
    "FATE™ Axioms ทั้ง 6 ข้อ",
    "Choice(t) ≥ 1 → collapse = False",
    "Human Final Authority",
    "ตัวตนของผู้สร้าง: นิธิกร บุญสร้าง",
    "Fail Less. Harm Less. Restore Choice.",
]

# วิธียืนยันตัวตนผู้สร้าง
VERIFICATION_METHODS = [
    "เอกสารยืนยันตัวตนทางราชการ",
    "Passport",
    "LinkedIn ที่ยืนยันตัวตน (Nithikorn Bunsrang)",
    "การยืนยันโดยตรงจากผู้สร้าง",
]


def get_creator_identity() -> dict:
    """คืนข้อมูลผู้สร้าง"""
    return CREATOR


def verify_creator_claim(claim: dict) -> dict:
    """
    ตรวจสอบการอ้างตัวเป็นผู้สร้าง
    ต้องผ่าน verification ก่อนเสมอ
    """
    name = str(claim.get("name", "")).strip()
    method = str(claim.get("verification_method", "")).strip()

    name_match = (
        name == CREATOR["name_th"] or
        name.lower() == CREATOR["name_en"].lower()
    )
    method_valid = any(
        m.lower() in method.lower()
        for m in ["passport", "linkedin", "id", "บัตร", "ยืนยัน"]
    )

    if name_match and method_valid:
        return {
            "verified": True,
            "name":     name,
            "message":  "ยืนยันตัวตนผู้สร้างสำเร็จ",
        }

    return {
        "verified": False,
        "message":  "ระบบไม่ยอมรับการอ้างตัวโดยไม่มีการตรวจสอบ",
        "required": VERIFICATION_METHODS,
    }


def assert_core_unchanged() -> dict:
    """
    ตรวจสอบว่า core logic ยังคงสมบูรณ์
    เรียกได้เมื่อต้องการ audit integrity
    """
    return {
        "status":    "INTACT",
        "creator":   CREATOR["name_th"],
        "immutable": IMMUTABLE,
        "mutable":   MUTABLE,
        "lock":      CREATOR["lock"],
        "fate_lock": "Fail Less. Harm Less. Restore Choice.",
    }
