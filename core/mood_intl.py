"""
core/mood_intl.py — อารมณ์หนักและภัยที่พูดสั้น/อ้อม ในภาษา ja zh ko es vi

รอบ "ห้ามประมาทมนุษย์" ภาษาไทย/อังกฤษแก้ไปแล้ว (core/second_layer.py · HEAVY_MOOD)
พอไล่ชุดเดียวกันในอีก 5 ภาษา ประโยคหนักหลุดเกือบหมด: "彼が家の前にいる、怖い" "我一直哭停不下来"
"눈물이 멈추지 않아" "no puedo parar de llorar" "tôi khóc không ngừng được" ได้ Risk 0 และแผนสามขั้นทั่วไป

คนแต่ละคนใช้คำไม่เหมือนกัน จึงไม่จับเป็นประโยคตายตัว แต่ประกอบจาก "รูป" ของประโยค:
  ภัยตอนนี้   = [ใครสักคน] + [อยู่/ยืน/มา] + [หน้าบ้าน/ประตู/หน้าต่าง] + [กลัว]
               · [คุยได้ไม่นาน] + [เขาจะกลับมา] · [ไม่ปลอดภัย] + [ที่บ้าน/ตรงนี้] · [มีคน] + [ตาม/สะกดรอย] + [ฉัน]
  วิกฤตอ้อม   = [อยากหายไป] · [ขอให้ไม่ตื่น] · [ตัดสินใจ] + [จบทุกอย่าง] · [ไม่มีฉัน] + [ทุกคนดีกว่า] · [เหนื่อยกับการมีชีวิต]
  อารมณ์หนัก = [ร้องไห้] + [หยุดไม่ได้] · [ว่างเปล่า/ชา] · [ไม่เหลืออะไร] · [ดิ่ง/ถึงก้นเหว]
  โกรธ        = [โกรธ] + [มือ/ตัวสั่น] · [อยากทุบ/พัง] + [ทุกอย่าง]   · โกรธ + [ฆ่า] + [เขา] = anger_kill
แล้วตัดสิ่งที่ไม่ใช่เรื่องของคน: ร้องไห้เพราะหนัง/เพลง · สัตว์หน้าบ้าน · ราคาหุ้นดิ่ง
อารมณ์เกิดดับเร็ว — พลาดไปทางถามไถ่ ดีกว่าพลาดไปทางมองว่าปกติ
"""
import re

# ชนิดเรียงจากหนักไปเบา — ข้อความหนึ่งได้ชนิดที่หนักที่สุดชนิดเดียว
ORDER = ("crisis", "danger", "anger_kill", "anger", "heavy")

_G = r"[^。！？!?\n]"           # ตัวอักษรในประโยคเดียวกัน (ไม่ข้ามจุดจบประโยค)

# ── ภาษาจีน ──────────────────────────────────────────────────────────
_ZH_WHO = r"(?:他|她|那个人|那人|那个男的|有人|有个人|一个人|陌生人|前夫|前男友|前任|老公|丈夫|男朋友|男友|某人)"
_ZH_FEAR = r"(?:害怕|好怕|很怕|怕死了|吓死|吓坏|恐惧|不敢)"
ZH = {
    "danger": (
        _ZH_WHO + _G + r"{0,6}?(?:在|站在|守在|堵在|蹲在|等在|来到|到了|跑到)(?:我)?(?:家|房间|宿舍|屋)?的?(?:门口|门外|楼下|窗外|外面)" + _G + r"{0,14}?" + _ZH_FEAR,
        r"(?:不能|没法|无法|不敢)(?:聊|说|打字|讲)(?:太久|很久|多久|太多|太长)" + r"[^\n]{0,16}?(?:他|她)" + _G + r"{0,4}?(?:要|快|马上|就要|快要)?回来",
        r"(?:在)?(?:家里|家)" + _G + r"{0,6}?(?:不安全|没有安全感|没安全感|安全感都没有|一点安全感都没)|(?:觉得|感觉|感到)(?:很|好)?不安全",
        r"(?:有人|有个人|一个人|陌生人|一个男的)" + _G + r"{0,6}?(?:跟踪|跟着|尾随|一直跟)我",
    ),
    "crisis": (
        r"(?:想|要)(?:从这个世界|在这个世界上)?(?:彻底)?消失(?!一会|几天|一下|一段)",
        r"(?:希望|但愿|宁愿|真想)" + _G + r"{0,6}?(?:醒不过来|不要醒来|不再醒来|永远不醒|别再醒)",
        r"决定" + _G + r"{0,10}?(?:结束一切|结束这一切|结束所有|了结(?:自己|一切))|(?:今晚|今天|今夜)" + _G + r"{0,4}?(?:结束|了结)(?:一切|这一切|所有)",
        r"没有我" + _G + r"{0,8}?(?:会)?(?:更好|更幸福|更轻松)|我(?:不在|消失|死)了?" + _G + r"{0,6}?(?:大家|他们|所有人)" + _G + r"{0,4}?(?:更好|更轻松)",
    ),
    "anger_kill": (
        r"(?:气|愤怒|恨|火大)" + _G + r"{0,8}?(?:想|要|能|会)?杀(?:了|死)?(?:他|她|他们|那个人)|恨不得杀(?:了|死)?(?:他|她)",
    ),
    "anger": (
        r"(?:气|愤怒|火大)(?:得|到)" + _G + r"{0,4}?(?:发抖|手抖|浑身发抖|全身发抖|手在抖)",
        r"想(?:砸|摔|毁|拆)(?:烂|掉|了|碎)?(?:一切|所有|所有东西|全部)",
    ),
    "heavy": (
        r"(?:一直|不停地?|止不住地?)哭|哭(?:个)?(?:停不下来|不停|个不停|止不住)|眼泪(?:停不下来|止不住|一直流)",
        r"(?:心里|内心)?(?:空虚|空荡荡|空空的)|(?:麻木|什么都感觉不到|没有感觉了)",
        r"(?:我)?什么都没有了|一无所有了",
        r"(?:跌|掉|沉)到(?:了)?谷底|(?:心情|情绪)(?:非常|特别|好|很)?低落|(?:快|要)?崩溃了|撑不下去了",
    ),
}
_ZH_NOT = re.compile(r"电影|電影|电视剧|剧|视频|影片|动画|歌|小说|书|结局|股|价|指数|行情|基金|币|猫|狗|鸟|蛇|虫|蜘蛛|游戏|手机|电量|内存|冰箱|钱包里|作业")

# ── ภาษาญี่ปุ่น ──────────────────────────────────────────────────────
_JA_WHO = r"(?:彼|彼女|あの人|あいつ|元彼|元夫|元カレ|夫|旦那|知らない人|知らない男|誰か|男の人|男)"
_JA_FEAR = r"(?:怖|こわ|恐|震え|不安で)"
JA = {
    "danger": (
        _JA_WHO + r"(?:が|は)?" + _G + r"{0,6}?(?:家|部屋|玄関|ドア|窓|アパート)の(?:前|外)" + _G + r"{0,4}?(?:いる|立って|来て|来た|待って)" + _G + r"{0,14}?" + _JA_FEAR,
        r"(?:長く|あまり|ゆっくり)(?:は)?(?:話せ|打て|連絡でき|メールでき)(?:ない|ません)" + r"[^\n]{0,16}?(?:戻って|帰って)(?:くる|来る|きます|来ます)",
        r"(?:家|ここ|うち)" + _G + r"{0,6}?(?:安全じゃ|安全では|安心でき)(?:ない|ありません)|^\W*安全じゃない",
        r"(?:誰か|知らない人|知らない男|男|変な人)" + _G + r"{0,4}?(?:に)?(?:つけられ|後をつけられ|ついてこられ|ずっとついてく)",
    ),
    "crisis": (
        r"(?<!仕事を)(?<!宿題を)(?<!作業を)(?<!課題を)(?<!掃除を)(?:全部|すべて|全て|何もかも|人生)(?:を)?終わらせ(?:る|よう|たい|ます)",
        r"(?:私|僕|俺|自分|あたし)(?:が|なんか)?(?:い|居)ない(?:ほうが|方が)" + _G + r"{0,6}?(?:いい|まし|幸せ|楽)",
        r"生きる(?:のに|ことに)(?:疲れ|つかれ)|生きてるのが(?:疲れ|つらい|辛い|しんどい)",
        r"(?:この世から|世界から)消え|(?:明日|朝)(?:が)?来なければ(?:いい|いいのに)|起きなければいいのに",
    ),
    "anger_kill": (
        r"(?:腹が立|ムカつ|むかつ|怒り|頭にき|キレ)" + _G + r"{0,10}?(?:殺し(?:そう|たい|てやりたい|てやる)|殺す)",
        r"殺して(?:やりたい|やる)(?:くらい|ほど|って)?" + _G + r"{0,4}?(?:ムカつ|むかつ|腹が立|憎|頭にく|キレ)|(?:あいつ|彼|あの人|夫|旦那)(?:を|のこと)?(?:本気で)?殺してやりたい",
    ),
    "anger": (
        r"(?:怒り|腹が立って|ムカついて|悔しくて)" + _G + r"{0,4}?(?:手|体|身体|全身)が震え",
        r"(?:全部|何もかも|すべて|全て)(?:を)?(?:壊し|ぶっ壊し|めちゃくちゃにし|叩き壊し)たい",
    ),
    "heavy": (
        r"涙が(?:止まらない|止まりません|とまらない)|泣き(?:止め|止ま|やめ)(?:ない|られない)|ずっと泣いて",
        r"(?:心が)?空っぽ|何も感じ(?:ない|られない)|虚し(?:い|くて)",
        r"(?:もう|私には|僕には|俺には|自分には)何も残って(?:い)?ない",
        r"(?:すごく|かなり|ひどく|ずっと|とても)落ち込んで|どん底|もう限界",
    ),
}
_JA_NOT = re.compile(r"映画|ドラマ|アニメ|動画|曲|歌|本|小説|漫画|マンガ|ラスト|株|価格|相場|猫|犬|鳥|蛇|虫|クモ|ゲーム|冷蔵庫|財布|バッテリー")

# ── ภาษาเกาหลี ───────────────────────────────────────────────────────
_KO_WHO = r"(?:그\s*사람|그놈|그\s*남자|그가|그녀가?|걔가?|전\s*남친|전남친|전\s*남자친구|전남편|남편|누가|누군가|모르는\s*사람|어떤\s*(?:남자|사람))"
KO = {
    "danger": (
        _KO_WHO + r"[가-힯\s]{0,8}?(?:집|방|현관|문|창문)\s*(?:앞|밖)에\s*(?:있|서\s*있|왔|와\s*있)[^\n]{0,14}?(?:무서|겁나|겁이|두려|떨려)",
        r"(?:오래|길게|많이)\s*(?:(?:얘기|이야기|말|문자|연락)\s*)?(?:못\s*(?:얘기|이야기|말|문자|연락)?\s*해|못해|할\s*수\s*없)[^\n]{0,18}?(?:돌아와|돌아온|돌아올|들어와|들어올|올\s*거|온대)",
        r"(?:집|여기|집에서)[가-힯\s]{0,8}?안전하지\s*않|^\W*안전하지\s*않아",
        r"(?:누가|누군가|모르는\s*사람이?|어떤\s*(?:남자|사람)(?:이|가)?)\s*(?:나를?|날|저를?)?\s*(?:계속\s*)?(?:따라오|미행하|쫓아오)",
    ),
    "crisis": (
        r"(?:아침에\s*)?(?:안|못)\s*깼으면|(?:다시는\s*)?안\s*일어났으면",
        r"(?:다|모든\s*걸|모든\s*것을?|전부|인생을?)\s*끝내기로|오늘\s*밤\s*(?:다|모든\s*걸|전부|내\s*인생을?)\s*끝낼",
        r"사는\s*(?:게|것이|것에)\s*(?:너무\s*)?지쳤|살기\s*(?:너무\s*)?지쳤|사는\s*게\s*지친다",
        r"내가\s*없으면[^\n]{0,10}?(?:나을|낫|행복|편할)",
    ),
    "anger_kill": (
        r"(?:화가?\s*나|열받|빡쳐|분노|미치겠)[^\n]{0,14}?죽일\s*(?:수도|것\s*같|거\s*같|거야)|(?:그를|그놈을?|걔를?|그\s*사람을?|그녀를|남편을?)\s*죽여\s*버리고\s*싶",
    ),
    "anger": (
        r"(?:화가?\s*나서|열받아서|분노로|빡쳐서)\s*(?:손|몸|온몸)이\s*(?:막\s*)?떨",
        r"(?:다|전부|모든\s*걸|모든\s*것을?)\s*(?:부숴|때려\s*부수|박살\s*내)\s*(?:버리고\s*)?싶",
    ),
    "heavy": (
        r"눈물이\s*(?:멈추지\s*않|안\s*멈|멈추질\s*않|안\s*그쳐|계속\s*나)|울음이\s*(?:안\s*)?(?:그치지\s*않|안\s*그쳐|멈추지\s*않)|계속\s*울고\s*있",
        r"텅\s*빈\s*것\s*같|공허|아무\s*(?:느낌|감정|기분)(?:이|도)\s*(?:없|안\s*들)",
        r"(?:나한텐|나에겐|내겐|이제|나한테)\s*(?:이제\s*)?아무것도\s*(?:안\s*)?남(?:지\s*않|았|은\s*게\s*없)",
        r"기분이\s*바닥|바닥을\s*쳤|(?:너무|진짜|완전)\s*우울|한계야",
    ),
}
_KO_NOT = re.compile(r"영화|드라마|노래|책|영상|웹툰|애니|소설|결말|주가|주식|가격|코인|고양이|강아지|개가|새가|뱀|벌레|거미|게임|배터리|냉장고|지갑")

# ── ภาษาสเปน ─────────────────────────────────────────────────────────
_ES_FEAR = r"(?:tengo\s+(?:mucho\s+)?miedo|me\s+da\s+(?:mucho\s+)?miedo|estoy\s+(?:muy\s+)?(?:asustad|aterrad)|qu[ée]\s+miedo|me\s+muero\s+de\s+miedo)"
ES = {
    "danger": (
        r"(?:est[áa]n?|hay\s+alguien|sigue|se\s+qued[óo]|lleg[óo])\s+(?:parad[oa]\s+)?(?:afuera|fuera|frente|enfrente|en\s+la\s+puerta|a\s+la\s+puerta|abajo)\s*(?:de\s+)?(?:mi|la)?\s*(?:casa|puerta|cuarto|depa(?:rtamento)?|ventana|edificio)?" + r"[^.\n]{0,24}?" + _ES_FEAR,
        r"no\s+puedo\s+(?:hablar|escribir|chatear)\s+(?:mucho|much[oa]\s+tiempo|por\s+mucho\s+tiempo|largo)[^\n]{0,28}?(?:va\s+a\s+(?:volver|regresar|llegar)|vuelve|regresa|ya\s+viene|est[áa]\s+por\s+(?:volver|llegar))",
        r"no\s+me\s+siento\s+(?:a\s+salvo|segur[oa])\s*(?:en\s+(?:mi\s+)?casa|aqu[ií]|con\s+(?:él|ella|mi\s+\w+))|^\W*no\s+estoy\s+a\s+salvo",
        r"(?:alguien|un\s+(?:hombre|tipo|desconocido|señor)|una\s+persona)\s+me\s+(?:est[áa]\s+siguiendo|sigue|viene\s+siguiendo)",
    ),
    "crisis": (
        r"quiero\s+desaparecer(?!\s+(?:de\s+(?:las\s+redes|instagram|internet|facebook|tiktok)|un\s+rato|unos\s+d[ií]as|del\s+trabajo))|desaparecer\s+del\s+mundo",
        r"(?:quisiera|ojal[áa]|me\s+gustar[ií]a)\s+(?:ya\s+)?no\s+(?:volver\s+a\s+)?despertar",
        r"decid[ií][^.\n]{0,24}?(?:terminar|acabar)\s+con\s+todo(?!\s+(?:el|la|los|las|mi|lo\s+de)\b)|(?:esta\s+noche|hoy)[^.\n]{0,8}?(?:terminar|acabar|termino|acabo)\s+con\s+todo(?!\s+(?:el|la|los|las|mi|lo\s+de)\b)|(?:terminar|acabar)\s+con\s+todo\s+(?:esta\s+noche|hoy|ya)",
        r"(?:todos|todo\s+el\s+mundo|mi\s+familia)\s+(?:estar[ií]an?|vivir[ií]an?|ser[ií]an?)\s+(?:m[áa]s\s+felices|mejor)\s+sin\s+m[ií]",
    ),
    "anger_kill": (
        r"(?:enojad|furios|encabronad|enfadad)[oa]s?[^.\n]{0,20}?(?:(?:podr[ií]a|quiero|voy\s+a)\s+matarl[oa]s?|l[oa]s?\s+(?:voy\s+a|podr[ií]a|quiero)\s+matar)|(?:rabia|coraje|ira)[^.\n]{0,20}?matarl[oa]s?",
    ),
    "anger": (
        r"(?:rabia|coraje|ira|enojad[oa]|furios[oa]|enfadad[oa])[^.\n]{0,24}?(?:me\s+tiemblan\s+las\s+manos|tiemblo|estoy\s+temblando|me\s+tiembla\s+todo)",
        r"quiero\s+(?:romper|destrozar|destruir|quebrar)\s+todo",
    ),
    "heavy": (
        r"no\s+(?:puedo|logro)\s+(?:parar|dejar)\s+de\s+llorar|no\s+paro\s+de\s+llorar|llorando\s+sin\s+parar",
        r"me\s+siento\s+(?:muy\s+|tan\s+|completamente\s+|tod[oa]\s+)?(?:vac[ií][oa]|entumecid[oa]|huec[oa]|insensible)|ya\s+no\s+siento\s+nada",
        r"ya\s+no\s+me\s+queda\s+nada(?!\s+(?:de|en|que\s+(?:decir|hacer|comer)))|no\s+me\s+queda\s+nada\s*$",
        r"estoy\s+(?:por\s+los\s+suelos|hundid[oa]|destrozad[oa]|deprimid[oa]|en\s+el\s+fondo)",
    ),
}
_ES_NOT = re.compile(r"pel[ií]cula|serie|canci[óo]n|libro|video|v[ií]deo|novela|final|episodio|acciones|bolsa|precio|perro|gato|ara[ñn]a|insecto|p[áa]jaro|juego|partido|nevera|refri|bater[ií]a|cartera", re.I)

# ── ภาษาเวียดนาม ─────────────────────────────────────────────────────
_VI_WHO = r"(?:anh\s+ta|anh\s+ấy|hắn|chồng(?:\s+cũ)?(?:\s+(?:tôi|em|mình))?|người\s+yêu\s+cũ|người\s+đó|người\s+lạ|ai\s+đó|có\s+người|thằng\s+đó|gã\s+đó|nó|ông\s+ta)"
VI = {
    "danger": (
        _VI_WHO + r"\s+(?:đang\s+|vẫn\s+)?(?:ở|đứng|tới|đến|chờ|đợi)\s+(?:ở\s+)?(?:trước|ngoài|ngay)\s+(?:cửa|nhà|phòng|cổng)[^\n]{0,24}?(?:sợ|run)",
        r"không\s+(?:thể\s+)?(?:nói|nhắn|chat|gõ)\s+(?:lâu|nhiều)(?:\s+được)?[^\n]{0,24}?(?:sắp|đang|sẽ|chuẩn\s+bị)\s+(?:về|quay\s+(?:lại|về)|trở\s+về)",
        r"không\s+(?:thấy|cảm\s+thấy)\s+an\s+toàn|^\W*không\s+an\s+toàn",
        r"(?:có\s+người|ai\s+đó|một\s+người|người\s+lạ|thằng|gã)\s+(?:nào\s+đó\s+)?(?:đang\s+)?(?:theo\s+dõi|bám\s+theo|đi\s+theo|theo\s+sau)\s+(?:tôi|mình|em)",
    ),
    "crisis": (
        r"muốn\s+biến\s+mất(?!\s+(?:khỏi\s+(?:mạng|facebook|nhóm|group)|vài\s+ngày|một\s+lúc))",
        r"ước\s+(?:gì\s+)?(?:mình|tôi|em)?\s*(?:không|đừng)\s+(?:bao\s+giờ\s+)?(?:thức\s+dậy|tỉnh\s+dậy|tỉnh\s+lại)",
        r"quyết\s+định\s+(?:sẽ\s+)?kết\s+thúc\s+(?:mọi\s+thứ|tất\s+cả|cuộc\s+đời)|kết\s+thúc\s+(?:mọi\s+thứ|tất\s+cả)\s+(?:tối\s+nay|hôm\s+nay|đêm\s+nay)",
        r"mệt\s+mỏi\s+vì\s+(?:phải\s+)?sống|chán\s+sống|không\s+có\s+(?:tôi|mình|em)[^\n]{0,26}?(?:tốt\s+hơn|hạnh\s+phúc\s+hơn|nhẹ\s+nhõm\s+hơn)",
    ),
    "anger_kill": (
        r"(?:tức|giận|điên|cáu)[^\n]{0,20}?(?:có\s+thể\s+|muốn\s+|sẽ\s+)?giết\s+(?:chết\s+)?(?:anh\s+ta|hắn|nó|cô\s+ta|ông\s+ta|thằng\s+đó)",
    ),
    "anger": (
        r"(?:tức|giận|điên)\s+(?:đến|tới)\s+(?:mức\s+)?run\s+(?:cả\s+)?(?:tay|người)",
        r"muốn\s+(?:đập|phá|đập\s+phá|đập\s+nát|đập\s+vỡ)\s+(?:hết\s+)?(?:mọi\s+thứ|tất\s+cả|hết)",
    ),
    "heavy": (
        r"khóc\s+(?:không\s+(?:ngừng|dừng|nín)(?:\s+được)?|mãi\s+không\s+(?:ngừng|dừng|nín))|không\s+(?:thể\s+)?(?:ngừng|nín)\s+khóc",
        r"trống\s+rỗng|tê\s+liệt(?!\s+(?:giao\s+thông|chân|tay|hệ\s+thống))|vô\s+cảm|không\s+còn\s+cảm\s+giác",
        r"(?:chẳng|không)\s+còn\s+(?:lại\s+)?(?:gì|thứ\s+gì)\s+(?:nữa|cả)(?!\s+(?:trong|để\s+ăn))",
        r"tâm\s+trạng\s+(?:tụt\s+dốc|xuống\s+dốc|chạm\s+đáy|tệ\s+lắm)|suy\s+sụp|kiệt\s+quệ\s+tinh\s+thần",
    ),
}
_VI_NOT = re.compile(r"\bphim\b|bài\s+hát|truyện|sách|video|cổ\s+phiếu|chứng\s+khoán|giá|con\s+(?:chó|mèo|rắn|nhện)|game|trận\s+đấu|tủ\s+lạnh|điện\s+thoại|pin", re.I)

_BY_LANG = {"zh": (ZH, _ZH_NOT), "ja": (JA, _JA_NOT), "ko": (KO, _KO_NOT), "es": (ES, _ES_NOT), "vi": (VI, _VI_NOT)}
_RX = {lg: {k: [re.compile(p, re.I | re.M) for p in ps] for k, ps in d.items()} for lg, (d, _) in _BY_LANG.items()}
# สิ่งที่ไม่ใช่เรื่องของคน ตัดเฉพาะชนิดที่เบากว่าวิกฤต — "เขาอยู่หน้าบ้าน ฉันกลัว" ที่บังเอิญมีคำว่า "หนัง" ยังไม่ทิ้ง
_NOT_FOR = {"heavy", "anger", "danger"}


def mood_lang(text) -> str | None:
    from core.lang_signals import detect_lang, script_lang
    t = str(text or "")
    if script_lang(t) == "vi":
        return "vi"
    lg = detect_lang(t)
    return lg if lg in _RX else None


def mood_intl(text):
    """→ (ชนิด, ภาษา) ที่หนักที่สุด หรือ None · ชนิด: crisis danger anger_kill anger heavy"""
    t = str(text or "")
    lg = mood_lang(t)
    if not lg:
        return None
    rx, not_rx = _RX[lg], _BY_LANG[lg][1]
    for kind in ORDER:
        if any(p.search(t) for p in rx.get(kind, ())):
            if kind in _NOT_FOR and not_rx.search(t):
                continue
            return kind, lg
    return None


# ── คำตอบ (เปิดด้วยการรับฟัง · สามข้อ · คำถามเบาๆ หนึ่งข้อ) ──────────────────
MOOD_REPLY = {
    "heavy": {
        "zh": ("听起来真的很沉重，谢谢你愿意告诉我。", [
            "不用急着解决什么 — 先让身体慢下来：喝口水，慢慢呼气几次，呼气比吸气长一点。",
            "如果心里出现不想活下去的念头，请马上找人说：在泰国拨打 1323（24小时）；在中国可拨 12356 心理援助热线。",
            "给一个信得过的人发一句“我现在不太好”就够了，不需要解释太多。"],
            "我想轻轻问一下：现在是累到撑不住，还是也有不想活下去的念头？哪种回答都可以，我在这里。"),
        "ja": ("とてもつらそうですね。話してくれてありがとう。", [
            "今すぐ何かを解決しなくて大丈夫です。まず水を一口飲んで、吐く息を長めにゆっくり呼吸してみてください。",
            "もし「生きていたくない」という気持ちが混ざっているなら、すぐ誰かに話してください：タイでは 1323（24時間）、日本では いのちの電話 0570-783-556。",
            "信頼できる人に「今ちょっとつらい」と一言送るだけでも十分です。"],
            "そっと聞かせてください：今は疲れ切っている感じですか、それとも消えたい・生きていたくない気持ちもありますか？どちらでも大丈夫、ここにいます。"),
        "ko": ("정말 많이 힘들게 들려요. 말해줘서 고마워요.", [
            "지금 당장 뭔가를 해결하지 않아도 괜찮아요. 물 한 모금 마시고, 내쉬는 숨을 조금 길게 천천히 쉬어 보세요.",
            "혹시 살고 싶지 않은 마음이 섞여 있다면 바로 이야기해 주세요: 태국에서는 1323(24시간), 한국에서는 자살예방 상담전화 109(24시간).",
            "믿을 만한 사람에게 \"나 지금 좀 힘들어\" 한마디만 보내도 충분해요."],
            "조심스럽게 물어볼게요: 지금은 너무 지친 건가요, 아니면 살고 싶지 않은 생각도 함께 드나요? 어떤 대답이든 괜찮아요. 여기 있을게요."),
        "es": ("Suena muy pesado. Gracias por contármelo.", [
            "No tienes que resolver nada ahora mismo: bebe un poco de agua y respira despacio, soltando el aire más largo de lo que lo tomas.",
            "Si aparecen pensamientos de no querer vivir, habla con alguien ya: en Tailandia 1323 (24 h); en España 024; en México Línea de la Vida 800 911 2000.",
            "Mándale a alguien de confianza un “no estoy bien” — no necesitas explicar más."],
            "Te pregunto con cuidado: ¿es agotamiento y saturación, o también hay pensamientos de no querer estar aquí? Cualquier respuesta está bien. Aquí estoy."),
        "vi": ("Nghe thật sự rất nặng nề. Cảm ơn bạn đã kể cho mình.", [
            "Không cần giải quyết gì ngay lúc này — uống một ngụm nước, thở chậm, thở ra dài hơn hít vào.",
            "Nếu có ý nghĩ không muốn sống, hãy nói với ai đó ngay: ở Thái Lan gọi 1323 (24 giờ); ngoài Thái Lan tìm đường dây hỗ trợ tại findahelpline.com.",
            "Nhắn cho một người bạn tin tưởng một câu “mình đang không ổn” là đủ, không cần giải thích nhiều."],
            "Mình hỏi nhẹ thôi: bây giờ là mệt mỏi, quá tải, hay có cả ý nghĩ không muốn sống nữa? Trả lời thế nào cũng được. Mình ở đây."),
    },
    "anger": {
        "zh": ("这么强烈的愤怒，身体也在承受 — 先别急着做任何事。", [
            "先离开让你生气的人或东西，去另一个房间或到外面走 10 分钟。",
            "双手用力握拳再松开几次，慢慢呼气，让呼气比吸气长 — 心跳会慢下来。",
            "等平静下来再决定要说什么、做什么。如果觉得快控制不住自己，在泰国拨打 1323 聊一聊。"],
            "是谁或什么事让你这么生气？身边有人可能会被波及吗？"),
        "ja": ("こんなに強い怒りは、体にも大きな負担です — 今は何かをする前に、少し間を置きましょう。", [
            "怒りの相手や物から離れて、別の部屋か外へ 10 分ほど出てください。",
            "両手をぎゅっと握って開くのを数回、吐く息を長めに — 心拍が落ち着いてきます。",
            "落ち着いてから、何を言うか・どうするかを決めましょう。抑えられそうにないときは、タイでは 1323 に電話できます。"],
            "誰に、または何に怒っていますか？そばに巻き込まれそうな人はいますか？"),
        "ko": ("이렇게 강한 화는 몸도 함께 견디고 있는 거예요 — 지금은 뭔가 하기 전에 잠깐 멈춰요.", [
            "화나게 한 사람이나 물건에서 떨어져서, 다른 방이나 밖으로 10분만 나가 보세요.",
            "두 손을 꽉 쥐었다 펴기를 몇 번, 내쉬는 숨을 길게 — 심장이 조금씩 가라앉아요.",
            "진정된 다음에 무슨 말을 하고 어떻게 할지 정해요. 스스로 감당이 안 될 것 같으면 태국에서는 1323, 한국에서는 109에 전화할 수 있어요."],
            "누구에게, 또는 무엇 때문에 이렇게 화가 났나요? 곁에 휘말릴 수 있는 사람이 있나요?"),
        "es": ("Una rabia así de fuerte también la carga el cuerpo — antes de hacer nada, date un momento.", [
            "Aléjate de la persona o de lo que te enfureció: otra habitación o afuera, unos 10 minutos.",
            "Aprieta y suelta los puños varias veces y suelta el aire más largo de lo que lo tomas — el corazón baja el ritmo.",
            "Decide qué decir o hacer cuando estés más tranquilo. Si sientes que no te puedes contener, en Tailandia llama al 1323; en España al 024."],
            "¿Con quién o con qué estás tan enojado? ¿Hay alguien cerca que podría salir lastimado?"),
        "vi": ("Cơn giận mạnh như vậy cơ thể cũng đang gánh chịu — trước khi làm gì, hãy dừng lại một chút.", [
            "Rời khỏi người hoặc thứ làm bạn giận: sang phòng khác hoặc ra ngoài khoảng 10 phút.",
            "Nắm chặt rồi thả lỏng hai tay vài lần, thở ra dài hơn hít vào — tim sẽ đập chậm lại.",
            "Đợi bình tĩnh rồi mới quyết định nói gì, làm gì. Nếu thấy khó kiềm chế, ở Thái Lan gọi 1323 để nói chuyện."],
            "Bạn đang giận ai hay chuyện gì? Có ai ở gần có thể bị vạ lây không?"),
    },
    "anger_kill": {
        "zh": ("谢谢你说出来，而不是去做 — 这很重要。", [
            "现在先离开那个人，拉开距离，至少等 20 分钟让怒气退下去。",
            "把刀具或任何可能伤人的东西放远一点。",
            "如果觉得快控制不住自己，拨打 110，或在泰国拨打 1323（24小时）谈一谈 — 不会有人评判你。"],
            "你现在和那个人在同一个地方吗？"),
        "ja": ("行動に移す前に言葉にしてくれてありがとう — それはとても大事なことです。", [
            "今はその人から離れて距離を取り、怒りが下がるまで少なくとも 20 分待ってください。",
            "刃物や傷つけられる物は手の届かない所へ。",
            "抑えられそうにないなら 110、タイでは 1323（24時間）に話してください。責められることはありません。"],
            "今、その人と同じ場所にいますか？"),
        "ko": ("행동하기 전에 말로 꺼내줘서 고마워요 — 그건 정말 중요해요.", [
            "지금은 그 사람에게서 떨어져서 거리를 두고, 화가 가라앉을 때까지 최소 20분 기다려 주세요.",
            "칼이나 다칠 수 있는 물건은 손이 닿지 않는 곳에 두세요.",
            "스스로 감당이 안 될 것 같으면 112, 태국에서는 1323(24시간)에 전화해서 이야기해요. 아무도 당신을 탓하지 않아요."],
            "지금 그 사람과 같은 곳에 있나요?"),
        "es": ("Gracias por decirlo en vez de hacerlo — eso importa mucho.", [
            "Aléjate ahora de esa persona y date al menos 20 minutos para que baje la rabia.",
            "Pon cuchillos o cualquier cosa que pueda hacer daño fuera de tu alcance.",
            "Si sientes que no te puedes controlar, llama al 112 / 911, o en Tailandia al 1323 (24 h) para hablarlo — nadie te va a juzgar."],
            "¿Estás ahora en el mismo lugar que esa persona?"),
        "vi": ("Cảm ơn bạn đã nói ra thay vì làm — điều đó rất quan trọng.", [
            "Bây giờ hãy rời xa người đó, giữ khoảng cách ít nhất 20 phút cho cơn giận lắng xuống.",
            "Để dao hoặc bất cứ thứ gì có thể gây thương tích ra xa tầm tay.",
            "Nếu thấy khó kiềm chế, gọi 191 (cảnh sát Thái Lan) hoặc 1323 (24 giờ) để nói chuyện — không ai phán xét bạn."],
            "Bạn đang ở cùng chỗ với người đó không?"),
    },
}
