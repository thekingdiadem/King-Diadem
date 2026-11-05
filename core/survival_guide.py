"""คู่มือเอาชีวิตรอดจากภัยพิบัติฉบับเต็ม — หน้า /survival · แชทลิงก์มาที่นี่เมื่อพูดถึงภัย

หลักที่ห้ามพลาด:
  · เขียนจากแนวทางที่หน่วยงานหลักยืนยันตรงกัน (กาชาด/IFRC · WHO · ปภ. · FEMA Ready.gov · USGS · NOAA · CDC)
    ไม่ใส่เคล็ดลับที่ยังถกเถียง · ตัวเลข/เบอร์ที่ไม่แน่ใจไม่ใส่
  · ลำดับในหมวด "ขณะเกิด" = ทำข้อแรกก่อน — ข้อที่ช่วยชีวิตอยู่บนสุด
  · ความเชื่อผิดที่ทำให้คนตายจริง ระบุไว้ตรงๆ (เช่น ยืนที่วงกบประตูตอนแผ่นดินไหว)
  · tests/test_survival_guide.py ล็อกข้อเท็จจริงที่ช่วยชีวิตไว้ — แก้แล้วผิด เทสต์ล้ม

โครงสร้าง: HAZARDS[key] = {icon, name{th,en}, signs, before, during, after, vulnerable, myths, sources}
ทุกหมวด (ยกเว้น sources) เป็น list ของ (ไทย, อังกฤษ)
"""
from __future__ import annotations

HOTLINES = [("1784", "ปภ. สายด่วนนิรภัย (ภัยพิบัติ)", "Thai Disaster Prevention & Mitigation"),
            ("1669", "เจ็บป่วยฉุกเฉิน", "Medical emergency (Thailand)"),
            ("191", "ตำรวจ", "Police"), ("199", "ดับเพลิง", "Fire"),
            ("1323", "สุขภาพจิต 24 ชม.", "Mental health, 24h")]

KIT = [
    ("น้ำดื่มคนละ 3–4 ลิตรต่อวัน อย่างน้อย 3 วัน", "Drinking water: 3–4 litres per person per day, at least 3 days"),
    ("อาหารแห้งที่ไม่ต้องหุง 3 วัน + ที่เปิดกระป๋อง", "3 days of no-cook food + can opener"),
    ("ยาประจำตัว 7 วัน + สำเนาใบสั่งยา · ชุดปฐมพยาบาล", "7 days of regular medicines + prescription copies · first-aid kit"),
    ("ไฟฉาย วิทยุใช้ถ่าน ถ่านสำรอง พาวเวอร์แบงก์ชาร์จเต็ม", "Torch, battery radio, spare batteries, charged power bank"),
    ("นกหวีด (เรียกคนช่วยได้ไกลกว่าตะโกน ไม่เปลืองแรง)", "Whistle (carries further than shouting and saves energy)"),
    ("หน้ากาก N95 · ถุงมือหนา · รองเท้าหุ้มส้น", "N95 masks · sturdy gloves · closed shoes"),
    ("สำเนาบัตรประชาชน/เอกสารสำคัญในถุงกันน้ำ · เงินสดย่อย", "Copies of ID/key documents in a waterproof bag · small cash"),
    ("เบอร์โทรคนในครอบครัวเขียนบนกระดาษ (มือถืออาจดับ) และจุดนัดพบ 2 ที่", "Family phone numbers on paper (phones die) and 2 meeting points"),
]

HAZARDS = {
    "quake": {
        "icon": "🌏", "name": ("แผ่นดินไหว", "Earthquake"),
        "signs": [
            ("แผ่นดินไหวเกิดโดยไม่มีสัญญาณเตือนล่วงหน้าที่เชื่อถือได้ — ไม่มีใครทำนายวันเวลาได้ ข่าวลือ \"จะเกิดวันที่…\" เป็นข่าวปลอม",
             "Earthquakes give no reliable advance warning — no one can predict the date; \"it will hit on…\" rumours are false"),
            ("อาคารสูงในกรุงเทพรู้สึกได้จากแผ่นดินไหวไกลหลายร้อยกิโลเมตร (เช่น เมียนมา มี.ค. 2568)",
             "Tall buildings in Bangkok can feel quakes hundreds of km away (e.g. Myanmar, March 2025)"),
        ],
        "before": [
            ("ยึดตู้ ชั้นวาง ทีวี เครื่องทำน้ำอุ่นติดผนัง · ของหนักไว้ชั้นล่าง · ไม่วางของหนักเหนือหัวเตียง",
             "Strap cabinets, shelves, TVs and water heaters to walls · heavy items low · nothing heavy above the bed"),
            ("รู้ตำแหน่งวาล์วแก๊สและเบรกเกอร์หลัก และวิธีปิด", "Know where the gas valve and main breaker are, and how to shut them"),
            ("ซ้อม \"หมอบ ป้อง เกาะ\" กับคนในบ้าน และเลือกจุดหลบในแต่ละห้อง (ใต้โต๊ะแข็งแรง ห่างกระจก)",
             "Practise Drop, Cover, Hold On with your household and pick a spot in each room (under a sturdy table, away from glass)"),
            ("เก็บรองเท้าและไฟฉายไว้ข้างเตียง — หลังแผ่นดินไหวพื้นมักมีเศษแก้ว", "Keep shoes and a torch by the bed — floors are often covered in glass afterwards"),
        ],
        "during": [
            ("หมอบ ป้อง เกาะ: หมอบลงก่อนถูกเหวี่ยงล้ม · มุดใต้โต๊ะแข็งแรงแล้วจับขาโต๊ะไว้ · ไม่มีโต๊ะ ให้หมอบชิดผนังด้านใน ใช้แขนป้องศีรษะและคอ",
             "Drop, Cover, Hold On: get down before you're thrown · get under a sturdy table and hold a leg · no table: crouch by an interior wall and protect head and neck with your arms"),
            ("อยู่กับที่จนกว่าจะหยุดสั่น — อย่าวิ่งออกนอกอาคารระหว่างสั่น คนบาดเจ็บส่วนใหญ่โดนของตกใส่ตอนวิ่งผ่านประตูหรือหน้าอาคาร",
             "Stay put until the shaking stops — don't run outside while it shakes; most injuries happen from falling objects while people move through doors or past façades"),
            ("อยู่บนเตียง: นอนต่อ คว่ำหน้า ใช้หมอนป้องศีรษะ", "In bed: stay there, face down, protect your head with a pillow"),
            ("อยู่ข้างนอก: ไปที่โล่ง ห่างอาคาร ป้าย เสาไฟ สายไฟ แล้วหมอบลง", "Outdoors: move to open ground away from buildings, signs, poles and wires, then drop"),
            ("ขับรถ: ชะลอแล้วจอดในที่โล่ง ห่างสะพาน ทางยกระดับ ต้นไม้ · คาดเข็มขัดอยู่ในรถจนหยุดสั่น",
             "Driving: slow down and stop in the open, away from bridges, overpasses and trees · stay buckled in until it stops"),
            ("ห้ามใช้ลิฟต์ · ถ้าติดอยู่ในลิฟต์ กดปุ่มทุกชั้นและปุ่มฉุกเฉิน แล้วรอ อย่าพยายามปีนออก",
             "Never use lifts · if stuck in one, press every floor and the alarm button, then wait — don't climb out"),
            ("อยู่ริมทะเล: สั่นแรงจนยืนลำบาก หรือสั่นนานเกิน 20 วินาที → ขึ้นที่สูงทันทีหลังหยุดสั่น ไม่ต้องรอประกาศเตือนสึนามิ",
             "On the coast: shaking strong enough to make standing hard, or lasting over 20 seconds → head to high ground as soon as it stops; don't wait for an official tsunami warning"),
        ],
        "after": [
            ("เตรียมรับอาฟเตอร์ช็อก — ทุกครั้งที่สั่นให้ หมอบ ป้อง เกาะ อีก", "Expect aftershocks — Drop, Cover, Hold On each time"),
            ("ได้กลิ่นแก๊ส: ห้ามกดสวิตช์หรือจุดไฟ เปิดหน้าต่าง ปิดวาล์วถ้าทำได้ปลอดภัย แล้วออกจากอาคาร โทรจากข้างนอก",
             "Smell gas: no switches or flames, open windows, shut the valve if safe, leave and call from outside"),
            ("อาคารร้าวลึก เอียง หรือมีเสียงลั่น: ออกทางบันได ห้ามกลับเข้าไปจนกว่าวิศวกร/เจ้าหน้าที่ตรวจ",
             "Deep cracks, tilting or creaking: leave by the stairs and don't go back in until an engineer or official checks it"),
            ("ติดใต้ซากอาคาร: อย่าจุดไฟ ปิดปากจมูกด้วยผ้า เคาะท่อหรือผนังเป็นจังหวะ หรือเป่านกหวีด — ตะโกนเป็นทางสุดท้ายเพราะสูดฝุ่นและเปลืองแรง",
             "Trapped under debris: no flames, cover mouth and nose with cloth, tap on a pipe or wall in a rhythm or use a whistle — shout only as a last resort (dust and exhaustion)"),
            ("ใช้โทรศัพท์เท่าที่จำเป็น ส่งข้อความแทนการโทร — เครือข่ายจะล่มเมื่อทุกคนโทรพร้อมกัน",
             "Use phones only when necessary and text instead of calling — networks jam when everyone calls at once"),
        ],
        "vulnerable": [
            ("ผู้ใช้วีลแชร์: ล็อกล้อ ก้มตัว ใช้แขนป้องศีรษะและคอ — ไม่ต้องพยายามลงจากเก้าอี้",
             "Wheelchair users: lock the wheels, bend over and cover head and neck — don't try to get out of the chair"),
            ("เด็กเล็ก: อุ้มเข้าใต้โต๊ะด้วยกัน ซ้อมเป็นเกมบ่อยๆ ให้จำได้ตอนตกใจ", "Young children: take them under the table with you; practise it as a game so they remember in a panic"),
        ],
        "myths": [
            ("❌ ยืนที่วงกบประตู — บ้านสมัยใหม่วงกบไม่ได้แข็งแรงกว่าส่วนอื่น และประตูอาจกระแทกใส่ · ให้มุดใต้โต๊ะแทน",
             "❌ Stand in a doorway — in modern homes doorways are no stronger than other parts and the door can swing into you · get under a table instead"),
            ("❌ \"สามเหลี่ยมชีวิต\" (นอนข้างเฟอร์นิเจอร์) — ไม่มีหลักฐานรองรับ หน่วยงานด้านแผ่นดินไหวยังแนะนำ หมอบ ป้อง เกาะ",
             "❌ The \"triangle of life\" (lying beside furniture) — no evidence supports it; earthquake agencies still recommend Drop, Cover, Hold On"),
        ],
        "sources": ["USGS · earthquake.usgs.gov", "Earthquake Country Alliance · earthquakecountry.org (Drop, Cover, Hold On)",
                    "FEMA · ready.gov/earthquakes", "กรมอุตุนิยมวิทยา · earthquake.tmd.go.th", "ปภ. · disaster.go.th"],
    },
    "tsunami": {
        "icon": "🌊", "name": ("สึนามิ", "Tsunami"),
        "signs": [
            ("สัญญาณจากธรรมชาติ (เชื่อได้มากกว่ารอประกาศ): แผ่นดินไหวแรงหรือนานริมทะเล · น้ำทะเลลดลงผิดปกติจนเห็นพื้นทะเล · เสียงคำรามดังจากทะเล",
             "Natural warnings (trust them more than waiting for an alert): strong or long shaking near the coast · the sea suddenly drawing back to expose the seabed · a loud roar from the ocean"),
            ("ฝั่งอันดามันของไทย (ภูเก็ต พังงา กระบี่ ระนอง ตรัง สตูล) มีหอเตือนภัยและป้ายเส้นทางอพยพ", "Thailand's Andaman coast has warning towers and evacuation-route signs"),
        ],
        "before": [
            ("ถ้าพักหรืออยู่ริมทะเล หาเส้นทางอพยพขึ้นที่สูงและจุดรวมพลไว้ตั้งแต่วันแรก — เดินเท้าได้ในไม่กี่นาที",
             "If you stay by the sea, find the evacuation route to high ground and the assembly point on day one — reachable on foot within minutes"),
            ("ถามที่พักว่าอาคารไหนเป็นอาคารหลบภัยแนวดิ่ง (คอนกรีตเสริมเหล็กหลายชั้น)", "Ask your hotel which building is a vertical evacuation shelter (multi-storey reinforced concrete)"),
        ],
        "during": [
            ("เห็นสัญญาณธรรมชาติหรือได้ยินเสียงเตือน: วิ่งขึ้นที่สูงหรือเข้าไปในแผ่นดินทันที — เป้าหมายคือสูงจากระดับทะเลราว 30 เมตร หรือห่างฝั่งราว 3 กม.",
             "Natural signs or a siren: go to high ground or inland immediately — aim for about 30 m above sea level or about 3 km inland"),
            ("ไปด้วยเท้าถ้าทำได้ — รถติดบนถนนเลียบหาดคือกับดัก", "Go on foot if you can — cars jammed on coastal roads become traps"),
            ("ไม่มีเวลาหนีขึ้นเนิน: ขึ้นชั้น 3 ขึ้นไปของอาคารคอนกรีตที่แข็งแรง หรือดาดฟ้า", "No time to reach a hill: go to the 3rd floor or higher of a strong concrete building, or its roof"),
            ("ถูกน้ำพัด: คว้าของที่ลอยได้ (ประตู ต้นไม้ ถังน้ำ) เกาะไว้ อย่าพยายามว่ายสวนกระแส", "Caught in the water: grab anything that floats (door, tree, container) and hold on — don't fight the current"),
        ],
        "after": [
            ("สึนามิมาเป็นหลายลูกติดต่อกันนานหลายชั่วโมง ลูกแรกมักไม่ใช่ลูกใหญ่ที่สุด — อยู่ที่สูงจนกว่าเจ้าหน้าที่ประกาศว่าปลอดภัย",
             "Tsunamis come as a series of waves over hours, and the first is often not the largest — stay high until officials say it's safe"),
            ("ระวังซากปรักหักพัง สายไฟ น้ำปนเปื้อน และอาคารที่โครงสร้างเสียหาย", "Watch for debris, power lines, contaminated water and structurally damaged buildings"),
        ],
        "vulnerable": [
            ("คนเดินช้า ผู้สูงอายุ เด็ก: ออกก่อนทันทีที่สงสัย ไม่ต้องรอยืนยัน", "Slow walkers, elderly people, children: leave the moment you suspect — don't wait for confirmation"),
        ],
        "myths": [
            ("❌ ลงไปดูหรือเก็บปลาตอนน้ำทะเลลด — นั่นคือสัญญาณว่าคลื่นกำลังมา มีคนเสียชีวิตแบบนี้จำนวนมากในปี 2547",
             "❌ Walking out to look or collect fish when the sea recedes — that is the sign the wave is coming; many died this way in 2004"),
            ("❌ คลื่นแรกผ่านไปแล้วกลับไปเก็บของได้ — คลื่นหลังอาจใหญ่กว่า", "❌ Going back for belongings after the first wave — later waves can be bigger"),
        ],
        "sources": ["NOAA · tsunami.gov", "FEMA · ready.gov/tsunamis", "UNESCO IOC · ioc.unesco.org", "ปภ. · disaster.go.th"],
    },
    "flood": {
        "icon": "🌧️", "name": ("น้ำท่วม · น้ำป่าไหลหลาก", "Flood · flash flood"),
        "signs": [
            ("ฝนตกหนักต่อเนื่องบนภูเขาต้นน้ำ · น้ำในลำห้วยขุ่นข้นและเพิ่มเร็ว · มีเสียงดังจากต้นน้ำ = น้ำป่ากำลังมา",
             "Persistent heavy rain upstream · creek water turning muddy and rising fast · a roar from upstream = a flash flood is coming"),
            ("ติดตามประกาศจากกรมอุตุนิยมวิทยา กรมชลประทาน และ ปภ.", "Follow alerts from the Thai Meteorological Department, Royal Irrigation Department and DDPM"),
        ],
        "before": [
            ("ย้ายของมีค่า ยา เอกสาร ขึ้นที่สูง · ชาร์จโทรศัพท์และพาวเวอร์แบงก์", "Move valuables, medicines and documents up high · charge phones and power banks"),
            ("รู้เส้นทางไปที่สูงและศูนย์พักพิงใกล้บ้าน · จอดรถไว้ที่สูง", "Know the route to high ground and the nearest shelter · park your car on high ground"),
        ],
        "during": [
            ("ได้รับคำสั่งอพยพ หรืออยู่ริมห้วยตอนน้ำป่ามา: ไปที่สูงทันที อย่ารอเก็บของ", "Ordered to evacuate, or by a creek as a flash flood comes: go to high ground now, don't stop for belongings"),
            ("อย่าเดินลุยน้ำไหล — น้ำไหลสูงแค่ราว 15 ซม. ก็ทำให้ล้มได้ · อย่าขับรถผ่านน้ำ — น้ำไหลราว 30 ซม. พัดรถได้ (\"เลี่ยงทาง อย่าเสี่ยงจม\")",
             "Don't walk through moving water — about 15 cm can knock you over · don't drive into it — about 30 cm of moving water can sweep a car away (\"Turn around, don't drown\")"),
            ("ตัดไฟที่เบรกเกอร์ถ้ามือ เท้า และพื้นแห้ง — ถ้าน้ำถึงปลั๊กแล้ว อย่าแตะอะไรที่เป็นไฟฟ้า", "Switch off at the main breaker only if your hands, feet and floor are dry — if water has reached sockets, touch nothing electrical"),
            ("ติดในบ้าน: ขึ้นชั้นบนสุด แต่อย่าขึ้นไปในห้องใต้หลังคาที่ปิดตาย (น้ำขึ้นแล้วออกไม่ได้) · ขึ้นหลังคาเมื่อจำเป็นเท่านั้น แล้วส่งสัญญาณขอความช่วยเหลือ",
             "Trapped at home: go to the highest floor, but not into a closed attic where rising water can trap you · go onto the roof only if necessary and signal for help"),
            ("รถจมน้ำ: ปลดเข็มขัด เปิดกระจกตั้งแต่ไฟยังใช้ได้ แล้วออกทางหน้าต่างทันที — อย่ารอให้น้ำเต็มรถ",
             "Car in water: unbuckle, open the window while power still works and get out through it immediately — don't wait for the car to fill"),
        ],
        "after": [
            ("น้ำท่วมมีเชื้อโรค สารเคมี และอาจมีไฟรั่ว — ใส่รองเท้าบูต ล้างมือบ่อย ทำแผลที่โดนน้ำทันที", "Floodwater carries germs, chemicals and possibly live current — wear boots, wash hands often, treat any wound that touched it at once"),
            ("มีไข้ ปวดกล้ามเนื้อน่อง ภายใน 2–3 สัปดาห์หลังลุยน้ำ: ไปหาหมอและบอกว่าลุยน้ำมา (อาจเป็นโรคฉี่หนู รักษาได้ถ้าเร็ว)",
             "Fever or calf pain within 2–3 weeks of wading: see a doctor and say you were in floodwater (possible leptospirosis — treatable if early)"),
            ("ต้มน้ำให้เดือดอย่างน้อย 1 นาทีก่อนดื่มจนกว่าประปาจะยืนยันว่าปลอดภัย · ทิ้งอาหารที่โดนน้ำท่วม", "Boil water at a rolling boil for at least 1 minute until the water supply is declared safe · throw away food that touched floodwater"),
            ("ห้ามใช้เครื่องปั่นไฟหรือเตาถ่านในบ้านหรือที่อับ — ก๊าซคาร์บอนมอนอกไซด์ไม่มีกลิ่นและฆ่าคนได้", "Never run generators or charcoal stoves indoors or in enclosed spaces — carbon monoxide is odourless and kills"),
            ("ระวังงู ตะขาบ และสัตว์มีพิษที่หนีน้ำเข้าบ้าน", "Watch for snakes, centipedes and other animals that sheltered in the house"),
        ],
        "vulnerable": [
            ("ผู้ป่วยติดเตียง/ใช้ออกซิเจน/ฟอกไต: ย้ายออกก่อนน้ำมา และแจ้ง อสม. หรือ ปภ. 1784 ล่วงหน้า", "Bed-bound people, oxygen or dialysis patients: move out before the water arrives and tell local health volunteers or 1784 early"),
            ("เด็ก: ห้ามเล่นน้ำท่วม — จมน้ำได้ในน้ำตื้นและอาจถูกไฟดูด", "Children: never play in floodwater — they can drown in shallow water or be electrocuted"),
        ],
        "myths": [
            ("❌ อยู่ในรถปลอดภัยกว่า — รถลอยและพลิกได้ในน้ำไม่ลึก การเสียชีวิตจากน้ำท่วมจำนวนมากเกิดในรถ",
             "❌ You're safer in the car — cars float and roll in shallow water; many flood deaths happen in vehicles"),
        ],
        "sources": ["FEMA · ready.gov/floods", "WHO · who.int (Flooding)", "CDC · cdc.gov (Floods, Leptospirosis)", "ปภ. · disaster.go.th", "กรมอุตุนิยมวิทยา · tmd.go.th"],
    },
    "storm": {
        "icon": "🌀", "name": ("พายุหมุน · พายุฤดูร้อน", "Tropical cyclone · severe storm"),
        "signs": [
            ("ติดตามเส้นทางพายุจากกรมอุตุนิยมวิทยา — พายุมีเวลาเตรียมตัวหลายวัน ใช้เวลานั้นให้เต็มที่",
             "Follow the storm track from the Meteorological Department — storms give days of warning; use them"),
        ],
        "before": [
            ("เก็บหรือผูกของที่ปลิวได้ (กระถาง ป้าย หลังคาสังกะสีหลวม) · ตัดกิ่งไม้ที่ยื่นเหนือบ้าน", "Bring in or tie down anything that can fly (pots, signs, loose roof sheets) · trim branches over the house"),
            ("อยู่ในพื้นที่คลื่นพายุซัดฝั่ง (ริมทะเลที่ต่ำ) และได้คำสั่งอพยพ: ไปก่อนพายุมา", "In a storm-surge zone (low coast) with an evacuation order: leave before the storm arrives"),
        ],
        "during": [
            ("อยู่ในอาคารแข็งแรง ห้องด้านในที่ไม่มีหน้าต่าง ชั้นล่างที่น้ำไม่ท่วม", "Stay in a strong building, in an interior room without windows, on the lowest floor that won't flood"),
            ("ลมสงบกลางพายุอาจเป็น \"ตาพายุ\" — ลมแรงจะกลับมาจากอีกทิศ อย่าออกไปข้างนอก", "A sudden calm may be the eye — the wind will return from the other direction; stay inside"),
            ("อย่าขับรถ อย่าหลบใต้ต้นไม้ใหญ่ ป้ายโฆษณา หรือเสาไฟ", "Don't drive; don't shelter under big trees, billboards or power poles"),
        ],
        "after": [
            ("สายไฟขาด: ถือว่ามีไฟทุกเส้น อยู่ห่างอย่างน้อย 10 เมตร แจ้งการไฟฟ้า", "Downed lines: treat every wire as live, stay at least 10 m away and report it"),
            ("ระวังน้ำท่วมและดินถล่มที่ตามมา · ห้ามใช้เครื่องปั่นไฟในที่อับ", "Watch for follow-on flooding and landslides · never run generators in enclosed spaces"),
        ],
        "vulnerable": [
            ("คนที่ต้องใช้ไฟฟ้ากับเครื่องมือแพทย์: เตรียมแบตสำรอง หรือย้ายไปที่มีไฟก่อนพายุมา", "People on powered medical devices: prepare backup power or move somewhere with power before the storm"),
        ],
        "myths": [
            ("❌ ติดเทปกากบาทที่กระจกกันแตก — ไม่ช่วยกันแตก และทำให้เศษชิ้นใหญ่ขึ้น · อยู่ห่างหน้าต่างแทน",
             "❌ Taping an X on windows stops them breaking — it doesn't, and makes larger shards · stay away from windows instead"),
        ],
        "sources": ["NOAA National Hurricane Center · nhc.noaa.gov", "FEMA · ready.gov/hurricanes", "WMO · wmo.int", "กรมอุตุนิยมวิทยา · tmd.go.th"],
    },
    "landslide": {
        "icon": "⛰️", "name": ("ดินถล่ม · โคลนถล่ม", "Landslide · mudflow"),
        "signs": [
            ("ฝนตกหนักหลายวันในพื้นที่ลาดชัน · ดินหรือถนนแตกร้าวใหม่ · ต้นไม้ เสาไฟ รั้ว เอียง · ประตูหน้าต่างเริ่มฝืด",
             "Days of heavy rain on slopes · new cracks in ground or roads · trees, poles or fences tilting · doors and windows starting to stick"),
            ("น้ำในลำห้วยขุ่นข้นทันที หรือลดลงทั้งที่ฝนยังตก (มีดินกั้นทางน้ำด้านบน) · เสียงดังครืนจากภูเขา",
             "Creek water suddenly muddy, or dropping while rain continues (debris damming upstream) · rumbling from the hillside"),
        ],
        "before": [
            ("บ้านตีนเขาหรือริมลำห้วย: รู้เส้นทางหนีที่ไม่ผ่านร่องน้ำ และตกลงกับเพื่อนบ้านว่าใครเฝ้าระวังกลางคืน",
             "Homes at the foot of slopes or by creeks: know an escape route that avoids channels, and agree with neighbours who watches at night"),
        ],
        "during": [
            ("เห็นสัญญาณ: ออกทันทีโดยวิ่งไปด้านข้าง ขวางทิศที่ดินไหลลงมา — อย่าวิ่งตามทางน้ำหรือหุบ",
             "See the signs: leave now, moving sideways across the slope away from the flow path — never down a channel or valley"),
            ("หนีไม่ทัน: ขดตัวเป็นลูกบอล ใช้แขนป้องศีรษะ", "Can't escape: curl into a tight ball and protect your head"),
        ],
        "after": [
            ("อยู่ห่างพื้นที่ถล่ม — ถล่มซ้ำได้ · แจ้ง 1784 เรื่องคนติดหรือหายโดยไม่เข้าไปเอง", "Stay away from the slide area — it can move again · report trapped or missing people to 1784 rather than going in"),
        ],
        "vulnerable": [],
        "myths": [],
        "sources": ["USGS Landslide Hazards · usgs.gov/programs/landslide-hazards", "กรมทรัพยากรธรณี · dmr.go.th", "ปภ. · disaster.go.th"],
    },
    "wildfire": {
        "icon": "🔥", "name": ("ไฟป่า", "Wildfire"),
        "signs": [
            ("ควันหนาใกล้เข้ามา เถ้าตกลงมา ลมแรงพัดมาทางบ้าน — ไฟป่าเคลื่อนเร็วกว่าที่คนวิ่งได้บนเนิน", "Thick smoke approaching, ash falling, strong wind toward you — wildfire moves uphill faster than people can run"),
        ],
        "before": [
            ("ถางวัสดุติดไฟรอบบ้านอย่างน้อย 10 เมตร (ใบไม้แห้ง กองฟืน) · เตรียมหน้ากาก N95", "Clear flammable material at least 10 m around the house (dry leaves, woodpiles) · keep N95 masks ready"),
        ],
        "during": [
            ("ได้คำสั่งอพยพ: ไปทันที ออกเร็วดีกว่าช้า — ควันทำให้ทางปิดได้ในไม่กี่นาที", "Ordered to evacuate: go now — early beats late; smoke can close roads within minutes"),
            ("ติดในรถ: จอดห่างพุ่มไม้และต้นไม้หนา ปิดกระจกและช่องลม ติดเครื่องไว้ เปิดไฟหน้า นอนลงที่พื้นรถ คลุมตัวด้วยผ้าห่ม",
             "Trapped in a car: park away from dense vegetation, close windows and vents, keep the engine running with headlights on, lie on the floor under a blanket"),
            ("ติดกลางแจ้ง: ไปที่ที่ไม่มีเชื้อเพลิง (ถนน ลานหิน แปลงที่ไหม้แล้ว) นอนคว่ำ คลุมตัว", "Trapped on foot: get to ground with no fuel (road, rock, already-burnt patch), lie face down and cover up"),
        ],
        "after": [
            ("กลับเข้าพื้นที่เมื่อเจ้าหน้าที่อนุญาต · ระวังตอไม้ที่ยังคุ ต้นไม้ไหม้ที่ล้มได้", "Return only when officials allow · watch for smouldering stumps and burnt trees that can fall"),
        ],
        "vulnerable": [
            ("เด็ก ผู้สูงอายุ คนเป็นหอบหืด/โรคหัวใจ: เลี่ยงควันเด็ดขาด อยู่ในห้องที่มีเครื่องฟอกอากาศ", "Children, older adults, people with asthma or heart disease: avoid smoke completely; stay in a room with an air purifier"),
        ],
        "myths": [
            ("❌ หน้ากากผ้าหรือหน้ากากอนามัยกันควันได้ — กันอนุภาคเล็กไม่ได้ ต้องเป็น N95 ที่แนบหน้า", "❌ Cloth or surgical masks protect from smoke — they don't stop fine particles; you need a well-fitted N95"),
        ],
        "sources": ["FEMA · ready.gov/wildfires", "CAL FIRE · readyforwildfire.org", "WHO · who.int (Wildfires)", "กรมอุทยานแห่งชาติฯ · dnp.go.th"],
    },
    "volcano": {
        "icon": "🌋", "name": ("ภูเขาไฟ (เมื่อเดินทางไปต่างประเทศ)", "Volcano (when travelling abroad)"),
        "signs": [
            ("ไทยไม่มีภูเขาไฟที่ยังปะทุ — เรื่องนี้สำคัญเมื่อไปอินโดนีเซีย ฟิลิปปินส์ ญี่ปุ่น ไอซ์แลนด์ ฯลฯ · ดูระดับเตือนภัยของประเทศนั้น",
             "Thailand has no active volcanoes — this matters when travelling to Indonesia, the Philippines, Japan, Iceland etc. · follow that country's alert level"),
        ],
        "before": [
            ("ลงทะเบียนกับสถานทูตไทยเมื่อเดินทาง · ห้ามเข้าเขตห้ามตามประกาศ", "Register with your embassy when travelling · never enter exclusion zones"),
        ],
        "during": [
            ("ทำตามคำสั่งอพยพทันที · หลีกเลี่ยงหุบเขาและท้องน้ำด้านล่างภูเขาไฟ — โคลนภูเขาไฟ (ลาฮาร์) ไหลตามทางน้ำได้ไกลหลายสิบกิโลเมตร",
             "Follow evacuation orders immediately · avoid valleys and river channels below the volcano — volcanic mudflows (lahars) travel tens of km along them"),
            ("เถ้าตก: อยู่ในอาคาร ปิดประตูหน้าต่าง · ออกนอกอาคารใส่ N95 แว่นกันลม แขนยาว", "Ashfall: stay indoors with doors and windows closed · outside, wear an N95, goggles and long sleeves"),
        ],
        "after": [
            ("เถ้าบนหลังคาหนักมากเมื่อเปียก หลังคาถล่มได้ — กวาดออกอย่างระวัง ไม่ขึ้นหลังคาคนเดียว", "Ash on roofs is very heavy when wet and can collapse them — clear carefully and never alone"),
            ("ขับรถช้า เถ้าลื่นและบดบังทัศนวิสัย", "Drive slowly — ash is slippery and cuts visibility"),
        ],
        "vulnerable": [], "myths": [],
        "sources": ["USGS Volcano Hazards · usgs.gov/programs/VHP", "IVHHN · ivhhn.org (ash health)", "WHO · who.int (Volcanic eruptions)"],
    },
    "heat": {
        "icon": "☀️", "name": ("ความร้อนจัด · ลมแดด (ฮีตสโตรก)", "Extreme heat · heatstroke"),
        "signs": [
            ("ฮีตสโตรก (ฉุกเฉิน): ตัวร้อนจัดมาก สับสน พูดไม่รู้เรื่อง ชัก หรือหมดสติ — ผิวอาจแห้งหรือยังมีเหงื่อก็ได้",
             "Heatstroke (emergency): very high body temperature, confusion, slurred speech, seizure or collapse — skin may be dry or still sweating"),
            ("เพลียแดด (ก่อนจะเป็นฮีตสโตรก): เหงื่อออกมาก อ่อนเพลีย เวียนหัว คลื่นไส้ ตะคริว", "Heat exhaustion (before heatstroke): heavy sweating, weakness, dizziness, nausea, cramps"),
        ],
        "before": [
            ("ดื่มน้ำสม่ำเสมอแม้ไม่กระหาย · เลี่ยงงานหนักกลางแจ้งช่วง 11:00–15:00 · ใส่เสื้อผ้าสีอ่อนหลวม", "Drink regularly even when not thirsty · avoid heavy outdoor work 11:00–15:00 · wear light, loose clothes"),
            ("โทรเช็กผู้สูงอายุที่อยู่คนเดียววันละครั้งช่วงร้อนจัด", "Call older people who live alone once a day during heatwaves"),
        ],
        "during": [
            ("สงสัยฮีตสโตรก: โทร 1669 ทันที แล้วลดอุณหภูมิให้เร็วที่สุดระหว่างรอ — แช่น้ำเย็นถ้าทำได้ หรือราดน้ำทั่วตัวแล้วเปิดพัดลม วางถุงน้ำแข็งที่คอ รักแร้ ขาหนีบ",
             "Suspected heatstroke: call 1669 now, then cool as fast as possible while waiting — cold-water immersion if possible, or soak the body and fan, ice packs on neck, armpits, groin"),
            ("ห้ามป้อนน้ำคนที่ไม่รู้สึกตัวเต็มที่ (สำลักได้)", "Don't give drinks to anyone not fully alert (choking risk)"),
            ("เพลียแดด: ย้ายเข้าที่เย็น นอนยกขา ดื่มน้ำหรือเกลือแร่ทีละน้อย — ไม่ดีขึ้นใน 30 นาที หรือแย่ลง ไปโรงพยาบาล",
             "Heat exhaustion: move somewhere cool, lie with legs raised, sip water or oral rehydration salts — not better in 30 minutes or getting worse, go to hospital"),
        ],
        "after": [("พักต่อเนื่องอย่างน้อย 1–2 วันหลังเพลียแดด ร่างกายยังฟื้นไม่เต็มที่", "Rest for at least 1–2 days after heat exhaustion — the body is still recovering")],
        "vulnerable": [
            ("ห้ามทิ้งเด็กหรือสัตว์เลี้ยงไว้ในรถแม้ไม่กี่นาที — ในรถร้อนถึงอันตรายได้เร็วมาก", "Never leave children or pets in a car, even for minutes — cars heat to deadly levels very fast"),
            ("ผู้สูงอายุ คนป่วยโรคหัวใจ/ไต/เบาหวาน คนกินยาขับปัสสาวะ: เสี่ยงสูง ต้องมีคนคอยดู", "Older adults, people with heart/kidney disease or diabetes, people on diuretics: high risk — someone should check on them"),
        ],
        "myths": [
            ("❌ พัดลมอย่างเดียวพอเสมอ — เมื่ออากาศร้อนจัดมาก (ราว 35°C ขึ้นไป) พัดลมอย่างเดียวกันฮีตสโตรกไม่ได้ ต้องเปียกตัวหรือเข้าที่เย็น",
             "❌ A fan is always enough — in extreme heat (around 35°C and above) a fan alone won't prevent heatstroke; wet the skin or get somewhere cool"),
            ("❌ ดื่มเหล้าเบียร์คลายร้อน — แอลกอฮอล์ทำให้ขาดน้ำเร็วขึ้น", "❌ Beer or alcohol cools you down — alcohol dehydrates you faster"),
        ],
        "sources": ["WHO · who.int (Heat and health)", "CDC · cdc.gov/heat-health", "กรมควบคุมโรค · ddc.moph.go.th"],
    },
    "haze": {
        "icon": "😷", "name": ("ฝุ่น PM2.5 · หมอกควัน", "PM2.5 · haze"),
        "signs": [("ดูค่าฝุ่นจริงที่ Air4Thai (air4thai.pcd.go.th) หรือแอป Air4Thai — สีส้มขึ้นไปเริ่มมีผลต่อสุขภาพ", "Check live readings on Air4Thai (air4thai.pcd.go.th) — orange and above affects health")],
        "before": [
            ("เตรียมหน้ากาก N95/KN95 ขนาดพอดีหน้า · ห้องนอนที่ปิดสนิทพร้อมเครื่องฟอกอากาศแบบ HEPA", "Keep well-fitting N95/KN95 masks · a sealable bedroom with a HEPA air purifier"),
        ],
        "during": [
            ("อยู่ในอาคาร ปิดประตูหน้าต่าง เปิดเครื่องฟอกอากาศ · ไม่มีเครื่องฟอก ทำเองได้จากพัดลมกล่อง + แผ่นกรองแอร์ (ฟิลเตอร์ MERV 13) ติดด้านหลัง",
             "Stay indoors, close doors and windows, run an air purifier · no purifier: a box fan with a MERV-13 furnace filter strapped to the back works"),
            ("ออกข้างนอกใส่ N95 ที่แนบหน้า (ไม่มีลมรั่วข้างแก้ม) · งดออกกำลังกายกลางแจ้ง", "Outside, wear an N95 sealed to the face (no gaps at the cheeks) · skip outdoor exercise"),
            ("หายใจลำบาก แน่นหน้าอก ไอไม่หยุด โดยเฉพาะคนมีโรคประจำตัว: ไปโรงพยาบาล", "Shortness of breath, chest tightness, non-stop coughing — especially with a chronic illness: go to hospital"),
        ],
        "after": [("เปลี่ยนแผ่นกรองเครื่องฟอกอากาศตามกำหนด ไส้กรองที่ตันไม่กรองอะไรแล้ว", "Replace purifier filters on schedule — a clogged filter stops working")],
        "vulnerable": [("เด็ก หญิงตั้งครรภ์ ผู้สูงอายุ คนเป็นโรคหัวใจ/ปอด: เริ่มป้องกันตั้งแต่ค่าฝุ่นสีเหลือง", "Children, pregnant women, older adults, people with heart/lung disease: protect yourself from yellow level")],
        "myths": [("❌ หน้ากากอนามัยหรือหน้ากากผ้ากัน PM2.5 ได้ — กันได้น้อยมาก", "❌ Surgical or cloth masks stop PM2.5 — they barely do")],
        "sources": ["กรมควบคุมมลพิษ · air4thai.pcd.go.th", "WHO · who.int (Air pollution)", "US EPA · airnow.gov"],
    },
    "lightning": {
        "icon": "⚡", "name": ("ฟ้าผ่า · พายุฝนฟ้าคะนอง", "Lightning · thunderstorm"),
        "signs": [("ได้ยินเสียงฟ้าร้อง = อยู่ใกล้พอที่ฟ้าจะผ่าได้", "If you can hear thunder, you are close enough to be struck")],
        "before": [("ดูพยากรณ์ก่อนไปกลางแจ้ง (ทุ่งนา สนามกอล์ฟ ชายหาด ภูเขา เรือ)", "Check the forecast before going out in the open (fields, golf courses, beaches, mountains, boats)")],
        "during": [
            ("ฟ้าร้องเมื่อไหร่ เข้าอาคารทันที — ที่ปลอดภัยคืออาคารที่ปิดมิดชิดมีระบบไฟฟ้าและประปา หรือรถยนต์หลังคาเหล็กที่ปิดกระจก",
             "When thunder roars, go indoors — safe shelter is an enclosed building with wiring and plumbing, or a hard-topped metal car with windows closed"),
            ("ศาลา เพิงโล่ง เต็นท์ ใต้ต้นไม้ ไม่ปลอดภัย · ขึ้นจากน้ำทันที", "Open pavilions, sheds, tents and trees are not safe · get out of the water immediately"),
            ("ในอาคาร: อย่าใช้โทรศัพท์บ้านแบบมีสาย อย่าอาบน้ำ อยู่ห่างหน้าต่างและประตูเหล็ก", "Indoors: avoid corded phones and showers, stay away from windows and metal doors"),
            ("ติดกลางแจ้งไม่มีที่หลบ: ลงจากที่สูง ห่างต้นไม้เดี่ยวและรั้วลวด ถ้าไปเป็นกลุ่มให้แยกห่างกันหลายเมตร แล้วรีบไปหาที่หลบต่อ",
             "Caught outside with no shelter: get off high ground, away from lone trees and wire fences; groups spread several metres apart — and keep heading for shelter"),
        ],
        "after": [
            ("รอ 30 นาทีหลังได้ยินเสียงฟ้าร้องครั้งสุดท้ายก่อนออกไปข้างนอก", "Wait 30 minutes after the last thunder before going back outside"),
            ("คนถูกฟ้าผ่าไม่มีไฟฟ้าค้างในตัว แตะได้ทันที — โทร 1669 และเริ่มทำ CPR ถ้าไม่หายใจ", "Lightning victims carry no charge — touch them at once; call 1669 and start CPR if they aren't breathing"),
        ],
        "vulnerable": [],
        "myths": [
            ("❌ ยางรถกันฟ้าผ่า — ที่ปกป้องคือโครงเหล็กของรถ ไม่ใช่ยาง (รถเปิดประทุน มอเตอร์ไซค์ ไม่ปลอดภัย)", "❌ Rubber tyres protect you — it's the metal body that does (convertibles and motorbikes aren't safe)"),
            ("❌ ฟ้าไม่ผ่าซ้ำที่เดิม — ผ่าซ้ำได้ โดยเฉพาะที่สูง", "❌ Lightning never strikes the same place twice — it does, especially tall objects"),
        ],
        "sources": ["NOAA National Weather Service · weather.gov/safety/lightning", "CDC · cdc.gov (Lightning)", "กรมอุตุนิยมวิทยา · tmd.go.th"],
    },
    "cold": {
        "icon": "❄️", "name": ("อากาศหนาวจัด", "Extreme cold"),
        "signs": [("ภาวะตัวเย็นเกิน: สั่นมาก แล้วกลับหยุดสั่น สับสน พูดช้า ง่วงผิดปกติ — อันตรายแม้ไม่ถึงจุดเยือกแข็งถ้าตัวเปียกและลมแรง",
                   "Hypothermia: violent shivering that then stops, confusion, slow speech, unusual drowsiness — dangerous above freezing if wet and windy")],
        "before": [("เตรียมเสื้อผ้าหลายชั้น หมวก ถุงเท้า ผ้าห่ม · ดูแลผู้สูงอายุและคนไร้บ้านในชุมชน", "Prepare layers, hats, socks, blankets · look out for older people and homeless people nearby")],
        "during": [
            ("ห้ามจุดเตาถ่าน เตาแก๊ส หรือเครื่องปั่นไฟในห้องปิด — มีคนเสียชีวิตจากก๊าซคาร์บอนมอนอกไซด์ทุกหน้าหนาว", "Never use charcoal braziers, gas heaters or generators in closed rooms — carbon monoxide kills people every cold season"),
            ("สงสัยตัวเย็นเกิน: พาเข้าที่อุ่น ถอดเสื้อผ้าเปียก ห่มผ้าแห้งที่ลำตัวก่อนแขนขา ดื่มเครื่องดื่มอุ่นถ้ารู้สึกตัวดี แล้วโทร 1669",
             "Suspected hypothermia: move somewhere warm, remove wet clothing, wrap the core before limbs, give warm drinks only if fully alert, call 1669"),
        ],
        "after": [("ปวดหัว เวียนหัว คลื่นไส้พร้อมกันหลายคนในห้องที่จุดเตา = อาจเป็นพิษคาร์บอนมอนอกไซด์ ออกไปที่อากาศถ่ายเทแล้วโทร 1669",
                   "Several people in a heated room with headache, dizziness, nausea = possible carbon-monoxide poisoning; get to fresh air and call 1669")],
        "vulnerable": [("ทารกและผู้สูงอายุเสียความร้อนเร็ว — ห่มให้อุ่นแต่ไม่คลุมหน้าทารก", "Babies and older adults lose heat fast — keep them warm but never cover a baby's face")],
        "myths": [("❌ ดื่มเหล้าช่วยให้อุ่น — รู้สึกอุ่นแต่ร่างกายเสียความร้อนเร็วขึ้น", "❌ Alcohol warms you up — it feels warm but makes the body lose heat faster"),
                  ("❌ ถูผิวที่เย็นจัดแรงๆ — ทำให้เนื้อเยื่อเสียหายมากขึ้น ให้ค่อยๆ อุ่นแทน", "❌ Rubbing frozen skin hard — it causes more damage; rewarm gently")],
        "sources": ["CDC · cdc.gov (Winter weather, Carbon monoxide)", "WHO · who.int", "กรมควบคุมโรค · ddc.moph.go.th"],
    },
    "drought": {
        "icon": "🏜️", "name": ("ภัยแล้ง · น้ำดื่มขาดแคลน", "Drought · water shortage"),
        "signs": [("ประปาไหลอ่อน/ไม่ไหล ประกาศงดจ่ายน้ำ น้ำบ่อแห้ง", "Weak or no tap water, supply cuts announced, wells drying up")],
        "before": [("สำรองน้ำดื่มคนละ 3–4 ลิตรต่อวัน อย่างน้อย 3 วัน ในภาชนะสะอาดมีฝาปิด", "Store 3–4 litres of drinking water per person per day for at least 3 days, in clean covered containers")],
        "during": [
            ("แยกน้ำดื่มออกจากน้ำใช้ · น้ำไม่แน่ใจ ต้มให้เดือดพล่านอย่างน้อย 1 นาที", "Keep drinking water separate from washing water · unsure water: bring to a rolling boil for at least 1 minute"),
            ("ต้มไม่ได้: หยดน้ำยาฟอกขาวชนิดไม่มีกลิ่น (คลอรีน 5–9%) ราว 2 หยดต่อน้ำ 1 ลิตร คนแล้วรอ 30 นาที ต้องยังได้กลิ่นคลอรีนอ่อนๆ",
             "Can't boil: add about 2 drops of unscented household bleach (5–9% chlorine) per litre, stir and wait 30 minutes — a faint chlorine smell should remain"),
            ("ขอรถน้ำจาก อบต./เทศบาล หรือ ปภ. 1784", "Request water trucks from the local council or DDPM 1784"),
        ],
        "after": [("ล้างภาชนะเก็บน้ำก่อนใช้ใหม่ · ระวังโรคท้องร่วงจากน้ำไม่สะอาด", "Clean storage containers before reuse · watch for diarrhoea from unsafe water")],
        "vulnerable": [("ทารก ผู้สูงอายุ คนป่วย: ขาดน้ำเร็ว — ปัสสาวะน้อย สีเข้ม ซึม ต้องให้ดื่มน้ำ/เกลือแร่และพาไปหาหมอ",
                        "Babies, older adults, sick people dehydrate fast — little dark urine or drowsiness needs fluids/ORS and a doctor")],
        "myths": [],
        "sources": ["WHO · who.int (Drinking-water)", "CDC · cdc.gov (Emergency water disinfection)", "US EPA · epa.gov (Emergency disinfection of drinking water)", "ปภ. · disaster.go.th"],
    },
    "fire": {
        "icon": "🚒", "name": ("ไฟไหม้อาคาร", "Building fire"),
        "signs": [("ควันจากไฟไหม้ทำให้หมดสติได้ภายในไม่กี่นาที — คนส่วนใหญ่เสียชีวิตจากควัน ไม่ใช่เปลวไฟ", "Fire smoke can knock you unconscious in minutes — most fire deaths are from smoke, not flames")],
        "before": [("ติดเครื่องตรวจจับควัน · รู้ทางหนีไฟ 2 ทางจากทุกห้อง · ห้ามล็อกหรือวางของขวางประตูหนีไฟ", "Fit smoke alarms · know two ways out of every room · never lock or block fire exits")],
        "during": [
            ("ออกทันที ไม่ย้อนกลับไปเอาของ ไม่ใช้ลิฟต์ — แล้วโทร 199 จากข้างนอก", "Get out now, never go back for belongings, never use lifts — then call 199 from outside"),
            ("มีควัน: ก้มต่ำคลานใต้ควัน อากาศดีอยู่ใกล้พื้น", "Smoke: get low and crawl under it — cleaner air is near the floor"),
            ("ก่อนเปิดประตู ใช้หลังมือแตะประตูและลูกบิด — ร้อน = มีไฟอีกฝั่ง ใช้ทางอื่น", "Before opening a door, touch it and the handle with the back of your hand — hot means fire behind it; use another way"),
            ("ออกไม่ได้: ปิดประตู อุดช่องด้วยผ้าเปียก โทร 199 บอกห้องและชั้น ส่งสัญญาณที่หน้าต่าง", "Can't get out: close the door, seal gaps with wet cloth, call 199 with your room and floor, signal from the window"),
            ("เสื้อผ้าติดไฟ: หยุด ล้มลง กลิ้ง ใช้มือปิดหน้า", "Clothes on fire: stop, drop and roll, covering your face"),
        ],
        "after": [("แผลไฟไหม้: ราดน้ำสะอาดอุณหภูมิห้อง 20 นาที ห้ามทายาสีฟัน น้ำปลา หรือน้ำแข็ง", "Burns: cool under clean room-temperature running water for 20 minutes — no toothpaste, fish sauce or ice")],
        "vulnerable": [("คนที่ลงบันไดเองไม่ได้: บอกนิติ/ผู้จัดการอาคารไว้ล่วงหน้า และรอที่จุดรอความช่วยเหลือใกล้บันไดหนีไฟ", "People who can't use stairs: tell building management in advance and wait at the refuge point by the fire stairs")],
        "myths": [("❌ ซ่อนในตู้หรือใต้เตียง — นักดับเพลิงหาเจอยาก ให้อยู่ใกล้หน้าต่างและส่งสัญญาณ", "❌ Hiding in a wardrobe or under a bed — firefighters can't find you; stay by a window and signal")],
        "sources": ["NFPA · nfpa.org", "FEMA · ready.gov/home-fires", "British Red Cross / IFRC (burns first aid)", "กรมป้องกันและบรรเทาสาธารณภัย · disaster.go.th"],
    },
    "gas": {
        "icon": "🧪", "name": ("แก๊สรั่ว · สารเคมีรั่วไหล", "Gas leak · chemical release"),
        "signs": [("กลิ่นแก๊สหุงต้ม (คล้ายไข่เน่า) · ประกาศโรงงาน/เจ้าหน้าที่เรื่องสารเคมีรั่ว · ควันหรือกลิ่นแปลกพร้อมแสบตาแสบจมูก",
                   "Cooking-gas smell (like rotten eggs) · factory/official alerts about a chemical release · strange smoke or smell with stinging eyes and nose")],
        "before": [("รู้ตำแหน่งวาล์วแก๊สและปิดหลังใช้ทุกครั้ง · บ้านใกล้นิคมอุตสาหกรรม: รู้เส้นทางอพยพของพื้นที่", "Know where the gas valve is and close it after use · near an industrial estate: know the area's evacuation route")],
        "during": [
            ("แก๊สรั่วในบ้าน: ห้ามกดสวิตช์ ถอดปลั๊ก จุดไฟ หรือใช้โทรศัพท์ในจุดนั้น · เปิดหน้าต่าง ปิดวาล์ว ออกไปข้างนอก แล้วโทรจากข้างนอก",
             "Gas leak at home: no switches, plugs, flames or phones in that area · open windows, shut the valve, go outside and call from there"),
            ("สารเคมีรั่วข้างนอกและสั่งให้หลบในอาคาร: เข้าอาคาร ปิดประตูหน้าต่าง ปิดแอร์/พัดลมดูดอากาศ อยู่ห้องด้านใน ติดตามประกาศ",
             "Chemical release outside with a shelter-in-place order: go inside, close doors and windows, turn off AC/extractor fans, stay in an interior room, follow announcements"),
            ("สั่งให้อพยพ: ไปทางที่ตั้งฉากกับทิศลมหรือเหนือลม ไม่เดินฝ่ากลุ่มควัน", "Ordered to evacuate: move crosswind or upwind — never through the cloud"),
            ("สารโดนตัว: ถอดเสื้อผ้าชั้นนอก (ตัดถ้าต้องดึงผ่านหน้า) ล้างตัวด้วยน้ำและสบู่จำนวนมาก แล้วโทร 1669",
             "Chemical on you: remove outer clothing (cut it rather than pull over your face), wash with plenty of soap and water, call 1669"),
        ],
        "after": [("กลับเข้าพื้นที่เมื่อเจ้าหน้าที่ยืนยัน · มีอาการไอ แน่นหน้าอก ตาพร่าตามมา ไปโรงพยาบาลและบอกว่าสัมผัสสารอะไร", "Return only when officials confirm · cough, chest tightness or blurred vision later: go to hospital and say what you were exposed to")],
        "vulnerable": [],
        "myths": [],
        "sources": ["FEMA · ready.gov/chemical", "CDC/ATSDR · atsdr.cdc.gov", "กรมควบคุมมลพิษ · pcd.go.th", "ปภ. · disaster.go.th"],
    },
}

ORDER = ["quake", "tsunami", "flood", "storm", "landslide", "wildfire", "heat", "haze", "lightning", "cold", "drought", "fire", "gas", "volcano"]

# ชื่อภัยจากระบบอื่น → คู่มือ (core/engine_bridge._HAZARDS · core/hazards GDACS)
ALIAS = {"quake": "quake", "EQ": "quake", "tsunami": "tsunami", "flood": "flood", "FL": "flood", "storm": "storm", "TC": "storm",
         "landslide": "landslide", "wildfire": "wildfire", "WF": "wildfire", "heat": "heat", "haze": "haze", "lightning": "lightning",
         "cold": "cold", "drought": "drought", "DR": "drought", "fire": "fire", "gas": "gas", "VO": "volcano", "volcano": "volcano"}


def public(lang: str = "th") -> dict:
    """คู่มือทั้งชุดในภาษาเดียว (th หรือ en) สำหรับหน้า /survival"""
    i = 0 if lang == "th" else 1
    pick = lambda rows: [r[i] for r in rows]
    return {"lang": "th" if i == 0 else "en",
            "hotlines": [{"n": n, "label": (th, en)[i]} for n, th, en in HOTLINES],
            "kit": pick(KIT),
            "hazards": [{"key": k, "icon": HAZARDS[k]["icon"], "name": HAZARDS[k]["name"][i],
                         **{sec: pick(HAZARDS[k][sec]) for sec in ("signs", "before", "during", "after", "vulnerable", "myths")},
                         "sources": list(HAZARDS[k]["sources"])} for k in ORDER]}
