"""
ENGINE/debt_engine.py — KING DIADEM
FATE™ Debt Freedom Engine
ระบบวางแผนปลดหนี้ภายใต้หลักการ FATE™

Architect: Nithikorn Bunsrang
Route: SURVIVAL
"""

from datetime import datetime, timedelta


# ==================================================
# DEBT MODELS
# ==================================================

def build_debt(name: str, balance: float, annual_rate: float) -> dict:
    return {
        "name":         name,
        "balance":      balance,
        "annual_rate":  annual_rate,
        "monthly_rate": annual_rate / 100 / 12,
    }


# ==================================================
# RANKING STRATEGIES
# ==================================================

def rank_avalanche(debts: list) -> list:
    """ดอกเบี้ยสูงก่อน — ประหยัดดอกเบี้ยรวมได้มากที่สุด"""
    return sorted(debts, key=lambda d: d["annual_rate"], reverse=True)


def rank_snowball(debts: list) -> list:
    """ยอดน้อยก่อน — ปิดหนี้ได้เร็ว สร้าง momentum"""
    return sorted(debts, key=lambda d: d["balance"])


def recommend_strategy(debts: list, monthly_extra: float) -> str:
    """
    แนะนำกลยุทธ์ตามสถานการณ์จริง
    - ถ้าหนี้หลายก้อน balance ต่างกันมาก → Snowball ดีกว่า เพราะ momentum
    - ถ้าดอกเบี้ยต่างกันมาก → Avalanche ดีกว่า เพราะประหยัดจริง
    """
    debts = [d for d in (debts or []) if float(d.get("balance", 0) or 0) > 0]
    if not debts:
        return "snowball"

    rates   = [float(d.get("annual_rate", 0) or 0) for d in debts]
    balances = [float(d["balance"]) for d in debts]

    rate_spread    = max(rates) - min(rates)
    balance_spread = max(balances) - min(balances)
    smallest_bal   = min(balances)

    # ถ้าโปะได้เกิน 30% ของหนี้ก้อนเล็กสุด → Snowball ได้ momentum ไว
    can_quick_win = (monthly_extra / smallest_bal) > 0.3

    if rate_spread > 10 and not can_quick_win:
        return "avalanche"
    if can_quick_win or balance_spread > 50000:
        return "snowball"
    return "avalanche"


# ==================================================
# PAYMENT CALCULATOR
# ==================================================

def simulate_payoff(debts: list, monthly_budget: float,
                    strategy: str = "avalanche") -> dict:
    """
    จำลองการโปะหนี้รายเดือน
    คืน timeline + จำนวนเดือนรวม + ดอกเบี้ยรวมที่จ่าย

    v2 — เงินที่จ่ายต่อเดือนไม่เกินงบจริง:
      เดิมจ่าย "ดอกเบี้ย+1" ทุกก้อนแม้งบไม่พอ (budget_left ติดลบ) → แผนอ้างว่าปลดหนี้ได้
      ทั้งที่จริงหนี้โตขึ้นทุกเดือน ตอนนี้ดอกเบี้ยที่จ่ายไม่ไหวถูกทบเข้าเงินต้น และบอก paid_off ตรงๆ
    """
    if strategy == "avalanche":
        ordered = rank_avalanche(debts)
    else:
        ordered = rank_snowball(debts)

    # deep copy เพื่อไม่แก้ของจริง
    active = [d.copy() for d in ordered]
    for d in active:
        d["balance"]       = max(0.0, float(d.get("balance", 0) or 0))
        d["monthly_rate"]  = float(d.get("monthly_rate", float(d.get("annual_rate", 0) or 0) / 1200))
        d["paid_interest"] = 0.0
        d["months_to_pay"] = 0

    budget = max(0.0, float(monthly_budget or 0))
    timeline = []
    month    = 0
    max_months = 360  # cap 30 ปี
    short_months = 0

    while any(d["balance"] > 0 for d in active) and month < max_months:
        month += 1
        budget_left = budget
        row = {"month": month, "debts": []}

        # จ่ายขั้นต่ำ (ดอกเบี้ย + 1) ทุกก้อนก่อน — เท่าที่งบเหลือ
        for d in active:
            if d["balance"] <= 0:
                row["debts"].append({"name": d["name"], "payment": 0,
                                     "interest": 0, "balance": 0})
                continue
            interest = d["balance"] * d["monthly_rate"]
            due      = min(interest + 1, d["balance"] + interest)
            pay      = min(due, budget_left)
            if pay < due:
                short_months += 1
            d["balance"]       = max(0.0, d["balance"] + interest - pay)
            d["paid_interest"] += interest
            budget_left        -= pay
            row["debts"].append({"name": d["name"], "payment": round(pay, 2),
                                 "interest": round(interest, 2),
                                 "balance": round(d["balance"], 2)})

        # โปะหนี้เป้าหมาย (ก้อนแรกในลิสต์ที่ยังมียอด)
        for d in active:
            if d["balance"] > 0 and budget_left > 0:
                extra = min(budget_left, d["balance"])
                d["balance"]   = max(0.0, d["balance"] - extra)
                budget_left   -= extra
                for r in row["debts"]:
                    if r["name"] == d["name"]:
                        r["payment"] = round(r["payment"] + extra, 2)
                        r["balance"] = round(d["balance"], 2)
                break

        # เช็คหนี้ที่ปิดได้เดือนนี้
        for d in active:
            if d["balance"] <= 0 and d["months_to_pay"] == 0:
                d["months_to_pay"] = month

        timeline.append(row)

    paid_off       = all(d["balance"] <= 0 for d in active)
    total_interest = sum(d["paid_interest"] for d in active)
    payoff_months  = max([d["months_to_pay"] for d in active] + [0]) if paid_off else None

    return {
        "strategy":       strategy,
        "paid_off":       paid_off,
        "payoff_months":  payoff_months,
        "payoff_years":   round(payoff_months / 12, 1) if payoff_months is not None else None,
        "total_interest": round(total_interest, 2),
        "remaining":      round(sum(d["balance"] for d in active), 2),
        "underfunded_payments": short_months,
        "timeline":       timeline,
        "debt_summary":   [{"name": d["name"],
                            "months": d["months_to_pay"] or None,
                            "interest_paid": round(d["paid_interest"], 2)}
                           for d in active],
    }


# ==================================================
# REFINANCE ADVISOR
# ==================================================

def advise_refinance(debts: list, monthly_income: float) -> list:
    """
    ตรวจสอบหนี้ที่ควรรีไฟแนนซ์หรือเจรจาปรับโครงสร้าง
    """
    advice = []
    total_debt = sum(float(d.get("balance", 0) or 0) for d in debts)
    dti = total_debt / (monthly_income * 12) if monthly_income > 0 else 999

    for d in debts:
        if d["annual_rate"] >= 20:
            advice.append({
                "debt":   d["name"],
                "rate":   d["annual_rate"],
                "action": "เจรจาลดดอกเบี้ยหรือรีไฟแนนซ์ด่วน",
                "reason": f"ดอกเบี้ย {d['annual_rate']}% สูงเกินไป ควรพยายามลดให้ต่ำกว่า 15%",
                "how": [
                    "โทรหาธนาคาร/เจ้าหนี้ขอปรับโครงสร้างหนี้",
                    "ถ้าเป็นบัตรเครดิต ขอแปลงเป็นสินเชื่อส่วนบุคคลดอกเบี้ยต่ำกว่า",
                    "เปรียบเทียบสินเชื่อรีไฟแนนซ์จากธนาคารอื่น",
                ]
            })
        elif d["annual_rate"] >= 12 and dti > 0.5:
            advice.append({
                "debt":   d["name"],
                "rate":   d["annual_rate"],
                "action": "พิจารณาปรับโครงสร้างหนี้",
                "reason": "ภาระหนี้รวมสูงเมื่อเทียบรายได้",
                "how": [
                    "ขอยืดระยะเวลาชำระเพื่อลดยอดต่อเดือน",
                    "รวมหนี้หลายก้อนเป็นก้อนเดียวดอกเบี้ยต่ำกว่า",
                ]
            })

    if not advice:
        advice.append({
            "debt":   "ทั้งหมด",
            "action": "ดอกเบี้ยอยู่ในระดับที่จัดการได้",
            "reason": "ไม่จำเป็นต้องรีไฟแนนซ์ด่วน โฟกัสโปะตามแผนดีกว่า",
            "how":    ["ใช้ strategy ที่แนะนำโปะต่อไป"]
        })

    return advice


# ==================================================
# SIDE INCOME IDEAS
# ==================================================

def suggest_side_income(skills: list, target_extra: float) -> list:
    """
    เสนออาชีพเสริมตามทักษะ — ไม่ขายฝัน ให้ตัวเลขจริง
    """
    SKILL_MAP = {
        "ทำอาหาร":   {"job": "รับจ้างทำอาหาร/ข้าวกล่อง/เบเกอรี่",
                      "income_min": 3000, "income_max": 12000,
                      "how": "เริ่มจากขายในกลุ่ม LINE/Facebook ก่อน ไม่ต้องเช่าร้าน"},
        "ถ่ายภาพ":   {"job": "รับถ่ายภาพงานอีเวนต์/พอร์ตเทรต",
                      "income_min": 2000, "income_max": 15000,
                      "how": "ลง Facebook/IG พร้อมผลงาน เริ่มจากราคาถูกเพื่อสร้าง portfolio"},
        "การตลาด":   {"job": "รับทำ Content/โฆษณา Facebook สำหรับธุรกิจเล็ก",
                      "income_min": 3000, "income_max": 10000,
                      "how": "หาลูกค้าจากร้านค้าในละแวกบ้าน เสนอทดลอง 1 เดือนก่อน"},
        "ขับรถ":     {"job": "ไรเดอร์ส่งอาหาร/รับส่งสินค้า",
                      "income_min": 8000, "income_max": 20000,
                      "how": "สมัคร Grab/Shopee Food/LINE MAN เริ่มได้เลยไม่มีเงินลงทุน"},
        "ซ่อมของ":   {"job": "รับซ่อมเครื่องใช้ไฟฟ้า/โทรศัพท์/คอม",
                      "income_min": 4000, "income_max": 12000,
                      "how": "ลงประกาศใน Kaidee/Facebook Marketplace พร้อมราคาชัดเจน"},
        "สอนหนังสือ": {"job": "ติวเตอร์/สอนพิเศษออนไลน์หรือออฟไลน์",
                       "income_min": 3000, "income_max": 12000,
                       "how": "หาในกลุ่ม Facebook ผู้ปกครอง หรือลง QueQ/Tutor Find"},
        "AI":        {"job": "รับงาน Freelance AI/Prompt Engineering",
                      "income_min": 5000, "income_max": 30000,
                      "how": "ลง Fastwork/Freelance.com ด้วยผลงานจริงที่มีอยู่แล้ว"},
    }

    results = []
    for skill in skills:
        for key, data in SKILL_MAP.items():
            if key in skill or skill in key:
                results.append({
                    "skill":      skill,
                    "job":        data["job"],
                    "income_min": data["income_min"],
                    "income_max": data["income_max"],
                    "realistic":  f"{data['income_min']:,}–{data['income_max']:,} บาท/เดือน",
                    "how_to_start": data["how"],
                    "covers_target": data["income_min"] >= target_extra
                })
                break

    if not results:
        results.append({
            "skill":      "ทั่วไป",
            "job":        "ไรเดอร์ส่งอาหาร",
            "income_min": 8000,
            "income_max": 20000,
            "realistic":  "8,000–20,000 บาท/เดือน",
            "how_to_start": "สมัคร Shopee Food/Grab Food ได้เลย ไม่มีเงินลงทุน",
            "covers_target": 8000 >= target_extra
        })

    return results


# ==================================================
# MAIN ENTRY — SURVIVAL ROUTE
# ==================================================

def run_debt_freedom(
    debts: list,
    monthly_income: float,
    monthly_expense: float,
    skills: list = None,
    target_months: int = 24
) -> dict:
    """
    Entry point สำหรับ SURVIVAL route
    รับข้อมูลหนี้ + รายได้ + รายจ่าย คืน plan ครบ
    """
    if skills is None:
        skills = []
    debts = [d for d in (debts or []) if isinstance(d, dict)]
    if not debts:
        return {"system": "FATE_DEBT_FREEDOM", "status": "NO_DEBT",
                "message": "ไม่มีรายการหนี้ให้วางแผน", "lock": "Fail less. Harm less. Restore Choice."}

    monthly_extra = monthly_income - monthly_expense
    if monthly_extra <= 0:
        return {
            "system":  "FATE_DEBT_FREEDOM",
            "status":  "WATERLINE_BREACH",
            "message": "รายได้ไม่พอรายจ่าย — ต้องแก้รายจ่ายหรือหารายได้เสริมก่อน",
            "choice":  "หาอาชีพเสริมเพื่อสร้าง monthly_extra ก่อนโปะหนี้",
            "lock":    "Fail less. Harm less. Restore Choice."
        }

    monthly_interest = sum(float(d.get("balance", 0) or 0) * float(d.get("annual_rate", 0) or 0) / 1200 for d in debts)
    if monthly_extra <= monthly_interest:
        return {
            "system":  "FATE_DEBT_FREEDOM",
            "status":  "BUDGET_BELOW_INTEREST",
            "monthly_extra":    monthly_extra,
            "monthly_interest": round(monthly_interest, 2),
            "message": "เงินโปะต่อเดือนไม่พอแม้แต่ดอกเบี้ย — หนี้จะโตขึ้นทุกเดือน ต้องเจรจาลดดอกเบี้ย/ปรับโครงสร้าง หรือเพิ่มรายได้ก่อน",
            "refinance_advice": advise_refinance(debts, monthly_income),
            "side_income":      suggest_side_income(skills, monthly_interest - monthly_extra + 1000),
            "lock":    "Fail less. Harm less. Restore Choice."
        }

    strategy   = recommend_strategy(debts, monthly_extra)
    plan_a     = simulate_payoff(debts, monthly_extra, "avalanche")
    plan_s     = simulate_payoff(debts, monthly_extra, "snowball")
    refinance  = advise_refinance(debts, monthly_income)
    side_jobs  = suggest_side_income(skills, monthly_extra * 0.5)

    recommended = plan_a if strategy == "avalanche" else plan_s

    return {
        "system":            "FATE_DEBT_FREEDOM",
        "status":            "OK",
        "monthly_extra":     monthly_extra,
        "recommended_strategy": strategy,
        "recommended_plan":  recommended,
        "avalanche_plan":    plan_a,
        "snowball_plan":     plan_s,
        "refinance_advice":  refinance,
        "side_income":       side_jobs,
        "fate_lock":         "Fail less. Harm less. Restore Choice.",
        "note": (
            f"ด้วยเงินโปะ {monthly_extra:,.0f} บาท/เดือน "
            f"คาดว่าปลดหนี้ได้ใน {recommended['payoff_months']} เดือน "
            f"({recommended['payoff_years']} ปี)"
            if recommended["paid_off"] else
            f"ด้วยเงินโปะ {monthly_extra:,.0f} บาท/เดือน ยังปลดหนี้ไม่หมดใน 30 ปี "
            f"(เหลือ {recommended['remaining']:,.0f} บาท) — ต้องลดดอกเบี้ยหรือเพิ่มเงินโปะ"
        )
    }
