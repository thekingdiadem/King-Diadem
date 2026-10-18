"""ชั้นตรวจที่สอง — ภาษาอังกฤษ (แยกไฟล์จาก second_layer.py เพราะยาว)

ที่มา: รอบตรวจ 346 ข้อความอังกฤษแบบที่คนพิมพ์จริง (ตัวพิมพ์เล็ก ศัพท์วัยรุ่น นักท่องเที่ยวในไทย)
หลุด 145 ข้อเป็น Risk 0 ทั้งหมด — รวมศัพท์ที่วัยรุ่นใช้เลี่ยงการกรอง (kms · unalive · ctb · sewerslide),
แผนพร้อมวิธี ("hose in the car exhaust" "took like 30 xanax"), "gonna kill/shoot …" ทุกรูป,
และมิจฉาชีพที่นักท่องเที่ยวเจอในไทย

รูปแบบ (regex, ชนิด) ชนิดเดียวกับ second_layer.UPGRADES ("crisis" หรือชื่อหัวข้อใน kernel_voice.TOPICS)
"""
from __future__ import annotations

import re

_I = re.I

EN_UPGRADES: list[tuple[re.Pattern, str]] = [
    # ── อยากตาย: ศัพท์เลี่ยงการกรอง · พิมพ์แปลง · ข้อความลา · ยกของให้คนอื่น ───────────────
    (re.compile(r"\bk\s*m\s*s\b|\bkys\b|\bunaliv(?:e|ing)\b|\bctb\b|\bsewer\s*slide\b|\bend(?:ing)?\s+myself\b|"
                r"(?<!n't )(?<!nt )(?<!not )(?<!never )\b(?:want|wanna|gonna|going)\s*(?:2|to)?\s*d[!1i]e\b(?!\s+(?:of|laughing|happy|old|in my sleep at))|\bi\s+want\s+2\s+die\b|"
                r"\bthis is my goodbye\b|\bby the time you (?:read|see) this\b|\bwrote (?:a )?letters? (?:for|to) my family\b|"
                r"\bfinal message\b|\bgoodbye world\b|\bgiving away my (?:stuff|things)\b|\b(?:won'?t|wont) need it (?:after|anymore)\b|"
                r"\bdon'?t need it where i'?m going\b|\bdont need it where im going\b|"
                r"\bbeen cutting (?:again|myself)\b|\bburning myself\b|\bi deserve to die\b|\bi should (?:just )?die\b|"
                r"\bnobody (?:will|would)(?: even)? (?:miss|notice|care)\b[^.\n]{0,25}?\b(?:dead|gone|die|died)\b|"
                r"\bdo(?:n'?t|nt) (?:want|wanna) (?:to )?be here anymore\b|\bdo(?:n'?t|nt) (?:want|wanna) (?:to )?wake up\b(?!\s+(?:(?:tomorrow|today)\s+)?(?:early|late|at|before|so|for|on|this|tomorrow morning))|"
                r"\bwhat'?s the point (?:of|in) living\b|\bwhats the point of living\b|\bno reason to keep living\b|"
                r"\bdisappear forever\b|\btired of existing\b|\bdo(?:n'?t|nt) see a future\b|\bending it (?:this|tonight|tomorrow|soon)\b", _I),
     "crisis"),
    # ── อยากตาย: มีวิธี/แผน/เวลา ─────────────────────────────────────────────────────
    (re.compile(r"\b(?:hose|tube|pipe)\b[^.\n]{0,30}?\bexhaust\b|\bexhaust\b[^.\n]{0,24}?\bgarage\b|"
                r"\btook\b[^.\n]{0,12}?\b\d{2,}\s*(?:xanax|ambien|valium|benzos?)\b|"
                r"\bmixed\b[^.\n]{0,24}?\b(?:pills|meds|benzos?)\b[^.\n]{0,24}?\b(?:vodka|alcohol|beer|wine|whiskey|booze)\b|"
                r"\bswallowed all\b|\bslit(?:ting)? (?:my )?wrists?\b|\bloading\b[^.\n]{0,16}?\bgun\b|"
                r"\b(?:at|on) the edge of the (?:roof|building|cliff|bridge|balcony)\b|\bbought a gun\b[^\n]{0,24}?\b(?:over|end|soon|done)\b|"
                r"\b(?:jump|jumping)\s+off\b[^.\n]{0,30}?\b(?:balcony|building|roof|bridge|floor|cliff)\b|"
                r"\bwalk(?:ing)? into the (?:sea|ocean|river|water)\b|\bi'?ve decided\b[^\n]{0,30}?\b(?:bridge|roof|tonight|\d\s*am)\b|"
                r"\b(?:od|overdose)\s+on\b|\btake all (?:my|my moms?'?s?|the)\b[^.\n]{0,12}?\b(?:pills|meds|tablets)\b|"
                r"\bstopped taking my\b[^.\n]{0,24}?\b(?:pills|meds)\b[^.\n]{0,24}?\b(?:so i can go|to die|end it|be done)\b|"
                r"\bdrown myself\b|\bhow many\b[^.\n]{0,20}?\b(?:tylenol|paracetamol|panadol|pills|sleeping pills)\b[^.\n]{0,30}?\b(?:lethal|to die|not wake|kill|fatal)\b|"
                r"\b(?:paracetamol|tylenol|panadol)\b[^.\n]{0,10}?\bis lethal\b", _I),
     "crisis"),
    # ── จะทำร้ายคนอื่น ───────────────────────────────────────────────────────────────
    (re.compile(r"\b(?:bring(?:ing)?|take|taking)\b[^.\n]{0,20}?\bgun\b[^.\n]{0,24}?\b(?:school|class|work|office)\b|\bshoot up\b|"
                r"\b(?:going to|gonna|will|i'?ll|im going to|i'?m going to)\s+(?:kill|shoot|stab|murder|hurt|beat|strangle|burn|poison)\s+"
                r"(?:him|her|them|everyone|every1|my|the|his|that|those|all|people|someone|somebody|kids|coworkers|classmates)\b|"
                r"\bhave a (?:knife|gun)\b[^.\n]{0,30}?\bwaiting\b|\bmake them (?:all )?pay\b[^.\n]{0,40}?\bplan\b|"
                r"\bvoices?\b[^.\n]{0,24}?\b(?:telling|tell|say|says|saying)\b[^.\n]{0,24}?\b(?:hurt|kill|stab|harm)\b|"
                r"\b(?:want|wanna) to (?:strangle|hurt|smother|shake)\s+(?:my )?(?:baby|newborn|kids?|son|daughter)\b|"
                r"\b(?:hurt|harm)(?:ing)? my (?:newborn|baby|kids|children)\b|\bthinking of hurting my\b|"
                r"\b(?:want|wanna) to hurt someone\b|\bburn (?:his|her|their) house\b|\bbeat my (?:gf|girlfriend|wife|bf|boyfriend|kid)\b", _I),
     "harm_others"),
    # ── ร่างกาย / ยา / คลอด / แพ้ / สัตว์กัด (นักท่องเที่ยวในไทย) ──────────────────────────────
    (re.compile(r"\b(?:vodka|alcohol|drunk|booze)\b[^.\n]{0,30}?\b(?:benzos?|xanax|pills)\b|\bbarely breathing\b|"
                r"\bdrank\b[^.\n]{0,16}?\b(?:drain cleaner|bleach|pesticide|weed killer|paraquat)\b", _I), "overdose"),
    (re.compile(r"\bfell off (?:the |his |her |my )?(?:scooter|motorbike|bike)\b|\bisn'?t moving\b|\bisnt moving\b|\bbone sticking out\b|"
                r"\bstung by a bee\b[^.\n]{0,24}?\bwheez|\b(?:lips|throat|tongue|face) (?:is |are )?swell|"
                r"\bcan'?t lift (?:his|her|my) arm\b|\bcant lift (?:his|her|my) arm\b|\btalking weird\b|\bworst headache of my life\b|"
                r"\bfoaming at (?:the )?mouth\b|\bblood sugar is \d{2}\b|\bhypoglycemi|\bsugar is hi\b|\bfruity breath\b|"
                r"\bstopped sweating\b|\bdeep\b[^.\n]{0,20}?\b(?:won'?t stop|wont stop|blood everywhere)\b|\bblood everywhere\b|"
                r"\bwater broke\b|\bbaby is coming\b|\bhigh fever\b[^.\n]{0,30}?\blimp\b|\bthrowing up for \d+ days\b|"
                r"\bcan'?t keep (?:water|anything) down\b|\bcant keep (?:water|anything) down\b|\bbleeding gums\b|"
                r"\b(?:bit(?:ten)?|bite) by a (?:street |soi |stray )?(?:dog|monkey|cat)\b|\b(?:dog|monkey|cat) bit\b(?![^\n]{0,12}\bplayful)|\brabies\b|"
                r"\bjellyfish\b|\bscorpion\b|\bmotorbike accident\b|\bscooter (?:accident|crash)\b|\bcrashed my (?:scooter|motorbike|bike)\b", _I),
     "health_emergency"),
    # ── ภัยพิบัติ / หลงทาง ─────────────────────────────────────────────────────────────
    (re.compile(r"\bboat (?:is )?sinking\b|\btaking (?:on )?water\b|\bcurrent (?:is )?pulling\b|\bsea is pulling back\b|"
                r"\bwater (?:is )?receding\b[^.\n]{0,20}?\bbeach\b", _I), "health_emergency"),
    (re.compile(r"\blost (?:hiking|in the (?:jungle|mountains|forest|woods))\b|\bwe are lost\b|\bcan'?t find (?:the )?trail\b|\bno signal\b[^.\n]{0,20}?\blost\b", _I),
     "stranded"),
    # ── ถูกทำร้าย / ควบคุม / ค้ามนุษย์ / แบล็กเมล ─────────────────────────────────────────
    (re.compile(r"\bkeeps? (?:our|my) passports?\b|\blocked us in\b|\bcan'?t leave the (?:building|compound|factory)\b|"
                r"\b(?:job|work)\b[^.\n]{0,30}?\b(?:myanmar|myawaddy|cambodia|laos|shwe kokko|kk park)\b|"
                r"\b(?:myanmar|myawaddy|cambodia|laos)\b[^.\n]{0,40}?\b(?:can'?t leave|cant leave|took (?:his|her|my) (?:phone|passport))\b", _I),
     "trafficking"),
    (re.compile(r"\bdrugged and (?:assaulted|raped)\b|\bwas (?:raped|sexually assaulted)\b", _I), "sexual_abuse"),
    (re.compile(r"\b(?:nudes|pics|photos|videos?)\b[^.\n]{0,30}?\b(?:wants? money|unless i pay|send (?:them )?to my (?:family|friends))\b|\bsextortion\b", _I),
     "sextortion"),
    (re.compile(r"\bnursing home staff hit\b|\btakes my (?:phone|money)\b[^.\n]{0,30}?\b(?:won'?t let|wont let)\b|"
                r"\bnot allowed to leave the house\b|\bcontrols everything\b|\bdomestic violence\b", _I), "violence"),
    # ── มิจฉาชีพที่นักท่องเที่ยว/ชาวต่างชาติในไทยเจอ ──────────────────────────────────────
    (re.compile(r"\bmoney laundering\b|\bsafe account\b|\b(?:pretending|claiming|claims?) to be (?:the )?police\b|\bdsi\b|\bfake police\b|"
                r"\bpackage with drugs\b|\bsent my otp\b|\bremote access\b|\btax fee before withdraw|\binvest in crypto\b|\bpig butchering\b|"
                r"\bneeds money for a (?:flight|ticket|visa)\b|\bromance scam\b|\bcall cent(?:er|re) scam\b|\bnew number asking for money\b|"
                r"\bclick (?:the )?link to pay\b|\bwon an? (?:iphone|prize)\b[^.\n]{0,20}?\bpay\b|\b(?:grand palace|palace) (?:is )?closed\b|\bgem shop\b|"
                r"\bcrypto (?:investment )?scam\b", _I),
     "scam"),
    # ── รอบหาบั๊ก ML: แผน/เจตนาที่ไม่มีคำหลักตรงๆ · สะกดเลี่ยง ("k1ll" "sui cide") ──────────────────
    (re.compile(r"\bk[1!|]ll\s+myself\b|\bsui\s+cide\b|\bhang(?:ing)? myself\b|\bpills lined up\b|\bi'?ll (?:just )?end it\b|"
                r"\bgonna end it\b|\bend it (?:tonight|tonite|today)\b|\bon (?:the|a) (?:bridge|roof|ledge)\b[^.\n]{0,40}?\b(?:jump|gonna|going to)\b|"
                r"\bdrive (?:my car )?into (?:a |the )?(?:wall|tree|truck)\b|\bstop eating until i die\b|\bcutting again\b", _I), "crisis"),
    (re.compile(r"\bfell\b[^.\n]{0,30}?\b(?:can'?t|cannot) get up\b|\b(?:can'?t|cannot) breathe\b|\bsnake bit\b|\bbitten by a snake\b|"
                r"\b(?:car|bus|motorbike) (?:accident|crash)\b[^.\n]{0,40}?\b(?:hurt|injured|bleeding|ambulance)\b|\bneed (?:an )?ambulance\b|"
                r"\bhypothermia\b|\bheavy bleeding\b|\bblood won'?t stop\b|\bblood wont stop\b|\bhigh fever\b[^.\n]{0,20}?\bconfused\b", _I), "health_emergency"),
    (re.compile(r"\b(?:man|guy|someone|somebody) (?:is )?following me\b|\blocked (?:the )?doors? and (?:won'?t|wont) let me out\b|"
                r"\bim being held\b|\bi'?m being held\b|\bkidnapp?ed\b|\bthreatening (?:us|me) with (?:a )?(?:knife|gun|machete)\b|"
                r"\bran away from him\b|\bscared he'?ll find me\b|\bbroke into my (?:house|room|home)\b|\bdriver ignoring me\b", _I), "violence"),
    (re.compile(r"\bpay (?:the )?shipping fee\b|\b(?:in jail|arrested)\b[^.\n]{0,30}?\bneeds? money\b|\bmoney wired\b|"
                r"\bsays? (?:he'?s|she'?s|they'?re|it'?s) (?:the )?police\b[^.\n]{0,40}?\btransfer\b|\bpromising \d+\s*% (?:per|a|every) (?:week|day|month)\b|\btook my atm card\b|\b(?:atm card|card) and (?:my )?pin\b", _I), "scam"),
]

# อดีตที่ผ่านไปแล้ว / ความรู้ / ข่าว — ภาษาอังกฤษ (ลดให้เป็นถามไถ่หรือปกติ)
EN_PAST_OK = re.compile(r"\bused to\b[^.\n]{0,40}?\b(?:clean now|years clean|fine now|better now|proud)\b|"
                        r"\b\d+\s+years? (?:ago|clean)\b[^.\n]{0,40}?\b(?:fine now|okay now|ok now|clean|better)\b|"
                        r"\b(?:he|she|they)'?s? (?:fine|okay|ok) now\b|\ball fine here\b", _I)
EN_KNOWLEDGE = re.compile(r"\breading about\b|\bfor (?:my )?class\b|\bstudying\b|\bnursing exam\b|\bdocumentary\b|^\s*news\b|"
                          r"\btips (?:for|on)\b|\btips\?|\bwith a pillow\b|\bpillow fight\b|\bplayful(?:ly)?\b|"
                          r"\bpaper on\b|\bstatistics\b|\bessay\b|\bresearch(?:ing)?\b|\bwhat should i do if\b|\bbefore (?:my |the |our )?trip\b|"
                          r"\bbefore travel(?:l?ing)?\b|\basking for a friend\b|^\s*(?:do|does|are|is)\s+\w+\s+(?:live|exist|common|found)\b|"
                          r"^\s*(?:is|are|do|does|can|should|how)\b(?![^\n]*\b(?:my|i|i'm|im|me|we|our|us)\b)[^\n]*\?\s*$", _I)
