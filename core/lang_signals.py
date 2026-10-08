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
              "puedo", "siento", "nadie", "nada", "muero", "triste", "dinero", "trabajo",
              "hay", "terremoto", "incendio", "esposo", "esposa", "amigo", "amiga", "socorro", "pegó", "suicidarse",
              "pidieron", "transferir", "casa", "mamá", "papá"}


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
    # สระมีเครื่องหมาย (mamá, desmayó) ก็บอกว่าเป็นสเปน — "mi mamá se desmayó" เคยถูกเดาเป็นอังกฤษ
    if _ES_CHARS.search(low) or re.search(r"[áéíóú]", low) or len(words & _ES_WORDS) >= 2 or words & _ES_STRONG:
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


# ══════════════════════════════════════════════════════════════════
# เรื่องด่วนภาษาอื่น (zh ja ko es) — ทดสอบรอบ 18: เดิมจับได้แค่ "อยากตาย"
# "แม่เป็นลม" "ถูกสามีตี" "แผ่นดินไหว" "ตำรวจให้โอนเงิน" ได้คำตอบ "ลองเรียงเรื่องทีละขั้น" ที่ Risk 45
# และ "เพื่อนบอกว่าอยากตาย" ถูกตอบเหมือนผู้ใช้อยากตายเอง
# ══════════════════════════════════════════════════════════════════
# (ชนิด, หัวข้อในระบบไทย, รูปประโยคต่อภาษา)
URGENT_INTL = (
    ("someone", "someone", {
        "zh": r"(?:朋友|同学|妈妈|爸爸|母亲|父亲|老公|老婆|丈夫|妻子|男朋友|女朋友|孩子|儿子|女儿|哥哥|姐姐|弟弟|妹妹|他|她)[^。！？\n]{0,8}?(?:说|說|发消息|留言|告诉我)?[^。！？\n]{0,6}?(?:想死|想自杀|想自殺|不想活|要自杀|要自殺|轻生)",
        "ja": r"(?:友達|友人|母|父|夫|妻|彼氏|彼女|子ども|子供|息子|娘|兄|姉|弟|妹|彼|彼女)[^。！？\n]{0,8}?(?:が|は)[^。！？\n]{0,10}?(?:死にたい|自殺|消えたい)",
        "ko": r"(?:친구|엄마|아빠|남편|아내|남자친구|여자친구|아이|아들|딸|형|오빠|언니|누나|동생|그|그녀)[가-힯\s]{0,8}?(?:가|이|는|은)?\s*[가-힯\s]{0,6}?(?:죽고\s*싶대|죽고\s*싶다고|자살하고\s*싶대|자살하겠다)",
        "es": r"\bmi\s+(?:amig[oa]|mamá|madre|papá|padre|herman[oa]|hij[oa]|novi[oa]|espos[oa]|pareja)\s+(?:dice\s+que\s+)?(?:quiere\s+(?:morir|suicidarse|matarse)|se\s+quiere\s+(?:morir|matar)|habla\s+de\s+suicid)",
    }),
    ("medical", "health_emergency", {
        "zh": r"晕倒|昏倒|昏迷|没有呼吸|沒有呼吸|不能呼吸|喘不过气|胸口(?:剧痛|很痛|疼)|心脏病发|中风|抽搐|大出血|吃了(?:很多|一整瓶|整瓶)?(?:药|安眠药)|喝了农药|溺水",
        "ja": r"倒れ(?:た|ている)|意識がない|息をしていない|呼吸(?:が|できない)|胸が(?:痛|苦し)|心臓発作|脳卒中|けいれん|大量出血|薬を(?:たくさん|大量に)飲|溺れ",
        "ko": r"쓰러졌|의식이\s*없|숨을\s*안\s*쉬|숨을\s*못\s*쉬|숨이\s*안\s*쉬어|가슴이\s*(?:너무\s*)?아파|심장마비|뇌졸중|경련|피가\s*멈추지\s*않|약을\s*(?:많이|한\s*통)|물에\s*빠졌",
        "es": r"se\s+desmay[óo]|inconsciente|no\s+respira|no\s+puedo\s+respirar|dolor\s+(?:fuerte\s+)?(?:en\s+el|de)\s+pecho|infarto|derrame\s+cerebral|convulsi|sangra\s+mucho|se\s+tom[óo]\s+(?:muchas|todas\s+las)\s+pastillas|se\s+est[áa]\s+ahogando",
    }),
    ("violence", "violence", {
        "zh": r"(?:被|挨)[^。！？\n]{0,4}?(?:打|殴打|家暴|强奸|性侵)|(?:老公|丈夫|老婆|男朋友|爸爸|妈妈)[^。！？\n]{0,3}?打我|家暴",
        "ja": r"(?:に|から)(?:殴られ|叩かれ|蹴られ|暴力を振るわれ|襲われ)|DV|性的暴行|レイプ",
        "ko": r"(?:한테|에게)\s*(?:맞았|맞고|폭행|성폭행)|때려요|때렸어|가정폭력|성폭력",
        "es": r"me\s+(?:peg[óoa]|golpe[óoa]|golpea|maltrata|viol[óo])|violencia\s+(?:doméstica|domestica|de\s+género)|abus[óo]\s+de\s+m[ií]",
    }),
    ("disaster", "disaster", {
        "zh": r"地震了|地震|着火了|著火了|失火|火灾|火災|发大水|洪水|海啸|海嘯|煤气泄漏|瓦斯外洩|燃气泄漏|山体滑坡|泥石流",
        "ja": r"地震|火事|火災|洪水|浸水|津波|ガス漏れ|土砂崩れ",
        "ko": r"지진|불이\s*났|화재|홍수|침수|쓰나미|해일|가스\s*(?:가\s*)?새|산사태",
        "es": r"terremoto|sismo|incendio|se\s+est[áa]\s+quemando|inundaci[óo]n|tsunami|fuga\s+de\s+gas|huele\s+a\s+gas|deslizamiento",
    }),
    ("scam", "scam", {
        "zh": r"(?:冒充|自称|说是)[^。！？\n]{0,6}?(?:警察|公安|银行|检察院|法院|客服)[^。！？\n]{0,16}?(?:转账|汇款|验证码|安全账户)|(?:让我|要我)转账[^。！？\n]{0,10}?(?:警察|安全账户)|验证码[^。！？\n]{0,6}?(?:告诉|发给)|安全账户|刷单",
        "ja": r"(?:警察|銀行|役所|税務署)(?:を名乗る|だと名乗る|と名乗る)[^。！？\n]{0,20}?(?:送金|振り込|暗証番号)|(?:送金|振り込み?)(?:しろ|して)と言われ|オレオレ|還付金|暗証番号を(?:教え|聞かれ)",
        "ko": r"(?:경찰|검찰|은행|금감원)(?:이라며|이라고\s*하면서|을\s*사칭)[가-힯\s]{0,20}?(?:돈|송금|이체|계좌)|보이스\s*피싱|인증번호를?\s*(?:알려|보내)|안전\s*계좌",
        "es": r"(?:dice|dijo|dicen)\s+(?:ser|que\s+es)\s+(?:de\s+la\s+)?(?:polic[ií]a|banco)[^.!?\n]{0,30}?(?:transfer|dinero|c[óo]digo)|me\s+pidieron\s+(?:transferir|depositar|enviar)\s+dinero|c[óo]digo\s+de\s+verificaci[óo]n|ganaste\s+un\s+premio",
    }),
)
_URGENT_RX = [(k, topic, {lg: re.compile(rx, re.I) for lg, rx in by.items()}) for k, topic, by in URGENT_INTL]


def strip_someone_intl(text) -> str:
    """ตัดประโยคที่เล่าว่าคนอื่นอยากตาย (zh ja ko es) — เหลือเฉพาะสิ่งที่ผู้ใช้พูดถึงตัวเอง"""
    t = str(text or "")
    for k, _, by in _URGENT_RX:
        if k == "someone":
            for rx in by.values():
                t = rx.sub(" ", t)
    return t


def urgent_intl(text, lang: str | None = None) -> list:
    """เรื่องด่วนในภาษา zh ja ko es → [(ชนิด, หัวข้อในระบบไทย)] เรียงตามความเร่งด่วน"""
    t = str(text or "")
    if lang == "all":                        # ภาษาปนกัน ("我朋友说他想自杀ค่ะ") — รูปประโยคแต่ละภาษาใช้ตัวอักษรของมันเอง ตรวจทุกภาษาได้
        return [(k, topic) for k, topic, by in _URGENT_RX if any(rx.search(t) for rx in by.values())]
    lang = lang or detect_lang(t)
    return [(k, topic) for k, topic, by in _URGENT_RX if lang in by and by[lang].search(t)]


URGENT_REPLY = {
    "someone": {
        "zh": ("谢谢你关心他/她 — 你的陪伴比你想象的更重要。", ["现在就直接问：“你是不是想结束生命？” 问出口不会让情况变糟。",
               "如果他/她有危险或已经伤害自己，立刻拨打 120（急救）或 110。", "尽量不要让他/她一个人待着，并把药物、刀具等收起来。"],
               "他/她现在和别人在一起吗？"),
        "ja": ("その人のことを気にかけてくれてありがとう。あなたがそばにいることには大きな意味があります。",
               ["「死にたいと思っている？」とはっきり聞いてください。聞いても悪化しません。",
                "危険な状態やすでに自分を傷つけているなら、すぐに 119 に電話してください。",
                "できるだけ一人にしないで、薬や刃物を遠ざけてください。"], "その人は今、誰かと一緒にいますか？"),
        "ko": ("그 사람을 걱정해줘서 고마워요. 곁에 있어 주는 것이 생각보다 큰 힘이 돼요.",
               ["\"혹시 죽고 싶은 생각이 있어?\"라고 직접 물어보세요. 묻는다고 더 나빠지지 않아요.",
                "위험하거나 이미 자해했다면 바로 119에 전화하세요. 자살예방 상담전화 109(24시간)에서 어떻게 도울지 상담할 수 있어요.",
                "가능하면 혼자 두지 말고, 약이나 칼 같은 것은 치워 주세요."], "그 사람은 지금 누군가와 함께 있나요?"),
        "es": ("Gracias por preocuparte por esa persona — estar ahí importa más de lo que crees.",
               ["Pregúntale directamente: \"¿Estás pensando en quitarte la vida?\". Preguntar no empeora las cosas.",
                "Si está en peligro o ya se hizo daño, llama ahora al 112 (España) o al 911 (México y EE. UU.).",
                "Intenta que no se quede sola y aleja medicamentos, cuchillos o armas."], "¿Esa persona está acompañada ahora mismo?"),
    },
    "medical": {
        "zh": ("这是紧急情况 — 先打电话，再做其他事。", ["立即拨打 120（急救），说清楚地址和症状。",
               "没有呼吸或叫不醒：按电话里急救人员的指导做胸外按压。", "不要喂水或食物，把吃过的药或东西的包装留着给医生看。"],
               "现在有人在病人身边吗？"),
        "ja": ("緊急事態です — まず電話してください。", ["今すぐ 119 に電話し、住所と症状を伝えてください。",
               "呼吸がない・呼びかけに反応しない場合は、電話の指示に従って胸骨圧迫をしてください。",
               "水や食べ物を与えず、飲んだ薬などの容器は医師に見せるため残しておいてください。"], "今、その人のそばに誰かいますか？"),
        "ko": ("응급 상황이에요 — 먼저 전화부터 해 주세요.", ["지금 바로 119에 전화해서 주소와 증상을 말해 주세요.",
               "숨을 쉬지 않거나 깨워도 반응이 없으면, 전화 안내에 따라 가슴압박을 해 주세요.",
               "물이나 음식을 주지 말고, 먹은 약이나 물건의 포장은 의사에게 보여줄 수 있게 남겨 두세요."], "지금 환자 곁에 누가 있나요?"),
        "es": ("Es una emergencia — primero llama, después todo lo demás.", ["Llama ahora al 112 (España) o al 911 (México y EE. UU.) y di la dirección y los síntomas.",
               "Si no respira o no responde, sigue las instrucciones del operador para hacer compresiones en el pecho.",
               "No le des agua ni comida, y guarda el envase de lo que haya tomado para enseñarlo al médico."], "¿Hay alguien con la persona ahora mismo?"),
    },
    "violence": {
        "zh": ("这不是你的错，你值得安全。", ["如果现在有危险，立刻拨打 110。", "先去安全的地方：邻居、亲友家，或人多的地方。",
               "保留证据：伤口照片、聊天记录、就医记录。全国妇联热线 12338 可以提供帮助。"], "你现在安全吗？"),
        "ja": ("あなたのせいではありません。あなたには安全でいる権利があります。", ["今危険なら、すぐに 110 に電話してください。",
               "まず安全な場所へ：近所、家族や友人の家、人の多い場所。", "証拠を残してください（けがの写真、メッセージ、診断書）。DV相談ナビ #8008 で相談できます。"],
               "今、安全な場所にいますか？"),
        "ko": ("당신 잘못이 아니에요. 안전할 권리가 있어요.", ["지금 위험하다면 바로 112에 전화하세요.",
               "먼저 안전한 곳으로 가세요: 이웃, 가족이나 친구 집, 사람이 많은 곳.", "증거를 남겨 두세요(상처 사진, 메시지, 진단서). 여성긴급전화 1366(24시간)에서 도움을 받을 수 있어요."],
               "지금 안전한 곳에 있나요?"),
        "es": ("No es tu culpa. Mereces estar a salvo.", ["Si estás en peligro ahora, llama al 112 (España) o al 911 (México y EE. UU.).",
               "Ve primero a un lugar seguro: un vecino, familiares o amigos, o un sitio con gente.",
               "Guarda pruebas (fotos de lesiones, mensajes, partes médicos). En España, el 016 atiende 24 horas y no deja rastro en la factura."],
               "¿Estás en un lugar seguro ahora mismo?"),
    },
    "disaster": {
        "zh": ("安全第一 — 东西可以再买，人最重要。", ["地震：先趴下、护住头、抓牢桌子；停止摇晃后走楼梯离开，不坐电梯。",
               "火灾或煤气泄漏：不要开关电器，捂住口鼻低身离开，到外面再拨打 119。", "洪水或海啸：立刻往高处走，不要涉水或开车穿过积水。"],
               "你现在在哪里，身边有人吗？"),
        "ja": ("今は身の安全が最優先です — 物は取り戻せます。", ["地震：姿勢を低くして頭を守り、机につかまる。揺れが収まったら階段で外へ（エレベーターは使わない）。",
               "火事・ガス漏れ：電気のスイッチに触れず、口と鼻を覆って低い姿勢で外へ出てから 119 へ。", "津波・洪水：すぐに高い所へ。水の中を歩いたり車で進んだりしない。"],
               "今どこにいますか？一緒にいる人はいますか？"),
        "ko": ("지금은 안전이 먼저예요 — 물건은 다시 마련할 수 있어요.", ["지진: 몸을 낮추고 머리를 보호하며 탁자를 잡으세요. 흔들림이 멈추면 계단으로 나가세요(엘리베이터 금지).",
               "화재·가스 누출: 전기 스위치를 건드리지 말고, 입과 코를 막고 낮은 자세로 나간 뒤 119에 전화하세요.", "쓰나미·홍수: 바로 높은 곳으로 가세요. 물속을 걷거나 차로 지나가지 마세요."],
               "지금 어디에 있고, 함께 있는 사람이 있나요?"),
        "es": ("Tu seguridad es lo primero — las cosas se pueden reponer.", ["Terremoto: agáchate, cúbrete la cabeza y sujétate a una mesa; cuando pare, sal por las escaleras (no uses el ascensor).",
               "Incendio o fuga de gas: no toques interruptores, cúbrete nariz y boca, sal agachado y llama al 112 / 911 desde fuera.",
               "Inundación o tsunami: sube a un lugar alto ya. No camines ni conduzcas por el agua."], "¿Dónde estás ahora y hay alguien contigo?"),
    },
    "scam": {
        "zh": ("这很像诈骗 — 先停下，不要转账。", ["真正的警察、法院、银行不会让你转账到“安全账户”，也不会要验证码。",
               "挂掉电话，自己查官方号码再打回去确认。", "如果已经转账，马上打银行电话止付，并拨打 110 或反诈热线 96110。"],
               "你已经转账或告诉对方验证码了吗？"),
        "ja": ("詐欺の可能性が高いです — 送金はいったん止めてください。", ["本物の警察や銀行が送金や暗証番号を求めることはありません。",
               "電話を切り、公式の番号を自分で調べてかけ直して確認してください。", "すでに送金したら、すぐ銀行に連絡し、警察相談専用電話 #9110 か 110 へ。"],
               "もう送金したり、番号を伝えたりしましたか？"),
        "ko": ("보이스피싱일 가능성이 높아요 — 송금하지 말고 잠깐 멈추세요.", ["진짜 경찰·검찰·은행은 \"안전 계좌\"로 돈을 보내라거나 인증번호를 묻지 않아요.",
               "전화를 끊고, 공식 번호를 직접 찾아서 다시 확인하세요.", "이미 송금했다면 바로 은행에 지급정지를 요청하고 112에 신고하세요."],
               "이미 돈을 보냈거나 인증번호를 알려줬나요?"),
        "es": ("Esto tiene señales de estafa — no transfieras nada todavía.", ["La policía o tu banco nunca te pedirán transferir dinero a una \"cuenta segura\" ni tus códigos.",
               "Cuelga y llama tú al número oficial para comprobarlo.", "Si ya transferiste, llama a tu banco para bloquearlo y denuncia a la policía (112 / 911)."],
               "¿Ya enviaste dinero o diste algún código?"),
    },
}


def compose_urgent_intl(lang: str, kind: str, status: str, sign: str, footer: bool = True) -> str:
    opener, steps, ask = URGENT_REPLY[kind][lang]
    tag = "\n" + FOOTER[lang] if footer else ""
    body = "\n".join(f"{i + 1}) {s}" for i, s in enumerate(steps))
    return f"{opener}\n\n{status}\n\n{body}\n\n{ASK_LABEL[lang]} {ask}\n\n{sign}" + tag
