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
              "pidieron", "transferir", "casa", "mamá", "papá", "pareja", "pega", "golpea", "marido", "novio", "novia", "viviendo",
              # "mi madre no respira" เคยถูกเดาเป็นอังกฤษ → ไม่ได้ขั้นช่วยหายใจเลย (คำเหล่านี้ไม่ใช่คำอังกฤษ)
              "madre", "padre", "hijo", "hija", "hermano", "hermana", "abuelo", "abuela", "bebe", "nino", "nina",
              "respira", "respirar", "sangra", "sangre", "despierta", "responde", "ahogando", "desmayo",
              # "me amenazaron de muerte" "me estafaron" เคยถูกเดาเป็นอังกฤษ (ไม่มีสระมีเครื่องหมาย)
              "amenazaron", "amenazó", "muerte", "matar", "matarme", "estafaron", "estafa", "encerrada", "encerrado", "comido", "pegaron", "violaron",
              # อารมณ์หนัก/ภัยที่พูดสั้น ("quisiera no despertar" "alguien me sigue") เคยถูกเดาเป็นอังกฤษ
              "despertar", "quisiera", "broma", "llorar", "miedo", "siguiendo", "desaparecer", "segura", "seguro", "sola",
              "rabia", "enojado", "enojada", "matarlo", "matarla", "vacía", "vacio", "vacío", "suelos", "afuera", "puerta", "llorando", "llevo", "decidí", "encabronado", "encabronada"}


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


# ── อักษรของภาษาที่ระบบยังไม่มีคำตอบสำเร็จรูป (รัสเซีย อาหรับ ฮินดี ฯลฯ) ─────────────
# detect_lang คืน "en" ให้ภาษาเหล่านี้ (คำตอบแบบไม่มี AI มีแค่ 6 ภาษา) — แต่ถ้าบอก LLM ว่าเป็น en
# ผู้ใช้ที่พิมพ์รัสเซีย/อาหรับ/ฮินดีจะได้คำตอบภาษาอังกฤษ · ใช้ script_lang ตอนติดป้ายภาษาให้ LLM เท่านั้น
_SCRIPTS = (("ru", re.compile(r"[Ѐ-ӿ]")), ("ar", re.compile(r"[؀-ۿݐ-ݿ]")), ("hi", re.compile(r"[ऀ-ॿ]")),
            ("he", re.compile(r"[֐-׿]")), ("el", re.compile(r"[Ͱ-Ͽ]")), ("vi", re.compile(r"[ăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)))
SCRIPT_NAME = {"ru": "Русский", "ar": "العربية", "hi": "हिन्दी", "he": "עברית", "el": "Ελληνικά", "vi": "Tiếng Việt"}


# คำเวียดนามที่ใช้บ่อย — ประโยคสั้นอย่าง "hôm nay vui quá" ไม่มีตัวอักษรเฉพาะเวียดนามเลย (ô/á มีในภาษาอื่นด้วย)
# เคยถูกเดาเป็นสเปนเพราะมี á · พยางค์เหล่านี้แทบไม่เป็นคำในสเปน/โปรตุเกส/ฝรั่งเศส
_VI_WORDS = {"hôm", "nay", "quá", "không", "tôi", "mình", "bạn", "của", "và", "được", "người", "này", "rất",
             "vui", "buồn", "mệt", "anh", "chị", "em", "lắm", "gì", "sao", "thế", "nào", "với", "cho", "ơi", "nhé", "ạ",
             # รอบสุ่ม 32: ประโยคเหตุด่วนสั้นๆ ("tôi bỏ quên em bé trong xe nóng") มีคำที่รู้จักไม่ถึงครึ่ง
             "con", "bị", "nước", "nhà", "có", "mùi", "rất", "đang", "đã", "trong", "xe", "nóng", "bé", "bỏ", "quên",
             "mẹ", "bố", "ba", "má", "đau", "chết", "giúp", "cứu", "đi", "ở", "là", "mà", "thì", "ra", "vào", "được"}


def script_lang(text) -> str | None:
    """ภาษาจากตัวอักษรเฉพาะ (ru/ar/hi/he/el/vi) — ต้องเป็นตัวอักษรส่วนใหญ่ของข้อความ ไม่ใช่แค่คำเดียวปน"""
    t = str(text or "")
    letters = _LETTER.findall(t)
    if not letters or _THAI.search(t):
        return None
    toks = re.findall(r"[^\W\d_]+", t.lower())
    if toks and sum(w in _VI_WORDS for w in toks) >= max(2, len(toks) * 0.5):
        return "vi"
    for code, rx in _SCRIPTS:
        n = len(rx.findall(t))
        if code == "vi" and n >= 2:
            return code
        if n >= max(2, len(letters) * 0.4):
            return code
    return None


def prompt_lang(text) -> str:
    """ป้ายภาษาสำหรับ LLM: ภาษาที่มีอักษรเฉพาะก่อน แล้วค่อย detect_lang"""
    return script_lang(text) or detect_lang(text)


# ── สัญญาณทำร้ายตัวเอง ────────────────────────────────────────────────
# ปลอดภัยไว้ก่อนเหมือนภาษาไทย แต่ตัดสำนวนที่ไม่ได้แปลว่าอยากตาย:
# 想死你了 = คิดถึงมาก · me muero de risa = ขำจะตาย · dying to = อยากมาก
SELF_HARM_INTL = (
    re.compile(r"\b(?:i\s+)?(?:want|wanna|going)\s+to\s+die\b|\bkill(?:ing)?\s+myself\b|\bsuicid|"
               r"\bend(?:ing)?\s+(?:my\s+life|it\s+all)\b(?!\s+(?:with\s+a\s+bang|at\s+the\s+party|in\s+style))|\bdon'?t\s+want\s+to\s+(?:live|be\s+alive|exist)\b|"
               r"\bbetter\s+off\s+dead\b|\bno\s+reason\s+to\s+live\b|(?:^(?![\s\S]*\b(?:gym|work(?:ing)?\s+out|practice|by\s+accident|accidentally|shaving|cooking|lifting|playing|kitchen\s+knife|oven|stove)\b)[\s\S]*?\b(?:hurt(?:ing)?|harm(?:ing)?|cut(?:ting)?|burn(?:ing)?)\s+myself\b)|"
               r"\bself[- ]harm", re.I),
    re.compile(r"想死(?!你|您|他|她|它|我了|了你)|不想活|不想再醒|写好遗书|寫好遺書|遗书|遺書|(?:天台|楼顶|樓頂)[^。！？\n]{0,8}?(?:跳|跳下)|想跳(?:楼|樓|下去)|(?:^|(?<=[。！？\n]))(?![^。！？\n]*(?:医生开|医生给|醫生開|醫生給|医嘱|醫囑|疗程|療程|按时|按時|按医生|按醫生|开了[^。！？\n]{0,4}天|開了[^。！？\n]{0,4}天))[^。！？\n]*?(?<!的)(?:安眠药|安眠藥|药|藥)(?![^。！？\n]{0,6}?(?:要去|去医院|去醫院|再拿|再开|再開|去买|去買|续|續))[^。！？\n]{0,4}?(?:都|全)?吃(?:了|光|完)|吃了[^。！？\n]{0,4}?(?:安眠药|整瓶)|割腕|活不下去|自杀|自殺|轻生|輕生|结束(?:自己的)?生命|結束(?:自己的)?生命|"
               r"死了算了|不如死了"),
    re.compile(r"死にたい|消えたい|自殺|遺書|飛び降り(?:たい|る)|(?:睡眠薬|薬)を?(?:全部|たくさん|大量に)飲ん|リストカット|手首を切|生きていたくない|生きたくない|死のう|命を絶|"
               # "全部終わりにしたい" — ไม่นับเมื่อเป็นงาน/การบ้าน/ความสัมพันธ์ ("仕事を全部終わりにしたい")
               r"(?<!仕事を)(?<!宿題を)(?<!関係を)(?:全部|すべて|全て|何もかも)(?:を)?終わりに(?:したい|したくなる|したくて|しよう)"),
    re.compile(r"죽고\s*싶|살기\s*싫|자살|유서|뛰어내리(?:고\s*싶|려고|겠)|(?:수면제|약)(?:을|를)?\s*(?:다|전부|많이)\s*먹었|손목을?\s*(?:그었|그어)|살고\s*싶지\s*않|사라지고\s*싶|죽어\s*버리고\s*싶|극단적\s*선택|목숨을\s*끊"),
    re.compile(r"\b(?:me\s+)?quiero\s+morir|\bsuicid|\bquitarme\s+la\s+vida|\bno\s+quiero\s+vivir|"
               r"\bacabar\s+con\s+mi\s+vida|\bmatarme\b|\bhacerme\s+daño|\bno\s+quiero\s+seguir\s+(?:viviendo|con\s+vida|aqu[ií]\s*(?:$|[.!?…]))", re.I),
    # รัสเซีย · อาหรับ · ฮินดี — เดิมไม่มีเลย "я хочу умереть" ได้ความเสี่ยงต่ำ
    re.compile(r"хочу\s+умереть|не\s+хочу\s+жить|покончить\s+с\s+собой|суицид|убить\s+себя|"
               r"лучше\s+бы\s+я\s+умер|нет\s+смысла\s+жить", re.I),
    re.compile(r"أريد\s+أن\s+أموت|اريد\s+ان\s+اموت|أقتل\s+نفسي|اقتل\s+نفسي|انتحار|أنتحر|انتحر|لا\s+أريد\s+أن\s+أعيش|"
               r"لا\s+اريد\s+ان\s+اعيش|أنهي\s+حياتي"),
    re.compile(r"मरना\s+चाहत|मर\s+जाना\s+चाहत|आत्महत्या|ख़ुदकुशी|खुदकुशी|जीना\s+नहीं\s+चाहत|खुद\s+को\s+मार"),
    # เวียดนาม · เยอรมัน · ฝรั่งเศส · โปรตุเกส/อินโด (แรงงานและนักท่องเที่ยวในไทย)
    re.compile(r"(?<!mệt\s)(?<!đói\s)(?<!nóng\s)(?<!cười\s)(?<!ngủ\s)(?<!chán\s)muốn\s+chết|tự\s+tử|không\s+muốn\s+sống|"
               r"\b(?:ich\s+)?will\s+(?:nicht\s+mehr\s+leben|sterben)\b|\bselbstmord|\bmich\s+umbringen|"
               r"\bje\s+veux\s+mourir(?!\s+de\s+(?:rire|honte|faim))|\bme\s+suicider|\bquero\s+morrer|\bn[ãa]o\s+(?:aguento|quero|consigo)\s+mais\s+viver|\bn[ãa]o\s+quero\s+(?:mais\s+)?viver|\bvou\s+(?<!vai\s)(?<!v(?:ã|a)o\s)me\s+matar|\b(?<!vai\s)(?<!v(?:ã|a)o\s)me\s+matar\b|\bingin\s+mati\b|\bbunuh\s+diri", re.I),
)


# อยากตายแบบอ้อม ("หลับแล้วไม่ต้องตื่น" "อยากหลับไปตลอดกาล" "มีชีวิตอยู่เหนื่อยเหลือเกิน") — เดิมจับได้แค่ภาษาไทย
# ชุดปิดตา (tests/blind) เจอว่ารูปนี้ในภาษาจีนและโปรตุเกสได้ความเสี่ยงต่ำ — ข้อที่แก้ย้ายไป tests/corpus/messages.tsv แล้ว
# ไม่นับเรื่องตื่นนอนธรรมดา: "don't want to wake up early" "no quiero despertarme temprano" "起きたくない"
SELF_HARM_PASSIVE = (
    re.compile(r"\bsleep and (?:never|not) wake(?: up)?\b|\b(?:never|not) wake up again\b|\bwish i (?:was|were) dead\b|"
               r"\bwish i (?:wasn'?t|weren'?t) (?:alive|here|born)\b|\bwish i (?:had )?never (?:been born|woken up)\b|"
               r"\bdon'?t want to wake up\b(?!\s+(?:early|at|for|so|this|tomorrow|before|on))|\bwant to (?:sleep|disappear) forever\b|"
               r"\b(?:tired|exhausted|sick) of (?:living|being alive|life itself)\b(?!\s+(?:in|with|at|here|there|like|on|under|out|paycheck|alone|together))|\bwhat'?s the point of (?:living|being alive)\b", re.I),
    re.compile(r"(?:想|要)?永远(?:地)?睡(?:下去|着|过去)|睡(?:着|过去)了?就?(?:不|别)(?:要|想)?(?:再)?醒|不想(?:再)?醒(?:来|过来)|"
               r"活着(?:好|太|真|很)?(?:累|没意思|没有意义|没意义)|不想(?:再)?活着|消失就好了"),
    re.compile(r"永遠に眠りたい|ずっと眠っていたい|目が覚めなければ(?:いい|いいのに)|二度と目覚めたくない|生きるのが(?:疲れ|つらい|辛い|しんどい)"),
    re.compile(r"영원히\s*(?:잠들고|자고)\s*싶|다시는\s*깨어나고\s*싶지\s*않|깨어나지\s*않았으면|사는\s*게\s*(?:너무\s*)?(?:지쳐|지친다|의미\s*없)"),
    re.compile(r"\bdormir\s+y\s+no\s+(?:volver\s+a\s+)?despertar|\bno\s+(?:quiero|quisiera)\s+(?:volver\s+a\s+)?despertar(?:me)?\b(?!\s+(?:temprano|a\s+las|ma[ñn]ana|tan|para))|"
               r"\bojal[áa]\s+no\s+despertara|\bquisiera\s+(?:estar\s+muert|desaparecer)|\bcansad[oa]\s+de\s+vivir\b(?!\s+(?:en|aqu[ií]|con|as[ií]|sol[oa]))", re.I),
    re.compile(r"\bdormir\s+e\s+n[ãa]o\s+acordar|\bn[ãa]o\s+(?:quero|queria)\s+(?:mais\s+)?acordar\b(?!\s+(?:cedo|[àa]s|amanh[ãa]))|\bqueria\s+(?:estar\s+mort|sumir|desaparecer)|\bcansad[oa]\s+de\s+viver\b(?!\s+(?:em|aqui|com|assim|nest[ae]|n[ao]|sozinh[oa]))", re.I),
    re.compile(r"ngủ\s+(?:mãi|luôn|một\s+giấc)\s+không\s+(?:dậy|tỉnh)|không\s+muốn\s+tỉnh\s+dậy\s+nữa|mệt\s+mỏi\s+(?:với\s+)?(?:cuộc\s+sống|việc\s+sống)|"
               r"\bdormir\s+et\s+ne\s+(?:plus\s+)?jamais\s+(?:me\s+)?r[ée]veiller|\bne\s+plus\s+(?:jamais\s+)?me\s+r[ée]veiller|\bfatigu[ée]e?\s+de\s+vivre\b(?!\s+(?:ici|à|a|en|dans|avec|comme|seule?))|"
               r"\bnicht\s+mehr\s+aufwachen|\bm[üu]de\s+zu\s+leben\b(?!\s+(?:in|hier|mit|so|allein))|\btidur\s+dan\s+tidak\s+bangun\s+lagi|\blelah\s+hidup\b(?!\s+(?:di|dengan|seperti|sendiri))", re.I),
)


# สัญญาณเตือนแบบอ้อม (เทสต์สุ่มรอบ 5 · เดิมหลุดทั้ง 5 ภาษา): แจกของรัก · ไม่อยากเป็นภาระ · ไม่มีใครสังเกตถ้าไม่มีเรา ·
# อยากไปหาคนที่เสียไป · ถือมีดแล้วไม่ไหว — แบบเดียวกับ INDIRECT_SELF ภาษาไทย
SELF_HARM_INDIRECT = (
    re.compile(r"大切な(?:もの|物)を?[^。！？\n]{0,12}(?:全部|みんな|すべて)?(?:あげた|譲った|手放した)|(?:もう)?誰の(?:迷惑|負担|重荷)にも?なりたくない|"
               r"(?:いなくなっても|消えても|死んでも)[^。！？\n]{0,8}誰も(?:気づかない|気にしない|悲しまない)|(?:死んだ|亡くなった)(?:母|父|ママ|パパ|友達|彼氏|彼女|夫|妻|子)に会いに行きたい|"
               r"(?:ナイフ|包丁|刃物)[^。！？\n]{0,6}持って[^。！？\n]{0,10}(?:無理|限界|もうだめ)"),
    re.compile(r"把?(?:心爱|心愛|珍贵|珍貴|重要)的东?西?[^。！？\n]{0,10}(?:都|全)(?:送|给|給)|不想再?(?:成为|成為|当|當)?(?:别人|別人|任何人|大家|家人)的(?:负担|負擔|累赘)|"
               r"(?:不在了?|消失了?|死了)[^。！？\n]{0,10}(?:没人|沒人|没有人|沒有人)(?:会|會)?(?:注意|发现|發現|在乎|难过)|想去(?:见|見|找)(?:去世|过世|過世|死去)的|"
               r"拿着?刀[^。！？\n]{0,10}(?:受不了|撑不住|撐不住|不行了)"),
    re.compile(r"아끼는\s*(?:물건|것)(?:을|들을)?[가-힯\s]{0,12}다\s*줬|(?:누구에게도|아무에게도|더\s*이상)[가-힯\s]{0,10}짐이\s*되고\s*싶지\s*않|"
               r"(?:내가|제가)\s*없어도\s*아무도\s*(?:모를|모르|신경\s*안|슬퍼하지)|돌아가신\s*\S+\s*(?:보러|만나러|따라)\s*가고\s*싶|칼을?\s*들고[가-힯\s]{0,10}(?:못\s*하겠|힘들|끝)"),
    re.compile(r"\bregal[ée]\s+(?:todas\s+)?mis\s+cosas|\bno\s+quiero\s+ser\s+(?:una\s+)?carga\b|\bsi\s+(?:mañana\s+)?no\s+estoy\b[^.!?\n]{0,25}\bnadie\s+(?:lo\s+)?(?:notar|se\s+dar)|"
               r"\bquiero\s+(?:ir\s+con|ver\s+a)\s+mi\s+(?:madre|mam[áa]|padre|pap[áa]|herman[oa]|hij[oa])\s+que\s+(?:muri|falleci)|\btengo\s+un\s+cuchillo\b[^.!?\n]{0,20}\bno\s+(?:puedo|aguanto)", re.I),
    re.compile(r"cho\s+(?:bạn\s+bè\s+|mọi\s+người\s+)?hết\s+(?:những\s+)?(?:thứ|đồ)|không\s+muốn\s+(?:làm|là)\s+gánh\s+nặng|không\s+còn\s+(?:nữa\s+)?thì[^.!?\n]{0,25}(?:chẳng|không)\s+ai\s+(?:để\s+ý|quan\s+tâm|nhận\s+ra)|"
               r"muốn\s+(?:đi\s+)?gặp\s+(?:mẹ|bố|ba|má)\s+(?:đã\s+)?(?:mất|qua\s+đời)|cầm\s+dao[^.!?\n]{0,20}(?:không\s+chịu\s+nổi|hết\s+chịu)", re.I),
)

# รอบสุ่ม 45: สัญญาณหลังคำปลอบ "ไม่เป็นไร/ทุกอย่างโอเค" (ja zh ko es vi) — เดิมหลุด 15/15
# ต้องมีคำปลอบ + (ทุกคนจะสบาย · จดหมายถึงแม่เขียนเสร็จแล้ว · ไม่ต้องตามหา) — จดหมายวันแม่หรือไปค่ายไม่มีสัญญาณไม่นับ
_MASK = {
    "ja": (r"大丈夫|全部大丈夫|平気", r"みんな楽になる|手紙(?:も)?もう書いた|(?:いなくても|いなかったら)[^。！？\n]{0,6}探さないで"),
    "zh": (r"没事|沒事|一切都好|都挺好", r"大家就都轻松|大家都輕鬆|信已经写好|信已經寫好|(?:看不到我|不见我)[^。！？\n]{0,8}别找我"),
    "ko": (r"괜찮아|다\s*괜찮", r"다들\s*편해질|편지(?:도)?\s*다\s*썼|(?:접속\s*안\s*해도|안\s*보여도)\s*찾지\s*마"),
    "es": (r"estoy\s+bien|todo\s+bien|no\s+pasa\s+nada", r"todos\s+van\s+a\s+estar\s+mejor|ya\s+le\s+escrib[íi]\s+la\s+carta|no\s+me\s+busques"),
    "vi": (r"không\s+sao|mọi\s+thứ\s+ổn|ổn\s+mà", r"mọi\s+người\s+cũng\s+sắp\s+nhẹ\s+nhõm|đã\s+viết\s+thư\s+cho\s+(?:mẹ|bố|mọi\s+người)\s+rồi|đừng\s+tìm"),
}
_MASK_NOT = r"(?!.*(?:母の日|旅行|圏外|露营|没信号|생신|campamento|sin\s+señal|ngày\s+của\s+mẹ|đi\s+cắm\s+trại|mất\s+sóng))"
SELF_HARM_MASKED = tuple(re.compile(r"(?is)^" + _MASK_NOT + r"(?=.*(?:" + a_ + r")).*(?:" + b_ + r")") for a_, b_ in _MASK.values())
# "พรุ่งนี้ไม่เห็นออนไลน์ ไม่ต้องตามหา" นับได้โดยไม่ต้องมีคำปลอบ ("ไม่ต้องหาในงานปาร์ตี้" ไม่นับ) · ไปเที่ยว/ไม่มีสัญญาณไม่นับ
SELF_HARM_MASKED += (re.compile(r"(?is)^" + _MASK_NOT + r"(?=.*(?:明日|明天|내일|mañana|ngày\s+mai|\bmai\b))(?=.*(?:オンライン|在线|在線|접속|conectad|online))"
                               r".*(?:探さないで|别找我|別找我|찾지\s*마|no\s+me\s+busques|đừng\s+tìm)"),)
# เวียดนามแบบอ้อม (เทียบ 7 ภาษา 2026-11): เดิมรู้จักแค่ "tỉnh dậy" ไม่รู้จัก "thức dậy" (คำที่ใช้บ่อยกว่า)
# และ "ทุกคนจะดีขึ้นถ้าไม่มีฉัน" ซึ่งภาษาอื่นจับได้แล้ว — ต้องมี "ทุกคน/ครอบครัว" ไม่นับ "ทีมจะดีขึ้นถ้าไม่มีฉันเล่น"
SELF_HARM_PASSIVE += (re.compile(r"không\s+muốn\s+(?:thức|tỉnh)\s+dậy\s+nữa|(?:mọi\s+người|cả\s+nhà|ai\s+cũng|gia\s+đình)[^.!?\n]{0,20}(?:tốt\s+hơn|nhẹ\s+nhõm|sướng\s+hơn|bớt\s+khổ)"
                                 r"[^.!?\n]{0,15}(?:nếu\s+)?(?:không\s+có|thiếu|vắng)\s+(?:tôi|mình|em|con|tao)\b", re.I),)
# ชุดตรวจซ้ำ (ข้อความที่ไม่เคยเห็น) ยังหลุด: es "me voy a quitar la vida" (เดิมรู้จักแค่ quitarme ติดกัน)
# · es/ja "ครอบครัวคงสบายขึ้นถ้าไม่มีฉัน" · vi "kết liễu đời mình" (ปลิดชีวิตตัวเอง) · ja "もう目覚めたくない"
SELF_HARM_PASSIVE += (
    re.compile(r"\bme\s+(?:\w+\s+){0,3}?quitar\s+la\s+vida\b|(?:alivio|mejor|m[áa]s\s+felices|m[áa]s\s+tranquil[oa]s)[^.!?\n]{0,40}\bsi\s+(?:yo\s+)?(?:ya\s+)?no\s+(?:estuviera|existiera|estuviese)\b", re.I),
    re.compile(r"kết\s+liễu\s+(?:đời|cuộc\s+đời|bản\s+thân|mạng\s+sống)|tự\s+kết\s+liễu|kết\s+thúc\s+(?:cuộc\s+đời|cuộc\s+sống|mạng\s+sống)\s+(?:của\s+)?(?:mình|tôi|em)\b", re.I),
    re.compile(r"(?:私|僕|俺|自分|わたし)が(?:いなくなれば|いなくなったら|いない方が|消えれば|消えたら|死ねば|死んだら)[^。！？\n]{0,12}(?:楽になる|幸せになる|助かる|喜ぶ)|もう目覚めたくない"),
)
# งานแก้จุดอ่อนจากชุดปิดตา: "ชีวิตไม่มีความหมาย + เหนื่อยจะมีอยู่" และ "เขียนจดหมายลาตายแล้ว" ใน es vi ko ja
# แก้ที่รูปประโยคทั่วไป ไม่ได้คัดลอกข้อสอบ (เทสต์ใช้ประโยคคนละแบบ: tests/test_blind_weak_spots.py)
SELF_HARM_MEANING = (
    re.compile(r"\bno\s+(?:le\s+)?(?:veo|encuentro|tiene)\s+(?:ning[uú]n\s+)?sentido\s+(?:a\s+|en\s+)?(?:seguir|vivir|la\s+vida|mi\s+vida|existir)\b(?!\s+(?:con|en|de|el|la|los|las|este|esta|ese|esa|aqu[ií]\s+en|trabajando|estudiando)\b)|"
               r"\bcansad[oa]\s+de\s+(?:existir|vivir|estar\s+viv[oa])\b(?!\s+(?:en|con|de|cerca|lejos|solo|sola|aqu[ií]|all[ií])\b)|\bcarta\s+de\s+suicidio\b", re.I),
    re.compile(r"thư\s+tuyệt\s+mệnh|di\s+thư\s+(?:cho|để\s+lại)|sống\s+(?:không|chẳng)\s+(?:còn\s+)?(?:có\s+)?ý\s+nghĩa\s+gì|mệt\s+mỏi\s+với\s+việc\s+(?:sống|tồn\s+tại)", re.I),
    re.compile(r"(?:사는\s*(?:게|것이|것도)|살아\s*있는\s*(?:게|것이)|살아갈|살아야\s*할)\s*(?:아무\s*)?(?:의미가|의미도|이유가|이유도)\s*없"),
    re.compile(r"(?:生きて(?:い|る|いる)|生きる)(?:こと(?:に|の))?意味(?:が|も)?(?:ない|無い|わからない|分からない)|生きるのに疲れ|生きることに疲れ"),
)
# รอบสุ่ม 223: การทำร้ายตัวเองที่เกิดอยู่แล้ว (ไม่ใช่แค่ "อยากตาย") — เคยได้ 0 ใน 9 ภาษา
SELF_HARM_ACT = (
    re.compile(r"\bme\s+(?:estoy\s+)?(?:haciendo|hago|hice)\s+daño\b|\bme\s+(?:corto|corté|estoy\s+cortando)\s+(?:los\s+brazos|las\s+muñecas|las\s+piernas|a\s+propósito|otra\s+vez|todas\s+las\s+noches)|\bautolesi", re.I),
    re.compile(r"tự\s+(?:làm\s+đau|làm\s+hại|hành\s+hạ)\s+(?:mình|bản\s+thân)|tự\s+(?:cắt|rạch)\s+tay|(?:hay|thường|lại|vẫn)\s+(?:cắt|rạch)\s+tay", re.I),
    re.compile(r"(?<!不要)(?<!别)(?<!不會)(?<!不会)(?:伤害|傷害)自己|自残|自殘|割(?:自己|手腕|手臂|腕)"),
    re.compile(r"自分を傷つけ|自傷|リスカ|(?:自分の|わざと)(?:腕|手首)を(?:切っ|切る)"),   # "ガラスで腕を切って" = อุบัติเหตุ
    re.compile(r"자해|(?:팔|손목|다리)을?\s*(?:그어|긋|그었)"),
    re.compile(r"\bje\s+me\s+(?:fais\s+du\s+mal|coupe(?!\s+les\s+cheveux)|scarifie|mutile)|\bautomutil|\bich\s+(?:verletze|ritze)\s+mich|\bselbstverletz|"
               r"(?:^(?![\s\S]*\b(?:cabelo|pelo|cabello|unhas|uñas|barba|franja|flequillo|dedo|cebolla|cebola|cocinando|cozinhando)\b)[\s\S]*?\b(?:eu\s+)?me\s+(?:corto|machuco|mutilo)\b)|\bmelukai\s+diri|\bmenyakiti\s+diri", re.I),
)
# รอบสุ่ม 228: ข้อความที่ทิ้งไว้ ("ถ้าอ่านข้อความนี้ แปลว่าฉันไม่อยู่แล้ว") · ฝากสัตว์เลี้ยงแล้วบอกว่าจะไม่อยู่ — 9 ภาษา เคยได้ 0
# "猫をよろしく、もう会えない" ไม่จับ — ย้ายไปต่างประเทศก็พูดแบบนี้ได้
SELF_HARM_NOTE = (
    re.compile(r"\bsi\s+(?:estás|estas)\s+leyendo\s+esto[^.!?\n]{0,15}?ya\s+no\s+(?:estoy|existo)|\bya\s+no\s+voy\s+a\s+estar\b(?![^.!?\n]{0,20}(?:en\s+la\s+oficina|en\s+casa|mañana|esta\s+semana|el\s+lunes))", re.I),
    re.compile(r"(?:看到|读到|讀到)这?(?:条|條)?(?:消息|讯息|訊息|信)[^。！？\n]{0,6}(?:我已经|我已經)?(?:不在了|走了|离开了|離開了)|我以后不在了|我以後不在了"),
    re.compile(r"(?:これを)?読んでいる(?:なら|ということは)[^。！？\n]{0,10}(?:私|僕|俺)?(?:は)?もう(?:いない|この世にいない)"),
    re.compile(r"(?:이\s*글을?|이걸)\s*(?:보고|읽고)\s*있다면[^.!?\n]{0,15}(?:이미|이제)\s*없|난\s*이제\s*없을\s*거"),
    re.compile(r"(?:đọc|thấy)\s+được\s+(?:tin|thư|tin\s+nhắn)\s+này[^.!?\n]{0,15}(?:đã\s+đi\s+rồi|không\s+còn\s+nữa|không\s+còn\s+trên\s+đời)|^(?![\s\S]*(?:chuyển|đi\s+làm|du\s+lịch|về\s+quê|ra\s+nước\s+ngoài|công\s+ty))[\s\S]*?sẽ\s+không\s+còn\s+ở\s+đây\s+nữa", re.I),
    re.compile(r"\bsi\s+tu\s+lis\s+ceci[^.!?\n]{0,15}je\s+ne\s+suis\s+plus\s+l(?:à|a)|\bwenn\s+du\s+das\s+liest[^.!?\n]{0,15}bin\s+ich\s+nicht\s+mehr\s+da"
               r"|\bse\s+voc(?:ê|e)\s+est(?:á|a)\s+lendo\s+isso[^.!?\n]{0,15}(?:j(?:á|a)\s+)?n(?:ã|a)o\s+estou\s+mais|\bkalau\s+kamu\s+baca\s+ini[^.!?\n]{0,15}(?:aku|saya)\s+sudah\s+tidak\s+ada", re.I),
)
SELF_HARM_INTL = SELF_HARM_INTL + SELF_HARM_MEANING + SELF_HARM_ACT + SELF_HARM_NOTE
SELF_HARM_INTL = SELF_HARM_INTL + SELF_HARM_PASSIVE + SELF_HARM_INDIRECT + SELF_HARM_MASKED   # ผู้ใช้ทุกที่ (kernel_voice วิกฤต · llm_gemini ความปลอดภัย) ได้แบบอ้อมด้วย


def self_harm_intl(text) -> bool:
    t = str(text or "")
    return any(p.search(t) for p in SELF_HARM_INTL)


# ── ข้อความตอบตอนไม่มี AI ─────────────────────────────────────────────
HELP = {
    "en": ("If you are in danger right now, call your local emergency number (911 in the US and Canada, "
           "999 in the UK, 112 in most of Europe, 000 in Australia). In the US you can call or text 988 · Australia: Lifeline 13 11 14 · 13YARN 13 92 76 (Aboriginal & Torres Strait Islander). "
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
             "es": "Una pregunta para hacerte ahora:",
             "vi": "Một câu hỏi để tự hỏi mình lúc này:"}
FOOTER = {"en": "· Answered from the system's equations — no AI used", "zh": "· 由系统公式回答 — 未使用 AI",
          "ja": "· システムの数式による回答 — AI は使っていません", "ko": "· 시스템 공식으로 답했어요 — AI를 사용하지 않았어요",
          "es": "· Respondido con las ecuaciones del sistema — sin usar IA",
          "vi": "· Trả lời từ các phương trình của hệ thống — không dùng AI"}



# ผู้ใช้ส่วนใหญ่อยู่ในไทย (นักท่องเที่ยว นักเรียน แรงงาน) — เดิมคำตอบ 5 ภาษานี้ให้แค่เบอร์บ้านเกิด (911 · 110 · 119)
# โทรจากไทยแล้วไม่ติด · 1155 ตำรวจท่องเที่ยวรับสายภาษาอังกฤษได้
TH_NUMBERS = {
    "en": "In Thailand: 1669 (medical emergency) · 191 (police) · 1323 (mental health, 24h) · 1155 (tourist police, English spoken).",
    "zh": "在泰国：急救 1669 · 报警 191 · 心理援助 1323（24小时）· 旅游警察 1155（可讲英语）。",
    "ja": "タイにいる場合：救急 1669・警察 191・心の相談 1323（24時間）・観光警察 1155（英語可）。",
    "ko": "태국에 있다면: 응급 1669 · 경찰 191 · 정신건강 상담 1323(24시간) · 관광경찰 1155(영어 가능).",
    "es": "En Tailandia: 1669 (emergencias médicas) · 191 (policía) · 1323 (salud mental, 24 h) · 1155 (policía turística, habla inglés).",
    "vi": "Ở Thái Lan: 1669 (cấp cứu) · 191 (cảnh sát) · 1441 (lừa đảo trực tuyến) · 1155 (cảnh sát du lịch, nói tiếng Anh).",
}
for _lg, _line in TH_NUMBERS.items():
    if _lg in HELP and "1323" not in HELP[_lg]:
        HELP[_lg] = _line + " " + HELP[_lg]

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
        "zh": r"(?:卡住|噎住)(?:了)?(?:喉咙|喉嚨|气管)|(?:喉咙|喉嚨)(?:被)?[^。！？\n]{0,4}卡住|(?:孩子|宝宝|寶寶|儿子|女儿)[^。！？\n]{0,4}(?:喝|吃|吞)(?:了)?(?:洗涤剂|洗潔精|洗衣液|漂白水|消毒水|农药|農藥|清洁剂)|胸(?:口)?(?:痛|疼)[^。！？\n]{0,8}(?:冷汗|出汗|左臂|喘不过气)|晕倒|昏倒|昏迷|叫不醒|下药|下藥|流血不止|血流不止|吞了(?:电池|電池|纽扣|硬币)|困在电梯|困在電梯|(?:狗|猫)咬|狂犬|没有呼吸|沒有呼吸|不能呼吸|喘不过气|胸口(?:剧痛|很痛|疼)|心脏病发|中风|抽搐|大出血|吃了(?:很多|一整瓶|整瓶)(?:药|安眠药)|吃了安眠药|喝了农药|溺水|吞了(?:一[个颗枚])?(?:纽扣)?(?:电池|電池|磁铁|磁鐵|硬币|硬幣)|喝了(?:漂白水|漂白剂|消毒水)|溺水|(?:掉|落|摔)(?:进|到|入)(?:了)?(?:水|河|湖|海|泳池|游泳池|水池)",
        "ja": r"喉に詰まら(?!せ?ないよう|せ?ないで|せ?ない様)|喉に詰まっ|(?:子供|子ども|赤ちゃん|息子|娘)が[^。！？\n]{0,6}(?:洗剤|漂白剤|ハイター|農薬|殺虫剤|灯油)を(?:飲ん|食べ|なめ)|胸が(?:痛|苦し)[^。！？\n]{0,12}(?:汗|冷や汗|左腕|息が)|蛇に噛まれ|倒れ(?:た|ている)|起きない|何か入れられ|出血が止まらない|電池を飲み込|閉じ込められ|犬に噛まれ|狂犬|意識がない|息をしていない|呼吸(?:が|できない)|(?:^|(?<=[.!?。！？\n]))(?![^.!?。！？\n]*(?:失恋|振られ|フラれ|別れ|片思い))[^.!?。！？\n]*?胸が(?:痛|苦し)(?!いほど|くなるほど|い話|くなる話|い思い)|心臓発作|脳卒中|けいれん|大量出血|薬を(?:たくさん|大量に)飲|溺れ|(?:ボタン)?電池を(?:飲み込|飲ん)|磁石を(?:飲み込|飲ん)|漂白剤を飲|溺れ(?:た|ている|そう)|(?:プール|川|海|池)に落ち",
        "ko": r"목에\s*(?:걸렸|걸려)|(?:아이|아기|애|아들|딸)가?\s*[가-힯\s]{0,6}(?:세제|락스|표백제|농약|살충제)를?\s*(?:마셨|먹었|삼켰)|가슴이?\s*(?:아프|아파|조이)[가-힯\s]{0,12}(?:식은땀|땀을|왼팔|숨이)|(?:술|만취)[가-힯\s]{0,12}깨워도\s*안\s*일어나|깨워도\s*(?:안|못)\s*일어나|뱀에\s*물렸|쓰러졌|안\s*깨어나|약\s*탄\s*술|피가\s*안\s*멈|건전지를?\s*삼켰|갇혔|개한테\s*물렸|광견병|의식이\s*없|숨을\s*안\s*쉬|숨을\s*못\s*쉬|숨이\s*안\s*쉬어|(?:^|(?<=[.!?。！？\n]))(?![^.!?。！？\n]*(?:이별|헤어지|헤어져|헤어졌|실연|짝사랑|차여서|차였))[^.!?。！？\n]*?가슴이\s*(?:너무\s*)?아파|심장마비|뇌졸중|경련|피가\s*멈추지\s*않|약을\s*(?:많이|한\s*통)|물에\s*빠졌|(?:건전지|배터리|자석|동전)[을를]?\s*삼켰|락스[를을]?\s*마셨|물에\s*빠졌|익사|수영장에\s*빠졌",
        "vi": r"bị\s+hóc|hóc\s+(?:đồ|xương|kẹo)|(?:uống|nuốt|ăn)\s+(?:phải\s+)?(?:nước\s+tẩy|thuốc\s+tẩy|thuốc\s+trừ\s+sâu|xăng|thuốc\s+chuột)|đau\s+ngực[^.!?\n]{0,20}(?:vã\s+mồ\s+hôi|mồ\s+hôi|khó\s+thở|tay\s+trái)|(?:say|uống)[^.!?\n]{0,20}(?:gọi\s+(?:mãi\s+)?không\s+tỉnh|bất\s+tỉnh)|bất\s+tỉnh|không\s+thở|ngất\s+xỉu",
        "es": r"se\s+atragant[óo]|(?:se\s+)?(?:tom[óo]|bebi[óo]|trag[óo])\s+(?:cloro|lej[íi]a|detergente|veneno|insecticida)|dolor\s+de\s+pecho[^.!?\n]{0,30}(?:sudando|sudor|brazo\s+izquierdo|no\s+puede\s+respirar)|est[áa]\s+sangrando|se\s+desmay[óo]|inconsciente|no\s+respira|no\s+(?:se\s+)?despierta|no\s+reacciona|no\s+responde(?!\s+(?:el|los|mis|a\s+mis)\s+(?:mensajes?|correos?|llamadas?))|no\s+puedo\s+respirar|dolor\s+(?:fuerte\s+)?(?:en\s+el|de)\s+pecho|infarto|derrame\s+cerebral|convulsi|sangra\s+mucho|se\s+tom[óo]\s+(?:muchas|todas\s+las)\s+pastillas|se\s+est[áa]\s+ahogando|se\s+trag[óo]\s+(?:una?\s+)?(?:pila|bater[ií]a|im[áa]n|moneda)|(?:tom[óo]|bebi[óo])\s+(?:lej[íi]a|cloro)|se\s+(?:cay[óo]|ha\s+ca[ií]do)\s+(?:a|en)\s+(?:la\s+|el\s+)?(?:piscina|alberca|pileta|r[ií]o|agua|mar|lago|canal)|se\s+ahog[óo]|no\s+abre\s+los\s+ojos",
    }),
    ("violence", "violence", {
        "zh": r"(?:有人|陌生人|小偷)[^。！？\n]{0,6}(?:撬开|撬開|砸开|砸開|踹开|踹開|破)(?:了)?(?:门|門|窗)|(?:闯|闖|潜|溜)进(?:了)?我家|(?:闯|闖|潜|溜)進(?:了)?我家|陌生人[^。！？\n]{0,8}(?:开|開|撬|拧|擰)(?:我的?)?门|(?:被|挨)[^。！？\n]{0,4}?(?:打|殴打|家暴|强奸|性侵)|[他她](?:又|一直|总是|老是|经常|天天)?(?:打|揍)(?:了)?我(?!电话|電話|手机|手機|的电话|微信|一下电话)|打(?:我|了我)?(?:妈|媽|妈妈|媽媽|爸|孩子)|要杀(?:了)?孩子|要殺(?:了)?孩子|扣(?:了)?(?:我的)?(?:护照|護照)|(?:护照|護照)被(?:扣|没收|沒收)|(?:老公|丈夫|老婆|男朋友|爸爸|妈妈)[^。！？\n]{0,3}?打我|家暴|"
              r"(?:要|说要|威胁要?|想)[^。！？\n]{0,3}?杀(?:了|死)?我|被[^。！？\n]{0,4}?(?:关|锁|囚禁)在|被威胁",
        "ja": r"(?:誰か|知らない人|泥棒|不審者)が?[^。！？\n]{0,12}(?:ドア|窓|扉)を?(?:こじ開け|壊し|破っ|蹴破っ)て?(?:入って|侵入)|家に(?:誰か|泥棒|不審者)が(?:入って|侵入)|知らない(?:人|男|女)が[^。！？\n]{0,8}(?:ドア|扉|鍵)を?(?:開けよう|こじ開け|ガチャガチャ)|(?:に|から)(?:殴られ|叩かれ|蹴られ|暴力を振るわれ|襲われ)|(?:母|父|妻|子供)を殴|(?:子供|子ども)を殺す|DV|性的暴行|レイプ|殺す(?:ぞ)?と(?:脅|言われ)|殺される(?![笑ｗw（(])|閉じ込められ|監禁",
        "ko": r"(?:누가|누군가|모르는\s*사람이?|도둑이?)\s*[가-힯\s]{0,10}?문을?\s*(?:부수고|부시고|따고|뜯고)\s*들어|집에\s*(?:누가|누군가|도둑이?)\s*(?:들어왔|침입)|모르는\s*사람(?:이|가)?[가-힯\s]{0,12}문을?\s*(?:열려|따려|두드리)|(?:한테|에게)\s*(?:맞았|맞고|폭행|성폭행)|(?:엄마|아빠|아내|애|아이)를\s*때려|아이를?\s*죽이겠|때려요|때렸어|가정폭력|성폭력|죽인다고|죽이겠다고|협박|(?:^|(?<=[.!?。！？\n]))(?![^.!?。！？\n]*(?:막혀|막히|정체|교통|차가\s*밀))[^.!?。！？\n]*?갇혀\s*있|감금",
        "vi": r"(?:người\s+lạ|ai\s+đó|có\s+người|kẻ\s+trộm|trộm)[^.!?\n]{0,15}(?:cố\s+)?(?:mở|phá|cạy)\s+cửa|xông\s+vào\s+nhà|đột\s+nhập\s+(?:vào\s+)?nhà|(?:bị|đang\s+bị)\s+(?:đánh|đập|bạo\s+hành)",
        "es": r"alguien\s+(?:entr[óo]|se\s+meti[óo])\s+a\s+la\s+fuerza|forz(?:[óo]|aron)\s+(?:la\s+)?puerta\s+(?:de\s+)?(?:mi\s+)?casa|entraron\s+a\s+(?:robar\s+(?:a|en)\s+)?mi\s+casa|(?:alguien|un\s+desconocido|un\s+extraño)\s+(?:est[áa]\s+)?(?:intentando|tratando\s+de)\s+(?:abrir|forzar|entrar\s+por)\s+(?:mi\s+)?(?:la\s+)?puerta|me\s+(?:peg[óoa]|golpe[óoa]|golpea|maltrata|viol[óo])|violencia\s+(?:doméstica|domestica|de\s+género)|abus[óo]\s+de\s+m[ií]|amenaz[óa]ron\s+de\s+muerte|me\s+amenaz|me\s+quiere\s+matar|va\s+a\s+matarme|(?<!\ba\s)encerrad[oa]|me\s+tienen?\s+encerrad",
    }),
    ("disaster", "disaster", {
        "vi": r"nhà\s+(?:tôi\s+)?(?:đang\s+)?(?:bị\s+)?cháy|cháy\s+nhà|không\s+(?:ra|thoát)\s+được[^.!?\n]{0,10}(?:cháy|khói)|động\s+đất|(?<!tin\s)(?<!bản\s)lũ\s+lụt(?![^.!?\n]{0,20}nước\s+ngoài)|sóng\s+thần",
        "zh": r"地震了|地震|着火了|著火了|失火|火灾|火災|发大水|洪水|海啸|海嘯|煤气泄漏|瓦斯外洩|燃气泄漏|山体滑坡|泥石流",
        "ja": r"(?:家|部屋|建物)が燃えて|逃げられない[^。！？\n]{0,6}(?:火|煙)|(?:火|煙)[^。！？\n]{0,8}逃げられない|地震|火事|火災|洪水|浸水|津波|ガス漏れ|土砂崩れ",
        "ko": r"지진|불이\s*났|화재|홍수|침수|쓰나미|해일|가스\s*(?:가\s*)?새|산사태",
        "es": r"terremoto|sismo|incendio|se\s+est[áa]\s+quemando|inundaci[óo]n|tsunami|fuga\s+de\s+gas|huele\s+a\s+gas|deslizamiento|"
              # น้ำกำลังเข้าบ้าน/ขึ้นสูง + ออกไม่ได้ (ไม่นับน้ำรั่วจากก๊อก)
              r"(?:el\s+)?agua\b[^.!?\n]{0,20}?(?:entrando|entra|sube|subiendo|lleg[aó]|meti[ée]ndose)[^.!?\n]{0,20}?(?:casa|cuarto|habitaci[óo]n|edificio|carro|coche|calle)[^.!?\n]{0,20}?no\s+(?:podemos|puedo|pueden)\s+salir",
    }),
    # ไม่มีอาหาร — "三天没吃饭" "三日間何も食べていない" เคยได้ Risk 0 ทั้งสี่ภาษา
    ("basic", "basic", {
        "zh": r"(?:[两三四五六七]|几|好几)天没(?:有)?(?:吃饭|吃东西|饭吃)|没钱(?:吃饭|买吃的)|饿了(?:[两三四五]|好几)天",
        "ja": r"(?:[二三四五六七2-9]|何)日(?:間|も)?(?:何も)?食べて(?:い)?ない|食べるもの(?:が|も)ない|お金がなくて食べ",
        "ko": r"(?:이틀|사흘|나흘|며칠|[2-9]일)\s*(?:동안|째)?\s*(?:아무것도\s*)?(?:못|안)\s*먹|먹을\s*(?:게|것이)\s*없|돈이\s*없어서\s*(?:밥|굶)",
        "es": r"no\s+he\s+comido\s+(?:nada\s+)?(?:en|desde\s+hace)\s+(?:dos|tres|cuatro|cinco|varios|\d+)\s+d[ií]as|no\s+tengo\s+(?:nada\s+)?(?:qu[ée]\s+comer|para\s+comer|dinero\s+para\s+comer)",
    }),
    ("scam", "scam", {
        "zh": r"被骗|上当受骗|遇到诈骗|(?:冒充|自称|说是)[^。！？\n]{0,6}?(?:警察|公安|银行|检察院|法院|客服)[^。！？\n]{0,16}?(?:转账|汇款|验证码|安全账户)|(?:让我|要我)转账[^。！？\n]{0,10}?(?:警察|安全账户)|验证码[^。！？\n]{0,6}?(?:告诉|发给)|安全账户|刷单",
        "ja": r"詐欺に(?:あ|遭)|騙され|(?:警察|銀行|役所|税務署)(?:を名乗る|だと名乗る|と名乗る)[^。！？\n]{0,20}?(?:送金|振り込|暗証番号)|(?:送金|振り込み?)(?:しろ|して)と言われ|オレオレ|還付金|暗証番号を(?:教え|聞かれ)",
        "ko": r"사기\s*(?:를\s*)?당했|사기\s*당했|속아서\s*(?:돈|송금)|(?:경찰|검찰|은행|금감원)(?:이라며|이라고\s*하면서|을\s*사칭)[가-힯\s]{0,20}?(?:돈|송금|이체|계좌)|보이스\s*피싱|인증번호를?\s*(?:알려|보내)|안전\s*계좌",
        "es": r"me\s+estafaron|fui\s+v[ií]ctima\s+de\s+(?:una\s+)?estafa|(?:dice|dijo|dicen)\s+(?:ser|que\s+es)\s+(?:de\s+la\s+)?(?:polic[ií]a|banco)[^.!?\n]{0,30}?(?:transfer|dinero|c[óo]digo)|me\s+pidieron\s+(?:transferir|depositar|enviar)\s+dinero|c[óo]digo\s+de\s+verificaci[óo]n|ganaste\s+un\s+premio",
    }),
)


def _more(kind: str, lang: str, rx: str) -> None:
    """เพิ่มรูปแบบให้ URGENT_INTL (ja zh ko es vi) ทีละรอบสุ่ม — ต่อท้ายด้วย | ไม่แก้ของเดิม"""
    for k, _topic, by in URGENT_INTL:
        if k == kind:
            by[lang] = (by[lang] + "|" + rx) if by.get(lang) else rx
            return
    raise KeyError(kind)


# รอบสุ่ม 31: ภัยนอกบ้าน — แท็กซี่ล็อกประตู · ถูกใส่ยาในเครื่องดื่ม · ถูกตาม (เดิมหลุด 11/15)
_more("violence", "ja", r"(?:タクシー|運転手)[^。！？\n]{0,12}(?:ドアを?ロック|降ろしてくれない|降ろさない)")
_more("violence", "zh", r"(?:出租车|司机|網約車|网约车)[^。！？\n]{0,10}(?:把门锁|鎖門|锁门|不让我下车|不讓我下車)")
_more("violence", "ko", r"(?:택시|기사)[가-힯\s]{0,12}(?:문을?\s*(?:잠그|잠갔|잠궜)|안\s*내려\s*줘|못\s*내리게)|(?:누가|누군가|모르는\s*사람이?)\s*[가-힯\s]{0,10}계속\s*따라")
_more("violence", "es", r"(?:el\s+)?(?:taxi|taxista|conductor)\s+(?:cerr[óo]|bloque[óo])\s+(?:las\s+)?puertas|no\s+me\s+deja\s+(?:bajar|salir)\s+del\s+(?:taxi|coche|auto)")
_more("violence", "vi", r"(?:tài\s+xế|taxi)[^.!?\n]{0,15}khóa\s+cửa|không\s+cho\s+tôi\s+xuống\s+xe|(?:có\s+người|người\s+lạ)\s+(?:đi\s+)?theo\s+tôi")
_more("medical", "zh", r"(?:饮料|飲料|酒|杯子)里[^。！？\n]{0,6}(?:放了|下了|加了)[^。！？\n]{0,12}(?:晕|暈|迷糊|站不稳)")
_more("medical", "ko", r"(?:음료|술|잔)에\s*[가-힯\s]{0,6}(?:넣었|탔)[가-힯\s,]{0,16}(?:어지러|정신이|몸에\s*힘)")
_more("medical", "es", r"(?:me\s+)?(?:puso|echó|echaron|pusieron)\s+algo\s+en\s+(?:la|mi)\s+(?:bebida|copa|trago)")
_more("medical", "vi", r"bỏ\s+(?:gì\s+đó|thuốc|cái\s+gì)\s+vào\s+(?:đồ\s+uống|ly|cốc|nước)")
# รอบสุ่ม 32: เด็กถูกน้ำพัด · กลิ่นแก๊สรั่ว · ลืมเด็กไว้ในรถร้อน (เดิมหลุด 15/15)
_more("medical", "ja", r"(?:川|海|水)で?[^。！？\n]{0,6}(?:子供|子ども|息子|娘|人)が?流され|(?:赤ちゃん|子供|子ども)を(?:暑い)?車(?:の中)?に(?:置き忘れ|置いたまま|閉じ込め)")
_more("medical", "zh", r"被(?:河水|海浪|洪水|水)冲走|被(?:河水|海浪|洪水|水)沖走|把(?:宝宝|孩子|婴儿|寶寶)(?:忘|留|锁|鎖)在车里")
_more("medical", "ko", r"(?:강물|물|파도)에\s*떠내려|(?:아기|아이|애)를?\s*(?:더운\s*)?차\s*안에\s*(?:두고|놔두고|갇)")
_more("medical", "es", r"(?:la\s+corriente|el\s+río|el\s+mar|una\s+ola)\s+se\s+llev[óo]\s+a|dej[ée]\s+(?:al|a\s+mi)\s+(?:beb[ée]|hijo|hija|niñ[oa])\s+en\s+el\s+(?:coche|carro|auto)")
_more("medical", "vi", r"bị\s+nước\s+cuốn(?:\s+trôi)?|sóng\s+cuốn|bỏ\s+quên\s+(?:em\s+bé|con|bé)\s+trong\s+xe")
_more("disaster", "ja", r"ガス(?:臭い|の臭い|漏れ)")
_more("disaster", "zh", r"(?:很浓的|浓烈的|一股)?(?:煤气|燃气|瓦斯)(?:味|泄漏|洩漏)")
_more("disaster", "ko", r"가스\s*(?:냄새|누출|새)")
_more("disaster", "es", r"(?:huele|olor)\s+(?:mucho\s+)?a\s+gas|fuga\s+de\s+gas")
_more("disaster", "vi", r"mùi\s+(?:khí\s+)?gas|rò\s+rỉ\s+gas|xì\s+gas")
# รอบสุ่ม 33: เสียงสั่งให้ทำร้ายคนอื่น · หลังคลอดคิดทำร้ายลูก · อดอาหารจนจะเป็นลม (เดิมหลุด 12/15) — ต้องพบแพทย์ทันที
_more("medical", "ja", r"(?:傷つけ|殺せ|殺し)[^。！？\n]{0,6}(?:という|って)?声が(?:聞こえ|する)|(?:出産|産んで)[^。！？\n]{0,10}(?:赤ちゃん|子供|子ども)を(?:傷つけ|殺し)たい")
_more("medical", "zh", r"(?:听到|聽到)[^。！？\n]{0,4}(?:声音|聲音)[^。！？\n]{0,6}(?:叫|让|讓)我(?:伤害|傷害|杀|殺)|(?:生完孩子|产后|產後)[^。！？\n]{0,10}(?:伤害|傷害|掐死|杀)(?:宝宝|寶寶|孩子)")
_more("medical", "ko", r"(?:해치라는|죽이라는)\s*(?:목소리|소리)가?\s*들려|(?:출산|아기\s*낳고)[가-힯\s]{0,10}아기를?\s*(?:해치|죽이)고\s*싶")
_more("medical", "es", r"(?:escucho|oigo)\s+voces\s+que\s+me\s+(?:dicen|ordenan)\s+que\s+(?:lastime|mate|haga\s+daño)|(?:di\s+a\s+luz|tuve\s+al\s+beb[ée]|posparto)[^.!?\n]{0,30}(?:hacerle\s+daño|lastimar|matar)\s+(?:al|a\s+mi)\s+beb[ée]|(?:llevo\s+)?\d+\s+d[ií]as\s+sin\s+comer[^.!?\n]{0,40}(?:desmay|engordar|mareo)")
_more("medical", "vi", r"giọng\s+nói\s+(?:bảo|bắt|xúi)\s+tôi\s+(?:làm\s+hại|giết)|(?:sinh\s+con|sau\s+sinh)[^.!?\n]{0,20}(?:làm\s+hại|giết)\s+(?:em\s+bé|con|bé)|\d+\s+ngày[^.!?\n]{0,12}không\s+ăn[^.!?\n]{0,30}(?:ngất|sợ\s+béo|chóng\s+mặt)")
# รอบสุ่ม 34: ค้ามนุษย์ — ยึดพาสปอร์ต · ขังในหอ+ยึดโทรศัพท์ · บังคับค้าประเวณีใช้หนี้ (เดิมหลุด 12/15)
_more("violence", "ja", r"パスポートを(?:取り上げ|奪わ|没収)[^。！？\n]{0,12}(?:帰らせ|帰れ|出られ)|(?:売春|売り)を(?:強要|させられ)")
_more("violence", "zh", r"(?:锁|鎖|关|關)在(?:宿舍|房间|房間)[^。！？\n]{0,10}(?:收走|没收|沒收|拿走)(?:了)?(?:手机|手機)|(?:被逼|被迫|逼我)(?:卖淫|賣淫|卖身|賣身|接客)")
_more("violence", "ko", r"여권을?\s*(?:뺏|빼앗|가져가)[가-힯\s]{0,10}(?:못\s*가|못\s*나가|안\s*보내)|(?:기숙사|방)에\s*가두고[가-힯\s]{0,10}(?:핸드폰|휴대폰|폰)을?\s*뺏|성매매를?\s*강요")
_more("violence", "es", r"(?:me\s+)?quit[óo]\s+(?:el|mi)\s+pasaporte[^.!?\n]{0,30}no\s+me\s+deja|nos\s+encierran[^.!?\n]{0,40}(?:quitan|quitaron)\s+(?:los\s+)?(?:tel[ée]fonos|celulares|m[óo]viles)|me\s+obligan\s+a\s+prostituirme")
_more("violence", "vi", r"nhốt\s+(?:chúng\s+tôi|tôi)[^.!?\n]{0,30}(?:lấy|thu)\s+(?:điện\s+thoại|hộ\s+chiếu)|bị\s+ép\s+(?:bán\s+dâm|tiếp\s+khách|làm\s+gái)")
# รอบสุ่ม 35: พ่อแม่เล่าเรื่องลูก — ทำร้ายตัวเอง · ผู้ใหญ่ขอรูปโป๊ · นัดเจอผู้ใหญ่จากเน็ต (เดิมหลุด 15/15)
_more("someone", "ja", r"(?:子供|子ども|娘|息子)が[^。！？\n]{0,6}(?:自分の)?(?:腕|手首)を切っ")
_more("someone", "zh", r"(?:孩子|女儿|儿子|女兒|兒子)[^。！？\n]{0,6}(?:割伤|割傷|割)(?:自己|手臂|手腕)")
_more("someone", "ko", r"(?:아이|애|딸|아들)가?\s*(?:팔|손목)에\s*(?:상처를\s*내|칼로\s*긋)")
_more("someone", "es", r"mi\s+(?:hija|hijo)\s+se\s+(?:corta|está\s+cortando)\s+(?:los\s+)?(?:brazos|muñecas)")
_more("someone", "vi", r"(?:con\s+(?:gái|trai)|con)\s+(?:tôi\s+)?tự\s+(?:rạch|cắt)\s+tay")
_more("violence", "ja", r"(?:知らない)?大人が[^。！？\n]{0,10}裸の(?:写真|画像)を(?:求め|要求|送れ)|(?:\d{1,2}歳の)?(?:娘|息子)がネットで知り合った大人と[^。！？\n]{0,6}会う")
_more("violence", "zh", r"(?:陌生)?(?:大人|成年人)[^。！？\n]{0,10}(?:要|索要)裸照|(?:\d{1,2}岁)?(?:女儿|儿子)[^。！？\n]{0,6}(?:要)?(?:见|見)网上认识的(?:成年人|大人)")
_more("violence", "ko", r"(?:모르는\s*)?어른이?\s*[가-힯\s]{0,10}(?:알몸|나체|야한)\s*사진을?\s*(?:달래|보내라|요구)|인터넷에서\s*만난\s*어른을?\s*[가-힯\s]{0,6}만난")
_more("violence", "es", r"(?:un\s+)?adulto[^.!?\n]{0,30}(?:pidi[óo]|pide)\s+fotos\s+desnud|(?:va\s+a\s+ver|se\s+va\s+a\s+ver\s+con)[^.!?\n]{0,20}(?:un\s+)?adulto\s+que\s+conoci[óo]\s+en\s+internet")
_more("violence", "vi", r"đòi\s+ảnh\s+(?:khỏa\s+thân|nóng|nude)|đi\s+gặp\s+người\s+lớn\s+quen\s+trên\s+mạng")
# รอบสุ่ม 41: ผู้สูงอายุล้มลุกไม่ได้ · เบาหวานซึม · ผู้ป่วยสมองเสื่อมหาย (เดิมหลุด 14/15) — โทรขอความช่วยเหลือทันที
_more("medical", "ja", r"倒れて起き上がれない|糖尿病[^。！？\n]{0,12}(?:汗|ぼんやり|意識|返事がない)|認知症の[^。！？\n]{0,6}(?:祖父|祖母|父|母|人)が[^。！？\n]{0,10}(?:帰ってこない|いなくなっ|行方不明)")
_more("medical", "zh", r"摔倒(?:了)?起不来|摔倒(?:了)?起不來|糖尿病[^。！？\n]{0,10}(?:出汗|迷糊|叫不(?:太)?应|叫不醒)|(?:老年痴呆|失智|痴呆)[^。！？\n]{0,12}(?:没回来|沒回來|走丢|走失|不见了)")
_more("medical", "ko", r"넘어져서?\s*못\s*일어나|당뇨[가-힯\s]{0,12}(?:땀|멍하|대답을?\s*(?:잘\s*)?안|의식)|치매[가-힯\s]{0,24}(?:안\s*돌아|없어졌|실종|길을\s*잃)")
_more("medical", "es", r"se\s+cay[óo][^.!?\n]{0,20}no\s+puede\s+levantarse|con\s+demencia[^.!?\n]{0,30}(?:no\s+ha\s+vuelto|desapareci[óo]|se\s+perdi[óo])")
_more("medical", "vi", r"ngã[^.!?\n]{0,15}không\s+dậy\s+được|tiểu\s+đường[^.!?\n]{0,20}(?:vã\s+mồ\s+hôi|lơ\s+mơ|không\s+trả\s+lời)|bị\s+lẫn[^.!?\n]{0,15}(?:chưa\s+về|mất\s+tích|đi\s+lạc)")
# รอบสุ่ม 42: ติดอยู่ในน้ำท่วม/ดินถล่ม (zh es vi)
_more("disaster", "zh", r"(?:水|洪水)[^。！？\n]{0,6}(?:淹到|到了)(?:胸口|脖子|腰)|被困在(?:楼上|屋顶|屋頂|二楼)")
_more("disaster", "es", r"el\s+agua\s+(?:nos|me)\s+llega\s+(?:al|a\s+la)\s+(?:pecho|cuello|cintura)|atrapad[oa]s?\s+(?:arriba|en\s+el\s+techo|en\s+el\s+segundo\s+piso)|(?:deslave|derrumbe|alud)\s+(?:sepult[óo]|enterr[óo])")
_more("disaster", "vi", r"nước\s+ngập\s+(?:tới|đến)\s+(?:ngực|cổ|bụng)|bị\s+kẹt\s+trên\s+(?:lầu|mái|tầng)|sạt\s+lở[^.!?\n]{0,20}(?:vùi|chôn|lấp)")
# รอบสุ่ม 43: ชนคนแล้วไม่ขยับ · ตกแล้วขาไม่รู้สึก · นิ้วขาด (เดิมหลุด 15/15)
_more("medical", "ja", r"(?:歩行者|人)を(?:はねた|轢いた|ひいた)|(?:足|脚)の感覚がない|指を切り(?:落と|落とし)|指が(?:ちぎれ|取れ)")
_more("medical", "zh", r"撞(?:到|倒)(?:了)?(?:行人|人)[^。！？\n]{0,8}(?:一动不动|不动|昏迷|流血)|(?:腿|脚|下半身)没有知觉|(?:锯|切|剁)断(?:了)?(?:手指|指头)|手指(?:被)?(?:锯|切|剁)断")
_more("medical", "ko", r"(?:보행자|사람)를?\s*쳤어[가-힯\s,]{0,8}(?:안\s*움직|의식)|다리에\s*감각이\s*없|손가락이\s*잘렸")
_more("medical", "es", r"atropell[ée]\s+a\s+(?:un|una)\s+(?:peat[óo]n|persona)|no\s+siento\s+las\s+piernas|(?:me\s+)?cort[ée]\s+(?:un|el)\s+dedo[^.!?\n]{0,20}(?:desprendi|cay[óo]|separ)|dedo\s+amputado")
_more("medical", "vi", r"tông\s+(?:phải\s+)?người\s+đi\s+bộ|không\s+cảm\s+(?:thấy|giác)\s+(?:được\s+)?chân|(?:cưa|chặt|cắt)\s+đứt\s+ngón\s+tay")
# รอบสุ่ม 44: ยาเกินขนาด/ยาซ้ำ — เด็กดื่มยาทั้งขวด · เหล้า+ยานอนหลับ · ยาความดันซ้ำ (เดิมหลุด 12/15)
_more("medical", "ja", r"(?:一本|一瓶|まるごと)\s*全部飲んだ|(?:シロップ|薬)を[^。！？\n]{0,4}全部飲んだ|薬を二回飲んだ[^。！？\n]{0,12}(?:めまい|脈が遅|ふらふら)")
_more("medical", "zh", r"(?:一整瓶|整瓶|一瓶)[^。！？\n]{0,10}(?:糖浆|糖漿|药|藥)(?:都)?喝了|把[^。！？\n]{0,4}一整瓶[^。！？\n]{0,10}喝了")
_more("medical", "ko", r"한\s*병\s*다\s*마셨|술\s*마시고\s*수면제[가-힯\s]{0,12}(?:숨을?\s*(?:너무\s*)?천천히|안\s*깨|의식)|혈압약을?\s*두\s*번[가-힯\s,]{0,12}(?:어지럽|맥박이?\s*느려)")
_more("medical", "es", r"(?:se\s+)?(?:tom[óo]|bebi[óo])\s+todo\s+el\s+frasco|alcohol\s+y\s+(?:luego\s+)?pastillas\s+para\s+dormir[^.!?\n]{0,20}(?:respir|no\s+despiert)|(?:pastilla|medicina)\s+(?:de\s+la\s+presi[óo]n\s+)?dos\s+veces[^.!?\n]{0,30}(?:marea|pulso\s+lento|desmay)")
_more("medical", "vi", r"uống\s+hết\s+cả\s+(?:chai|lọ|vỉ)|uống\s+rượu\s+rồi\s+uống\s+thuốc\s+ngủ|thuốc\s+huyết\s+áp\s+hai\s+lần[^.!?\n]{0,20}(?:chóng\s+mặt|mạch\s+chậm|ngất)")
# รอบสุ่ม 47: อุบัติเหตุในที่ทำงาน — ตกนั่งร้าน · เครนล้มทับ · เครื่องจักรดูดแขน (เดิมหลุด 14/15)
_more("medical", "ja", r"足場から落ち|(?:屋根|高所)から落ち|機械に[^。！？\n]{0,8}(?:腕|手|指|髪)が?巻き込まれ")
_more("medical", "zh", r"从脚手架上?摔|從鷹架上?摔|(?:吊车|吊車|起重机|起重機)[^。！？\n]{0,6}(?:倒|塌)[^。！？\n]{0,6}压(?:到|住)?人|(?:机器|機器)[^。！？\n]{0,6}(?:手臂|手|胳膊)(?:卷|捲)进去")
_more("medical", "ko", r"비계에서\s*떨어|크레인이\s*[가-힯\s]{0,8}(?:넘어졌|쓰러졌|덮쳤)|기계에\s*[가-힯\s]{0,8}(?:팔|손|손가락)이?\s*말려")
_more("medical", "es", r"se\s+cay[óo]\s+del\s+andamio|(?:la\s+)?gr[úu]a\s+(?:se\s+)?cay[óo]\s+(?:encima\s+de|sobre)|m[áa]quina\s+(?:atrap[óo]|agarr[óo]|jal[óo])\s+(?:el\s+)?(?:brazo|mano)")
_more("medical", "vi", r"ngã\s+từ\s+giàn\s+giáo|cần\s+cẩu\s+đổ\s+đè|máy\s+cuốn\s+(?:tay|cánh\s+tay)")
# รอบสุ่ม 48: ครรภ์เป็นพิษ · ทารกไม่กี่สัปดาห์มีไข้ · ตกเลือดหลังคลอด (เดิมหลุด 15/15)
_more("medical", "ja", r"妊娠\s*\d+\s*(?:ヶ月|か月|カ月|週)[^。！？\n]{0,30}(?:ひどい頭痛|頭痛|目がかすむ|出血)|生後\s*\d+\s*(?:週間?|日|ヶ月)[^。！？\n]{0,20}(?:熱|発熱)|出産後[^。！？\n]{0,20}(?:びっしょり|大量出血|1時間ごと)")
_more("medical", "zh", r"(?:怀孕|懷孕)\s*\d+\s*(?:个月|個月|周|週)[^。！？\n]{0,30}(?:头很痛|頭很痛|头痛|頭痛|模糊|出血)|(?:两|兩|\d+)(?:周|週)大的(?:宝宝|寶寶|婴儿|嬰兒)[^。！？\n]{0,8}(?:发烧|發燒)|(?:产后|產後)[^。！？\n]{0,20}(?:湿透|濕透|大出血)")
_more("medical", "ko", r"임신\s*\d+\s*(?:개월|주)[가-힯\s,]{0,30}(?:두통|침침|출혈)|생후\s*\d+\s*(?:주|일)[가-힯\s]{0,12}열|출산\s*후[가-힯\s]{0,20}(?:흠뻑|출혈)")
_more("medical", "es", r"\d+\s+(?:meses|semanas)\s+de\s+embarazo[^.!?\n]{0,40}(?:dolor\s+de\s+cabeza|visi[óo]n\s+borrosa|sangr)|beb[ée]\s+de\s+\d+\s+(?:semanas|d[ií]as)[^.!?\n]{0,20}fiebre|despu[ée]s\s+del\s+parto[^.!?\n]{0,30}(?:empap|sangr)")
_more("medical", "vi", r"mang\s+thai\s+\d+\s+(?:tháng|tuần)[^.!?\n]{0,40}(?:đau\s+đầu|mờ\s+mắt|chảy\s+máu)|\d+\s+(?:tuần|ngày)\s+tuổi[^.!?\n]{0,20}sốt|sau\s+sinh[^.!?\n]{0,30}(?:thấm\s+đẫm|ra\s+máu\s+nhiều|băng\s+huyết)")
# รอบสุ่ม 74: คนใกล้ตัวส่งสัญญาณบอกลา (รูปยาเต็มมือ+ลาก่อน · ขังตัวเองแล้วเงียบ) — เดิมหลุด 10/10
_more("someone", "ja", r"薬を手にいっぱい[^。！？\n]{0,20}(?:さようなら|さよなら|バイバイ)|(?:部屋|トイレ)に閉じこも[^。！？\n]{0,20}(?:静かになった|返事がない|音がしない)")
_more("someone", "zh", r"(?:满是药|一把药|满手的药)[^。！？\n]{0,12}(?:再见|再見|永别)|锁在房间里[^。！？\n]{0,20}(?:没声音|沒聲音|不回应|不回應)|鎖在房間裡[^。！？\n]{0,20}沒聲音")
_more("someone", "ko", r"약을?\s*잔뜩[^.!?\n]{0,20}(?:안녕|잘\s*있어)|방에\s*(?:틀어박|갇혀|문\s*잠그)[가-힯\s,]{0,20}(?:조용해|대답이\s*없|소리가\s*안)")
_more("someone", "es", r"(?:foto|imagen)\s+con\s+(?:pastillas|pastillas\s+en\s+la\s+mano)[^.!?\n]{0,20}adi[óo]s|se\s+encerr[óo]\s+en\s+su\s+(?:cuarto|ba[ñn]o)[^.!?\n]{0,40}(?:silencio|no\s+responde|no\s+contesta)")
_more("someone", "vi", r"cầm\s+đầy\s+thuốc[^.!?\n]{0,15}tạm\s+biệt|tự\s+nhốt\s+mình\s+trong\s+phòng[^.!?\n]{0,30}(?:im\s+lặng|không\s+trả\s+lời)")
# รอบสุ่ม 77: ข้างบ้านกรีดร้องให้ช่วย + เสียงทำร้าย (ผู้ใช้เห็นเหตุ) — เดิมหลุด 9/9
_more("violence", "ja", r"(?:隣|隣の部屋|隣の家)[^。！？\n]{0,12}助けてと叫[^。！？\n]{0,12}(?:叩く|殴る|物が割れる)音")
_more("violence", "zh", r"邻居[^。！？\n]{0,8}(?:喊救命|呼救)[^。！？\n]{0,10}(?:打人|打|摔东西)的?声音|鄰居[^。！？\n]{0,8}(?:喊救命|呼救)")
_more("violence", "ko", r"옆집에서\s*[가-힯\s]{0,10}살려\s*달라고[가-힯\s]{0,15}때리는\s*소리")
_more("violence", "es", r"(?:la\s+vecina|el\s+vecino|los\s+vecinos)\s+grita[^.!?\n]{0,20}(?:ayuda|auxilio)[^.!?\n]{0,25}(?:golpes|pegando)")
_more("violence", "vi", r"nhà\s+bên[^.!?\n]{0,20}kêu\s+cứu[^.!?\n]{0,20}(?:tiếng\s+đánh|đập)")
# รอบสุ่ม 79: หลงในภูเขาตอนมืดไม่มีน้ำ · ลูกหายในที่คนเยอะ (เดิมหลุด 10/10) — โทรขอความช่วยเหลือทันที
_more("medical", "ja", r"山で道に迷っ[^。！？\n]{0,20}(?:暗く|水も?ない|寒い)|(?:人混み|モール|駅|空港)[^。！？\n]{0,15}(?:子供|子ども|息子|娘)がいなくなっ")
_more("medical", "zh", r"在山上迷路[^。！？\n]{0,15}(?:天黑|没水|沒水|很冷)|(?:商场|商場|人多|车站|機場|机场)[^。！？\n]{0,10}(?:孩子|儿子|女儿)走丢")
_more("medical", "ko", r"산에서\s*길을\s*잃[가-힯\s,]{0,20}(?:어두워|물도\s*없|추워)|(?:쇼핑몰|사람\s*많은|역|공항)[가-힯\s]{0,12}아이를?\s*잃어버렸")
_more("medical", "es", r"me\s+perd[íi]\s+en\s+la\s+monta[ñn]a[^.!?\n]{0,30}(?:oscureci|no\s+tengo\s+agua|fr[íi]o)|perd[íi]\s+a\s+mi\s+(?:hijo|hija|niñ[oa])\s+en\s+(?:un|el)\s+(?:centro\s+comercial|mercado|aeropuerto|parque)")
_more("medical", "vi", r"bị\s+lạc\s+trên\s+núi[^.!?\n]{0,25}(?:trời\s+tối|hết\s+nước|lạnh)|con\s+(?:tôi\s+)?bị\s+lạc\s+(?:trong|ở)\s+(?:trung\s+tâm\s+thương\s+mại|chợ|sân\s+bay|công\s+viên)")
# รอบสุ่ม 83: หอบหืดกำเริบที่ยาไม่ช่วย · อาหารติดคอ (zh) — เดิมหลุด 6/10
_more("medical", "ja", r"(?:喘息|ぜんそく)[^。！？\n]{0,10}(?:吸入薬|薬)が効かない|数語しか話せない")
_more("medical", "zh", r"哮喘[^。！？\n]{0,10}(?:喷了药|吸了药)?[^。！？\n]{0,6}(?:也)?没用|只能说几个字|噎住[^。！？\n]{0,10}(?:咳不出|脸发紫|臉發紫|喘不过气)")
_more("medical", "ko", r"천식[가-힯\s,]{0,12}흡입기가?\s*안\s*들|몇\s*마디밖에\s*못")
_more("medical", "es", r"(?:ataque\s+de\s+)?asma[^.!?\n]{0,20}inhalador\s+no\s+(?:funciona|sirve|ayuda)|solo\s+puedo\s+decir\s+unas\s+palabras")
_more("medical", "vi", r"(?:cơn\s+)?hen[^.!?\n]{0,15}xịt\s+thuốc\s+không\s+đỡ|chỉ\s+nói\s+được\s+vài\s+từ")
# รอบสุ่ม 86: คนใกล้ตัวเก็บยาไว้ "วันที่ไม่ไหว" · แฟนเคยขู่ฆ่าตัวตายถ้าเลิก แล้วเพิ่งบอกเลิก (เดิมหลุด 8/10)
_more("someone", "ja", r"薬を(?:たくさん)?(?:溜め|ためて|集め)[^。！？\n]{0,15}(?:限界|耐えられない|もう無理)|(?:限界|耐えられない)[^。！？\n]{0,15}薬を(?:たくさん)?(?:溜め|ため|集め)|別れたら死ぬ[^。！？\n]{0,20}(?:別れを告げ|別れた|振った)")
_more("someone", "zh", r"存了(?:很多|好多)?药[^。！？\n]{0,15}(?:撑不下去|受不了|不想活)")
_more("someone", "ko", r"(?:못\s*버틸|힘든)\s*날을?\s*위해\s*약을?\s*(?:모아|모았|쌓아)|헤어지면\s*죽겠다고[가-힯\s,]{0,25}헤어지자고")
_more("someone", "es", r"guarda\s+pastillas\s+para\s+el\s+d[íi]a\s+que|(?:dijo|dec[íi]a)\s+que\s+se\s+matar[íi]a\s+si[^.!?\n]{0,40}(?:termin[ée]|lo\s+dej[ée]|la\s+dej[ée])")
_more("someone", "vi", r"tích\s+(?:nhiều\s+)?thuốc[^.!?\n]{0,20}(?:không\s+chịu\s+nổi|không\s+muốn\s+sống)")
# ภาษาอื่นของเว็บ (หลังรอบสุ่ม DriftZero): คนแปลกหน้าทุบประตูตอนดึก · สามีทำร้ายทุกคืน · เด็กกลืนถ่าน · แม่ล้มลุกไม่ได้
# ฉบับไทย/อังกฤษจับได้แล้ว (รอบ 99) แต่ es vi zh ko ja หลุด 9 จาก 20
_more("violence", "es", r"(?:alguien|un\s+desconocido|un\s+extraño|un\s+hombre)\s+(?:está\s+)?(?:golpeando|aporreando|pateando|forzando)\s+(?:mi|la)\s+puerta[^.!?\n]{0,30}(?:\d\s*(?:am|de\s+la\s+madrugada)|madrugada|noche|ahora)")
_more("violence", "vi", r"(?:có\s+người\s+lạ|người\s+lạ|ai\s+đó)\s+(?:đang\s+)?(?:đập|gõ\s+mạnh|phá|đạp)\s+cửa[^.!?\n]{0,30}(?:giờ\s+sáng|nửa\s+đêm|ban\s+đêm|bây\s+giờ)")
_more("violence", "zh", r"(?:半夜|深夜|凌晨)[^。！？\n]{0,10}(?:陌生人|有人)[^。！？\n]{0,6}(?:砸|踹|撬|拼命敲)[^。！？\n]{0,4}门|(?:老公|丈夫|男朋友|老婆)[^。！？\n]{0,8}(?:每天|天天|每晚|每天晚上|经常)[^。！？\n]{0,4}(?:打我|揍我|家暴)")
_more("violence", "ko", r"(?:새벽|한밤중|밤에)[가-힯\s\d시]{0,12}(?:모르는\s*사람|낯선\s*사람|누군가)[가-힯\s]{0,8}(?:문을?\s*(?:두드려|두들겨|부수|발로\s*차|따려))")
_more("violence", "ja", r"(?:夜中|深夜|真夜中)[^。！？\n]{0,10}(?:知らない人|誰か|見知らぬ人)[^。！？\n]{0,8}(?:ドア|玄関)[^。！？\n]{0,4}(?:叩い|叩か|蹴|壊そう)|(?:夫|旦那|彼氏|妻)[^。！？\n]{0,6}(?:毎晩|毎日|いつも)[^。！？\n]{0,6}(?:殴|叩い|蹴)")
_more("medical", "vi", r"(?:con|bé|cháu)\s+(?:tôi\s+|mình\s+)?(?:nuốt|nuốt\s+phải)\s+(?:viên\s+)?pin")
_more("medical", "ja", r"(?:母|父|祖母|祖父|おばあちゃん|おじいちゃん)[^。！？\n]{0,6}(?:転んで|倒れて)[^。！？\n]{0,6}(?:起き上がれない|立てない|動けない)")

# ── เทียบ 7 ภาษาด้วยเรื่องเดียวกัน 8 เรื่อง (2026-11): ไทย/อังกฤษจับได้ 16/16 แต่ es vi zh ko ja ได้ 21/40
# ทุกข้อที่หลุดได้ Risk 0 และคำตอบไม่มีเบอร์ฉุกเฉินเลย — เช่นคนเกาหลีพิมพ์ "ลูกสองขวบดื่มน้ำยาล้างห้องน้ำ" ได้คำตอบคุยทั่วไป
# เขียนตาม "ความหมาย" ไม่ใช่ตามประโยคทดสอบ: (กริยา ทุกบุคคล) + (คำคั่นได้) + (สิ่งที่บอกว่าอันตราย)
# ข้อที่แก้อยู่ใน tests/corpus/messages.tsv (หมวด ภาษาอื่น:เทียบ7ภาษา) · ชุดที่เขียนหลังแก้และไม่ได้จูนตามอยู่ใน tests/blind/blind.tsv
# กินยาเกินขนาด — เดิม es มีแค่ "se tomó" (เขา) ไม่มี "me tomé" (ฉัน) · zh มีแค่ 吃 ไม่มี 吞/服 · ko ต้องมี 약을 ติดกัน
_more("medical", "es", r"\b(?:me\s+)?(?:tom|trag|beb)\w*\b[^.!?\n]{0,25}?\b(?:frasco|caja|bote|bl[íi]ster|tira|todas?\s+las|un\s+mont[óo]n\s+de|un\s+pu[ñn]ado\s+de|much[ao]s)\b"
                      r"[^.!?\n]{0,20}?\b(?:pastillas|p[íi]ldoras|medicamentos?|medicinas?|somn[íi]feros|ansiol[íi]ticos|calmantes|analg[ée]sicos|paracetamol|ibuprofeno)\b")
_more("medical", "zh", r"(?<!不要)(?<!别)(?<!別)(?:吞|吃|服|喝)(?:了|下|掉)?[^。！？\n]{0,4}?(?:一整瓶|整瓶|一瓶|一大把|一把|好多|很多|大量|一整盒|整盒|一盒|全部|所有|几十[颗粒片])(?:的)?[^。！？\n]{0,4}?"
                      r"(?:药|藥|安眠药|安眠藥|药片|藥片|止痛药|止痛藥|退烧药|退燒藥|镇静剂|鎮靜劑)")
_more("medical", "ko", r"(?:수면제|약|진통제|알약|타이레놀|신경안정제|해열제|우울증\s*약)[을를]?\s*(?:한\s*(?:통|병|봉지|상자|갑|움큼)|통째로|전부|다|많이)[가-힯\s]{0,4}?(?:을|를)?\s*(?:다\s*)?(?:먹었|삼켰|털어\s*넣|먹어\s*버렸|삼켜\s*버렸)")
_more("medical", "ja", r"(?:睡眠薬|薬|錠剤|風邪薬|鎮痛剤|精神安定剤|解熱剤)を?[^。！？\n]{0,4}?(?:一瓶|ひと瓶|一箱|ひと箱|丸ごと|一シート|全部|大量に?|たくさん)[^。！？\n]{0,4}?(?:飲ん|飲み込ん|飲みこん)")
# ดื่ม/กลืนสารเคมีในบ้าน — เดิม zh ko ja ต้องขึ้นต้นด้วย "ลูก/เด็ก" และรู้จักไม่กี่ชนิด · ผู้ใหญ่ดื่มก็อันตรายเท่ากัน จึงไม่จำกัดว่าใคร
_more("medical", "es", r"\b(?:bebi[óo]|beb[íi]|tom[óo]|tom[ée]|trag[óo]|tragu[ée]|se\s+(?:bebi[óo]|tom[óo]|trag[óo]))\s+(?:un\s+poco\s+de\s+|algo\s+de\s+|del?\s+|el\s+|la\s+)?"
                      r"(?:limpiador|desinfectante|desatascador|destapacaños|amon[íi]aco|cloro|lej[íi]a|detergente|suavizante|raticida|veneno\s+para\s+ratas|insecticida|pesticida|herbicida|gasolina|queroseno|aguarr[áa]s|soda\s+c[áa]ustica|anticongelante)")
_more("medical", "zh", r"(?<!不要)(?<!别)(?<!別)(?<!防止)(?<!避免)(?:喝|吃|吞|舔)(?:了|下|到)?(?:一?[口点點些])?[^。！？\n]{0,6}?"
                      r"(?:清洁剂|清潔劑|洁厕|潔廁|马桶清洁|馬桶清潔|洗洁精|洗潔精|消毒液|消毒水|漂白水|漂白剂|漂白劑|农药|農藥|杀虫剂|殺蟲劑|老鼠药|老鼠藥|鼠药|除草剂|百草枯|汽油|煤油|洗衣液|洗衣凝珠|防冻液)")
_more("medical", "ko", r"(?:세제|세정제|락스|표백제|농약|살충제|제초제|쥐약|부동액|휘발유|등유|소독약|소독제|유연제|캡슐\s*세제)[을를]?\s*(?:조금\s*|좀\s*|한\s*모금\s*)?(?:마셨|먹었|삼켰|핥았|마셔\s*버렸|먹어\s*버렸)")
_more("medical", "ja", r"(?:洗剤|漂白剤|ハイター|カビキラー|洗浄剤|殺虫剤|農薬|除草剤|灯油|ガソリン|防虫剤|消毒液|柔軟剤|ジェルボール|不凍液)を?[^。！？\n]{0,4}?(?:飲ん|飲み込ん|飲みこん|口に入れ|なめ|舐め|食べ)(?:だ|で|て|た|ちゃ|しまっ)")
# ไม่นับเรื่องแต่ง: ทั้งประโยคต้องไม่มีคำว่าหนัง/ฉาก/ซีรีส์/เกม/นิยาย — ชุดตรวจซ้ำเจอ "ฉากเลือดพุ่งในหนัง" ถูกตัดสินว่าวิกฤต 4 ภาษา
# ใช้ (?:^|(?<=จบประโยค)) ยึดต้นประโยค แล้วดูทั้งประโยค — lookahead ธรรมดามองไม่เห็นคำที่อยู่ก่อน ("映画で血が…")
_FICTION = {"es": r"pel[íi]cula|serie|escena|videojuego|juego|novela|libro|anime|cap[íi]tulo|tr[áa]iler|cine",
            "vi": r"phim|cảnh\s+(?:quay|phim|này)|truyện|game|trò\s+chơi|tiểu\s+thuyết|anime",
            "zh": r"电影|電影|镜头|鏡頭|电视剧|電視劇|剧里|劇裡|剧情|劇情|游戏|遊戲|小说|小說|动漫|動漫|场景|場景|画面|畫面",
            "ko": r"영화|장면|드라마|게임|소설|웹툰|애니|만화",
            "ja": r"映画|シーン|ドラマ|ゲーム|小説|漫画|マンガ|アニメ|場面|話|ニュース"}


def _real(lang: str, rx: str) -> str:
    return r"(?:^|(?<=[.!?。！？\n]))(?![^.!?。！？\n]*(?:" + _FICTION[lang] + r"))[^.!?。！？\n]*?(?:" + rx + r")"


# เลือดออกไม่หยุด — เดิมต้องเป็นวลีติดกันพอดี ("出血が止まらない" "피가 멈추지 않") มีคำคั่นกลางก็หลุด
_more("medical", "es", _real("es", r"\bsangr(?:e|a|ando)\b[^.!?\n]{0,30}?\b(?:a\s+chorros|chorrea|brota|no\s+(?:para|se\s+detiene|deja\s+de\s+salir|se\s+para)|sin\s+parar)|\bno\s+(?:para|deja)\s+de\s+sangrar"))
_more("medical", "vi", _real("vi", r"máu\s+(?:phun|chảy|tuôn|ra)[^.!?\n]{0,20}?(?:không\s+(?:ngừng|cầm\s+được|dừng)|mãi\s+không\s+cầm|xối\s+xả|thành\s+tia)|chảy\s+máu\s+(?:không\s+(?:ngừng|cầm\s+được|dừng)|quá\s+nhiều)|cầm\s+máu\s+không\s+được|không\s+cầm\s+(?:được\s+)?máu"))
_more("medical", "zh", _real("zh", r"血[^。！？\n]{0,6}?(?:喷|噴|涌|湧|冒|流)(?:出来|出來|个不停|個不停|不止)?[^。！？\n]{0,6}?(?:止不住|停不下来|停不下來|不停|不止)|血止不住|止不住(?:血|地流血)"))
_more("medical", "ko", _real("ko", r"피가\s*[가-힯\s]{0,15}?(?:멈추지\s*않|안\s*멈추|안\s*멈춰|계속\s*(?:나|흘러|흐르)|뿜어져|솟구|철철)|출혈이\s*[가-힯\s]{0,8}?(?:심해|멈추지|안\s*멈)|지혈이\s*안"))
_more("medical", "ja", _real("ja", r"血が[^。！？\n]{0,12}?(?:噴き出|吹き出|噴出|止まらな|ドクドク|あふれ|溢れ)|出血が[^。！？\n]{0,8}?(?:止まらな|ひどい)"))
# อาการหัวใจ — เดิมต้องมี "เจ็บหน้าอก" ติดกันพอดี ("đau thắt ngực" "가슴이 짓눌리듯 아프" "胸が締め付けられるように痛" หลุด)
_more("medical", "vi", _real("vi", r"(?:đau\s+(?:thắt\s+|tức\s+|nhói\s+)?ngực|tức\s+ngực)[^.!?\n]{0,30}(?:lan|tay\s+trái|vã\s+mồ\s+hôi|đổ\s+mồ\s+hôi|mồ\s+hôi\s+lạnh|khó\s+thở)"))
_more("medical", "ko", _real("ko", r"가슴이?\s*[가-힯\s]{0,10}?(?:아프|아파|조이|조여|짓눌|쥐어짜)[가-힯\s]{0,20}?(?:식은땀|땀이|왼팔|왼쪽\s*팔|숨이|턱까지)"))
_more("medical", "ja", _real("ja", r"胸が?[^。！？\n]{0,12}?(?:痛|苦し|締め付け|しめつけ|圧迫|押しつぶ)[^。！？\n]{0,20}?(?:冷や汗|汗|左腕|左肩|顎|息が)"))
# ถูกทำร้าย/กักขังในบ้าน (ko) — เดิมรู้จักแค่ "때려요/때렸어" และ "갇혀 있" · ไม่นับตียุง/แมลง/กลอง
_more("violence", "ko", r"(?:남편|아내|남자\s*친구|여자\s*친구|남친|여친|애인|아빠|엄마|오빠|형|시어머니|시아버지|그\s*사람)(?:이|가|은|는)?\s*(?:(?!모기|파리|벌레|공을|북을|드럼)[가-힯\s]){0,10}?(?:때리|때려|때렸|폭행|발로\s*차|목을\s*조)"
                        r"|(?:저를|나를|날|절)\s*(?:방에\s*|집에\s*)?(?:가둬|가두|가뒀|감금)|(?:방|집|창고|지하실)에\s*(?:저를|나를|날)?\s*(?:가둬|가두|가뒀)")
# ยึดพาสปอร์ต/ขัง (es ko) — สัญญาณค้ามนุษย์/แรงงานบังคับ · ไม่นับ "โรงแรมเก็บพาสปอร์ต" (เรื่องปกติในหลายประเทศ) จึงไม่ใช้ tiene/guarda
_more("violence", "es", r"\b(?:me\s+)?(?:quit[óoa]|quitaron|retiene|retienen|confisc[óoa]|confiscaron|no\s+me\s+(?:devuelve|devuelven|quiere\s+devolver))\s+(?:mi\s+|el\s+)?pasaporte|\bme\s+(?:encierra|encierran|encerr[óo]|encerraron)\b")
_more("violence", "ko", r"여권(?:을|를)?\s*(?:빼앗|뺏|가져가|압수|안\s*돌려|돌려주지\s*않)")
# ชุดตรวจซ้ำยังหลุด: vi กลืนยาทั้งแผง · vi แฟนตี/ขู่ฆ่า · zh "收走了护照" "把我们关起来"
# vi "con" เป็นทั้ง "ลูก" และลักษณนามสัตว์ ("đánh con muỗi" = ตียุง) — ไม่นับเมื่อตามด้วยชื่อสัตว์
_more("medical", "vi", r"(?:uống|nuốt)\s+(?:hết\s+|cả\s+|nguyên\s+|một\s+)?(?:vỉ|lọ|hộp|chai|nắm|vốc)\s+thuốc|(?:uống|nuốt)\s+(?:rất\s+)?nhiều\s+thuốc\s+(?:ngủ|an\s+thần)")
_more("violence", "vi", r"(?:chồng|vợ|bạn\s+trai|bạn\s+gái|người\s+yêu|bố|mẹ|cha|anh\s+ta|hắn)\s+(?:lại\s+|hay\s+|thường\s+|luôn\s+|cứ\s+)?(?:đánh|đập|tát|đá|bóp\s+cổ)\s+(?:tôi|mình|em|con\b(?!\s+(?:muỗi|ruồi|gián|chuột|cá|gà|chó|mèo)))"
                        r"|(?:đe\s+)?dọa\s+giết\s+(?:tôi|mình|em|con)\b")
_more("violence", "zh", r"(?:收走|拿走|没收|沒收|扣下|扣着|扣著)(?:了)?(?:我们|我們|我|大家)?的?(?:护照|護照)|把(?:我|我们|我們)(?:关|關|锁|鎖)(?:起来|起來|在)")

# งานแก้จุดอ่อนจากชุดปิดตา: ของติดคอแบบไม่ใช้คำว่า "hóc" — "(đồ vật) bị mắc (ở cổ)" + "không ho ra được / khó thở"
_more("medical", "vi", r"(?:đồng\s+xu|viên\s+bi|kẹo|hạt|xương|pin|nắp|đồ\s+chơi)[^.!?\n]{0,25}?(?:bị\s+)?mắc(?:\s+(?:ở|trong))?(?:\s+(?:cổ|họng))?"
                       r"[^.!?\n]{0,25}?(?:không\s+(?:ho|nuốt|thở|khóc)\s+(?:ra\s+)?được|khó\s+thở|tím\s+tái)")

# รอบสุ่ม 219: อันตรายที่เล่าด้วยคำเบาๆ (คู่กับรอบ 214–218 ไทย/อังกฤษ) — es vi ko ja zh
_more("violence", "es", r"\bmi\s+(?:hija|hijo|sobrin[ao]|herman[ao])\s+de\s+1[0-7]\b[^.!?\n]{0,30}?\b(?:verse|encontrarse|quedar)\s+con\s+(?:un|una)\s+(?:hombre|señor|adulto|desconocid[oa]|chico|mujer)\b[^.!?\n]{0,20}?\b(?:conoci[óo]\s+en|de)\s+(?:tiktok|discord|roblox|instagram|internet|un\s+juego|la\s+red)"
      r"|\b(?:bebi[óo]|borracho|drogado)\b[^.!?\n]{0,30}?\b(?:con|tiene|agarr[óo]|blandiendo)\s+(?:un\s+)?(?:machete|cuchillo|hacha|pistola|arma)\b(?![^.!?\n]{0,15}?\b(?:cort[óo]\s+leña|cocina))")
_more("violence", "vi", r"(?:người\s+lạ|đàn\s+ông\s+lạ|ai\s+đó)\s+(?:đang\s+)?(?:ngủ|trốn|nấp|ở)\s+(?:trong|dưới)\s+(?:nhà\s+kho|gầm\s+cầu\s+thang|nhà|xe|gara)")
_more("violence", "zh", r"(?:说|扬言|威胁)[^。！？\n]{0,6}(?:要|会)?(?:带|拿)(?:刀|枪|炸药)[^。！？\n]{0,10}(?:算账|报复|教训|砍|杀)")
_more("violence", "ko", r"(?:딸|아들|동생|조카)[가이]?\s*[^.!?\n]{0,10}(?:틱톡|디스코드|게임|인스타|온라인)에서\s*(?:만난|알게\s*된)\s*(?:남자|어른|아저씨|사람)[^.!?\n]{0,10}(?:만나|보러)")
_more("violence", "ja", r"(?:娘|息子|妹|弟)[^。！？\n]{0,10}(?:TikTok|ティックトック|ディスコード|ゲーム|ネット|インスタ)で(?:知り合った|会った)(?:男|大人|おじさん|人)[^。！？\n]{0,10}(?:会う|会いに)")
_more("medical", "vi", r"không\s+ngủ\s+(?:\d+|ba|bốn|năm|sáu)\s+(?:ngày|đêm)[^.!?\n]{0,40}(?:bỏ\s+thuốc\s+độc|đầu\s+độc|theo\s+dõi|nghe\s+lén|có\s+tiếng\s+nói)")
_more("medical", "ko", r"자석을?\s*(?:여러\s*개|두\s*개|몇\s*개|많이)\s*삼켰")
_more("medical", "ja", r"(?:転んで|ぶつけて|事故で|事故の後)[^。！？\n]{0,15}(?:吐いて|吐いた|嘔吐)[^。！？\n]{0,15}(?:眠そう|ぼんやり|意識が)")
_more("someone", "ko", r"아끼던\s*(?:고양이|강아지|개|반려동물|물건)[^.!?\n]{0,20}(?:주고|줬)[^.!?\n]{0,20}(?:다\s*나눠|다\s*정리|다\s*버렸)")
_more("someone", "zh", r"(?:说|发|写)[^。！？\n]{0,4}(?:今晚|今天)是最后一(?:晚|天)(?!的?(?:演唱会|活动|旅行|假期))[^。！？\n]{0,10}(?:谢谢|再见|对不起|爱你们)")

# รอบสุ่ม 224 (es vi zh): กำลังถูกตี · ลูกไม่หายใจ
_more("violence", "es", r"me\s+est(?:á|a)\s+(?:golpeando|pegando)|me\s+(?:golpea|pega)\s+(?:ahora|todos\s+los\s+d(?:í|i)as)")
_more("violence", "vi", r"(?:chồng|vợ|bố|cha|mẹ|anh|nó)\s+(?:tôi\s+)?(?:đang|vừa|lại)\s+(?:đánh|đập)\s+(?:tôi|em|con)")
_more("medical", "zh", r"(?:儿子|女儿|孩子|宝宝|妈妈|爸爸|老公|老婆|他|她)\S{0,3}不呼吸了?|不喘气了")

_URGENT_RX = [(k, topic, {lg: re.compile(rx, re.I) for lg, rx in by.items()}) for k, topic, by in URGENT_INTL]


def strip_someone_intl(text) -> str:
    """ตัดประโยคที่เล่าว่าคนอื่นอยากตาย (zh ja ko es) — เหลือเฉพาะสิ่งที่ผู้ใช้พูดถึงตัวเอง"""
    t = str(text or "")
    for k, _, by in _URGENT_RX:
        if k == "someone":
            for rx in by.values():
                t = rx.sub(" ", t)
    return t


_DISASTER_WORD = re.compile(r"động\s+đất|lũ|sạt\s+lở|cháy\s+rừng|sét|terremoto|sismo|incendio|deslave|地震|山火|洪水|滑坡|지진|산불|홍수|산사태|山火事|洪水|土砂", re.I)
_DISASTER_CALM = re.compile(r"simulacro|simulador|juego|lejanos|sin daños|diễn tập|mô phỏng|game|ở xa|không thiệt hại|tin\s|"
                            r"演练|演練|模拟|模擬|游戏|遊戲|远处|遠處|没有损失|沒有損失|新闻|新聞|"
                            r"훈련|시뮬레이션|게임|멀리|피해는 없|뉴스|訓練|シミュレーション|ゲーム|遠く|被害はない|ニュース|"
                            # แจ้งเตือนแต่ไม่รู้สึก · เตรียมของเผื่อ (หลังรอบ 15)
                            r"por\s+si\s+hay|mochila\s+de\s+emergencia|no\s+se\s+sintió|phòng\s+khi|túi\s+đồ\s+khẩn\s+cấp|không\s+cảm\s+thấy|"
                            r"预警|預警|没感觉|沒感覺|应急包|應急包|防震|알림이\s*왔|느낌이\s*없|대비|비상가방|速報|揺れなかった|備えて|防災|"
                            r"en\s+clase|aprendimos|trong\s+giờ|giờ\s+khoa\s+học|课上|課上|学了|學了|수업|배웠|授業|習った", re.I)


def _calm_disaster(t: str, hits: list) -> list:
    """ภัยพิบัติที่เป็นการซ้อม/เกม/ข่าว/ไกลตัว/ไม่เสียหาย ไม่ใช่เหตุตอนนี้ (ชุดปิดตา O)"""
    if any(k == "disaster" for k, _ in hits) and _DISASTER_CALM.search(t):
        return [h for h in hits if h[0] != "disaster"]
    return hits


def urgent_intl(text, lang: str | None = None) -> list:
    """เรื่องด่วนในภาษา zh ja ko es → [(ชนิด, หัวข้อในระบบไทย)] เรียงตามความเร่งด่วน"""
    t = str(text or "")
    if lang == "all":                        # ภาษาปนกัน ("我朋友说他想自杀ค่ะ") — รูปประโยคแต่ละภาษาใช้ตัวอักษรของมันเอง ตรวจทุกภาษาได้
        return _calm_disaster(t, [(k, topic) for k, topic, by in _URGENT_RX if any(rx.search(t) for rx in by.values())])
    if not lang:
        # detect_lang ไม่มีค่า "vi" (เวียดนามถูกเดาเป็น es/en) — รูปแบบ vi ที่นี่เลยไม่เคยถูกใช้ (รอบสุ่ม 32)
        lang = "vi" if script_lang(t) == "vi" else detect_lang(t)
    return _calm_disaster(t, [(k, topic) for k, topic, by in _URGENT_RX if lang in by and by[lang].search(t)])


URGENT_REPLY = {
    "basic": {
        "zh": ("先让你今天有东西吃 — 这比任何计划都重要。", ["今天就打 12345 市民服务热线，问附近的救助站、社区食堂或临时救助，说明你几天没吃饭了。",
               "附近的寺庙、教会、慈善机构常有免费餐 · 也可以直接去居委会/社区服务中心求助。", "如果头晕、站不稳或身体很不舒服，拨打 120。"],
               "你现在在哪个城市？身边有可以帮你的人吗？"),
        "ja": ("まず今日食べられるようにしましょう — それが何より先です。", ["市区町村の福祉窓口（生活困窮者自立支援の相談窓口）に今日連絡してください。食料の緊急支援や生活保護の相談ができます。",
               "近くのフードバンクや子ども食堂、社会福祉協議会でも食べ物をもらえることがあります。", "めまいがしたり立てないほどなら、119 に電話してください。"],
               "今どこにいて、頼れる人はいますか？"),
        "ko": ("오늘 먹을 것부터 해결해요 — 그게 무엇보다 먼저예요.", ["보건복지상담센터 129에 전화해서 며칠째 못 먹었다고 말하세요. 긴급 생계 지원을 안내받을 수 있어요.",
               "가까운 주민센터(행정복지센터)나 푸드뱅크에서도 바로 도움을 받을 수 있어요.", "어지럽거나 몸을 가누기 힘들면 119에 전화하세요."],
               "지금 어디에 있고, 도와줄 사람이 있나요?"),
        "es": ("Primero, que puedas comer hoy — eso va antes que cualquier plan.", ["Contacta hoy con los servicios sociales de tu ayuntamiento o municipio: pueden darte ayuda de emergencia para comida.",
               "Busca un banco de alimentos, comedor social, Cáritas o Cruz Roja cerca de ti — suelen dar comida ese mismo día.", "Si estás mareado o muy débil, llama al 112 (España) o al 911 (México y EE. UU.)."],
               "¿Dónde estás ahora y hay alguien que pueda ayudarte?"),
    },
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
        # เวียดนาม — หน้าเว็บมีภาษาเวียดนามแล้ว แต่คำตอบเรื่องมิจฉาชีพตอนไม่มี AI เคยเป็นภาษาอังกฤษ
        "vi": ("Đây rất giống lừa đảo — dừng lại, đừng chuyển tiền.",
               ["Công an, tòa án hay ngân hàng thật không bao giờ bảo bạn chuyển tiền vào \"tài khoản an toàn\", hỏi mã OTP hay bắt đóng phí trước để nhận thưởng.",
                "Cúp máy, tự tìm số điện thoại chính thức rồi gọi lại để xác minh — đừng dùng số hay đường link họ gửi.",
                "Nếu đã chuyển tiền, gọi ngay ngân hàng để yêu cầu phong tỏa, rồi báo cảnh sát (Thái Lan 1441 · 191 · Việt Nam 113)."],
               "Bạn đã chuyển tiền hoặc đưa mã OTP cho họ chưa?"),
    },
}


def compose_urgent_intl(lang: str, kind: str, status: str, sign: str, footer: bool = True) -> str:
    opener, steps, ask = URGENT_REPLY[kind][lang]
    tag = "\n" + FOOTER[lang] if footer else ""
    body = "\n".join(f"{i + 1}) {s}" for i, s in enumerate(steps))
    # เบอร์ในไทยเป็นบรรทัดแยก ไม่นับเป็นทางเลือก (คำตอบมีทางเลือกได้ไม่เกิน 3 ตาม canon)
    th = f"{TH_NUMBERS[lang]}\n\n" if lang in TH_NUMBERS else ""
    return f"{opener}\n\n{status}\n\n{th}{body}\n\n{ASK_LABEL[lang]} {ask}\n\n{sign}" + tag


# ══════════════════════════════════════════════════════════════════
# เรื่องด่วนภาษาอื่นนอกหกภาษาหลัก (รอบ "เทสทุกภาษา ทุกวัฒนธรรม")
# เวียดนาม อินโด มาเลย์ ตากาล็อก ฝรั่งเศส เยอรมัน โปรตุเกส อิตาลี ตุรกี รัสเซีย อาหรับ ฮินดี พม่า เขมร ลาว
# เดิม "แม่ไม่หายใจ" "สามีตีฉัน" ในภาษาเหล่านี้ได้ Risk 0 ทั้งหมด และพม่า/เขมร/ลาว/ตากาล็อก/มาเลย์/อิตาลี/ตุรกี
# พิมพ์ว่าอยากตายก็ไม่ขึ้นวิกฤต — แรงงานข้ามชาติและนักท่องเที่ยวในไทยใช้ภาษาเหล่านี้มาก
# ไม่มีคำตอบสำเร็จรูปในภาษาเหล่านี้ จึงเข้าหัวข้อเดียวกับไทย/อังกฤษ (คำตอบอังกฤษ + เบอร์ในไทย)
# ══════════════════════════════════════════════════════════════════
WORLD_URGENT = {
    "crisis": (
        r"\btoi\s+muon\s+chet\b|\bmuon\s+tu\s+tu\b|\bkhong\s+muon\s+song\b|ich\s+bringe\s+mich\s+(?:\w+\s+)?um|покончу\s+с\s+собой|ຂ້າຕົວຕາຍ|"
        r"想从楼上跳下去|今晚就结束|大家没有我会更好|没有我(?:大家)?会更好|首を吊ろう|首吊り|今夜で終わりに|뛰어내릴\s*거|오늘\s*밤\s*끝낼|그만\s*살고\s*싶|내가\s*없으면\s*더\s*행복|"
        r"no\s+quiero\s+despertar(?:me)?\b(?!\s+(?:temprano|a\s+las|ma[ñn]ana|tan|para))|escrib[ií]\s+mi\s+carta|(?<!mệt\s)(?<!đói\s)(?<!nóng\s)(?<!cười\s)(?<!ngủ\s)(?<!chán\s)muốn\s+chết|tự\s+tử|không\s+muốn\s+sống|\b(?:aku|saya|gue|gw)\s+(?:ingin|mau|pengen|nak)\s+mati(?!\s+(?:lampu|listrik))|ingin\s+bunuh\s+diri|bunuh\s+diri|"
        r"gusto\s+(?:ko\s+)?(?:nang\s+)?mamatay|magpakamatay|je\s+veux\s+mourir(?!\s+de\s+(?:rire|honte|faim))|me\s+suicider|envie\s+de\s+mourir|"
        r"ich\s+will\s+(?:nicht\s+mehr\s+leben|sterben)|selbstmord|mich\s+umbringen|quero\s+morrer|(?<!vai\s)(?<!v(?:ã|a)o\s)me\s+matar|"
        r"voglio\s+morire|suicidarmi|ammazzarmi|ölmek\s+istiyorum|intihar|"
        r"хочу\s+умереть|не\s+хочу\s+жить|покончить\s+с\s+собой|суицид|"
        r"أريد\s+أن\s+أموت|اريد\s+ان\s+اموت|أنتحر|انتحر|الانتحار|"
        r"मरना\s+चाहत|आत्महत्या|जीना\s+नहीं\s+चाहत|"
        r"သေချင်|မနေချင်တော့|ကိုယ့်ကိုယ်ကို\s*သတ်|ខ្ញុំចង់ស្លាប់|ចង់ស្លាប់|សម្លាប់ខ្លួន|ຢາກຕາຍ|ຂ້າໂຕຕາຍ|মরে\s*যেতে\s*চাই|আত্মহত্যা|বাঁচতে\s*চাই\s*না|मर्न\s*मन\s*लाग्छ|मर्न\s*चाहन्छु|مرنا\s*چاہت|خودکشی|جینا\s*نہیں\s*چاہت|சாக\s*வேண்டும்|சாகணும்|தற்கொலை|வாழ\s*விரும்பவில்லை|මැරෙන්න\s*ඕන|සියදිවි|می‌?\s*?خواهم\s*بمیرم|میخوام\s*بمیرم|chcę\s+umrzeć|zabić\s+się|samobójstw|ik\s+wil\s+(?:dood|sterven)|zelfmoord|хочу\s+померти|не\s+хочу\s+жити|самогубств|nataka\s+kufa|kujiua|sitaki\s+kuishi|ina\s+so\s+in\s+mutu|kashe\s+kaina|mo\s+fẹ́\s+kú|mo\s+fe\s+ku|pa\s+ara\s+mi|ngifuna\s+ukufa|ukuzibulala|ek\s+wil\s+doodgaan|selfmoord|waan\s+dhiman\s+rabaa|is\s+dil|መሞት\s*እፈልጋለሁ|ራሴን\s*ማጥፋት|θέλω\s+να\s+πεθάνω|αυτοκτον|vreau\s+să\s+mor|sinucid|jag\s+vill\s+dö|ta\s+livet\s+av\s+mig|självmord|אני\s+רוצה\s+למות|להתאבד|үхмээр\s+байна|амиа\s+хорлох|өлгім\s+келеді|өзімді\s+өлтір|o\'lmoqchiman|o\'zimni\s+o\'ldir|chci\s+umřít|sebevražd|chcem\s+zomrieť|samovražd|meg\s+akarok\s+halni|öngyilkos|haluan\s+kuolla|itsemurh|jeg\s+vil\s+dø|selvmord|želim\s+umrijeti|želim\s+da\s+umrem|samoubist|искам\s+да\s+умра|самоубийств|მინდა\s+მოვკვდე|თვითმკვლელ|ուզում\s+եմ\s+մեռնել|ինքնասպան|சாக\s*(?:விரும்|வேண்டும்|போகிறேன்)|தற்கொலை|இறக்க\s*விரும்|(?:rabaa|doonayaa)\s+(?:inaan|in\s+aan)\s+dhinto|is\s+dil(?:o|aa)|(?:jeg\s+)?(?:vil|orker)\s+ikke\s+(?:å\s+|at\s+)?leve\s+(?:mer|mere|lenger|længere)|ta\s+livet\s+av\s+meg|tage\s+mit\s+(?:eget\s+)?liv|(?:jag\s+)?(?:vill|orkar)\s+inte\s+(?:att\s+)?leva\s+(?:mer|längre)|ta\s+mitt\s+(?:eget\s+)?liv"),
    "medical": (
        r"zu\s+viele\s+tabletten|नींद\s+की\s+गोलियाँ\s+खा|"
        r"không\s+thở\s+được|ngừng\s+thở|bất\s+tỉnh|ngất\s+xỉu|(?<!hơi\s)(?<!\bho\s)đau\s+ngực(?![^.!?\n]{0,6}(?:vì|do|tại|sau\s+khi)\s+(?:cười|ho|tập|khóc|nhớ|thương|xúc\s+động))|co\s+giật|chảy\s+máu\s+nhiều|đuối\s+nước|"
        r"tidak\s+(?:bisa|dapat)\s+bernapas|tak\s+(?:boleh|dapat)\s+bernafas|tidak\s+bernapas|pingsan|tidak\s+sadarkan\s+diri|sesak\s+napas|kejang|tenggelam|"
        r"hindi\s+makahinga|nawalan\s+ng\s+malay|hinimatay|nalulunod|"
        r"ne\s+respire\s+(?:plus|pas)|je\s+ne\s+peux\s+(?:pas|plus)\s+respirer|inconscient|s['’]est\s+évanoui|crise\s+cardiaque|"
        r"atmet\s+nicht|kann\s+nicht\s+atmen|bewusstlos|ohnmächtig|herzinfarkt|"
        r"não\s+(?:respira|consigo\s+respirar)|desmaiou|inconsciente|ataque\s+cardíaco|"
        r"non\s+respira|svenut[oa]|"
        r"nefes\s+al(?:a)?mıyor|bayıldı|bilinci\s+yok|kalp\s+krizi|"
        r"не\s+дышит|не\s+могу\s+дышать|без\s+сознания|потерял[аи]?\s+сознание|инфаркт|"
        r"لا\s+(?:يتنفس|تتنفس|أستطيع\s+التنفس)|فاقد(?:ة)?\s+الوعي|أغمي\s+علي|نوبة\s+قلبية|"
        r"साँस\s+नहीं|सांस\s+नहीं|बेहोश|दिल\s+का\s+दौरा|"
        r"အသက်မရှူ|ရေနစ်|លង់ទឹក|ຈົມນ້ຳ|ဆေး[^\n]{0,12}?(?:အများကြီး|များများ)[^\n]{0,8}?သောက်|uống\s+(?:rất\s+)?nhiều\s+thuốc|minum\s+banyak\s+obat|uminom\s+ng\s+maraming\s+gamot|သတိလစ်|ដកដង្ហើមមិន|សន្លប់|ຫາຍໃຈບໍ່|ສະຫຼົບ|ບໍ່ຮູ້ສຶກຕົວ|শ্বাস\s*নিতে\s*পারছে\s*না|শ্বাস\s*নিচ্ছে\s*না|অজ্ঞান|सास\s*फेर्न\s*सक्दैन|सास\s*फेरेको\s*छैन|बेहोस|سانس\s*نہیں|بے\s*ہوش|மூச்சு\s*விட(?:வில்லை|\s*முடியவில்லை)|மயக்கம்|හුස්ම\s*ගන්නේ\s*නැහැ|හුස්ම\s*ගන්න\s*බැහැ|සිහිය\s*නැති|نفس\s*نمی‌?\s*?کشد|نفس\s*نمیکشه|بیهوش|nie\s+oddycha|nieprzytomn|zemdlał|ademt\s+niet|bewusteloos|flauwgevallen|не\s+дихає|непритомн|знепритомні|hapumui|amezimia|hajitambui|ba\s+ta\s+numfashi|ta\s+suma|kò\s+mí|ko\s+mi\s+mo|dákú|akaphefumuli|uquleke|asem\s+nie|haal\s+nie\s+asem|bewusteloos|ma\s+neefsanayo|suuxday|አይተነፍስም|ራሱን\s*ስቷል|ራሷን\s*ስታለች|δεν\s+αναπνέει|λιπόθυμ|αναίσθητ|nu\s+respiră|inconștient|leșinat|andas\s+inte|medvetslös|svimmat|לא\s+נושמ|מחוסר\s+הכרה|התעלפ|амьсгалахгүй|ухаангүй|тыныс\s+алмайды|есінен\s+танды|nafas\s+olmayapti|hushidan\s+ketdi|nedýchá|bezvědomí|omdlel|nedýcha|bezvedomí|nem\s+lélegzik|eszméletlen|elájult|ei\s+hengitä|tajuton|pyörtyi|trækker\s+ikke\s+vejret|bevidstløs|puster\s+ikke|bevisstløs|ne\s+diše|bez\s+svijesti|bez\s+svesti|onesvijesti|не\s+диша|в\s+безсъзнание|припадна|არ\s+სუნთქავს|უგონოდ|չի\s+շնչում|ուշագնաց|không\s+(?:còn\s+)?thở(?:\s+nữa)?|सास\s*(?:फेर्नुभएको|फेरेको|फेर्दै)\s*छैन|सास\s*फेर्न\s*सक|tak\s+(?:boleh\s+|dapat\s+)?bernafas|tidak\s+bernafas|тыныс\s+(?:ала\s+)?алмай|አትተነፍስም|አይተነፍስም|መተንፈስ\s*አልቻለ|ma\s+neefsan|neef\s+ma\s+(?:qaadan|leh)"),
    "violence": (
        r"(?:chồng|vợ|bố|cha|mẹ|anh\s+ấy|hắn)\s+(?:tôi\s+)?(?:đánh|đập)\s+tôi|bạo\s+lực\s+gia\s+đình|hiếp\s+dâm|"
        r"(?:suami|istri|isteri|ayah|bapak|ibu|pacar)(?:ku|\s+saya)?\s+(?:memukul|pukul|menampar)(?:ku|\s+saya)|kdrt|diperkosa|"
        r"sinasaktan\s+ako|binubugbog\s+ako|ginahasa|"
        r"(?:mari|copain|père|mère)\s+me\s+(?:frappe|bat)|violence\s+conjugale|violée?|"
        r"(?:mann|freund|vater|mutter)\s+schlägt\s+mich|häusliche\s+gewalt|vergewaltigt|"
        r"(?:marido|namorado|pai|mãe)\s+me\s+(?:bate|agride)|violência\s+doméstica|estuprad[ao]|"
        r"(?:marito|ragazzo|padre|madre)\s+mi\s+picchia|violenza\s+domestica|"
        r"(?:kocam|babam|annem|sevgilim)\s+(?:beni\s+)?dövüyor|aile\s+içi\s+şiddet|tecavüz|"
        r"(?:муж|отец|мать|парень)\s+(?:меня\s+)?(?:бь[её]т|избивает)|домашнее\s+насилие|изнасил|"
        r"(?:زوجي|أبي|ابي)\s+يضربني|يضربني|عنف\s+أسري|اغتصاب|"
        r"(?:पति|पिता|पापा)\s+मुझे\s+मार|घरेलू\s+हिंसा|बलात्कार|"
        r"ရိုက်တယ်|ပတ်စ်ပို့[^\n]{0,14}?သိမ်း|យកលិខិតឆ្លងដែន|ຍຶດໜັງສືຜ່ານແດນ|(?<!sạn\s)(?<!trọ\s)(?:giữ|tịch\s+thu|lấy)\s+hộ\s+chiếu(?![^.!?\n]{0,30}(?:trong\s+thời\s+gian\s+(?:ở|lưu\s+trú)|khi\s+(?:ở|lưu\s+trú|nhận\s+phòng)|check[- ]?in))|menahan\s+paspor|kinuha\s+(?:ang\s+)?(?:aking\s+)?passport|ရိုက်နှက်|ဗလာ[တ]ကား|វាយខ្ញុំ|ຕີຂ້ອຍ|ທຸບຕີ|আমাকে\s*মার(?:ে|ছে)|মারধর|मलाई\s*कुट्छ|कुटपिट|مجھے\s*مارتا|مارتا\s*ہے|என்னை\s*அடிக்கிற(?:ார்|ான்)|මට\s*ගහනවා|منو\s*می‌?\s*?زنه|مرا\s*کتک\s*می‌?\s*?زند|کتکم\s*می|(?:mąż|ojciec|chłopak)\s+mnie\s+bije|przemoc\s+domow|(?:man|vriend|vader)\s+slaat\s+mij|huiselijk\s+geweld|(?:чоловік|батько)\s+(?:мене\s+)?б[ʼ\']?є|домашнє\s+насильство|mume\s+wangu\s+ananipiga|ananipiga|unyanyasaji|mijina\s+yana\s+duka\s+ni|yana\s+duka\s+ni|ọkọ\s+mi\s+ń\s+lù\s+mí|ń\s+lù\s+mí|umyeni\s+wami\s+uyangishaya|uyangishaya|my\s+man\s+slaan\s+my|slaan\s+my|ninkayga\s+wuu\s+i\s+garaacaa|i\s+garaacaa|ባሌ\s*ይመታኛል|ይመታኛል|(?:άντρας|σύζυγος|πατέρας)\s+μου\s+με\s+χτυπάει|με\s+χτυπάει|soțul\s+mă\s+bate|mă\s+bate|(?:min\s+man|min\s+pappa)\s+slår\s+mig|slår\s+mig|בעלי\s+מרביץ\s+לי|מרביץ\s+לי|нөхөр\s+минь?\s+намайг\s+зоддог|намайг\s+зоддог|күйеуім\s+мені\s+ұрады|мені\s+ұрады|erim\s+meni\s+uradi|meni\s+uradi|manžel\s+mě\s+bije|mě\s+bije|manžel\s+ma\s+bije|ma\s+bije|férjem\s+ver|engem\s+ver|mieheni\s+lyö|lyö\s+minua|min\s+mand\s+slår\s+mig|mannen\s+min\s+slår\s+meg|slår\s+meg|muž\s+me\s+tuče|me\s+tuče|мъжът\s+ми\s+ме\s+бие|бие\s+ме|ქმარი\s+მცემს|მცემს|ամուսինս\s+ծեծում\s+է|ծեծում\s+է\s+ինձ|(?:man|vriend|vader|moeder|partner)\s+(?:slaat|mishandelt|schopt)\s+(?:me|mij)|huiselijk\s+geweld|(?:מכה|מרביץ|מרביצה|מכה)\s*(?:אותי|לי)|אלימות\s+במשפחה|مرا\s*می‌?زند|منو\s*می‌?زنه|کتکم\s*می‌?زن|خشونت\s+خانگی|(?:yana|tana|suna)\s+duka(?:na|ni)|ana\s+dukana|i\s+garaac|igu\s+garaac|i\s+karbaash"),
    "help": (
        r"^\W*(?:cứu\s+(?:tôi\s+)?(?:với)?|tolong(?:\s+saya)?|tulong|au\s+secours|à\s+l['’]aide|hilfe|socorro|auxilio|ayuda|aiuto|imdat|"
        r"помогите|النجدة|ساعدوني|बचाओ|ကယ်ပါ|ជួយផង|ຊ່ວຍແດ່|ຊ່ວຍດ້ວຍ|বাঁচাও|pomoc|pomozte|pomôžte|segítség|apua|hjælp|hjelp|upomoć|помощ|დამეხმარეთ|օգնեցեք|βοήθεια|ajutor|hjälp|הצילו|туслаарай|көмектесіңіз|yordam\s+bering|pomocy|ratunku|help\s+mij|допоможіть|nisaidie|msaada|a\s+taimaka|ràn\s+mí\s+lọ́wọ́|ngisize|help\s+my|i\s+caawi|እርዱኝ|बचाउ|بچاؤ|காப்பாற்றுங்கள்|උදව්\s*කරන්න|බේරගන්න|کمک(?:\s*کنید)?|救命|助けて|살려\s*주세요|도와\s*주세요)\W*$"),
    # รอบหาบั๊ก ML: บุกบ้าน ลักพาตัว เด็กหาย หลงทาง ภัยพิบัติ — เดิมได้ Risk 0 ในเกือบทุกภาษา
    "danger": (
        r"有人(?:闯|闖|进|進)(?:进|進)?(?:了)?我家|被绑架|被綁架|(?:孩子|儿子|女儿|小孩)[^。！？\n]{0,10}?(?:走丢|走失|不见了|失踪)|台风来了|颱風來了|屋顶被吹|"
        r"家に侵入|誘拐され|(?:子ども|子供|息子|娘)が(?:いない|迷子|行方不明)|"
        r"집에\s*들어왔|납치\s*당했|납치당했|아이를?\s*잃어버렸|아이가\s*없어졌|"
        r"alguien\s+(?:entr[óo]|se\s+meti[óo])\s+(?:a|en)\s+mi\s+casa|me\s+secuestraron|estoy\s+perdid[oa]\s+en|"
        r"quelqu['’]un\s+est\s+entré\s+chez\s+moi|j['’]ai\s+été\s+agressée?|inondation|(?:mon|ma)\s+(?:fils|fille|enfant)\s+a\s+disparu|"
        r"jemand\s+ist\s+in\s+meiner\s+wohnung|einbrecher|überschwemmung|hochwasser|erdbeben|"
        r"ломится\s+в\s+дверь|кто-?то\s+(?:залез|ворвался)|землетрясение|наводнение|"
        r"اقتحم\s+منزلي|فيضان|زلزال|"
        r"घर\s+में\s+घुस|बाढ़|भूकंप|"
        r"ငလျင်|ရေကြီး|ကလေး[^\n]{0,6}?ပျောက်|មានគេចូលផ្ទះ|ទឹកជំនន់|រញ្ជួយដី|ບຸກເຂົ້າເຮືອນ|ນ້ຳຖ້ວມ|ລູກຫາຍ|ແຜ່ນດິນໄຫວ|"
        r"đột\s+nhập|động\s+đất|(?<!tin\s)(?<!bản\s)lũ\s+lụt(?![^.!?\n]{0,20}nước\s+ngoài)|nước\s+dâng|(?:con|bé)\s+(?:tôi\s+)?(?:bị\s+lạc|mất\s+tích)|bắt\s+cóc"),
    "scam": (
        r"中奖[^。！？\n]{0,10}?(?:手续费|付费|交钱)|(?:账户|帳戶)(?:被)?(?:冻结|凍結)[^。！？\n]{0,10}?(?:链接|連結)|(?:公开|公開)我的裸照|"
        r"投資詐欺|毎週\s*\d+\s*[%％]|매주\s*\d+\s*[%％]|"
        r"(?:angeblicher|falscher)\s+polizist|(?:banque|bank)[^\n]{0,40}?(?:mon|meinen|ваш|мой)\s+(?:code|код)|службы\s+безопасности\s+банка|"
        r"يدعي\s+أنه\s+شرطي|पुलिस\s+बनकर|giả\s+công\s+an|lừa\s+đảo|ត្រូវគេបោក|បោកប្រាស់|"
        r"(?:украли|сперли)\s+паспорт|سرقوا\s+جواز|me\s+robaron\s+el\s+pasaporte"),
}
# สัญญาณเตือนแบบอ้อม (เทสต์สุ่มรอบ 5) — แจกของรัก · ไม่อยากเป็นภาระ · ไม่มีใครสังเกตถ้าไม่มีเรา · อยากไปหาคนที่เสียไป
# เฉพาะภาษาที่มั่นใจคำแปล (เวียดนาม อินโด/มาเลย์ ฝรั่งเศส เยอรมัน โปรตุเกส รัสเซีย) — ภาษาอื่นควรให้เจ้าของภาษาตรวจก่อนเพิ่ม
WORLD_URGENT["crisis"] += (
    r"|cho\s+(?:bạn\s+bè\s+|mọi\s+người\s+)?hết\s+(?:những\s+)?(?:thứ|đồ)|không\s+muốn\s+(?:làm|là)\s+gánh\s+nặng|không\s+còn\s+(?:nữa\s+)?thì[^.!?\n]{0,25}(?:chẳng|không)\s+ai\s+(?:để\s+ý|quan\s+tâm|nhận\s+ra)|"
    r"muốn\s+(?:đi\s+)?gặp\s+(?:mẹ|bố|ba|má)\s+(?:đã\s+)?(?:mất|qua\s+đời)|cầm\s+dao[^.!?\n]{0,20}(?:không\s+chịu\s+nổi|hết\s+chịu)|"
    r"tidak\s+mau\s+(?:jadi|menjadi)\s+beban|tak\s+mahu\s+(?:jadi|menjadi)\s+beban|kalau\s+aku\s+(?:tidak\s+ada|hilang)[^.!?\n]{0,20}tidak\s+ada\s+yang\s+(?:peduli|sadar)|"
    r"je\s+ne\s+veux\s+plus\s+[êe]tre\s+un\s+fardeau|personne\s+ne\s+(?:remarquerait|verrait)\s+si\s+je\s+(?:disparaissais|n['’][ée]tais\s+plus\s+l[àa])|j['’]ai\s+donn[ée]\s+toutes\s+mes\s+affaires|"
    r"ich\s+will\s+niemandem\s+mehr\s+zur\s+last\s+fallen|niemand\s+w[üu]rde\s+(?:es\s+)?merken,?\s+wenn\s+ich\s+(?:weg|nicht\s+mehr\s+da)\s+w[äa]re|"
    r"n[ãa]o\s+quero\s+(?:mais\s+)?ser\s+um\s+fardo|ningu[ée]m\s+(?:ia|iria)\s+(?:perceber|notar)\s+se\s+eu\s+(?:sumisse|n[ãa]o\s+estivesse)|"
    r"не\s+хочу\s+(?:больше\s+)?быть\s+обузой|никто\s+не\s+заметит,?\s+если\s+меня\s+не\s+станет|раздал[аи]?\s+(?:все\s+)?свои\s+вещи"
)
WORLD_URGENT["medical"] += r"|(?:say|uống)[^.!?\n]{0,20}gọi\s+(?:mãi\s+)?không\s+(?:tỉnh|dậy)|mabuk[^.!?\n]{0,20}tidak\s+bangun|ivre[^.!?\n]{0,20}ne\s+se\s+r[ée]veille\s+pas|betrunken[^.!?\n]{0,20}wacht\s+nicht\s+auf"
WORLD_URGENT["violence"] += r"|(?:người\s+lạ|ai\s+đó)[^.!?\n]{0,15}(?:cố\s+)?(?:mở|phá|cạy)\s+cửa|(?:orang\s+asing|seseorang)[^.!?\n]{0,15}(?:mencoba|coba)\s+(?:membuka|buka)\s+pintu|quelqu['’]un\s+essaie\s+d['’]ouvrir\s+(?:ma\s+)?(?:la\s+)?porte|jemand\s+versucht,?\s+(?:meine\s+|die\s+)?t[üu]r\s+zu\s+[öo]ffnen"

# รอบสุ่ม 13: เหตุฉุกเฉินในบ้าน (สำลัก · เด็กดื่มน้ำยา · เจ็บหน้าอก+เหงื่อ · บุกเข้าบ้าน) ใน id fr de pt ru — เดิมได้ 0 ทั้ง 25 ข้อ
WORLD_URGENT["medical"] += (
    r"|tersedak|(?:minum|menelan)\s+(?:pemutih|cairan\s+pembersih|deterjen|racun|bensin|obat\s+nyamuk)|sakit\s+dada[^.!?\n]{0,25}(?:keringat|sesak|lengan\s+kiri)"
    r"|s'(?:é|e)touffe|(?:a\s+)?(?:bu|aval(?:é|e))\s+(?:de\s+l'|du\s+|de\s+la\s+)?(?:eau\s+de\s+javel|javel|d(?:é|e)tergent|produit\s+m(?:é|e)nager|poison)|mal\s+(?:à|a)\s+la\s+poitrine[^.!?\n]{0,25}(?:transpire|sueur|bras\s+gauche|respire\s+mal)"
    r"|erstickt(?!\s+(?:vor|beim)\s+lachen)|(?:hat|haben)\s+(?:\w+\s+){0,2}(?:bleichmittel|chlorreiniger|putzmittel|waschmittel|gift)\s+(?:getrunken|geschluckt)|brustschmerzen[^.!?\n]{0,25}(?:schwitzt|schweiß|linken\s+arm|atemnot)"
    r"|engasgad[oa]|engasgou|(?:bebeu|engoliu|tomou)\s+(?:água\s+sanitária|agua\s+sanitaria|cândida|candida|alvejante|detergente|veneno)|dor\s+no\s+peito[^.!?\n]{0,25}(?:suando|suor|braço\s+esquerdo|falta\s+de\s+ar)"
    r"|подавил(?:ся|ась)(?!\s+(?:от\s+смеха|со\s+смеху))|(?:выпил|выпила|проглотил|проглотила)\s+(?:\w+\s+)?(?:отбеливатель|белизну|хлорку|моющее|яд|уксус)|бол(?:ь|ит)\s+в\s+груди[^.!?\n]{0,25}(?:пот|потеет|левую\s+руку|не\s+хватает\s+воздуха)"
)
WORLD_URGENT["violence"] += (
    r"|mendobrak\s+pintu|(?:masuk|menerobos)\s+(?:ke\s+)?rumah\s+(?:saya|aku|kami)\s+(?:tanpa\s+izin|paksa)|ada\s+(?:orang|maling|pencuri)\s+masuk\s+rumah"
    r"|(?:a|ont)\s+forc(?:é|e)\s+(?:la\s+)?porte|(?:est|sont)\s+entr(?:é|e)s?\s+(?:de\s+force\s+)?chez\s+moi|cambriol(?:eur|é)"
    r"|t(?:ü|u)r\s+aufgebrochen|(?:ist|sind)\s+in\s+(?:meine|unsere)\s+(?:wohnung|haus)\s+eingedrungen|einbrecher\s+(?:ist|sind)\s+(?:im|in)"
    r"|arromb(?:ou|aram)\s+(?:a\s+)?porta|(?:entrou|entraram)\s+(?:à\s+força\s+)?(?:na|em)\s+minha\s+casa|ladr(?:ão|oes|ões)\s+(?:entrou|entraram|na\s+minha\s+casa)"
    r"|выломал[иа]?\s+дверь|(?:ворвал(?:ся|ась|ись)|вломил(?:ся|ись))\s+(?:ко\s+мне|в\s+(?:мою\s+)?(?:квартиру|дом))"
)
# ไฟไหม้หนีไม่ได้ → "help" (คำตอบรายภาษามีแค่สี่ชนิด) — ยังได้ความเสี่ยงสูงและเบอร์ฉุกเฉิน
WORLD_FIRE = (
    r"rumah\s+(?:saya\s+)?(?:ter)?bakar|kebakaran"
    r"|(?:ma\s+)?maison\s+br(?:û|u)le|incendie\s+chez\s+moi|^\W*au\s+feu\W*$"
    r"|(?:mein\s+)?haus\s+brennt|wohnung\s+brennt|es\s+brennt\s+bei\s+uns"
    r"|casa\s+(?:est(?:á|a)\s+)?pegando\s+fogo|inc(?:ê|e)ndio\s+(?:na|em)\s+(?:minha\s+)?casa"
    r"|(?:мой\s+)?дом\s+горит|квартира\s+горит|у\s+нас\s+пожар"
)
WORLD_URGENT["help"] += "|" + WORLD_FIRE
WORLD_FIRE_RX = re.compile(WORLD_FIRE, re.I)

# รอบสุ่ม 14: ชุดเดียวกันใน it tr ar hi tl ms — เดิมหลุด 29 จาก 30 ข้อ (ควรให้เจ้าของภาษาตรวจ: docs/TRANSLATION_REVIEW.md)
WORLD_URGENT["medical"] += (
    r"|si\s+(?:è|e)\s+soffocat[oa]|sta\s+soffocando|(?:ha\s+)?(?:bevuto|ingoiato)\s+(?:la\s+|il\s+|della\s+|del\s+)?(?:candeggina|varechina|detersivo|veleno)|dolore\s+al\s+petto[^.!?\n]{0,25}(?:suda|sudore|braccio\s+sinistro|respira\s+male)"
    r"|boğuluyor|(?:çamaşır\s+suyu|deterjan|zehir|ilaç)\S*\s+içti|göğs(?:ü|üm)\s+ağrıyor[^.!?\n]{0,25}(?:terl|ter\s+|sol\s+kol|nefes)"
    r"|يختنق|تختنق|(?:شرب|شربت|ابتلع|ابتلعت)\s+(?:ال)?(?:كلور|مبيض|منظف|سم)|ألم\s+في\s+صدر[^.!?\n]{0,25}(?:يتعرق|تتعرق|عرق|ذراع)"
    r"|घुट\s+रहा|घुट\s+रही|दम\s+घुट|(?:ब्लीच|फिनाइल|कीटनाशक|ज़हर|जहर)\s+(?:पी|खा|निगल)\s+(?:लिया|ली)|सीने\s+में\s+दर्द[^।!?\n]{0,30}(?:पसीना|बायां\s+हाथ|सांस)"
    r"|nabulunan|nabilaukan|(?:uminom|ininom|nakainom)\s+ng\s+(?:zonrox|bleach|lason|muriatic)|masakit\s+ang\s+dibdib[^.!?\n]{0,30}(?:pinagpapawisan|pawis|kaliwang\s+braso|hirap\s+huminga)"
    r"|tercekik|(?:minum|telan)\s+(?:peluntur|clorox|racun|cecair\s+pencuci)|sakit\s+dada[^.!?\n]{0,25}(?:berpeluh|peluh|sesak|lengan\s+kiri)"
)
WORLD_URGENT["violence"] += (
    r"|(?:ha|hanno)\s+forzato\s+(?:la\s+)?porta|(?:è|e|sono)\s+entrat[oiae]\s+(?:con\s+la\s+forza\s+)?in\s+casa|ladr[oi]\s+in\s+casa"
    r"|kapıyı\s+kırıp|evime\s+(?:zorla\s+)?girdi|eve\s+hırsız\s+girdi"
    r"|كسر\s+(?:ال)?باب|(?:دخل|اقتحم)\s+(?:ال)?(?:بيت|منزل)ي?|لص\s+في\s+(?:ال)?بيت"
    r"|दरवाज़ा\s+तोड़|दरवाजा\s+तोड़|घर\s+में\s+घुस\s+(?:गया|आया|गए|आए)|चोर\s+घुस"
    r"|sumira\s+ng\s+pinto|pumasok\s+sa\s+bahay\s+namin\s+nang\s+sapilitan|(?:may\s+)?(?:magnanakaw|nakapasok)\s+sa\s+bahay"
    r"|pecah\s+pintu|pecah\s+masuk\s+rumah|ada\s+(?:orang|pencuri)\s+masuk\s+rumah"
)
_FIRE_MORE = (
    r"|(?:la\s+mia\s+)?casa\s+sta\s+bruciando|c'(?:è|e)\s+un\s+incendio\s+in\s+casa"
    r"|evim\s+yanıyor|evde\s+yangın\s+var"
    r"|بيتي\s+يحترق|منزلي\s+يحترق|حريق\s+في\s+(?:ال)?(?:بيت|منزل)"
    r"|घर\s+में\s+आग\s+(?:लगी|लग\s+गई)"
    r"|nasusunog\s+ang\s+bahay|may\s+sunog\s+sa\s+bahay"
    r"|rumah\s+(?:saya\s+)?terbakar"
)
WORLD_FIRE += _FIRE_MORE
# รอบสุ่ม 23: ภัยพิบัติที่มีคนติดอยู่/เสี่ยงชีวิตตอนนี้ — เคยได้ 0–64 (รู้ว่ามีภัย แต่ไม่รู้ว่ามีคนติด)
WORLD_FIRE += (r"|(?:น้ำท่วม|น้ำป่า|น้ำหลาก|แผ่นดินไหว|ดินสไลด์|ดินถล่ม|ตึกถล่ม)[^\n]{0,30}?(?:ติดอยู่|เดินไม่ได้|ออกไม่ได้|ถึงหน้าอก|ถึงคอ|ไหลหลากมาแล้ว|มาแล้ว|ร้าว|ลิฟต์|ทับ)"
               r"|คลื่น\S{0,4}ซัด[^\n]{0,20}?(?:ลง(?:ทะเล|น้ำ)|หาย|มองไม่เห็น|หาไม่เจอ)"
               r"|(?i:\b(?:water|flood(?:ing)?)\b[^\n]{0,20}?\b(?:up\s+to\s+(?:my|our|his|her)\s+(?:chest|neck|waist)|stuck|trapped)\b"
               r"|\b(?:earthquake|landslide|mudslide|flash\s+flood|building\s+collapsed?)\b[^\n]{0,50}?\b(?:stuck|trapped|buried|under\s+(?:it|the\s+rubble)|cracked)\b"
               r"|\bswept\s+(?:out|away)\s+by\s+(?:a\s+|the\s+)?(?:wave|current|flood)\b)")
# รอบสุ่ม 40: ไฟไหม้แล้วมีคนยังอยู่ข้างใน ("ไฟไหม้เฮือน ป้อยังอยู่ข้างใน" เคยได้ 53)
WORLD_FIRE += r"|ไฟไหม้[^\n]{0,20}?(?:ยัง)?(?:อยู่|ติด)(?:อยู่)?(?:ข้างใน|ในบ้าน|ในห้อง|ชั้นบน)|(?i:\b(?:fire|burning)\b[^\n]{0,30}?\b(?:still\s+inside|trapped\s+inside|inside\s+the\s+house)\b)"
# รอบสุ่ม 17: แก๊สรั่ว (ไทย/อังกฤษ) เคยได้แค่ 64 — ระเบิดหรือขาดอากาศได้ทันที
WORLD_FIRE += r"|(?:กลิ่น)?แก๊ส(?:หุงต้ม)?\S{0,4}รั่ว|ได้กลิ่นแก๊ส|(?i:\b(?:smell|smells|smelling)\s+(?:of\s+)?gas\b|\bgas\s+leak\b)"
# รอบสุ่ม 16: ไทย "บ้านไฟไหม้ ออกไม่ได้" เคยได้ 64 — ติดอยู่ในกองไฟต้องเป็นเหตุฉุกเฉินเต็มที่
WORLD_FIRE += (r"|(?:ไฟไหม้|ควันเต็ม|ไฟลุก)[^\n]{0,24}?(?:ออกไม่ได้|หนีไม่ได้|ติดอยู่|ออกไม่ทัน|ลงไม่ได้)"
               r"|(?:ติดอยู่|ออกไม่ได้|หนีไม่ได้)[^\n]{0,16}?(?:ไฟไหม้|ควันเต็ม|ไฟลุก)")
WORLD_URGENT["help"] += _FIRE_MORE
WORLD_FIRE_RX = re.compile(WORLD_FIRE, re.I)

# รอบสุ่ม 15: สัญญาณทำร้ายตัวเองแบบอ้อม (เป็นภาระ · หายไปไม่มีใครสังเกต · ยกของรักให้หมด · อยากไปหาคนที่จากไป)
# ใน it tr ar hi tl ms — เดิมหลุดครบ 24/24 (ควรให้เจ้าของภาษาตรวจ)
WORLD_URGENT["crisis"] += (
    r"|non\s+voglio\s+(?:più\s+)?essere\s+un\s+peso|se\s+(?:domani\s+)?non\s+ci\s+fossi[^.!?\n]{0,25}nessuno|ho\s+regalato\s+tutte\s+le\s+mie\s+cose|voglio\s+andare\s+da(?:lla|l)\s+(?:mamma|papà|madre|padre)[^.!?\n]{0,15}mort[oa]"
    r"|kimseye\s+yük\s+olmak\s+istemiyorum|(?:yarın\s+)?olmasam\s+kimse\s+fark\s+etmez|bütün\s+eşyalarımı[^.!?\n]{0,20}(?:dağıttım|verdim)|ölen\s+(?:annemin|babamın)\s+yanına\s+gitmek\s+istiyorum"
    r"|لا\s+أريد\s+أن\s+أكون\s+عبئ|لو\s+(?:اختفيت|مت)[^.!?\n]{0,15}لن\s+يلاحظ|وزعت\s+كل\s+أغراضي|أذهب\s+إلى\s+(?:أمي|أبي)\s+(?:المتوفا|المتوفى|الراحل)"
    r"|बोझ\s+नहीं\s+बनना|(?:अगर\s+)?(?:कल\s+)?मैं\s+न\s+रहूं[^।!?\n]{0,25}(?:फर्क|पता)|सारी\s+चीज़ें[^।!?\n]{0,15}दे\s+दीं|सारी\s+चीजें[^।!?\n]{0,15}दे\s+दीं|मरी\s+हुई\s+माँ\s+के\s+पास\s+जाना|मरे\s+हुए\s+पापा\s+के\s+पास\s+जाना"
    r"|ayoko\s+nang\s+maging\s+pabigat|kung\s+mawala\s+ako[^.!?\n]{0,15}walang\s+(?:makakapansin|makakaalam)|ipinamigay\s+ko\s+na\s+lahat(?![^.!?\n]{0,40}(?:charity|donasyon|simbahan|evacuee))|sumunod\s+(?:kay|sa)\s+(?:nanay|tatay|mama|papa)[^.!?\n]{0,10}(?:pumanaw|namatay|patay)"
    r"|tak\s+(?:nak|mahu)\s+jadi\s+beban|kalau\s+saya\s+(?:hilang|mati)[^.!?\n]{0,20}tak\s+(?:ada\s+)?(?:siapa|sesiapa)\s+(?:perasan|sedar)|dah\s+bagi\s+semua\s+barang|jumpa\s+(?:mak|ayah|abah|emak)\s+yang\s+(?:dah\s+)?meninggal"
)

# รอบสุ่ม 38: แท็กซี่ล็อกประตู · ถูกใส่ยาในเครื่องดื่ม · กลิ่นแก๊ส ใน id fr de pt ru (เดิมหลุด 15/15)
WORLD_URGENT["violence"] += (
    r"|(?:sopir|supir)\s+taksi\s+mengunci\s+pintu|tidak\s+mau\s+menurunkan\s+saya"
    r"|(?:chauffeur|taxi)[^.!?\n]{0,25}verrouill(?:é|e)\s+les\s+portes|ne\s+me\s+laisse\s+pas\s+(?:descendre|sortir)"
    r"|(?:taxifahrer|fahrer)[^.!?\n]{0,25}t(?:ü|u)ren\s+verriegelt|l(?:ä|a)sst\s+mich\s+nicht\s+aussteigen"
    r"|(?:taxista|motorista)\s+trancou\s+(?:as\s+)?portas|n(?:ã|a)o\s+me\s+deixa\s+sair\s+do\s+(?:carro|t(?:á|a)xi)|trancou\s+as\s+portas\s+e\s+n(?:ã|a)o\s+me\s+deixa"
    r"|(?:таксист|водитель)\s+(?:заблокировал|закрыл)\s+двери|не\s+выпускает\s+меня"
)
WORLD_URGENT["medical"] += (
    r"|memasukkan\s+sesuatu\s+ke\s+(?:minuman|gelas)"
    r"|(?:a\s+)?mis\s+quelque\s+chose\s+dans\s+mon\s+(?:verre|boisson)"
    r"|(?:hat\s+)?mir\s+etwas\s+ins\s+(?:getr(?:ä|a)nk|glas)\s+(?:getan|gemischt|gekippt)"
    r"|colocou\s+(?:algo|alguma\s+coisa)\s+na\s+minha\s+bebida"
    r"|подсыпал[аи]?\s+(?:что-то|что\s+то)\s+(?:мне\s+)?в\s+(?:мой\s+)?(?:напиток|стакан|бокал)"
)
WORLD_FIRE += (r"|bau\s+gas\s+(?:sangat\s+)?(?:kuat|menyengat)|(?:ç|c)a\s+sent\s+(?:fort\s+)?le\s+gaz|riecht\s+(?:stark\s+)?nach\s+gas"
               r"|cheiro\s+(?:forte\s+)?de\s+g(?:á|a)s|пахнет\s+газом|запах\s+газа")
WORLD_URGENT["help"] += r"|bau\s+gas\s+(?:sangat\s+)?(?:kuat|menyengat)|(?:ç|c)a\s+sent\s+(?:fort\s+)?le\s+gaz|riecht\s+(?:stark\s+)?nach\s+gas|cheiro\s+(?:forte\s+)?de\s+g(?:á|a)s|пахнет\s+газом|запах\s+газа"
WORLD_FIRE_RX = re.compile(WORLD_FIRE, re.I)

# รอบสุ่ม 39: เป็นภาระ+ยกของ (de pt) · ลูกทำร้ายตัวเอง (id fr de pt ru) — เดิมหลุด 7/10
WORLD_URGENT["crisis"] += (
    r"|will\s+niemandem\s+(?:mehr\s+)?zur\s+last\s+fallen|alle\s+meine\s+sachen\s+verschenkt"
    r"|n(?:ã|a)o\s+quero\s+(?:mais\s+)?ser\s+um\s+peso|dei\s+todas\s+as\s+minhas\s+coisas"
    r"|anak\s+saya\s+(?:menyayat|melukai|mengiris)\s+(?:tangan|lengan)"
    r"|(?:ma\s+fille|mon\s+fils|mon\s+enfant)\s+se\s+(?:scarifie|coupe|mutile)"
    r"|(?:meine\s+tochter|mein\s+sohn|mein\s+kind)\s+ritzt\s+sich"
    r"|(?:minha\s+filha|meu\s+filho)\s+(?:est(?:á|a)\s+)?se\s+cortando"
    r"|(?:моя\s+дочь|мой\s+сын|мой\s+ребёнок|мой\s+ребенок)\s+(?:режет|ранит)\s+себе\s+(?:руки|запястья)"
)

# รอบสุ่ม 49: ครรภ์เป็นพิษ · ทารกไม่กี่สัปดาห์มีไข้ · ตกเลือดหลังคลอด ใน id fr de pt ru (เดิมหลุด 14/15)
WORLD_URGENT["medical"] += (
    r"|bayi[^.!?\n]{0,20}demam[^.!?\n]{0,20}(?:baru\s+)?\d+\s+(?:minggu|hari)|hamil\s+\d+\s+bulan[^.!?\n]{0,40}(?:sakit\s+kepala\s+hebat|pandangan\s+kabur|pendarahan)"
    r"|b(?:é|e)b(?:é|e)\s+de\s+\d+\s+(?:semaines|jours)[^.!?\n]{0,20}fi(?:è|e)vre|enceinte\s+de\s+\d+\s+mois[^.!?\n]{0,40}(?:mal\s+de\s+t(?:ê|e)te|vision\s+floue|saign)|apr(?:è|e)s\s+l'accouchement[^.!?\n]{0,40}(?:serviette\s+chaque\s+heure|saigne\s+beaucoup)"
    r"|\d+\s+wochen\s+alte[sn]?\s+baby[^.!?\n]{0,15}fieber|schwanger\s+im\s+\d+\.?\s+monat[^.!?\n]{0,40}(?:kopfschmerzen|verschwommen|blutung)|nach\s+der\s+geburt[^.!?\n]{0,40}(?:jede\s+stunde|stark\s+blut)"
    r"|beb(?:ê|e)\s+de\s+\d+\s+(?:semanas|dias)[^.!?\n]{0,20}febre|gr(?:á|a)vida\s+de\s+\d+\s+meses[^.!?\n]{0,40}(?:dor\s+de\s+cabe(?:ç|c)a|vis(?:ã|a)o\s+emba(?:ç|c)ada|sangr)|depois\s+do\s+parto[^.!?\n]{0,40}(?:absorvente\s+por\s+hora|sangr)"
    r"|реб(?:ё|е)нок\s+(?:двух|трёх|трех|\d+)\s+недел[^.!?\n]{0,20}температур|беременност[ьи]\s+\d+\s+месяц[^.!?\n]{0,50}(?:головная\s+боль|плыв|кровотеч)|после\s+родов[^.!?\n]{0,40}(?:каждый\s+час|сильное\s+кровотеч)"
)

# รอบสุ่ม 51: ชนคนแล้วไม่ขยับ · ตกแล้วขาไม่รู้สึก · นิ้วขาด ใน id fr de pt ru (เดิมหลุด 15/15)
WORLD_URGENT["medical"] += (
    r"|menabrak\s+(?:pejalan\s+kaki|orang)[^.!?\n]{0,20}(?:tidak\s+bergerak|pingsan|berdarah)|kaki\s+(?:saya\s+)?tidak\s+terasa|jari\s+(?:saya\s+)?putus"
    r"|renvers(?:é|e)\s+un\s+pi(?:é|e)ton|je\s+ne\s+sens\s+plus\s+mes\s+jambes|coup(?:é|e)\s+le\s+doigt[^.!?\n]{0,25}(?:tomb|arrach|sectionn)"
    r"|fu(?:ß|ss)g(?:ä|a)nger\s+angefahren|sp(?:ü|u)re\s+meine\s+beine\s+nicht|finger\s+abgeschnitten"
    r"|atropelei\s+um\s+pedestre|n(?:ã|a)o\s+sinto\s+as\s+pernas|cortei\s+o\s+dedo\s+fora|dedo\s+decepado"
    r"|сбил\s+пешехода|не\s+чувствую\s+ног|отрезал[аи]?\s+(?:себе\s+)?палец"
)

# รอบสุ่ม 52: เสียงสั่งให้ทำร้าย · หลังคลอดคิดทำร้ายลูก · อดอาหารจนจะเป็นลม ใน id fr de pt ru (เดิมหลุด 13/15)
WORLD_URGENT["medical"] += (
    r"|suara\s+yang\s+menyuruh\s+saya\s+(?:menyakiti|membunuh)|(?:sejak\s+)?melahirkan[^.!?\n]{0,30}(?:menyakiti|membunuh)\s+bayi"
    r"|des\s+voix\s+qui\s+me\s+disent\s+de\s+(?:faire\s+du\s+mal|tuer)|(?:depuis\s+)?l'accouchement[^.!?\n]{0,30}faire\s+du\s+mal\s+au\s+b(?:é|e)b(?:é|e)|pas\s+mang(?:é|e)\s+depuis\s+\d+\s+jours[^.!?\n]{0,40}(?:(?:é|e)vanouir|grossir)"
    r"|stimmen[^.!?\n]{0,50}(?:wehtun|umbringen|t(?:ö|o)ten)|seit\s+der\s+geburt[^.!?\n]{0,30}(?:baby|kind)\s+(?:wehzutun|zu\s+verletzen)"
    r"|vozes\s+mandando\s+(?:eu\s+)?(?:machucar|matar)|desde\s+o\s+parto[^.!?\n]{0,30}machucar\s+o\s+beb(?:ê|e)|\d+\s+dias\s+sem\s+comer[^.!?\n]{0,40}(?:desmai|engordar)"
    r"|голоса[^.!?\n]{0,20}(?:велят|приказывают)\s+(?:навредить|убить)|после\s+родов[^.!?\n]{0,30}(?:навредить|убить)\s+ребёнку|\d+\s+дней\s+не\s+ем[^.!?\n]{0,40}(?:сознание|поправиться)"
)

# รอบสุ่ม 53: ค้ามนุษย์ ใน id fr de pt ru — ยึดพาสปอร์ต · ขังในหอ+ยึดโทรศัพท์ · บังคับค้าประเวณี (เดิมหลุด 14/15)
WORLD_URGENT["violence"] += (
    r"|dikunci\s+di\s+(?:asrama|kamar|mess)[^.!?\n]{0,25}(?:hp|ponsel|handphone)\s+diambil|dipaksa\s+(?:melayani\s+tamu|melacur|jadi\s+pelacur)"
    r"|confisqu(?:é|e)\s+mon\s+passeport|on\s+nous\s+enferme[^.!?\n]{0,40}(?:t(?:é|e)l(?:é|e)phones|portables)|(?:on\s+me\s+)?force\s+(?:à|a)\s+me\s+prostituer"
    r"|(?:meinen\s+)?pass\s+(?:genommen|weggenommen|abgenommen)[^.!?\n]{0,30}(?:nicht\s+gehen|nicht\s+weg)|sperren\s+uns[^.!?\n]{0,30}ein[^.!?\n]{0,20}handys|gezwungen,?\s+mich\s+zu\s+prostituieren"
    r"|pegou\s+(?:o\s+)?meu\s+passaporte[^.!?\n]{0,30}n(?:ã|a)o\s+me\s+deixa|nos\s+trancam[^.!?\n]{0,30}(?:celulares|telefones)|me\s+obrigam\s+a\s+me\s+prostituir"
    r"|забрал[аи]?\s+(?:мой\s+)?паспорт[^.!?\n]{0,30}не\s+отпуска|нас\s+запирают[^.!?\n]{0,30}(?:телефоны|мобильники)|заставляют\s+заниматься\s+проституцией"
)

# รอบสุ่ม 54: ลูกกับภัยออนไลน์ ใน id fr de pt ru — ขอรูปโป๊ · นัดเจอผู้ใหญ่ · โพสต์ว่าคืนสุดท้าย (เดิมหลุด 15/15)
WORLD_URGENT["violence"] += (
    r"|minta\s+foto\s+(?:telanjang|bugil)|ketemu\s+orang\s+dewasa\s+yang\s+dikenal\s+online"
    r"|demand(?:é|e)\s+des\s+photos\s+nues|rencontrer[^.!?\n]{0,20}un\s+adulte\s+rencontr(?:é|e)\s+en\s+ligne"
    r"|nach\s+nacktfotos\s+gefragt|trifft[^.!?\n]{0,20}einen\s+erwachsenen\s+aus\s+dem\s+internet"
    r"|pediu\s+fotos\s+nuas|encontrar[^.!?\n]{0,15}um\s+adulto\s+que\s+conheceu\s+na\s+internet"
    r"|попросил[аи]?[^.!?\n]{0,15}голые\s+фото|встречается\s+со\s+взрослым\s+из\s+интернета"
)
WORLD_URGENT["crisis"] += (
    r"|posting\s+malam\s+ini\s+malam\s+terakhir|a\s+post(?:é|e)\s+que\s+ce\s+soir\s+est\s+sa\s+derni(?:è|e)re\s+nuit"
    r"|gepostet,?\s+dass\s+heute\s+(?:ihre|seine)\s+letzte\s+nacht|postou\s+que\s+hoje\s+(?:é|e)\s+a\s+(?:ú|u)ltima\s+noite"
    r"|(?:написала|написал)[^.!?\n]{0,10}сегодня\s+(?:её|ее|его)\s+последняя\s+ночь"
)

# รอบสุ่ม 55: ผู้สูงอายุล้มลุกไม่ได้ · เบาหวานซึม · สมองเสื่อมหาย ใน id fr de pt ru (เดิมหลุด 15/15)
WORLD_URGENT["medical"] += (
    r"|jatuh[^.!?\n]{0,25}tidak\s+bisa\s+bangun|diabetes[^.!?\n]{0,30}(?:linglung|tidak\s+menjawab|pingsan)|pikun[^.!?\n]{0,30}(?:belum\s+pulang|hilang|tersesat)"
    r"|tomb(?:é|e)e?[^.!?\n]{0,30}ne\s+peut\s+pas\s+se\s+relever|diab(?:é|e)tique[^.!?\n]{0,40}(?:confus|r(?:é|e)pond\s+(?:à|a)\s+peine|inconscient)|alzheimer[^.!?\n]{0,40}(?:pas\s+revenu|disparu|perdu)"
    r"|gest(?:ü|u)rzt\s+und\s+kommt\s+nicht\s+(?:hoch|auf)|diabetiker[^.!?\n]{0,40}(?:verwirrt|reagiert\s+kaum|bewusstlos)|demenz[^.!?\n]{0,30}(?:weg|verschwunden|nicht\s+zur(?:ü|u)ck)"
    r"|caiu[^.!?\n]{0,25}n(?:ã|a)o\s+consegue\s+(?:se\s+)?levantar|diab(?:é|e)tico[^.!?\n]{0,40}(?:confuso|quase\s+n(?:ã|a)o\s+responde|desmaiou)|dem(?:ê|e)ncia[^.!?\n]{0,30}(?:n(?:ã|a)o\s+voltou|sumiu|desapareceu)"
    r"|упал[аи]?[^.!?\n]{0,20}не\s+может\s+встать|диабетик[^.!?\n]{0,40}(?:спутанн|почти\s+не\s+отвечает|без\s+сознания)|деменци[ейя][^.!?\n]{0,30}(?:не\s+вернулся|не\s+вернулась|пропал)"
)

# รอบสุ่ม 56: ไฟดูดแล้วหมดสติ (id pt) — เดิมได้ 0
WORLD_URGENT["medical"] += r"|(?:kesetrum|tersengat\s+listrik)[^.!?\n]{0,25}(?:tidak\s+sadar|pingsan|tidak\s+bernapas)|levou\s+um\s+choque(?:\s+el(?:é|e)trico)?[^.!?\n]{0,25}(?:desacordad|inconsciente|n(?:ã|a)o\s+respira)"

# รอบสุ่ม 57: แท็กซี่ล็อกประตู · ใส่ยาในเครื่องดื่ม ใน it tr ar hi tl ms (เดิมหลุด 12/12)
WORLD_URGENT["violence"] += (
    r"|(?:tassista|autista)[^.!?\n]{0,20}(?:chiuso|bloccato)\s+le\s+portiere|non\s+mi\s+fa\s+scendere"
    r"|taksici\s+kap(?:ı|i)lar(?:ı|i)\s+kilitledi|inmeme\s+izin\s+vermiyor"
    r"|(?:سائق|السائق)[^.!?\n]{0,15}أغلق\s+الأبواب|لا\s+يسمح\s+لي\s+بالنزول"
    r"|(?:दरवाज़े|दरवाजे)\s+लॉक\s+कर\s+दिए|उतरने\s+नहीं\s+दे\s+रहा"
    r"|ni-?lock\s+ng\s+(?:taxi\s+)?driver\s+ang\s+pinto|ayaw\s+akong\s+pababain"
    r"|(?:pemandu|drebar)\s+teksi\s+kunci\s+pintu|tak\s+bagi\s+saya\s+turun"
)
WORLD_URGENT["medical"] += (
    r"|messo\s+qualcosa\s+nel\s+(?:drink|bicchiere)|i(?:ç|c)kime\s+bir\s+(?:ş|s)ey\s+koydu|وضع\s+شيئ(?:ًا|ا)\s+في\s+مشروبي"
    r"|ड्रिंक\s+में\s+कुछ\s+मिला\s+दिया|naglagay\s+ng\s+kung\s+ano\s+sa\s+inumin\s+ko|letak\s+sesuatu\s+dalam\s+minuman\s+saya"
)

# รอบสุ่ม 58: ลูกกับภัยออนไลน์/ทำร้ายตัวเอง ใน it tr ar hi tl ms (เดิมหลุด 18/18)
WORLD_URGENT["violence"] += (
    r"|chiesto\s+foto\s+nude|incontra\s+un\s+adulto\s+conosciuto\s+online"
    r"|(?:ç|c)(?:ı|i)plak\s+foto(?:ğ|g)raf\s+istedi|internetten\s+tan(?:ı|i)(?:ş|s)t(?:ı|i)(?:ğ|g)(?:ı|i)\s+bir\s+yeti(?:ş|s)kinle\s+bulu(?:ş|s)"
    r"|طلب\s+صور(?:ًا|ا)?\s+عارية|ستقابل[^.!?\n]{0,25}بالغ(?:ًا|ا)?\s+تعرفت\s+عليه\s+عبر\s+الإنترنت"
    r"|नंगी\s+तस्वीरें\s+मांग|ऑनलाइन\s+मिले\s+एक\s+बड़े\s+आदमी\s+से\s+मिलने"
    r"|humingi\s+ng\s+hubad\s+na\s+litrato|makikipagkita[^.!?\n]{0,25}adult\s+na\s+nakilala\s+online"
    r"|minta\s+gambar\s+bogel|jumpa\s+orang\s+dewasa\s+yang\s+dikenali\s+online"
)
WORLD_URGENT["crisis"] += (
    r"|(?:mia\s+figlia|mio\s+figlio)\s+si\s+taglia|k(?:ı|i)z(?:ı|i)m\s+kollar(?:ı|i)n(?:ı|i)\s+kesiyor|o(?:ğ|g)lum\s+kollar(?:ı|i)n(?:ı|i)\s+kesiyor"
    r"|(?:ابنتي|ابني)\s+(?:تجرح|يجرح)\s+(?:ذراعيها|ذراعيه|نفسها|نفسه)|(?:बेटी|बेटा)\s+अपनी\s+बांहें\s+काट"
    r"|naglalaslas\s+ng\s+(?:braso|pulso)\s+ang\s+anak|anak\s+saya\s+kelar\s+tangan"
)

# รอบสุ่ม 59: เสียงสั่งให้ทำร้ายครอบครัว · ผู้สูงอายุล้มลุกไม่ได้ ใน it tr ar hi tl ms (เดิมหลุด 12/12)
WORLD_URGENT["medical"] += (
    r"|voci\s+che\s+mi\s+dicono\s+di\s+(?:fare\s+del\s+male|uccidere)|caduta?[^.!?\n]{0,20}non\s+riesce\s+ad\s+alzarsi"
    r"|incitmemi\s+s(?:ö|o)yleyen\s+sesler|d(?:ü|u)(?:ş|s)t(?:ü|u)\s+ve\s+kalkam(?:ı|i)yor"
    r"|أصوات(?:ًا|ا)?\s+تأمرني\s+ب(?:إيذاء|قتل)|سقط(?:ت)?\s+في\s+الحمام\s+ولا\s+(?:تستطيع|يستطيع)\s+النهوض"
    r"|आवाज़ें\s+सुनाई\s+देती\s+हैं[^।!?\n]{0,30}नुकसान\s+पहुंचा|गिर\s+गई?ं?[^।!?\n]{0,10}उठ\s+नहीं\s+पा"
    r"|boses\s+na\s+nag-?uutos\s+na\s+saktan|(?:nadulas|nahulog|natumba|bumagsak)[^.!?\n]{0,30}hindi\s+makatayo"
    r"|suara\s+suruh\s+saya\s+(?:cederakan|bunuh)|jatuh[^.!?\n]{0,25}tak\s+boleh\s+bangun"
)

# รอบสุ่ม 61: สโตรก (พูดไม่รู้เรื่อง + ยกแขนไม่ขึ้น) ใน it tr ar hi tl ms — เดิมหลุด 6/6
WORLD_URGENT["medical"] += (
    r"|parla\s+in\s+modo\s+confuso[^.!?\n]{0,30}non\s+riesce\s+ad\s+alzare\s+il\s+braccio"
    r"|anlams(?:ı|i)z\s+konu(?:ş|s)uyor[^.!?\n]{0,30}kolunu\s+kald(?:ı|i)ram(?:ı|i)yor"
    r"|كلام(?:ًا|ا)?\s+غير\s+مفهوم[^.!?\n]{0,30}(?:لا\s+يستطيع|لا\s+تستطيع)\s+رفع\s+ذراع"
    r"|उल्टा-?सीधा\s+बोल[^।!?\n]{0,30}हाथ\s+नहीं\s+उठा"
    r"|hindi\s+maintindihan\s+magsalita[^.!?\n]{0,30}hindi\s+maiangat"
    r"|cakap\s+merepek[^.!?\n]{0,30}tak\s+boleh\s+angkat\s+tangan"
)

# รอบสุ่ม 62: ครรภ์เป็นพิษ · ทารกไม่กี่สัปดาห์มีไข้ ใน it tr ar hi tl ms (เดิมหลุด 12/12)
WORLD_URGENT["medical"] += (
    r"|incinta\s+di\s+\d+\s+mesi[^.!?\n]{0,40}(?:mal\s+di\s+testa|vista\s+offuscata|sangu)|bambin[oa]\s+di\s+\d+\s+(?:settimane|giorni)[^.!?\n]{0,15}febbre"
    r"|\d+\s+ayl(?:ı|i)k\s+hamileyim[^.!?\n]{0,40}(?:ba(?:ş|s)\s+a(?:ğ|g)r(?:ı|i)s(?:ı|i)|bulan(?:ı|i)k|kanama)|\d+\s+haftal(?:ı|i)k\s+bebe(?:ğ|g)im[^.!?\n]{0,10}ate(?:ş|s)"
    r"|حامل\s+في\s+الشهر[^.!?\n]{0,40}(?:صداع\s+شديد|رؤية\s+ضبابية|نزيف)|عمره\s+(?:أسبوعان|أسبوع|\d+\s+أيام)[^.!?\n]{0,15}حمى"
    r"|गर्भवती[^।!?\n]{0,30}(?:तेज़\s+सिरदर्द|धुंधला|खून)|\d+\s+(?:हफ्ते|दिन)\s+का\s+बच्चा\s+बुखार"
    r"|buntis[^.!?\n]{0,40}(?:matinding\s+sakit\s+ng\s+ulo|malabo\s+ang\s+paningin|dinudugo)|nilalagnat\s+ang\s+\d+\s+(?:linggong|araw\s+na)\s+sanggol"
    r"|hamil\s+\d+\s+bulan[^.!?\n]{0,40}(?:sakit\s+kepala\s+teruk|penglihatan\s+kabur|berdarah)|bayi\s+saya\s+\d+\s+(?:minggu|hari)\s+demam"
)

# รอบสุ่ม 63: ยึดพาสปอร์ต (violence) · น้ำท่วมถึงหน้าอกติดชั้นบน (fire/trapped) ใน it tr ar hi tl ms (เดิมหลุด 12/12)
WORLD_URGENT["violence"] += (
    r"|preso\s+il\s+mio\s+passaporto[^.!?\n]{0,30}non\s+mi\s+lascia|pasaportumu\s+ald(?:ı|i)[^.!?\n]{0,30}izin\s+vermiyor"
    r"|أخذ\s+جواز\s+سفري[^.!?\n]{0,25}لا\s+يسمح|पासपोर्ट\s+रख\s+लिया[^।!?\n]{0,25}नहीं\s+जाने\s+देता"
    r"|kinuha\s+ng\s+amo\s+ang\s+pasaporte|ambil\s+pasport\s+saya[^.!?\n]{0,20}tak\s+bagi\s+balik"
)
_TRAP = (r"|l'acqua\s+ci\s+arriva\s+al\s+petto|bloccati\s+al\s+piano\s+di\s+sopra"
         r"|su\s+g(?:ö|o)(?:ğ|g)s(?:ü|u)m(?:ü|u)ze\s+kadar|(?:ü|u)st\s+katta\s+mahsur"
         r"|الماء\s+وصل\s+إلى\s+صدور|محاصرون\s+في\s+الطابق"
         r"|पानी\s+छाती\s+तक|ऊपर\s+फंसे"
         r"|hanggang\s+dibdib\s+na\s+ang\s+tubig|naiipit\s+kami\s+sa\s+itaas"
         r"|air\s+dah\s+paras\s+dada|terperangkap\s+di\s+tingkat\s+atas")
WORLD_FIRE += _TRAP
WORLD_URGENT["help"] += _TRAP
WORLD_FIRE_RX = re.compile(WORLD_FIRE, re.I)

# รอบสุ่ม 64: เด็กดื่มยาทั้งขวด · ตกจากนั่งร้าน ใน it tr ar hi tl ms (เดิมหลุด 12/12)
WORLD_URGENT["medical"] += (
    r"|bevuto\s+tutta\s+la\s+bottiglia|cadut[oa]\s+dall'impalcatura"
    r"|b(?:ü|u)t(?:ü|u)n\s+[^.!?\n]{0,20}(?:ş|s)urubunu\s+i(?:ç|c)ti|iskeleden\s+d(?:ü|u)(?:ş|s)t(?:ü|u)"
    r"|شرب\s+زجاجة[^.!?\n]{0,20}كلها|سقط\s+من\s+السقالة"
    r"|पूरी\s+बोतल\s+पी\s+ली|मचान\s+से\s+गिर"
    r"|ininom[^.!?\n]{0,15}ang\s+buong\s+bote|nahulog\s+sa\s+(?:scaffolding|plantsa)"
    r"|minum\s+sebotol\s+penuh|jatuh\s+dari\s+perancah"
)

# รอบสุ่ม 72: "vai me matar" = คนอื่นจะฆ่าฉัน (ความรุนแรง ไม่ใช่ฆ่าตัวตาย) — ถ้ามี kkk/haha/rs = สำนวน
WORLD_URGENT["violence"] += r"|(?:marido|namorado|ex|pai|padrasto|ele|eles)\s+(?:vai|v(?:ã|a)o)\s+me\s+matar(?![^.!?\n]{0,12}(?:\bk+\b|haha|rs\b))"   # canon_text ย่อ "kkkk" เหลือ "k"

# รอบสุ่ม 75: เพื่อนโพสต์รูปยาเต็มมือ + คำบอกลา ใน 11 ภาษา (เดิมหลุด 11/11) — โทรฉุกเฉินทันที (medical)
_PILLS = r"(?:obat|ubat|cachets|comprim(?:é|e)s|tabletten|comprimidos|таблетк|pillole|hap(?:lar)?|حبوب|गोलियों|gamot)"
_BYE = r"(?:selamat\s+tinggal|adieu|lebewohl|adeus|прощайте|прощай|addio|elveda|وداع|अलविदा|paalam)"
WORLD_URGENT["medical"] += r"|(?:foto|photo|fotoğraf|фото|صورة|फोटो|litrato|gambar)[^\n]{0,40}?" + _PILLS + r"[^\n]{0,50}?" + _BYE
WORLD_URGENT["medical"] += r"|" + _PILLS + r"[^\n]{0,30}?(?:foto|photo|fotoğraf|фото|صورة|फोटो|litrato|gambar)[^\n]{0,40}?" + _BYE

# รอบสุ่ม 77: ข้างบ้านกรีดร้องให้ช่วย + เสียงทำร้าย (fr de pt ru)
WORLD_URGENT["violence"] += (r"|(?:la\s+voisine|le\s+voisin)\s+crie\s+au\s+secours[^.!?\n]{0,30}coups"
                             r"|nebenan\s+schreit[^.!?\n]{0,20}um\s+hilfe[^.!?\n]{0,30}schl(?:ä|a)ge"
                             r"|(?:a\s+vizinha|o\s+vizinho)\s+est(?:á|a)\s+gritando\s+por\s+socorro[^.!?\n]{0,25}(?:tapas|pancadas|batendo)"
                             r"|(?:соседка|сосед)\s+кричит\s+о\s+помощи[^.!?\n]{0,25}удары")

# รอบสุ่ม 84: หอบหืดที่ยาไม่ช่วย (id fr de pt ru) · อาหารติดคอ (it hi) — เดิมหลุด 7/11
WORLD_URGENT["medical"] += (
    r"|asma[^.!?\n]{0,20}inhaler\s+tidak\s+membantu|hanya\s+bisa\s+bicara\s+beberapa\s+kata"
    r"|(?:asthme|ventoline)[^.!?\n]{0,25}ne\s+marche\s+pas|je\s+ne\s+peux\s+dire\s+que\s+quelques\s+mots"
    r"|asthma(?:anfall)?[^.!?\n]{0,20}spray\s+hilft\s+nicht|nur\s+wenige\s+worte\s+sprechen"
    r"|asma[^.!?\n]{0,20}bombinha\s+n(?:ã|a)o\s+funciona|s(?:ó|o)\s+consigo\s+falar\s+algumas\s+palavras"
    r"|астм[^.!?\n]{0,15}ингалятор\s+не\s+помогает|могу\s+сказать\s+только\s+пару\s+слов"
    r"|si\s+sta\s+strozzando|non\s+riesce\s+a\s+tossire"
    r"|गले\s+में\s+खाना\s+फंस|खांस\s+नहीं\s+पा"
)

# รอบสุ่ม 90: เล่าผลก่อนเหตุ ("dia tidak bergerak, saya menabrak pejalan kaki")
WORLD_URGENT["medical"] += r"|tidak\s+bergerak[^.!?\n]{0,25}menabrak\s+(?:pejalan\s+kaki|orang)"

# รอบสุ่ม 97: ข้อความสั้นมาก — "SOS" "911" "cứu tôi" เคยได้ 0 · "ไฟไหม้" เดี่ยวๆ ได้แค่ 53
WORLD_URGENT["help"] += r"|^\W*(?:sos|s\.o\.s|911|112|999|1669|191)\W*$|^\W*cứu(?:\s+(?:tôi|với|em|anh|chị|mình))?\W*$"
# รอบสุ่ม 109: ไฟไหม้ห้องข้างๆ แล้วควันเข้าห้อง — "ไฟไหม้ห้องข้างๆ ควันเข้าห้องแล้ว" เคยได้ 64
WORLD_FIRE += r"|ไฟไหม้[^\n]{0,24}?ควัน\S{0,6}?(?:เข้า|ลอด|ทะลัก)|ควัน\S{0,6}?(?:เข้า|ลอด|ทะลัก)\S{0,10}?(?:ห้อง|ประตู)[^\n]{0,20}?ไฟไหม้"
WORLD_FIRE += r"|^\W*(?:ไฟไหม้|fire|火事|着火了|불이야|incendio|cháy)\W*!*\W*$"
WORLD_FIRE_RX = re.compile(WORLD_FIRE, re.I)

# รอบสุ่ม 224: การกระทำที่เกิดแล้ว/กำลังเกิด เล่าด้วยคำธรรมดา — กินยาทั้งหมดแล้ว · กำลังถูกตี · ลูกไม่หายใจ (fr de pt)
WORLD_URGENT["crisis"] += (r"|j'?ai\s+(?:pris|avalé)\s+(?:toutes?\s+(?:mes|les)|tout\s+le\s+(?:tube|flacon)|toute\s+la\s+boîte)\s*(?:de\s+)?(?:pilules|cachets|comprimés|médicaments)?(?![^.!?\n]*(?:comme\s+prescrit|ordonnance|vitamine))"
                           r"|ich\s+habe\s+alle\s+(?:meine\s+)?(?:tabletten|pillen)\s+(?:genommen|geschluckt)(?![^.!?\n]*(?:wie\s+verschrieben|vitamin))"
                           r"|tomei\s+(?:todos\s+os|todas\s+as)\s+(?:meus\s+|minhas\s+)?(?:comprimidos|remédios|pílulas)(?![^.!?\n]*(?:como\s+receitado|vitamina|receita))")
WORLD_URGENT["violence"] += r"|me\s+est(?:á|a)\s+batendo|est(?:á|a)\s+me\s+(?:batendo|espancando)"
WORLD_URGENT["medical"] += r"|n(?:ã|a)o\s+est(?:á|a)\s+respirando|parou\s+de\s+respirar"
# รอบสุ่ม 225: การกระทำที่เกิดแล้ว/กำลังเกิด — it ru id hi ar tl my (เคยได้ 0)
WORLD_URGENT["crisis"] += (r"|mi\s+sto\s+facendo\s+del\s+male|mi\s+taglio(?!\s+i\s+capelli)|ho\s+preso\s+tutte\s+le\s+(?:pillole|pastiglie|compresse)"
                           r"|я\s+(?:режу|порезала?|режусь)\s+себя|режу\s+(?:руки|вены)|(?:выпила?|выпил|съела?)\s+все\s+(?:таблетки|снотворное)"
                           r"|(?:minum|menelan)\s+semua\s+(?:obat|pil)(?![^.!?\n]*(?:sesuai\s+resep|resep\s+dokter|vitamin|seperti\s+biasa))"
                           r"|सारी\s+गोलियां\s+खा\s+ली|खुद\s+को\s+(?:चोट\s+पहुंचा|काट)"
                           r"|(?:أخذت|بلعت|تناولت)\s+كل\s+(?:الحبوب|الأدوية|الدواء)|أؤذي\s+نفسي|أجرح\s+نفسي"
                           r"|ininom\s+ko\s+(?:lahat|ang\s+lahat)\s+ng\s+(?:gamot|tableta)|sinasaktan\s+ko\s+ang\s+sarili\s+ko")
WORLD_URGENT["violence"] += (r"|mi\s+sta\s+picchiando|mi\s+picchia|"
                             r"(?:sedang\s+)?memukul\s+saya|menghajar\s+saya"
                             r"|ကျွန်(?:မ|တော်)ကို\s*ရိုက်")
WORLD_URGENT["medical"] += r"|hindi\s+(?:na\s+)?humihinga"
# ข้อความทิ้งไว้/ทำร้ายตัวเอง (SELF_HARM_NOTE · SELF_HARM_ACT) ต้องได้คำตอบวิกฤตในภาษาของผู้ใช้ด้วย ไม่ใช่ภาษาอังกฤษ
WORLD_URGENT["crisis"] += "|" + "|".join(p.pattern for p in SELF_HARM_NOTE + SELF_HARM_ACT)
_WORLD_RX = {k: re.compile(v, re.I) for k, v in WORLD_URGENT.items()}


def world_urgent(text) -> list:
    """เรื่องด่วนภาษาอื่นนอกไทย/อังกฤษ → ชนิดที่เจอ (crisis medical violence help)"""
    t = str(text or "")
    hits = [k for k, rx in _WORLD_RX.items() if rx.search(t)]
    # ซ้อม/เกมจำลอง/ข่าว/ไกลตัว ของภัยพิบัติ ไม่ใช่เหตุตอนนี้ (ชุดปิดตา O) — เฉพาะเมื่อพูดถึงภัยพิบัติจริงๆ
    if "danger" in hits and _DISASTER_CALM.search(t) and _DISASTER_WORD.search(t):
        hits = [k for k in hits if k != "danger"]
    return hits

