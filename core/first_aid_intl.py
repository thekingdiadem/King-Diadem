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
