"""
core/followup.py — ข้อความสั้นที่ตอบต่อจากเรื่องหนัก (กลโกงไซเบอร์ · อารมณ์หนัก · ความโกรธ)

คำตอบรอบแรกของเรื่องเหล่านี้จบด้วยคำถาม ("ได้กดลิงก์ไปแล้วหรือยังคะ" "มีความคิดไม่อยากอยู่ปนมาด้วยไหมคะ")
แต่เดิมคำตอบกลับสั้นๆ ไม่ถูกผูกกับเรื่องเดิม:
  "โอนไปห้าพันแล้ว" "เงินหายไปแล้ว" ต่อจากเรื่องมิจฉาชีพ → Risk 0 แผนสามขั้นทั่วไป
  "ก็มีบ้าง" ต่อจากคำถามว่ามีความคิดไม่อยากอยู่ไหม → Risk 0 (ทั้งเจ็ดภาษา)
  "yes i already paid it" → คำตอบแรกซ้ำ "อย่าเพิ่งกดลิงก์"
ไฟล์นี้อ่านคำตอบสั้นของผู้ใช้เทียบกับเรื่องเดิม แล้วให้ขั้นถัดไปที่ตรงกับสิ่งที่เขาเพิ่งบอก
"""
import re

# ── ผู้ใช้บอกว่าทำไปแล้ว / ยัง (เรื่องมิจฉาชีพ) ─────────────────────────────
_NOT_YET = re.compile(r"^\W*(?:ยัง|ยังไม่|ไม่ได้(?!\s*เงิน)|เปล่า|ไม่ได้กด|ไม่ได้โอน|ไม่ได้ให้|ไม่ได้ลง)|"
                      r"(?i:^\W*(?:not yet|nah\b|no\b|nope|nothing|haven'?t|didn'?t|i didn'?t|i haven'?t))", re.I)
_DONE = re.compile(r"(?:ไป)?แล้ว|ให้\S{0,12}ไป|โอน|กรอก|กดไป|ลงไป|ติดตั้งไป|ให้ไป|เงินหาย|หายไป|โดนดูด|ถูกดูด|ถูกโอน|โดนหัก|"
                   r"(?i:\b(?:already|paid|sent|transferred|entered|typed|installed|clicked|tapped|gave|handed|gone|missing|drained|stolen|yes|yeah|yep)\b)")
# คนที่อ้างเป็นเจ้าหน้าที่มาถึงหน้าบ้านแล้ว — เรื่องความปลอดภัยตอนนี้ ไม่ใช่เรื่องเงิน
_AT_DOOR = re.compile(r"(?:มา|มาถึง|อยู่)(?:ที่)?(?:หน้า)?(?:บ้าน|ประตู)(?:แล้ว)?|(?i:\b(?:is|are|'s|'re) (?:here|outside|at (?:my|the) door)\b)")

# ── ผู้ใช้ตอบคำถามว่ามีความคิดไม่อยากอยู่ไหม ───────────────────────────────
# "มีบ้าง" "บางที" "sometimes" "少しある" "有一点" "조금 있어" "a veces sí" "có một chút" = ใช่ ต้องได้การดูแลระดับวิกฤต
_YES_SOME = re.compile(
    r"^\W*(?:มี|ก็มี|มีบ้าง|ก็มีบ้าง|บางที|บางครั้ง|ใช่|ค่ะ\s*มี|ครับ\s*มี|นิดหน่อย|นิดนึง|ก็คิด|คิดอยู่|คิดบ่อย|อาจจะ|ก็นิดนึง)|"
    # ตอบรับสั้นๆ ต่อคำถามว่ามีความคิดไม่อยากอยู่ไหม = มี (พลาดไปทางดูแล ดีกว่าพลาดไปทางมองข้าม)
    r"^\W*(?:ค่ะ|ค่า|คะ|ครับ|คับ|อือ|อื้อ|อืม|ฮื่อ|ช่าย|เออ)\W*$|"
    r"(?i:^\W*(?:i think so|mhm+|uh[- ]?huh|hmm+,? (?:sometimes|yes|yeah|maybe)|prob(?:ably)?|kinda|sort of)\b)|"
    r"มีความคิด(?:แบบนั้น|นั้น)|คิด(?:แบบนั้น|อย่างนั้น)(?:อยู่|บ่อย|บ้าง)|"
    r"(?i:^\W*(?:yes|yeah|yep|sometimes|a (?:bit|little)|kind of|kinda|i do|maybe|a lot|often)\b)|"
    r"^\W*(?:少し|すこし|ある|あります|はい|たまに|うん|時々)|^\W*(?:有|有一点|有时候|有時候|是|嗯|偶尔)|"
    r"^\W*(?:조금|있어|있어요|네|가끔|응|그래)|(?i:^\W*(?:s[ií]\b|a veces|un poco|tal vez|quiz[áa]s))|"
    r"(?i:^\W*(?:có|một chút|đôi khi|ừ|vâng|thỉnh thoảng))")
_JUST_TIRED = re.compile(
    r"แค่เหนื่อย|ไม่มี(?:หรอก|นะ|ค่ะ|ครับ)?\s*$|ไม่ได้คิด|(?i:\b(?:just (?:tired|exhausted|overwhelmed)|no\b|not really|nope)\b)|"
    r"疲れた(?:だけ)?|ない(?:よ|です)?\s*$|只是累|没有|그냥\s*피곤|없어|(?i:\bsolo cansad[oa]|\bno\b)|(?i:\bchỉ mệt|\bkhông có)")


def cyber_answer(text) -> str | None:
    """คำตอบสั้นต่อจากเรื่องมิจฉาชีพ → "door" / "done" / "not_yet" / None"""
    t = str(text or "").strip()
    if not t or len(t) > 60:
        return None
    if _AT_DOOR.search(t):
        return "door"
    if _NOT_YET.search(t):
        return "not_yet"
    if _DONE.search(t):
        return "done"
    return None


def heavy_answer(text) -> str | None:
    """คำตอบสั้นต่อคำถามเรื่องความคิดไม่อยากอยู่ → "yes" / "tired" / None"""
    t = str(text or "").strip()
    if not t or len(t) > 60:
        return None
    if _JUST_TIRED.search(t) and not re.search(r"^\W*(?:มีบ้าง|ก็มี|sometimes|少し|有一点|조금|a veces|có)", t, re.I):
        return "tired"
    if _YES_SOME.search(t):
        return "yes"
    return None


AOC = {"th": "1441 (ศูนย์ AOC ตำรวจไซเบอร์ 24 ชม.)", "en": "1441 (Thailand cyber police AOC, 24h)"}
CYBER_NEXT = {
    "done": {
        "th": ("ไม่เป็นไรนะคะ เกิดขึ้นได้กับทุกคน — ตอนนี้ยิ่งเร็วยิ่งมีโอกาสได้เงินคืน",
               ["โทรธนาคารเดี๋ยวนี้ (เบอร์หลังบัตรหรือในแอปจริง) ขอระงับบัญชีและอายัดรายการที่โอนออก — บอกเวลาและเลขบัญชีปลายทาง",
                "โทร " + AOC["th"] + " ขออายัดบัญชีปลายทาง แล้วแจ้งความออนไลน์ที่ thaipoliceonline.go.th",
                "เปลี่ยนรหัสแอปธนาคารและอีเมลจากเครื่องอื่น · ถ้าลงแอปจากลิงก์ เปิดโหมดเครื่องบินแล้วลบแอปนั้น · เก็บสลิป แชท เบอร์ และลิงก์ไว้เป็นหลักฐาน"],
               "ตอนนี้โทรหาธนาคารได้แล้วหรือยังคะ"),
        "en": ("It's okay — this happens to careful people too. Right now, speed gives you the best chance of getting money back.",
               ["Call your bank now (number on the back of your card or in the real app): freeze the account and dispute the transfer — give the time and the receiving account.",
                "In Thailand call " + AOC["en"] + " to freeze the receiving account, and report at thaipoliceonline.go.th — elsewhere, your local police / fraud line.",
                "Change banking and email passwords from another device · if you installed an app from a link, airplane mode and delete it · keep receipts, chats, numbers and links as evidence."],
               "Have you been able to reach your bank yet?"),
    },
    "not_yet": {
        "th": ("ดีมากเลยค่ะ ที่หยุดไว้ก่อน — ตอนนี้ยังไม่เสียอะไร",
               ["ลบข้อความหรือบล็อกเบอร์นั้นได้เลย ไม่ต้องตอบกลับ",
                "ถ้ายังไม่แน่ใจว่าเรื่องจริงไหม เช็กเองจากแอปหรือเบอร์ทางการที่หาเอง",
                "ถ้าอยากช่วยคนอื่น แจ้งเบอร์หรือลิงก์นั้นที่ " + AOC["th"]],
               "มีอะไรที่ยังกังวลอยู่อีกไหมคะ"),
        "en": ("Good call stopping there — you haven't lost anything.",
               ["Delete the message or block the number — no need to reply.",
                "If you're unsure whether it's real, check through the official app or a number you look up yourself.",
                "To help others, report the number or link (Thailand: " + AOC["en"] + ")."],
               "Is there anything else you're still worried about?"),
    },
    "door": {
        "th": ("ไม่ต้องเปิดประตูนะคะ — เจ้าหน้าที่จริงไม่มารับเงินหรือทองที่บ้าน",
               ["ล็อกประตูไว้ ไม่ต้องคุยหรือส่งอะไรออกไป",
                "โทร 191 (ตำรวจ) บอกว่ามีคนอ้างเป็นเจ้าหน้าที่มารับเงินที่บ้าน และบอกที่อยู่",
                "ถ้ามีคนอยู่ด้วย ให้เขาอยู่ใกล้ๆ · จดหรือถ่ายรูปคนและรถจากในบ้านได้ถ้าปลอดภัย"],
               "ตอนนี้มีใครอยู่กับคุณไหมคะ"),
        "en": ("Don't open the door — real officers never come to collect cash or gold at your home.",
               ["Keep the door locked; don't talk to them or hand anything out.",
                "Call the police (191 in Thailand, 911 / 112 elsewhere): someone posing as an officer is at your door to collect money — give your address.",
                "If someone is with you, keep them close · note or photograph the person and vehicle from inside if it's safe."],
               "Is anyone with you right now?"),
    },
}

HEAVY_NEXT = {
    "yes": {
        "th": ("ขอบคุณที่บอกตรงๆ นะคะ — ต้องใช้ความกล้ามาก และฉันดีใจที่คุณยังคุยอยู่ตรงนี้",
               ["ตอนนี้โทร 1323 (สายด่วนสุขภาพจิต ฟรี 24 ชม.) ได้เลย — บอกเขาแบบเดียวกับที่บอกฉันก็พอ",
                "ถ้าคิดว่าจะทำร้ายตัวเองตอนนี้ หรือมีของที่ใช้ทำร้ายตัวเองอยู่ใกล้ เอาไปไว้ไกลตัว แล้วโทร 1669",
                "ส่งข้อความหาคนที่ไว้ใจสักคนว่า \"ตอนนี้ไม่ไหว อยู่เป็นเพื่อนหน่อย\" ไม่ต้องอธิบายมาก"],
               "ตอนนี้คุณปลอดภัยไหมคะ"),
        "en": ("Thank you for telling me honestly — that takes real courage, and I'm glad you're still here talking.",
               ["Please call a crisis line now — 1323 in Thailand (24h, free), 988 in the US, or findahelpline.com. You can say exactly what you told me.",
                "If you might act on it now, or something you could use is nearby, put it out of reach and call emergency services (1669 in Thailand).",
                "Text one person you trust: \"I'm not okay, can you stay with me?\" — no explanation needed."],
               "Are you safe right now?"),
        "ja": ("正直に話してくれてありがとう。とても勇気がいることです。ここで話してくれていて、うれしいです。",
               ["今すぐ相談してください：タイでは 1323（24時間・無料）、日本では いのちの電話 0570-783-556。私に話したのと同じことを伝えれば大丈夫です。",
                "今にも行動してしまいそうなら、手の届く所にある危ない物を遠ざけて、救急（タイ 1669・日本 119）へ。",
                "信頼できる人に「今つらい、そばにいて」と一言送ってください。説明はいりません。"],
               "今、安全な場所にいますか？"),
        "zh": ("谢谢你愿意说实话，这需要很大的勇气。你还在这里和我说话，我很高兴。",
               ["现在就联系心理援助：在泰国拨打 1323（24小时，免费）；在中国拨打 12356。把你告诉我的话告诉他们就可以。",
                "如果你觉得现在可能会伤害自己，把身边危险的东西拿远，拨打急救（泰国 1669 · 中国 120）。",
                "给一个信得过的人发一句“我现在不太好，陪陪我”，不用多解释。"],
               "你现在安全吗？"),
        "ko": ("솔직하게 말해줘서 고마워요. 정말 용기가 필요한 일이에요. 여기서 이야기해 줘서 다행이에요.",
               ["지금 바로 연락해 주세요: 태국에서는 1323(24시간·무료), 한국에서는 자살예방 상담전화 109. 저에게 말한 그대로 말하면 돼요.",
                "지금 행동할 것 같거나 위험한 물건이 가까이 있다면 멀리 치우고 119(태국 1669)에 전화하세요.",
                "믿을 만한 사람에게 \"지금 너무 힘들어, 옆에 있어 줘\"라고 한마디만 보내세요."],
               "지금 안전한 곳에 있나요?"),
        "es": ("Gracias por decírmelo con sinceridad — eso requiere mucho valor, y me alegra que sigas aquí hablando conmigo.",
               ["Llama ahora a una línea de crisis: en Tailandia 1323 (24 h, gratis), en España 024, en México 800 911 2000. Puedes decir exactamente lo que me dijiste.",
                "Si sientes que podrías hacerlo ahora o tienes algo peligroso cerca, aléjalo y llama a emergencias (1669 en Tailandia · 112 / 911).",
                "Escríbele a una persona de confianza: “no estoy bien, ¿puedes acompañarme?” — no hace falta explicar más."],
               "¿Estás a salvo ahora mismo?"),
        "vi": ("Cảm ơn bạn đã nói thật — điều đó cần rất nhiều can đảm, và mình mừng vì bạn vẫn đang trò chuyện ở đây.",
               ["Hãy gọi ngay đường dây hỗ trợ: ở Thái Lan 1323 (24 giờ, miễn phí), ngoài Thái Lan tìm tại findahelpline.com. Bạn chỉ cần kể như đã kể với mình.",
                "Nếu thấy mình có thể làm điều đó ngay bây giờ, hãy cất những thứ nguy hiểm ra xa và gọi cấp cứu (Thái Lan 1669 · Việt Nam 115).",
                "Nhắn cho một người bạn tin tưởng: “mình đang không ổn, ở cạnh mình một chút nhé” — không cần giải thích."],
               "Bây giờ bạn có an toàn không?"),
    },
    "tired": {
        "th": ("ขอบคุณที่ตอบนะคะ — เหนื่อยจนท่วมท้นก็หนักพออยู่แล้ว ไม่ต้องรอให้หนักกว่านี้ถึงจะพักได้",
               ["คืนนี้ทำแค่สิ่งเดียวที่ช่วยให้ร่างกายได้พัก: กินอะไรอุ่นๆ อาบน้ำ หรือนอนเร็วขึ้นหน่อย",
                "เลือกเรื่องที่หนักที่สุดมาหนึ่งเรื่อง แล้วดูว่ามีอะไรที่วางลงหรือขอให้คนอื่นช่วยได้",
                "ถ้าวันไหนความเหนื่อยเปลี่ยนเป็นความคิดอยากหายไป โทร 1323 ได้ตลอด 24 ชม."],
               "ตอนนี้เรื่องไหนดึงแรงคุณไปมากที่สุดคะ"),
        "en": ("Thanks for answering — being worn out and overwhelmed is heavy enough on its own. You don't have to wait for it to get worse to rest.",
               ["Tonight, do just one thing for your body: something warm to eat, a shower, or an earlier night.",
                "Pick the single heaviest thing and see what you could put down or ask someone to help with.",
                "If the tiredness ever turns into wanting to disappear, a crisis line is there any time (1323 in Thailand, 988 in the US)."],
               "What's taking the most out of you right now?"),
    },
}
for _lg, (_o, _s, _q) in {
    "ja": ("答えてくれてありがとう。疲れ切っているだけでも、十分につらいことです。", ["今夜は体のために一つだけ：温かいものを食べる、お風呂、早めに寝る。", "一番重いことを一つ選んで、手放せること・頼めることを探してみましょう。", "疲れが「消えたい」気持ちに変わったら、いつでも相談を（タイ 1323・日本 0570-783-556）。"], "今、何が一番エネルギーを奪っていますか？"),
    "zh": ("谢谢你回答。累到撑不住，本身就已经很辛苦了。", ["今晚只为身体做一件事：吃点热的、洗个澡，或早点睡。", "挑出最重的那一件事，看看有什么可以放下或请别人帮忙。", "如果疲惫变成了想消失的念头，随时可以求助（泰国 1323 · 中国 12356）。"], "现在最消耗你的是什么？"),
    "ko": ("대답해 줘서 고마워요. 너무 지친 것만으로도 충분히 힘든 일이에요.", ["오늘 밤은 몸을 위해 한 가지만: 따뜻한 음식, 샤워, 조금 일찍 자기.", "가장 무거운 일 하나를 골라, 내려놓거나 도움을 청할 수 있는 걸 찾아봐요.", "지침이 사라지고 싶은 마음으로 바뀌면 언제든 전화하세요(태국 1323 · 한국 109)."], "지금 무엇이 가장 힘을 빼앗고 있나요?"),
    "es": ("Gracias por responder — estar agotado y saturado ya es bastante pesado.", ["Esta noche haz solo una cosa por tu cuerpo: algo caliente de comer, una ducha o acostarte antes.", "Elige lo más pesado y mira qué podrías soltar o pedir ayuda.", "Si el cansancio se convierte en ganas de desaparecer, llama cuando quieras (Tailandia 1323 · España 024)."], "¿Qué es lo que más energía te quita ahora?"),
    "vi": ("Cảm ơn bạn đã trả lời — mệt mỏi và quá tải thôi cũng đã đủ nặng nề rồi.", ["Tối nay chỉ làm một việc cho cơ thể: ăn gì đó ấm, tắm, hoặc đi ngủ sớm hơn.", "Chọn chuyện nặng nhất và xem có gì có thể buông bớt hoặc nhờ người khác giúp.", "Nếu sự mệt mỏi biến thành ý muốn biến mất, hãy gọi bất cứ lúc nào (Thái Lan 1323)."], "Điều gì đang lấy đi nhiều năng lượng nhất của bạn lúc này?"),
}.items():
    HEAVY_NEXT["tired"][_lg] = (_o, _s, _q)

# ความโกรธ: คำตอบสั้นต่อคำถาม "โกรธใคร มีใครอยู่ใกล้ไหม" ("แฟน" "หัวหน้า" "อยู่คนเดียว")
ANGER_NEXT = {
    "any": {
        "th": ("ขอบคุณที่บอกนะคะ — ตอนนี้ยังไม่ต้องคุย ตอบโต้ หรือตัดสินอะไรกับเรื่องนั้น ให้ร่างกายเย็นลงก่อน",
               ["ถ้าคนนั้นอยู่ใกล้ แยกกันอยู่คนละห้องหรือออกไปข้างนอกก่อนสักพัก · วางโทรศัพท์ไว้ อย่าเพิ่งพิมพ์หาเขา",
                "ระบายใส่สิ่งที่ไม่มีใครเจ็บ: เขียนทุกอย่างที่อยากพูดลงกระดาษ แล้วยังไม่ต้องส่ง",
                "ถ้ารู้สึกว่าจะคุมตัวเองไม่อยู่ หรือกลัวว่าจะมีใครเจ็บ โทร 1323 คุยได้ตลอด 24 ชม. · ถ้าอันตรายตอนนี้ 191"],
               "ตอนนี้ร่างกายเย็นลงบ้างหรือยังคะ"),
        "en": ("Thanks for telling me — you don't have to talk to them, reply, or decide anything about it yet. Let your body cool down first.",
               ["If they're nearby, get into a different room or step outside for a while · put the phone down before messaging them.",
                "Let it out somewhere no one gets hurt: write everything you want to say on paper — and don't send it yet.",
                "If you feel you might lose control or someone could get hurt, call a crisis line (1323 in Thailand, 988 in the US) · police 191 / 911 if there's danger now."],
               "Has your body started to cool down at all?"),
    },
}

FOOTER = {"th": "· ตอบจากสมการของระบบ — ไม่ได้ใช้ AI", "en": "· Answered from the system's equations — no AI used"}


_SCRIPT = (("th", r"[\u0E00-\u0E7F]"), ("ko", r"[\uac00-\ud7af]"), ("ja", r"[\u3040-\u30ff]"), ("zh", r"[\u4e00-\u9fff]"))
_EN_SURE = re.compile(r"(?i)\b(?:i|i'?m|it|is|the|yes|no|not|just|already|my|money|yet|sometimes|tired)\b")


def _lang(prior, now):
    """ภาษาของคำตอบ: ใช้ภาษาของเรื่องเดิมเป็นหลัก — คำตอบสั้นเดาภาษาเองไม่ได้
    ("solo cansada" เคยถูกเดาเป็นอังกฤษ · "có một chút" ไม่มีตัวอักษรเวียดนามพอ เคยถูกเดาเป็นสเปน)
    เปลี่ยนตามคำตอบเฉพาะเมื่อใช้ตัวอักษรคนละแบบชัดเจน หรือเป็นคำอังกฤษแน่ๆ ("yes" ต่อจากเรื่องภาษาไทย)"""
    from core.mood_intl import mood_lang
    from core.lang_signals import detect_lang
    lp = mood_lang(prior) or detect_lang(prior)
    now = str(now or "")
    for code, rx in _SCRIPT:
        if re.search(rx, now):
            ln = "ja" if code == "zh" and re.search(_SCRIPT[2][1], now) else code
            return lp if (ln == "zh" and lp == "ja") else ln
    if re.search(r"[A-Za-z]", now) and lp in ("th", "ja", "zh", "ko") and _EN_SURE.search(now):
        return "en"
    return lp


def compose_next(prior_text: str, text: str, voice_mode: str = "lyla", footer: bool = True) -> str | None:
    """คำตอบต่อจากเรื่องหนักในข้อความก่อนหน้า — None = ใช้ทางเดิม"""
    from core.kernel_voice import assess, status_line
    from core.lang_signals import FOOTER as FOOT_INTL
    pa = assess(prior_text)
    if pa.get("crisis"):
        return None                     # เรื่องอยากตายมีตัวตอบต่อของตัวเองอยู่แล้ว (compose_followup)
    lg = _lang(prior_text, text)
    if pa.get("cyber") or pa.get("scam"):
        kind, table = cyber_answer(text), CYBER_NEXT
        lg = lg if lg in ("th", "en") else "en"
    elif _is_anger(prior_text, pa):
        kind, table = ("any" if 0 < len(str(text or "").strip()) <= 40 else None), ANGER_NEXT
        lg = lg if lg in ("th", "en") else "en"
    elif (pa.get("mood_intl") or (None,))[0] == "heavy" or "soft_check" in (pa.get("topics") or []):
        kind, table = heavy_answer(text), HEAVY_NEXT
    else:
        return None
    if not kind or lg not in table[kind]:
        return None
    opener, steps, ask = table[kind][lg]
    vega = str(voice_mode or "").lower() == "vega"
    if vega and lg == "th":
        opener = opener.replace("นะคะ", "นะครับ").replace("ค่ะ", "ครับ")
        ask = ask.replace("คะ", "ครับ")
        steps = [s.replace("ฉัน", "ผม") for s in steps]
        opener = opener.replace("ฉัน", "ผม")
    sign = "— VEGA ◆" if vega else "— LYLA ◈"
    risk = RISK[kind]
    st = status_line({"risk": risk, "risk_shown": risk, "text_risk": risk}, lg)
    body = "\n".join(f"{i + 1}) {s}" for i, s in enumerate(steps))
    tag = ("\n" + (FOOTER.get(lg) or FOOT_INTL.get(lg, FOOTER["en"]))) if footer else ""
    head = f"{opener}\n\n{st}\n\n" if st else f"{opener}\n\n"
    return f"{head}{body}\n\n{ask}\n\n{sign}{tag}"


RISK = {"done": 75, "door": 85, "not_yet": 20, "yes": 90, "tired": 45, "any": 45}
# บอก AI ว่าข้อความสั้นนี้ตอบต่อจากเรื่องอะไร และต้องทำอะไรต่อ (ไม่ให้ทักทายใหม่หรือเปลี่ยนเรื่อง)
CTX = {
    "done": "[ผู้ใช้เพิ่งบอกว่าโอนเงิน/กรอกข้อมูล/ติดตั้งแอปให้มิจฉาชีพไปแล้ว: ไม่ตำหนิ บอกว่ายิ่งเร็วยิ่งมีโอกาสได้เงินคืน "
            "ให้โทรธนาคารขอระงับและอายัดรายการทันที · โทร 1441 (ศูนย์ AOC ตำรวจไซเบอร์ 24 ชม.) · แจ้งความที่ thaipoliceonline.go.th · "
            "เปลี่ยนรหัสจากเครื่องอื่น แล้วถามว่าติดต่อธนาคารได้หรือยัง]",
    "door": "[คนที่อ้างเป็นเจ้าหน้าที่มาถึงบ้านผู้ใช้แล้ว: บอกว่าไม่ต้องเปิดประตู เจ้าหน้าที่จริงไม่มารับเงินที่บ้าน ให้โทร 191 ทันที ถามว่ามีใครอยู่ด้วยไหม]",
    "not_yet": "[ผู้ใช้ยังไม่ได้โอน/กด/ให้ข้อมูลมิจฉาชีพ: ชมที่หยุดไว้ บอกให้บล็อกหรือลบข้อความ และเช็กจากช่องทางทางการเอง]",
    "yes": "[ผู้ใช้ตอบว่ามีความคิดไม่อยากมีชีวิตอยู่ปนอยู่ด้วย: ขอบคุณที่บอกตรงๆ ไม่ตกใจ ไม่เทศน์ ให้โทร 1323 (สายด่วนสุขภาพจิต 24 ชม.) ตอนนี้ "
           "ถ้าอันตรายตอนนี้ 1669 ชวนให้เอาของที่ใช้ทำร้ายตัวเองไปไว้ไกล ให้ส่งข้อความหาคนที่ไว้ใจ แล้วถามว่าตอนนี้ปลอดภัยไหม]",
    "any": "[ผู้ใช้กำลังโกรธมาก และข้อความนี้ตอบต่อจากเรื่องนั้น: ไม่ตัดสิน ไม่เข้าข้างหรือด่าอีกฝ่าย ชวนแยกตัวจากคนนั้นและพักให้ร่างกายเย็นลงก่อนคุยหรือตัดสินใจ "
           "ถ้ากลัวคุมตัวเองไม่อยู่ 1323 · อันตรายตอนนี้ 191 แล้วถามว่าตอนนี้เย็นลงบ้างหรือยัง]",
    "tired": "[ผู้ใช้ตอบว่าแค่เหนื่อย ไม่ได้มีความคิดไม่อยากอยู่: เชื่อเขา ไม่ถามซ้ำ ช่วยเรื่องพักและเรื่องที่หนักที่สุด และบอกว่า 1323 มีให้เสมอ]",
}


def _is_anger(prior_text, pa):
    from core.second_layer import ANGER_MOOD, ANGER_NOT
    if (pa.get("mood_intl") or (None,))[0] == "anger":
        return True
    return bool(ANGER_MOOD.search(prior_text or "") and not ANGER_NOT.search(prior_text or ""))


def classify_next(prior_text: str, text: str):
    """→ (ครอบครัวเรื่อง "scam"/"heavy", คำตอบ, ความเสี่ยง) เมื่อข้อความสั้นนี้ตอบต่อจากเรื่องหนัก หรือ None"""
    from core.kernel_voice import assess
    pa = assess(prior_text)
    if pa.get("crisis"):
        return None
    if pa.get("cyber") or pa.get("scam"):
        k = cyber_answer(text)
        return ("scam", k, RISK[k]) if k else None
    if _is_anger(prior_text, pa):
        t = str(text or "").strip()
        return ("anger", "any", RISK["any"]) if 0 < len(t) <= 40 else None
    if (pa.get("mood_intl") or (None,))[0] == "heavy" or "soft_check" in (pa.get("topics") or []):
        k = heavy_answer(text)
        return ("heavy", k, RISK[k]) if k else None
    return None
