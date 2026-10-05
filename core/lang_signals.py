"""
core/lang_signals.py — ภาษาอื่นนอกจากไทย (ชุดแรก 5 ภาษา: en zh ja ko es)

สมการของระบบ (W, Risk, Choice(t)) ไม่ขึ้นกับภาษาอยู่แล้ว — ไฟล์นี้เติมสองอย่างที่ขึ้นกับภาษา:
1) คำที่ใช้จับสัญญาณทำร้ายตัวเอง  2) ข้อความตอบตอนไม่มี AI
เดิม "quiero morir", "我想死", "死にたい", "죽고 싶어" ไม่ถูกจับเลย (Risk 0, ไม่มีสายด่วน)
และคำตอบตอนไม่มี AI เป็นภาษาไทยเสมอ
"""
import re

LANGS = ("th", "en", "zh", "ja", "ko", "es")

_THAI = re.compile(r"[฀-๿]")
_HANGUL = re.compile(r"[가-힯ᄀ-ᇿ㄰-㆏]")
_KANA = re.compile(r"[぀-ヿ]")
_HAN = re.compile(r"[一-鿿]")
_LETTER = re.compile(r"[^\W\d_]")
_ES_CHARS = re.compile(r"[ñ¿¡]")
_ES_WORDS = {"que", "de", "la", "el", "y", "los", "las", "por", "para", "estoy", "quiero", "mi", "una",
             "con", "pero", "muy", "tengo", "porque", "hola", "gracias", "vida", "ayuda", "soy", "está",
             "esta", "qué", "cómo", "como", "nada", "nadie", "más", "también", "ya", "puedo", "mí"}

# คำที่แทบไม่เจอในภาษาอังกฤษ — เจอคำเดียวก็พอ ("quiero morir" มีคำทั่วไปแค่คำเดียว)
_ES_STRONG = {"quiero", "estoy", "tengo", "hola", "gracias", "ayuda", "morir", "vivir", "necesito",
              "puedo", "siento", "nadie", "nada", "muero", "triste", "dinero", "trabajo"}


def detect_lang(text) -> str:
    """เดาภาษาจากตัวอักษร: ไทย → th · ฮันกึล → ko · คานะ → ja · ฮั่น → zh · ละติน → es/en
    ไม่มีตัวอักษรเลย ("555", "?") → th (ภาษาหลักของแอป) · อักษรอื่น → en (คนอ่านได้มากกว่าไทย)"""
    t = str(text or "")
    if _THAI.search(t) or not _LETTER.search(t):
        return "th"
    if _HANGUL.search(t):
        return "ko"
    if _KANA.search(t):
        return "ja"
    if _HAN.search(t):
        return "zh"
    low = t.lower()
    words = set(re.findall(r"[a-záéíóúüñ]+", low))
    if _ES_CHARS.search(low) or len(words & _ES_WORDS) >= 2 or words & _ES_STRONG:
        return "es"
    return "en"


# ── สัญญาณทำร้ายตัวเอง ────────────────────────────────────────────────
# ปลอดภัยไว้ก่อนเหมือนภาษาไทย แต่ตัดสำนวนที่ไม่ได้แปลว่าอยากตาย:
# 想死你了 = คิดถึงมาก · me muero de risa = ขำจะตาย · dying to = อยากมาก
SELF_HARM_INTL = (
    re.compile(r"\b(?:i\s+)?(?:want|wanna|going)\s+to\s+die\b|\bkill(?:ing)?\s+myself\b|\bsuicid|"
               r"\bend(?:ing)?\s+(?:my\s+life|it\s+all)\b|\bdon'?t\s+want\s+to\s+(?:live|be\s+alive|exist)\b|"
               r"\bbetter\s+off\s+dead\b|\bno\s+reason\s+to\s+live\b|\b(?:hurt|harm|cut)(?:ting)?\s+myself\b|"
               r"\bself[- ]harm", re.I),
    re.compile(r"想死(?!你|您|他|她|它|我了|了你)|不想活|活不下去|自杀|自殺|轻生|輕生|结束(?:自己的)?生命|結束(?:自己的)?生命|"
               r"死了算了|不如死了"),
    re.compile(r"死にたい|消えたい|自殺|生きていたくない|生きたくない|死のう|命を絶"),
    re.compile(r"죽고\s*싶|자살|살고\s*싶지\s*않|사라지고\s*싶|죽어\s*버리고\s*싶|극단적\s*선택|목숨을\s*끊"),
    re.compile(r"\b(?:me\s+)?quiero\s+morir|\bsuicid|\bquitarme\s+la\s+vida|\bno\s+quiero\s+vivir|"
               r"\bacabar\s+con\s+mi\s+vida|\bmatarme\b|\bhacerme\s+daño", re.I),
)


def self_harm_intl(text) -> bool:
    t = str(text or "")
    return any(p.search(t) for p in SELF_HARM_INTL)


# ── ข้อความตอบตอนไม่มี AI ─────────────────────────────────────────────
HELP = {
    "en": ("If you are in danger right now, call your local emergency number (911 in the US and Canada, "
           "999 in the UK, 112 in most of Europe). In the US you can call or text 988. "
           "Find a free, confidential helpline in your country at findahelpline.com"),
    "zh": "如果你现在有危险，请立即拨打当地的紧急电话（中国大陆 120 或 110）。在 findahelpline.com 可以找到你所在国家或地区的免费心理援助热线",
    "ja": "今危険な状態なら、すぐに119に電話してください。findahelpline.com で、お住まいの国の無料の相談窓口を探せます",
    "ko": "지금 위험하다면 바로 119에 전화하세요. 자살예방 상담전화 109는 24시간 열려 있어요. 다른 나라에 있다면 findahelpline.com에서 상담전화를 찾을 수 있어요",
    "es": ("Si estás en peligro ahora, llama al número de emergencias de tu país (112 en España y gran parte de Europa, "
           "911 en México y EE. UU.). En findahelpline.com puedes encontrar una línea de ayuda gratuita y confidencial en tu país"),
}

CRISIS = {
    "en": ("I hear you, and I'm glad you wrote to me.\n\nRight now, just two things:\n"
           "1) Reach out for help — {help}\n"
           "2) Be near someone, or tell one person \"I'm not okay right now\". You don't have to explain why.\n\n"
           "What you feel right now is very heavy, but it is not all of you — you still have choices. "
           "You can keep writing to me anytime. I'm here."),
    "zh": ("我听到你说的了，谢谢你愿意说出来。\n\n现在只需要做两件事：\n"
           "1) 联系可以帮助你的人 — {help}\n"
           "2) 待在别人身边，或者告诉一个人“我现在不太好”，不需要解释原因。\n\n"
           "你现在的感受很沉重，但它不是你的全部 — 你仍然有选择。随时可以继续跟我说，我在这里。"),
    "ja": ("話してくれてありがとう。ちゃんと受け止めています。\n\n今は2つだけお願いします：\n"
           "1) 助けてくれる人に連絡してください — {help}\n"
           "2) 誰かのそばにいるか、一人に「今つらい」と伝えてください。理由は説明しなくて大丈夫です。\n\n"
           "今の気持ちはとても重いけれど、それがあなたのすべてではありません。まだ選べる道があります。"
           "いつでも続けて書いてください。ここにいます。"),
    "ko": ("말해줘서 고마워요. 당신의 이야기를 듣고 있어요.\n\n지금은 두 가지만 부탁할게요:\n"
           "1) 도움을 줄 수 있는 곳에 연락해 주세요 — {help}\n"
           "2) 다른 사람 곁에 있거나, 한 사람에게 \"지금 많이 힘들어\"라고 말해 주세요. 이유는 설명하지 않아도 괜찮아요.\n\n"
           "지금 느끼는 감정은 아주 무겁지만, 그게 당신의 전부는 아니에요. 아직 선택할 수 있는 길이 있어요. "
           "언제든 계속 이야기해 주세요. 여기 있을게요."),
    "es": ("Te escucho, y me alegra que me hayas escrito.\n\nAhora mismo, solo dos cosas:\n"
           "1) Busca ayuda — {help}\n"
           "2) Quédate cerca de alguien, o dile a una persona \"ahora no estoy bien\". No necesitas explicar por qué.\n\n"
           "Lo que sientes ahora pesa mucho, pero no es todo lo que eres — todavía tienes opciones. "
           "Puedes seguir escribiéndome cuando quieras. Estoy aquí."),
}

# ทางทั่วไป (แปลจาก kernel_voice.GENERAL) — ตัวเลขสถานะ W · Risk · Choice(t) ใช้ร่วมทุกภาษา
GENERAL = {
    "en": ("Let's lay this out step by step.",
           ["Write what happened in one sentence — what is the real problem?",
            "Split it in two: what you can control · what you can't — put your energy only into the first.",
            "Pick the smallest step you can take within 24 hours."],
           "If this were resolved, what would that day look like — and how would you know?"),
    "zh": ("我们先一步一步把这件事理清楚。",
           ["用一句话写下发生了什么 — 真正的问题是什么？",
            "分成两边：你能控制的 · 你不能控制的 — 只把力气放在第一边。",
            "选一个 24 小时内能做到的最小一步。"],
           "如果这件事解决了，那一天会是什么样子 — 你怎么知道它解决了？"),
    "ja": ("まず、順番に整理してみましょう。",
           ["起きたことを一文で書いてみてください — 本当の問題は何でしょう？",
            "二つに分けます：自分で変えられること・変えられないこと — 力は前者だけに使いましょう。",
            "24時間以内にできる一番小さな一歩を選んでください。"],
           "これが解決したら、その日はどんな一日でしょう — どうやってそれが分かりますか？"),
    "ko": ("먼저 하나씩 차근차근 정리해 볼게요.",
           ["일어난 일을 한 문장으로 적어 보세요 — 진짜 문제는 무엇인가요?",
            "둘로 나눠 보세요: 내가 바꿀 수 있는 것 · 바꿀 수 없는 것 — 힘은 앞쪽에만 쓰세요.",
            "24시간 안에 할 수 있는 가장 작은 한 걸음을 골라 보세요."],
           "이 일이 해결된다면 그날은 어떤 모습일까요 — 그걸 어떻게 알 수 있을까요?"),
    "es": ("Vamos a ordenarlo paso a paso.",
           ["Escribe lo que pasó en una sola frase — ¿cuál es el problema real?",
            "Divídelo en dos: lo que puedes controlar · lo que no — pon tu energía solo en lo primero.",
            "Elige el paso más pequeño que puedas dar en las próximas 24 horas."],
           "Si esto se resolviera, ¿cómo sería ese día — y cómo lo sabrías?"),
}

ASK_LABEL = {"en": "One question to ask yourself now:", "zh": "现在可以问自己一个问题：",
             "ja": "今、自分に一つだけ問いかけてみてください：", "ko": "지금 스스로에게 물어볼 질문 하나:",
             "es": "Una pregunta para hacerte ahora:"}
FOOTER = {"en": "· Answered from the system's equations — no AI used", "zh": "· 由系统公式回答 — 未使用 AI",
          "ja": "· システムの数式による回答 — AI は使っていません", "ko": "· 시스템 공식으로 답했어요 — AI를 사용하지 않았어요",
          "es": "· Respondido con las ecuaciones del sistema — sin usar IA"}


def compose_intl(lang: str, crisis: bool, status: str, sign: str, footer: bool = True) -> str:
    """คำตอบตอนไม่มี AI สำหรับภาษาที่ไม่ใช่ไทย"""
    lang = lang if lang in CRISIS else "en"
    tag = "\n" + FOOTER[lang] if footer else ""
    if crisis:
        return CRISIS[lang].format(help=HELP[lang]) + f"\n\n{sign}" + tag
    opener, paths, ask = GENERAL[lang]
    body = "\n".join(f"{i + 1}) {p}" for i, p in enumerate(paths))
    return f"{opener}\n\n{status}\n\n{body}\n\n{ASK_LABEL[lang]} {ask}\n\n{sign}" + tag
