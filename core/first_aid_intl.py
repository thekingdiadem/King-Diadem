"""คำแนะนำปฐมพยาบาลเฉพาะเรื่องสำหรับภาษาอื่นนอกจากไทย (en es vi zh ko ja)

ตัวจับแบบประกอบชิ้นส่วน (core/frames.py) เห็นอันตรายได้ทุกภาษา แต่คำตอบภาษาอื่นเคยเป็นแบบทั่วไป
เช่น งูกัดในภาษาสเปนได้ "เขียนเรื่องที่เกิดเป็นประโยคเดียว" หรือภาษาอังกฤษได้แค่ "จดเวลาที่อาการเริ่ม"
ที่นี่เก็บหนึ่งบรรทัดต่อเรื่อง ต่อภาษา ใส่แทนขั้นที่สองของคำตอบฉุกเฉิน (ขั้นแรกยังเป็นการโทรเรียกรถพยาบาล)

กฎล้วน ไม่ใช้ AI — ถ้อยคำควรให้แพทย์ตรวจก่อนใช้จริง
"""
from __future__ import annotations

# เรียงตามความสำคัญ — ถ้าข้อความเข้าหลายเรื่อง ใช้เรื่องแรกที่พบ
LINES = {
    "snakebite": {
        "en": "Snakebite: keep still, splint the limb and keep it below the heart, remove rings · no tourniquet, no cutting, no sucking out venom · don't try to catch the snake.",
        "es": "Mordedura de serpiente: quieto, inmoviliza la extremidad por debajo del corazón y quita anillos · no hagas torniquete, no cortes ni succiones el veneno · no intentes atrapar la serpiente.",
        "vi": "Rắn cắn: giữ nằm yên, cố định chi bị cắn thấp hơn tim, tháo nhẫn · không garô, không rạch, không hút nọc · đừng cố bắt con rắn.",
        "zh": "被蛇咬：保持不动，把被咬的肢体固定并放低于心脏，摘下戒指 · 不要扎止血带，不要切开或吸毒 · 不要去抓蛇。",
        "ko": "뱀에 물렸을 때: 움직이지 말고 물린 팔다리를 고정해 심장보다 낮게 두고 반지를 빼세요 · 지혈대로 묶거나 째거나 독을 빨지 마세요 · 뱀을 잡으려 하지 마세요.",
        "ja": "ヘビにかまれたら：動かず、かまれた手足を固定して心臓より低くし、指輪を外す · 縛らない、切らない、毒を吸わない · ヘビを捕まえようとしない。",
    },
    "mushroom": {
        "en": "Wild mushrooms: everyone who ate them should go to hospital, even if they feel better — some poisonous mushrooms damage the liver later · bring leftovers or a photo · don't force vomiting.",
        "es": "Hongos silvestres: todos los que comieron deben ir al hospital aunque se sientan mejor — algunos dañan el hígado después · lleva los restos o una foto · no provoques el vómito.",
        "vi": "Nấm rừng: mọi người đã ăn đều phải đến bệnh viện, kể cả khi thấy đỡ — có loại nấm độc phá hủy gan về sau · mang nấm còn lại hoặc ảnh chụp · không móc họng gây nôn.",
        "zh": "吃了野蘑菇：所有吃过的人都要去医院，即使感觉好转 — 有些毒蘑菇之后会损伤肝脏 · 带上剩下的蘑菇或照片 · 不要催吐。",
        "ko": "야생 버섯: 먹은 사람 모두 병원에 가세요. 나아진 것 같아도 일부 독버섯은 나중에 간을 손상시킵니다 · 남은 버섯이나 사진을 가져가세요 · 억지로 토하게 하지 마세요.",
        "ja": "野生のキノコ：食べた人は全員、良くなったようでも病院へ — 後から肝臓を壊す毒キノコがあります · 残りか写真を持参 · 無理に吐かせない。",
    },
    "elder_fall": {
        "en": "Older person who can't get up after a fall: don't pull them up — the hip may be broken · keep them warm with a pillow under the head · tell the doctor if they were on the floor for hours.",
        "es": "Persona mayor que no puede levantarse tras una caída: no la levantes a la fuerza, puede tener la cadera rota · abrígala y ponle una almohada · avisa al médico si estuvo horas en el suelo.",
        "vi": "Người già ngã không dậy được: đừng kéo dậy — có thể gãy xương hông · giữ ấm, kê gối dưới đầu · báo bác sĩ nếu đã nằm dưới sàn nhiều giờ.",
        "zh": "老人摔倒起不来：不要硬拉起来，可能髋部骨折 · 给他保暖，头下垫枕头 · 如果在地上躺了好几个小时，要告诉医生。",
        "ko": "어르신이 넘어져 못 일어나면: 억지로 일으키지 마세요. 고관절 골절일 수 있어요 · 따뜻하게 덮고 머리에 베개를 받쳐 주세요 · 바닥에 몇 시간 있었다면 의사에게 꼭 말하세요.",
        "ja": "高齢者が転んで起き上がれない：無理に起こさない — 股関節の骨折かもしれません · 保温し頭に枕を · 何時間も床にいた場合は医師に伝える。",
    },
    "alcohol_withdrawal": {
        "en": "Alcohol withdrawal with hallucinations, seizures or confusion can be fatal — it needs hospital care · don't give alcohol or sleeping pills to calm it · stay with them; if they seize, roll them onto their side.",
        "es": "La abstinencia de alcohol con alucinaciones, convulsiones o confusión puede ser mortal — necesita hospital · no le des alcohol ni pastillas para dormir · quédate con la persona; si convulsiona, ponla de lado.",
        "vi": "Cai rượu mà có ảo giác, co giật hoặc lú lẫn có thể tử vong — cần nằm viện · không cho uống rượu hay thuốc ngủ để đỡ · ở bên cạnh; nếu co giật, đặt nằm nghiêng.",
        "zh": "戒酒后出现幻觉、抽搐或神志不清可能致命 — 需要住院 · 不要给酒或安眠药来缓解 · 有人陪着；抽搐时让他侧躺。",
        "ko": "술을 끊은 뒤 환각, 경련, 혼란이 오면 생명이 위험할 수 있어요 — 입원 치료가 필요합니다 · 술이나 수면제를 주지 마세요 · 곁에 있어 주고, 경련하면 옆으로 눕혀 주세요.",
        "ja": "断酒後の幻覚・けいれん・錯乱は命に関わります — 入院が必要です · お酒や睡眠薬で抑えようとしない · そばにいて、けいれんしたら横向きに寝かせる。",
    },
    "rabies_exposure": {
        "en": "Animal bite or scratch: wash it with soap and running water for at least 15 minutes, then get a rabies vaccine today — even for a small scratch. Once symptoms start rabies can't be cured, but the vaccine in time prevents it.",
        "es": "Mordedura o arañazo de animal: lava con agua corriente y jabón al menos 15 minutos y ve hoy a vacunarte contra la rabia, aunque sea un rasguño. Con síntomas ya no tiene cura; la vacuna a tiempo la evita.",
        "vi": "Bị chó mèo cắn hoặc cào: rửa vết thương bằng xà phòng dưới vòi nước ít nhất 15 phút rồi đi tiêm phòng dại ngay hôm nay, dù chỉ là vết xước. Khi đã phát bệnh dại thì không chữa được, nhưng tiêm kịp thời sẽ phòng được.",
        "zh": "被动物咬伤或抓伤：用肥皂和流动的水冲洗至少 15 分钟，今天就去打狂犬疫苗，哪怕只是抓伤。狂犬病一旦发病无法治愈，及时打疫苗可以预防。",
        "ko": "동물에게 물리거나 긁혔다면: 비누와 흐르는 물로 15분 이상 씻고 오늘 바로 광견병 예방접종을 받으세요. 작은 상처라도요. 증상이 나타나면 치료가 안 되지만 제때 맞으면 막을 수 있어요.",
        "ja": "動物にかまれた・引っかかれた：石けんと流水で 15 分以上洗い、今日中に狂犬病ワクチンを受けてください。小さな傷でも。発症すると治せませんが、間に合えば防げます。",
    },
    "leptospirosis": {
        "en": "Fever after wading in floodwater or rice fields: tell the doctor exactly what you were doing — it may be leptospirosis, which antibiotics treat well if started early.",
        "es": "Fiebre después de caminar en agua de inundación o en arrozales: dile al médico lo que hiciste — puede ser leptospirosis, que se trata bien con antibióticos si se empieza pronto.",
        "vi": "Sốt sau khi lội nước lũ hoặc làm ruộng: nói rõ với bác sĩ bạn đã làm gì — có thể là bệnh xoắn khuẩn (leptospira), điều trị tốt bằng kháng sinh nếu bắt đầu sớm.",
        "zh": "蹚水或下田后发烧：告诉医生你做过什么 — 可能是钩端螺旋体病，早用抗生素效果很好。",
        "ko": "홍수 물이나 논에 들어간 뒤 열이 나면: 의사에게 무엇을 했는지 꼭 말하세요 — 렙토스피라증일 수 있고, 일찍 항생제를 쓰면 잘 낫습니다.",
        "ja": "洪水や田んぼに入った後の発熱：何をしていたか医師に必ず伝える — レプトスピラ症の可能性があり、早く抗菌薬を始めればよく治ります。",
    },
    "melioidosis": {
        "en": "Fever in someone with diabetes who works in soil or rice fields: go to hospital today and mention the farm work — it may be melioidosis, which needs specific antibiotics quickly.",
        "es": "Fiebre en una persona con diabetes que trabaja la tierra o el arrozal: al hospital hoy y menciona el trabajo en el campo — puede ser melioidosis, que necesita antibióticos específicos pronto.",
        "vi": "Người tiểu đường làm ruộng, tiếp xúc đất bùn mà sốt: đến bệnh viện ngay hôm nay và nói rõ việc làm ruộng — có thể là bệnh Whitmore, cần kháng sinh đặc hiệu sớm.",
        "zh": "糖尿病人干农活、接触泥土后发烧：今天就去医院，并说明务农经历 — 可能是类鼻疽，需要尽快用特定抗生素。",
        "ko": "당뇨가 있고 흙이나 논에서 일하는 분이 열이 나면: 오늘 병원에 가서 농사일을 한다고 말하세요 — 유비저일 수 있고 빨리 특정 항생제가 필요합니다.",
        "ja": "糖尿病があり土や田んぼで働く人の発熱：今日病院へ行き、農作業のことを伝える — 類鼻疽の可能性があり、早く専用の抗菌薬が必要です。",
    },
    "preeclampsia": {
        "en": "Pregnant with a severe headache, blurred vision, upper belly pain or sudden swelling of face and hands: this may be pre-eclampsia — go to hospital now and bring your pregnancy record.",
        "es": "Embarazada con dolor de cabeza fuerte, visión borrosa, dolor en la boca del estómago o hinchazón repentina de cara y manos: puede ser preeclampsia — ve al hospital ahora con tu cartilla de embarazo.",
        "vi": "Mang thai mà đau đầu dữ dội, mờ mắt, đau vùng thượng vị hoặc phù mặt tay đột ngột: có thể là tiền sản giật — đến bệnh viện ngay, mang theo sổ khám thai.",
        "zh": "怀孕时剧烈头痛、视物模糊、上腹痛或脸手突然浮肿：可能是子痫前期 — 现在就去医院，带上孕检手册。",
        "ko": "임신 중 심한 두통, 흐린 시야, 명치 통증, 얼굴과 손이 갑자기 부으면: 전자간증일 수 있어요 — 지금 산모수첩을 챙겨 병원에 가세요.",
        "ja": "妊娠中のひどい頭痛・目のかすみ・みぞおちの痛み・顔や手の急なむくみ：妊娠高血圧腎症の可能性 — 母子手帳を持って今すぐ病院へ。",
    },
}

# เรื่องที่พบบ่อยจากรอบก่อนๆ — บรรทัด en ใช้เฉพาะตอนข้อความภาษาอังกฤษได้คำตอบฉุกเฉินทั่วไป (เรื่องที่มี en_stroke en_allergy ฯลฯ ใช้คำตอบเดิม)
LINES.update({
    "cardiac": {
        "en": "Possible heart attack: have them sit and rest, loosen tight clothing · don't let them drive or walk to get help · if they stop responding and aren't breathing, start chest compressions.",
        "es": "Posible infarto: que se siente y descanse, afloja la ropa · no lo dejes conducir ni caminar · si deja de responder y no respira, empieza compresiones en el pecho.",
        "vi": "Có thể là nhồi máu cơ tim: cho ngồi nghỉ, nới lỏng quần áo · không để tự lái xe hay đi lại · nếu bất tỉnh và ngừng thở, ép tim ngay.",
        "zh": "可能是心梗：让他坐下休息，松开衣服 · 不要让他自己开车或走动 · 如果叫不醒、没有呼吸，马上做胸外按压。",
        "ko": "심근경색일 수 있어요: 앉혀서 쉬게 하고 옷을 느슨하게 · 직접 운전하거나 걷게 하지 마세요 · 반응이 없고 숨을 안 쉬면 바로 가슴압박을 시작하세요.",
        "ja": "心筋梗塞の可能性：座って安静にし、服をゆるめる · 自分で運転・歩かせない · 反応がなく呼吸していなければすぐ胸骨圧迫を。",
    },
    "stroke": {
        "en": "This could be a stroke — every minute counts: note the time symptoms started · no food, drink or medicine · treatment works much better within 4.5 hours.",
        "es": "Puede ser un ictus — cada minuto cuenta: anota la hora en que empezaron los síntomas · no le des comida, bebida ni medicinas · el tratamiento funciona mucho mejor en las primeras 4,5 horas.",
        "vi": "Có thể là đột quỵ — từng phút đều quan trọng: ghi lại giờ bắt đầu triệu chứng · không cho ăn uống hay uống thuốc · điều trị trong 4,5 giờ đầu hiệu quả hơn nhiều.",
        "zh": "可能是中风，每一分钟都重要：记下症状开始的时间 · 不要给吃喝或吃药 · 4.5 小时内治疗效果好得多。",
        "ko": "뇌졸중일 수 있어요. 1분 1초가 중요합니다: 증상이 시작된 시각을 적어 두세요 · 음식, 물, 약을 주지 마세요 · 4.5시간 안에 치료하면 훨씬 효과가 좋아요.",
        "ja": "脳卒中の可能性 — 一分一秒が大切：症状が始まった時刻をメモ · 食べ物・飲み物・薬を与えない · 4.5時間以内の治療がずっと効果的です。",
    },
    "anaphylaxis": {
        "en": "Severe allergy: use an epinephrine auto-injector (EpiPen) now if there is one · sit up if breathing is hard, lie down with legs raised if faint · don't leave them alone.",
        "es": "Alergia grave: si tiene autoinyector de adrenalina (EpiPen), úsalo ya · si le cuesta respirar, que se siente; si se marea, acuéstalo con las piernas en alto · no lo dejes solo.",
        "vi": "Dị ứng nặng: nếu có bút tiêm adrenaline (EpiPen), tiêm ngay · khó thở thì cho ngồi; choáng thì nằm kê chân cao · không để ở một mình.",
        "zh": "严重过敏：如果有肾上腺素笔（EpiPen）马上用 · 呼吸困难就坐着，头晕就平躺抬高双腿 · 不要让他一个人待着。",
        "ko": "심한 알레르기: 에피네프린 자동주사기(에피펜)가 있으면 바로 쓰세요 · 숨쉬기 힘들면 앉히고, 어지러우면 눕혀서 다리를 올려 주세요 · 혼자 두지 마세요.",
        "ja": "重いアレルギー：エピペンがあればすぐ使う · 息が苦しければ座らせ、ふらつくなら足を上げて寝かせる · 一人にしない。",
    },
    "poison": {
        "en": "Swallowed a chemical: don't make them vomit and don't give milk or oil · rinse the mouth with water · keep the container and call poison control (1367 in Thailand, 1-800-222-1222 in the US).",
        "es": "Tragó un químico: no provoques el vómito y no le des leche ni aceite · enjuágale la boca con agua · guarda el envase y llama a toxicología o a emergencias.",
        "vi": "Uống phải hóa chất: không gây nôn, không cho uống sữa hay dầu · súc miệng bằng nước · giữ lại chai lọ và gọi cấp cứu hoặc trung tâm chống độc.",
        "zh": "误服化学品：不要催吐，不要喝牛奶或油 · 用清水漱口 · 保留瓶子，打急救或中毒咨询电话。",
        "ko": "화학제품을 삼켰다면: 억지로 토하게 하지 말고 우유나 기름도 주지 마세요 · 물로 입을 헹궈 주세요 · 용기를 챙겨 119나 중독상담에 전화하세요.",
        "ja": "化学品を飲んだ：無理に吐かせない、牛乳や油を飲ませない · 水で口をすすぐ · 容器を持って救急か中毒110番に電話。",
    },
    "electric": {
        "en": "Electric shock: cut the power before touching them; if you can't, push them away with something dry and non-metal · no breathing: chest compressions · go to hospital even if they seem fine.",
        "es": "Descarga eléctrica: corta la corriente antes de tocarlo; si no puedes, apártalo con algo seco que no sea metal · si no respira, compresiones en el pecho · al hospital aunque parezca bien.",
        "vi": "Bị điện giật: ngắt điện trước khi chạm vào; nếu không được, dùng vật khô không phải kim loại đẩy ra · ngừng thở thì ép tim · vẫn đi bệnh viện dù trông ổn.",
        "zh": "触电：先断电再碰他；断不了就用干燥的非金属物把他推开 · 没呼吸就做胸外按压 · 看起来没事也要去医院。",
        "ko": "감전: 먼저 전원을 끄고 만지세요. 끌 수 없으면 마른 비금속 물건으로 떼어 내세요 · 숨을 안 쉬면 가슴압박 · 괜찮아 보여도 병원에 가세요.",
        "ja": "感電：触る前に電源を切る。切れなければ乾いた金属以外の物で離す · 呼吸がなければ胸骨圧迫 · 大丈夫そうでも病院へ。",
    },
    "drowning": {
        "en": "Drowning: throw something that floats or a rope — don't jump in unless trained · once out, if not breathing start chest compressions · don't hang them upside down to drain water.",
        "es": "Ahogamiento: lanza algo que flote o una cuerda, no te tires si no sabes rescatar · ya fuera del agua, si no respira empieza compresiones en el pecho · no lo cuelgues boca abajo para sacar agua.",
        "vi": "Đuối nước: ném vật nổi hoặc dây, đừng nhảy xuống nếu không biết cứu hộ · lên bờ mà ngừng thở thì ép tim ngay · không dốc ngược để xốc nước.",
        "zh": "溺水：扔漂浮物或绳子，不会救生就不要跳下去 · 上岸后没呼吸马上胸外按压 · 不要倒挂控水。",
        "ko": "물에 빠졌을 때: 뜨는 물건이나 줄을 던지고, 구조를 모르면 뛰어들지 마세요 · 물 밖에서 숨을 안 쉬면 바로 가슴압박 · 거꾸로 들어 물을 빼려 하지 마세요.",
        "ja": "溺水：浮く物やロープを投げ、救助の訓練がなければ飛び込まない · 水から出て呼吸がなければすぐ胸骨圧迫 · 逆さにして水を吐かせようとしない。",
    },
})


def frame_names(text) -> list:
    from core.frames import explain
    seen = []
    for r in explain(text):
        if r["frame"] not in seen and not r["blocked_by"]:
            seen.append(r["frame"])
    return seen


def specific_line(text, lang: str) -> str | None:
    """บรรทัดคำแนะนำเฉพาะเรื่องของข้อความนี้ในภาษานี้ — ไม่มีคืน None (ใช้คำตอบเดิม)"""
    names = frame_names(text)
    for k, by in LINES.items():
        if k in names and lang in by:
            return by[lang]
    return None


def with_specific(steps: list, line: str | None) -> list:
    """ใส่แทนขั้นที่สอง — ขั้นแรกยังเป็นการโทรขอความช่วยเหลือ"""
    if not line or len(steps) < 2:
        return list(steps)
    return [steps[0], line] + list(steps[2:])


# ══════════════════════════════════════════════════════════════════
# ภาษาเวียดนาม: เหตุฉุกเฉิน 20 อย่างที่เจ้าของโปรเจกต์รวบรวมมา — เดิมพลาด 17 จาก 23 ประโยค
# (บางประโยคถูกตอบเป็นภาษาสเปนหรือโยรูบา) · หนึ่งแถว = รูปประโยค · ชนิดคำตอบ · ขั้นเฉพาะเรื่อง
# เบอร์ในเวียดนาม: 113 ตำรวจ · 114 ดับเพลิง/กู้ภัย · 115 รถพยาบาล
# ══════════════════════════════════════════════════════════════════
VI_EVENTS = (
    (r"đuối\s+nước|chết\s+đuối|bị\s+chìm", "medical",
     "Đuối nước: ném vật nổi hoặc dây, đừng nhảy xuống nếu không biết cứu hộ · lên bờ mà ngừng thở thì ép tim ngay · không dốc ngược để xốc nước."),
    (r"hóc\s+(?:dị\s+vật|xương|đồ|kẹo|thức\s+ăn)|bị\s+hóc", "medical",
     "Hóc dị vật: còn ho được thì để tự ho, đừng móc họng · không nói hay thở được: đứng sau lưng, ôm bụng và ấn mạnh vào trên rốn (Heimlich) · trẻ dưới 1 tuổi: úp sấp, vỗ lưng 5 cái."),
    (r"đau\s+tim|nhồi\s+máu\s+cơ\s+tim|lên\s+cơn\s+tim", "medical",
     "Có thể là nhồi máu cơ tim: cho ngồi nghỉ, nới lỏng quần áo · không để tự lái xe hay đi lại · nếu bất tỉnh và ngừng thở, ép tim ngay."),
    (r"tai\s+nạn\s+(?:giao\s+thông|xe)|đâm\s+xe|tông\s+xe|xe\s+(?:đâm|tông)", "medical",
     "Tai nạn giao thông: bật đèn cảnh báo, đứng xa dòng xe · không di chuyển người bị thương nếu không có nguy hiểm (có thể chấn thương cột sống) · không tháo mũ bảo hiểm · ép chặt vết thương đang chảy máu."),
    (r"sốc\s+phản\s+vệ|dị\s+ứng\s+(?:nặng|nghiêm\s+trọng)", "medical",
     "Sốc phản vệ: nếu có bút tiêm adrenaline (EpiPen), tiêm ngay · khó thở thì cho ngồi; choáng thì nằm kê chân cao · không để ở một mình."),
    (r"ngã\s+từ\s+(?:trên\s+)?(?:cao|tầng|mái|thang|cầu\s+thang)|rơi\s+từ\s+(?:trên\s+)?(?:cao|tầng)", "medical",
     "Ngã từ trên cao: không di chuyển nạn nhân, giữ yên đầu và cổ (có thể chấn thương cột sống) · ép chặt vết thương chảy máu · ngừng thở thì ép tim."),
    (r"cháy\s+nhà|hỏa\s+hoạn|hoả\s+hoạn|đám\s+cháy", "disaster", None),   # ไม่ใช้ "bị cháy": พับวรรณยุกต์แล้วตรงกับ "bị chảy (máu)" (เลือดไหล)
    (r"rò\s+rỉ\s+(?:khí\s+)?gas|rò\s+(?:khí\s+)?ga\b|mùi\s+gas|xì\s+gas", "help",
     "Rò rỉ khí gas: không bật/tắt công tắc điện, không bật lửa, không dùng điện thoại trong phòng · khóa van bình gas, mở cửa cho thoáng · ra ngoài rồi mới gọi 114."),
    (r"lũ\s+quét|ngập\s+lụt|lũ\s+lụt|nước\s+lũ\s+lên|lũ\s+(?:dâng|về)", "help",
     "Lũ: lên chỗ cao ngay, không lội hay lái xe qua dòng nước chảy (nước 15 cm đã có thể quật ngã người) · ngắt điện nếu nước vào nhà · gọi 114 nếu bị mắc kẹt."),
    (r"động\s+đất", "help",
     "Động đất: cúi thấp, che đầu, bám vào gầm bàn chắc · tránh xa cửa kính · hết rung mới ra chỗ trống, không dùng thang máy · bị kẹt thì gõ vào ống nước để người ngoài nghe thấy."),
    (r"sập\s+(?:nhà|công\s+trình|tòa\s+nhà|tường|cầu|mái)|nhà\s+(?:bị\s+)?sập", "help",
     "Sập nhà/công trình: tránh xa khu vực, có thể sập thêm · gọi 114 và 115, báo có bao nhiêu người bị kẹt · không tự đào bới nếu không an toàn · bị kẹt thì gõ vào vật cứng, che miệng tránh bụi."),
    (r"kẹt\s+(?:trong\s+)?thang\s+máy|thang\s+máy\s+(?:bị\s+)?(?:kẹt|dừng|hỏng)", "help",
     "Kẹt thang máy: bấm nút chuông khẩn cấp và gọi số trên bảng của tòa nhà hoặc 114 · giữ bình tĩnh, không ép mở cửa hay trèo ra ngoài · thang máy kín vẫn có đủ không khí."),
    (r"có\s+trộm|bị\s+trộm|kẻ\s+trộm|ăn\s+trộm", "violence",
     "Có trộm: đừng đối đầu, giữ an toàn cho mình trước · gọi 113 · ghi nhớ đặc điểm và hướng chạy, không chạm vào hiện trường."),
    (r"bị\s+cướp|cướp\s+giật|bị\s+giật\s+(?:túi|điện\s+thoại|đồ)|kẻ\s+cướp", "violence",
     "Bị cướp: đừng giằng co, tính mạng quan trọng hơn đồ đạc · đến chỗ đông người rồi gọi 113 · khóa thẻ ngân hàng và điện thoại ngay."),
    (r"hành\s+hung|bị\s+đánh|đánh\s+nhau|ẩu\s+đả", "violence",
     "Bị hành hung: rời khỏi chỗ nguy hiểm, đến nơi đông người · gọi 113 · nếu bị thương, gọi 115 · chụp ảnh vết thương làm bằng chứng."),
    (r"mất\s+hộ\s+chiếu|hộ\s+chiếu\s+bị\s+mất|mất\s+passport", "help",
     "Mất hộ chiếu: báo công an nơi gần nhất để lấy giấy xác nhận · liên hệ đại sứ quán hoặc lãnh sự quán của nước bạn để làm giấy tờ thay thế · giữ bản chụp hộ chiếu nếu có."),
    (r"lạc\s+đường|bị\s+lạc", "help",
     "Bị lạc: ở yên chỗ an toàn, có đèn và người · mở bản đồ hoặc chia sẻ vị trí cho người thân · hỏi cửa hàng, khách sạn hoặc công an gần đó · ở Thái Lan, cảnh sát du lịch 1155 nói tiếng Anh."),
    (r"xe\s+(?:bị\s+)?(?:hỏng|chết\s+máy|thủng\s+lốp|nổ\s+lốp)|hỏng\s+xe", "help",
     "Xe hỏng giữa đường: tấp vào lề, bật đèn cảnh báo, đặt biển hoặc vật báo hiệu phía sau xe · ra khỏi xe, đứng xa dòng xe · gọi cứu hộ hoặc bảo hiểm xe."),
)
# ข่าว ซ้อม เกม หนัง บทเรียน เตรียมตัว — ไม่ใช่เหตุที่กำลังเกิด ("Diễn tập động đất ở trường" "Cảnh tai nạn xe trong phim")
VI_CALM = r"diễn\s+tập|mô\s+phỏng|trò\s+chơi|\bgame\b|trong\s+phim|\bphim\b|xem\s+tin|tin\s+tức|\bbáo\b|nước\s+ngoài|chuẩn\s+bị|phòng\s+khi|\bhọc\b|giờ\s+khoa\s+học|"\
          r"dien\s+tap|mo\s+phong|tro\s+choi|trong\s+phim|xem\s+tin|chuan\s+bi|phong\s+khi"
VI_CALM_GUARD = r"(?:^(?![\s\S]*(?:" + VI_CALM + r"))[\s\S]*?)"
_VI_CALM_RX = __import__("re").compile(VI_CALM, __import__("re").I)
_VI_EVENT_RX = tuple((__import__("re").compile(rx, __import__("re").I), kind, line) for rx, kind, line in VI_EVENTS)


def vi_event(text):
    """(ชนิดคำตอบ, ขั้นเฉพาะเรื่อง) ของเหตุภาษาเวียดนามแรกที่พบ — ไม่พบคืน None"""
    if _VI_CALM_RX.search(str(text or "")):
        return None
    for rx, kind, line in _VI_EVENT_RX:
        if rx.search(str(text or "")):
            return kind, line
    return None


VI_WORDS_MORE = {"cháy", "lũ", "quét", "ngập", "lụt", "động", "đất", "sập", "trộm", "cướp", "hành", "hung", "mất", "hộ", "chiếu",
                 "lạc", "đường", "hỏng", "giữa", "kẹt", "thang", "máy", "ngất", "tim", "tai", "nạn", "giao", "thông", "đuối", "hóc",
                 "sốc", "phản", "vệ", "ngã", "từ", "trên", "cao", "rò", "rỉ", "khí", "gas", "điện", "giật", "công", "trình", "cứu",
                 "hỏa", "hoạn", "xảy", "dị", "vật", "nhà", "người", "xe"}


# ══════════════════════════════════════════════════════════════════
# ภาษาญี่ปุ่น: เหตุฉุกเฉินจากรายการ 200 วลีที่เจ้าของโปรเจกต์รวบรวม — เดิมประโยคอันตราย 59 จาก 80 ได้คำตอบทั่วไป
# และไฟไหม้/สึนามิ/น้ำท่วม/แก๊สรั่วได้คำแนะนำเรื่องแผ่นดินไหวเป็นข้อแรก
# ชนิด: medical (119 รถพยาบาล) · violence (110 ตำรวจ) · disaster (ภัยพิบัติ) · help (ไม่ถึงชีวิต: ของหาย หลงทาง รถเสีย)
# ══════════════════════════════════════════════════════════════════
JA_EVENTS = (
    # ── การแพทย์ ──
    (r"意識が(?:ありません|ない|戻らない)|呼びかけに反応(?:しない|がない)|息をしていない|呼吸(?:が|を)?(?:していない|止まっ)", "medical",
     "反応がなく普段どおりの呼吸がなければ、すぐ胸骨圧迫（胸の真ん中を強く速く、1分に100〜120回）· 近くの人に AED を持ってきてもらう。"),
    (r"息が苦しい|息ができない|呼吸が苦しい|喘息", "medical",
     "息が苦しいとき：楽な姿勢（座って前かがみ）にし、服をゆるめる · 喘息の吸入薬があれば使う · 唇が紫・話せないほどなら 119。"),
    (r"心臓発作|心筋梗塞|胸が(?:痛い|苦しい|締め付け)", "medical",
     "心筋梗塞の可能性：座って安静にし、服をゆるめる · 自分で運転・歩かせない · 反応がなく呼吸していなければすぐ胸骨圧迫を。"),
    (r"脳卒中|脳梗塞|ろれつが回らない|顔の片側が下が", "medical",
     "脳卒中の可能性 — 一分一秒が大切：症状が始まった時刻をメモ · 食べ物・飲み物・薬を与えない · 4.5時間以内の治療がずっと効果的です。"),
    (r"出血(?:しています|が止まらない|がひどい)|血が止まらない", "medical",
     "出血：清潔な布で傷口を強く押さえ続ける（10分は離さない）· 手足なら心臓より高く · 布がにじんでも外さず上から重ねる。"),
    (r"骨折", "medical",
     "骨折：動かさず、添え木（雑誌・段ボール）で固定 · 骨が出ている・変形が大きい・首や背中を痛めたときは動かさずに 119。"),
    (r"やけど|火傷", "medical",
     "やけど：すぐ流水で 20 分冷やす · 指輪や時計を外す · 氷・油・軟膏は塗らない、水ぶくれはつぶさない · 手のひらより広い・顔や関節なら病院へ。"),
    (r"アレルギー|アナフィラキシー", "medical",
     "重いアレルギー：エピペンがあればすぐ使う · 息が苦しい・唇やのどが腫れる・ぐったりしたら 119 · 息が苦しければ座らせ、ふらつくなら足を上げて寝かせる。"),
    (r"食中毒|嘔吐|下痢|脱水", "medical",
     "嘔吐・下痢：経口補水液を少しずつ何度も · 尿がほとんど出ない・ぐったり・血便・高熱なら病院へ · 同じ物を食べた人がいれば一緒に受診。"),
    (r"熱中症", "medical",
     "熱中症：涼しい所へ移し、首・脇・足の付け根を冷やす · 意識がはっきりしていれば水分と塩分を · 反応が鈍い・水を飲めないなら 119。"),
    (r"低体温", "medical",
     "低体温症：暖かい場所へ移し、濡れた服を脱がせて毛布で包む · 急に熱い湯に入れたり手足をこすったりしない · 反応が鈍ければ 119。"),
    (r"高熱|熱が下がらない", "medical",
     "高熱：水分をとり、薄着で休む · 首が硬い・意識がおかしい・けいれん・息が苦しい・赤ちゃんなら すぐ受診。"),
    (r"蛇に(?:噛|か)まれ|ヘビに(?:噛|か)まれ|マムシ|ハブ", "medical", None),     # LINES["snakebite"] を使う
    (r"(?:犬|猫|動物)に(?:噛|か)まれ", "medical", None),                         # LINES["rabies_exposure"]
    (r"虫に刺され|ハチに刺され|蜂に刺され", "medical",
     "虫・ハチに刺された：針が残っていればカードなどでこすり取る（つままない）· 冷やす · 息苦しい・全身のじんましん・顔の腫れが出たら 119。"),
    (r"異物を飲み込|電池を飲み込|磁石を飲み込", "medical",
     "異物を飲み込んだ：無理に吐かせない · ボタン電池・磁石・とがった物はすぐ病院へ · 息が苦しい・よだれが止まらないなら 119。"),
    (r"喉に詰まら|のどに詰まら|喉に詰まっ", "medical",
     "のどに詰まった：せきができるなら強くせきをさせる · 声が出ない・息ができないなら背中を強く叩く／後ろから腹部を突き上げる（ハイムリック法）。"),
    (r"陣痛|破水|出産しそう|生まれそう", "medical",
     "陣痛・破水：母子手帳と保険証を持って産院に連絡 · 出血が多い・強い腹痛が続く・赤ちゃんが動かないなら 119。"),
    (r"倒れ(?:ました|た|ている)|気を失", "medical",
     "倒れた人：まず肩をたたいて呼びかける · 反応がなく普段どおりの呼吸がなければ胸骨圧迫と AED · 呼吸があれば横向きに寝かせる。"),
    (r"救急車を呼んで|救急車", "medical", None),
    (r"溺れ|おぼれ|海難事故", "medical", None),                                 # LINES["drowning"]
    # ── 事故 ──
    (r"交通事故|車にひかれ|正面衝突|追突事故|自転車事故|人身事故|ひき逃げ|事故です|事故が", "medical",
     "交通事故：ハザードをつけ、車から離れた安全な所へ · けが人は危険がなければ動かさない（首・背中を守る）· ヘルメットは外さない · ひき逃げは車の特徴とナンバーを 110 へ。"),
    # ── 犯罪・安全 ──
    (r"強盗|ひったくり|スリに遭|盗まれ|盗難|泥棒|空き巣", "violence",
     "盗難・強盗：抵抗しない、命が先です · 人の多い所へ移ってから 110 · カードと携帯をすぐ止める · 交番で被害届を出し、受理番号を控える（保険請求に必要）。"),
    (r"暴力を受け|殴られ|喧嘩が起き|けんかが起き|武器を持っ|刃物を持っ|危険な人物", "violence",
     "暴力・武器：その場から離れ、鍵のかかる所や人の多い所へ · 110 に電話 · けがは写真に残し、病院で診断書を。"),
    (r"不審者|つきまとわれ|誰かに見られ|後をつけられ", "violence",
     "不審者・つきまとい：人の多い店や交番に入る · 家まで後をつけられないよう遠回りする · 110 か警察相談 #9110 へ。"),
    (r"痴漢", "violence",
     "痴漢：大声を出す・周りの人や駅員に知らせる · 110 へ · 日時と場所、相手の特徴をメモ · あなたは悪くありません。"),
    (r"脅迫|脅され", "violence",
     "脅迫：相手に返事をしない · メッセージや録音を証拠として残す · 110 か警察相談 #9110 へ。"),
    (r"閉じ込められ", "help",
     "閉じ込められた：エレベーターなら非常ボタンで管理会社に連絡し、扉を無理に開けない（空気は足ります）· 部屋に閉じ込められたなら 110 へ。"),
    (r"子ども?が(?:いなくなり|見つからない|行方不明)|迷子|行方不明", "violence",
     "人がいなくなった：すぐ 110 へ — 服装・身長・最後に見た場所と時刻を伝える · 子どもは時間がとても大切です · 店や駅なら係員にも知らせる。"),
    # ── 災害 ──
    (r"火事|火災|燃えて|煙が(?:出て|充満)|放火|爆発", "disaster",
     "火事：大声で知らせ、すぐ外へ · 煙は低い姿勢で口と鼻を覆う · エレベーターは使わず階段で · 外に出てから 119、戻らない。"),
    (r"ガス漏れ|ガスの臭い|有毒ガス|化学物質が漏れ", "disaster",
     "ガス漏れ・有毒ガス：火をつけない、電気のスイッチに触れない · 窓を開け、口と鼻を覆って風上へ避難 · 外に出てから 119。"),
    (r"地震|余震", "disaster",
     "地震：姿勢を低くして頭を守り、机につかまる · 揺れが収まったら火の始末、階段で外へ（エレベーターは使わない）· 海の近くなら津波に備えて高台へ。"),
    (r"津波", "disaster",
     "津波：すぐ高台か高い建物の3階以上へ · 車ではなく歩いて · 警報が解除されるまで戻らない。"),
    (r"洪水|氾濫|冠水|大雨|台風", "disaster",
     "大雨・洪水：高い所へ早めに避難 · 冠水した道は歩かず車で入らない（30cmで車も流されます）· 自治体の避難情報に従う。"),
    (r"土砂崩れ|落石|雪崩|竜巻|噴火|落雷|建物が傾", "disaster",
     "土砂崩れ・噴火・竜巻など：その場から離れ、頑丈な建物の中か高い所へ · 崖や川の近くを避ける · 自治体の避難情報に従う。"),
    (r"放射能", "disaster",
     "放射性物質の危険：屋内に入り窓とドアを閉め、換気扇を止める · 外にいたなら服を替え、手と顔を洗う · 自治体とテレビ・ラジオの指示に従う。"),
    (r"避難指示|避難勧告|津波警報|警報が鳴", "disaster",
     "避難指示が出たら：すぐ避難を — 非常用持ち出し袋、薬、身分証を持つ · 近所の高齢者に声をかける · 避難所は自治体のサイトや防災無線で確認。"),
    (r"電線が切れ|電線が垂れ", "disaster",
     "切れた電線：近づかない、触らない（8m以上離れる）· 電力会社か 110 へ連絡。"),
    (r"高台に逃げ", "disaster", "津波：すぐ高台か高い建物の3階以上へ · 車ではなく歩いて · 警報が解除されるまで戻らない。"),
    (r"救助(?:して|を待っ|を求め)|助けに来て", "disaster",
     "救助を待つとき：その場の安全を確保し、体力を温存する · 声は限られるので、物を叩いたり笛やライトで合図 · 119 に現在地とけが人の人数を伝える。"),
    (r"警察を呼んで", "violence", None),
    (r"逆走車", "violence", "逆走車：近づかず安全な所に停車し、110 に場所と進行方向を伝える。"),
    # ── 困りごと（命に関わらない） ──
    (r"パスポートを(?:なくし|盗まれ|紛失)|パスポートが(?:ない|見つからない)", "help",
     "パスポート紛失：交番か警察署で遺失届・被害届を出し受理番号をもらう · 自国の大使館・領事館で渡航書を申請 · コピーや写真があれば役立ちます。"),
    (r"(?:財布|スマホ|カバン|鍵|カード)を(?:なくし|紛失)|カードを紛失", "help",
     "落とし物：最後にいた店・駅に問い合わせ、交番に遺失届を · カードと携帯はすぐ停止 · タイの観光警察 1155 は英語可。"),
    (r"道に迷|迷いました", "help",
     "道に迷った：明るく人のいる所にとどまる · 地図アプリで現在地を共有 · コンビニや交番で聞く · 訪日外国人向けホットライン 050-3816-2787（24時間・多言語）。"),
    (r"車が故障|パンク|ガス欠|バッテリーが上が", "help",
     "車の故障：路肩に寄せてハザード、三角表示板を後ろに · 高速道路ではガードレールの外へ避難 · JAF #8139 か保険会社のロードサービスへ。"),
)
_JA_EVENT_RX = tuple((__import__("re").compile(rx), kind, line) for rx, kind, line in JA_EVENTS)
# ข่าว ซ้อม เกม คำถามหาสถานที่ อาการเล็กน้อย/หายแล้ว และสำนวน ("胸が痛いほど感動した" ซึ้งจนเจ็บอก · "失恋して胸が痛い" อกหัก)
JA_CALM = __import__("re").compile(r"訓練|ゲーム|映画|ドラマ|ニュース|アニメ|夢で|もし|備えて|準備|練習|授業|はどこですか|ないでください|無事です|大丈夫|平気|"
                                   r"ないように|ほど|感動|失恋|少し|軽い|良くなった|よくなった|治った|落ち着い|コントロール|くしゃみ|水たまり|持ち歩|有点|一点|没事")
JA_NONLIFE = {"help"}
_JA_DEFAULT = {   # 行が None のとき使う LINES の項目
    "蛇": "snakebite", "ヘビ": "snakebite", "マムシ": "snakebite", "ハブ": "snakebite",
    "犬": "rabies_exposure", "猫": "rabies_exposure", "動物": "rabies_exposure", "溺": "drowning", "おぼれ": "drowning", "海難": "drowning",
}


def ja_event(text):
    """(ชนิดคำตอบ, ขั้นเฉพาะเรื่อง) ของเหตุภาษาญี่ปุ่นแรกที่พบ — ข่าว ซ้อม คำถามหาสถานที่ ไม่นับ"""
    t = str(text or "")
    if JA_CALM.search(t):
        return None
    for rx, kind, line in _JA_EVENT_RX:
        if rx.search(t):
            if line is None:
                key = next((v for k, v in _JA_DEFAULT.items() if k in t), None)
                line = LINES.get(key, {}).get("ja") if key else None
            return kind, line
    return None


JA_DISASTER_REST = ["安全な所に移ってから 119（消防・救急）に電話し、住所と状況を伝えてください。",
                    "近くの人と声をかけ合い、自治体の防災情報（防災無線・テレビ・ラジオ）に従ってください。"]
JA_HELP_REST = ["けがや危険があれば 119（救急）· 110（警察）。",
                "外国語で相談したいとき：訪日外国人向けホットライン 050-3816-2787（24時間・多言語）。"]


# ══════════════════════════════════════════════════════════════════
# ภาษาจีน: เหตุฉุกเฉินจากรายการ 200 วลีที่เจ้าของโปรเจกต์รวบรวม — เดิมประโยคอันตราย 45 จาก 65 ได้คำตอบทั่วไป
# และไฟไหม้/แก๊สรั่ว/น้ำท่วม/ดินถล่มได้คำแนะนำแผ่นดินไหวเป็นข้อแรก
# เบอร์ในจีน: 110 ตำรวจ · 119 ดับเพลิง · 120 รถพยาบาล · 122 อุบัติเหตุจราจร
# ══════════════════════════════════════════════════════════════════
ZH_EVENTS = (
    # ── 医疗 ──
    (r"昏迷|叫不醒|没有呼吸|没呼吸|不呼吸了|晕倒", "medical",
     "叫不醒、没有正常呼吸：马上胸外按压（胸口正中用力快速按，每分钟 100–120 次）· 请旁人去拿 AED · 有呼吸就让他侧躺。"),
    (r"呼吸困难|喘不上气|喘不过气|缺氧|高原反应", "medical",
     "呼吸困难：坐起来、身体前倾，松开衣服 · 有哮喘喷雾就用 · 高原反应要停止上升、尽量下撤、吸氧 · 嘴唇发紫或说不出话打 120。"),
    (r"胸口痛|胸痛|心口痛|心脏病发作|心梗", "medical",
     "可能是心梗：坐下休息，松开衣服 · 不要自己开车或走动 · 叫不醒、没呼吸就马上胸外按压。"),
    (r"抽搐|抽筋不停|癫痫发作", "medical",
     "抽搐时：让他侧躺，移开身边的硬物 · 不要往嘴里塞东西、不要按住手脚 · 记下时间，超过 5 分钟或反复发作打 120。"),
    (r"流血|出血|血止不住", "medical",
     "出血：用干净的布用力按住伤口，持续按 10 分钟不要松开 · 手脚出血就抬高 · 布湿透了就在上面再加，不要拿掉。"),
    (r"骨折", "medical",
     "骨折：不要乱动，用木板或硬纸板固定 · 骨头外露、明显变形，或伤到脖子和背，不要移动，直接打 120。"),
    (r"烫伤|烧伤", "medical",
     "烫伤：马上用流动的凉水冲 20 分钟 · 摘下戒指手表 · 不要涂牙膏、酱油、冰块，不要弄破水泡 · 面积比手掌大或在脸上、关节处要去医院。"),
    (r"过敏了|药物过敏|食物过敏|海鲜过敏|严重过敏|过敏性休克|过敏反应", "medical",   # 不含 "花粉过敏"（季节性）
     "严重过敏：有肾上腺素笔（EpiPen）马上用 · 呼吸困难、嘴唇或喉咙肿、全身发软就打 120 · 呼吸困难就坐着，头晕就平躺抬高双腿。"),
    (r"食物中毒|上吐下泻|呕吐不止", "medical",
     "食物中毒：少量多次喝口服补液盐 · 尿很少、没精神、便血、高烧就去医院 · 一起吃的人也要注意，保留剩下的食物。"),
    (r"高烧|发高烧|烧到\s*(?:39|40)", "medical",
     "高烧：多喝水，穿薄一点休息 · 脖子僵硬、意识不清、抽搐、呼吸困难或是婴儿，要马上去医院。"),
    (r"被蛇咬|蛇咬", "medical", None),
    (r"狗咬|被狗咬|猫抓|被猫抓|被猫咬", "medical", None),
    (r"溺水|落水|掉进水里|掉河里", "medical", None),
    (r"触电", "medical", None),
    (r"漏电", "disaster", "漏电：不要用手碰电器和湿的地方 · 先拉下总电闸 · 有人被电到，先断电再救人 · 打电工或物业，冒烟起火打 119。"),
    (r"摔倒|摔伤|从高处掉下|坠楼", "medical",
     "摔伤：头撞到、站不起来、髋部或背部剧痛时不要硬扶起来 · 保暖，等 120 · 头撞到后呕吐、嗜睡要马上就医。"),
    (r"快叫救护车|叫救护车|救护车", "medical", None),
    (r"受伤了|受伤", "medical",
     "有人受伤：先确认周围安全 · 出血就用力按住 · 伤到头、脖子、背不要移动 · 打 120 说清楚地址和伤情。"),
    # ── 交通 ──
    (r"车祸|撞人|撞车|被车撞|交通事故", "medical",
     "车祸：打开双闪，人离开车道站到护栏外 · 伤者没有危险不要移动（保护脖子和背）· 不要摘头盔 · 打 122 报事故、120 叫救护车 · 拍照留证据。"),
    # ── 犯罪 · 安全 ──
    (r"抢劫|抢我的|被抢|有人抢", "violence",
     "被抢劫：不要反抗，命比东西重要 · 到人多的地方再打 110 · 马上冻结银行卡、挂失手机 · 去派出所开报案证明（报保险要用）。"),
    (r"被偷|小偷|扒窃|被扒", "violence",
     "被偷：不要追，先保证安全 · 打 110 或去最近的派出所报案，开报案证明 · 马上冻结银行卡、挂失手机。"),
    (r"跟踪|骚扰|别碰我|离我远", "violence",
     "被跟踪或骚扰：马上去人多的商店、酒店前台或派出所 · 大声求助 · 打 110 · 记下对方特征和时间地点。"),
    (r"打架|打人|被打|动手了", "violence",
     "打架、被打：离开现场，到安全的地方 · 打 110 · 受伤打 120 · 拍下伤口，去医院开诊断证明。"),
    (r"报警|叫警察", "violence", None),
    (r"孩子(?:走丢|丢了|不见了|找不到)|老人(?:走失|走丢|不见了)|人不见了|走失", "violence",
     "有人走失：马上打 110 — 说清楚衣着、身高、最后看到的地点和时间 · 孩子走丢时间非常关键 · 在商场或车站要马上告诉工作人员。"),
    # ── 火灾 · 气体 ──
    (r"着火|起火|火灾|失火|冒烟|浓烟|烧焦味", "disaster",
     "着火：大声喊人，马上往外撤 · 用湿毛巾捂住口鼻，弯腰低姿走 · 不坐电梯，走楼梯 · 到外面再打 119，不要回去拿东西。"),
    (r"煤气泄漏|天然气泄漏|燃气泄漏|煤气味|燃气味|有毒气体", "disaster",
     "燃气泄漏：不要开灯、不要按门铃、不要用明火和手机 · 关掉燃气阀门，打开窗户 · 离开后在外面打 119 或燃气公司电话。"),
    (r"有人被困|被困在", "disaster",
     "有人被困：不要冒险进去 · 打 119 说清楚地址、楼层和被困人数 · 被困的人用湿毛巾捂住口鼻，在窗口挥手或用手机灯光求救。"),
    # ── 自然灾害 ──
    (r"地震|余震", "disaster",
     "地震：趴下、护住头、抓牢桌子 · 停止摇晃后关火，走楼梯离开（不坐电梯）· 远离窗户和外墙。"),
    (r"洪水|积水很深|暴雨|发大水|被水淹|水漫", "disaster",
     "暴雨、洪水：尽快往高处转移 · 不要蹚过或开车进积水（30 厘米的水就能冲走车）· 水进屋要先断电 · 听当地政府的避险通知。"),
    (r"台风|雷暴|打雷闪电|暴雪|冰雹|沙尘暴", "disaster",
     "台风、雷暴等恶劣天气：待在坚固的室内，远离窗户 · 不要在树下、电线杆下避雨 · 户外打雷时蹲低，远离高处和水边。"),
    (r"山体滑坡|泥石流|塌方", "disaster",
     "山体滑坡、泥石流：马上往两侧高处跑，不要顺着沟往下跑 · 远离山坡和河道 · 打 119 报告被困的人。"),
    # ── 困难（不危及生命） ──
    (r"护照(?:丢|不见|被偷)|签证丢|身份证丢|居留许可丢", "help",
     "护照丢了：去附近派出所开报案证明（丢失证明）· 联系泰国驻华大使馆或总领事馆办旅行证 · 有护照复印件或照片会更快。"),
    (r"(?:钱包|手机|背包|行李|房卡|东西)(?:丢了|落在|不见了)", "help",
     "东西丢了：联系最后去过的店、出租车公司（看发票上的车牌）或地铁失物招领 · 银行卡和手机马上挂失 · 需要的话去派出所开证明。"),
    (r"迷路|找不到路|找不到酒店", "help",
     "迷路了：待在明亮、人多的地方 · 用地图软件把位置发给亲友 · 向商店、酒店前台或警察问路 · 把酒店名片或地址给出租车司机看。"),
    (r"被关在电梯|电梯故障|困在电梯", "help",
     "被困电梯：按电梯里的紧急呼叫按钮，或打电梯里贴的维保电话、119 · 不要扒门或爬出去 · 电梯里空气够用，保持冷静。"),
    (r"车坏了|爆胎|没油了", "help",
     "车坏了：靠边停车，打开双闪，在车后放三角警示牌 · 人站到护栏外 · 打保险公司或租车公司的救援电话，高速上可打 122。"),
)
_ZH_EVENT_RX = tuple((__import__("re").compile(rx), kind, line) for rx, kind, line in ZH_EVENTS)
ZH_CALM = __import__("re").compile(r"演习|演练|游戏|电影|电视剧|新闻|小说|如果|万一|防止|预防|准备|在哪里|在哪儿|有点|一点|没事|好了|好多了|已经不|控制得|"
                                   r"感动|失恋|心痛|笑死|开玩笑|别担心|安全了")
_ZH_DEFAULT = {"蛇": "snakebite", "狗": "rabies_exposure", "猫": "rabies_exposure", "溺": "drowning", "落水": "drowning",
               "掉进水": "drowning", "掉河": "drowning", "触电": "electric"}


def zh_event(text):
    """(ชนิดคำตอบ, ขั้นเฉพาะเรื่อง) ของเหตุภาษาจีนแรกที่พบ — ข่าว ซ้อม คำถามหาสถานที่ อาการเล็กน้อย ไม่นับ"""
    t = str(text or "")
    if ZH_CALM.search(t):
        return None
    for rx, kind, line in _ZH_EVENT_RX:
        if rx.search(t):
            if line is None:
                key = next((v for k, v in _ZH_DEFAULT.items() if k in t), None)
                line = LINES.get(key, {}).get("zh") if key else None
            return kind, line
    return None


ZH_DISASTER_REST = ["到安全的地方后打 119（消防）或 120（急救），说清楚地址和情况。",
                    "互相照应身边的人，听当地政府和应急广播的通知。"]
ZH_HELP_REST = ["有危险或受伤：110（警察）· 120（急救）。",
                "在中国的泰国人可联系泰国驻华大使馆或总领事馆；不会说中文时，请旁人帮忙或用翻译软件。"]
