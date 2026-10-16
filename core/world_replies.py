"""คำตอบแบบไม่มี AI สำหรับภาษาในยุโรป อเมริกา และแอฟริกา + คำตอบเรื่องทั่วไปของทุกภาษาที่ไม่ใช่หกภาษาหลัก

ต่อจาก core/asia_replies.py (เรื่องด่วนของ 16 ภาษาเอเชีย):
- ภาษาใหม่: ฝรั่งเศส เยอรมัน (รวมออสเตรีย) โปรตุเกส (บราซิล/โปรตุเกส) อิตาลี รัสเซีย ยูเครน โปแลนด์ ดัตช์
  สวาฮีลี อัมฮาริก เฮาซา โยรูบา ซูลู แอฟริคานส์ โซมาลี — มีครบ 4 เรื่องด่วน (crisis medical violence help)
- "general": เดิมคนที่พิมพ์เรื่องทั่วไปเป็นภาษาเหล่านี้ (รวมภาษาเอเชีย) ได้คำตอบภาษาอังกฤษ ตอนนี้ได้ภาษาของตัวเอง
ให้เบอร์ในไทยก่อน (คนที่ใช้ภาษาเหล่านี้ในไทยมีทั้งแรงงานและนักท่องเที่ยว) แล้วตามด้วยเบอร์ของประเทศต้นทาง
ข้อความแปลควรให้เจ้าของภาษาตรวจซ้ำ โดยเฉพาะภาษาแอฟริกา
"""
import re

from core.asia_replies import REPLY as ASIA_REPLY, asia_lang


def _set(opener, steps, ask):
    return (opener, steps, ask)


# ── เรื่องด่วน 4 ชนิด + เรื่องทั่วไป ของภาษาใหม่ ─────────────────────────────────
WORLD_REPLY = {
    "fr": {
        "crisis": _set("Je vous entends, et merci de me l'avoir dit.",
                       ["En Thaïlande, appelez le 1323 (santé mentale, 24 h/24). En danger maintenant : 1669.",
                        "Ne restez pas seul·e — dites à une personne de confiance que ça ne va pas.",
                        "En France : 3114 (prévention du suicide) · Europe : 112 · ailleurs : findahelpline.com"],
                       "Êtes-vous en sécurité en ce moment ?"),
        "medical": _set("C'est une urgence — appelez d'abord.",
                        ["Appelez le 1669 maintenant (Thaïlande) · 112 en Europe · 911 au Canada. Donnez l'adresse et les symptômes.",
                         "S'il ne respire pas ou ne répond pas : appuyez fort au centre de la poitrine, 100 à 120 fois par minute.",
                         "Ne donnez ni eau ni nourriture. Gardez l'emballage du médicament pour le médecin."],
                        "Quelqu'un est-il avec la personne en ce moment ?"),
        "violence": _set("Ce n'est pas votre faute. Vous méritez d'être en sécurité.",
                         ["En danger maintenant : 191 (police thaïlandaise) · 112 en Europe · 911 au Canada.",
                          "Allez d'abord dans un lieu sûr : un voisin, un ami, un endroit avec du monde.",
                          "Gardez les photos des blessures et les messages comme preuves. Aide sociale 24 h en Thaïlande : 1300."],
                         "Êtes-vous en sécurité maintenant ?"),
        "help": _set("Je suis là. Dites-moi ce qui se passe.",
                     ["Danger ou blessure maintenant : 1669 (médical) · 191 (police) en Thaïlande · 112 en Europe.",
                      "Écrivez en une phrase ce qui s'est passé.",
                      "Si vous pouvez, rapprochez-vous d'autres personnes."],
                     "Où êtes-vous, et quelqu'un est-il avec vous ?"),
        "general": _set("Prenons les choses une étape à la fois.",
                        ["Écrivez en une phrase ce qui se passe vraiment.",
                         "Listez ce que vous pouvez faire aujourd'hui, même quelque chose de petit.",
                         "Choisissez une seule action pour les prochaines 24 heures."],
                        "Qu'est-ce qui vous pèse le plus en ce moment ?"),
    },
    "de": {
        "crisis": _set("Ich höre Ihnen zu – danke, dass Sie es mir sagen.",
                       ["In Thailand: 1323 anrufen (psychische Gesundheit, 24 Std.). Jetzt in Gefahr: 1669.",
                        "Bleiben Sie nicht allein – sagen Sie einer Person, der Sie vertrauen, dass es Ihnen nicht gut geht.",
                        "Deutschland: TelefonSeelsorge 0800 111 0 111 · Österreich: 142 · Notruf 112 · sonst: findahelpline.com"],
                       "Sind Sie gerade in Sicherheit?"),
        "medical": _set("Das ist ein Notfall – rufen Sie zuerst an.",
                        ["Jetzt 1669 anrufen (Thailand) · 112 in Europa. Adresse und Beschwerden nennen.",
                         "Atmet die Person nicht oder reagiert nicht: fest in der Mitte der Brust drücken, 100–120 Mal pro Minute.",
                         "Kein Wasser und kein Essen geben. Die Medikamentenpackung für den Arzt aufheben."],
                        "Ist gerade jemand bei der Person?"),
        "violence": _set("Das ist nicht Ihre Schuld. Sie haben ein Recht auf Sicherheit.",
                         ["Jetzt in Gefahr: 191 (Polizei Thailand) · 112 in Europa · Österreich Polizei 133.",
                          "Gehen Sie zuerst an einen sicheren Ort: Nachbarn, Freunde, ein Ort mit Menschen.",
                          "Bewahren Sie Fotos von Verletzungen und Nachrichten als Beweis auf. Hilfetelefon DE: 116 016 · AT: 0800 222 555."],
                         "Sind Sie jetzt in Sicherheit?"),
        "help": _set("Ich bin da. Erzählen Sie mir, was passiert.",
                     ["Jetzt Gefahr oder Verletzung: 1669 (medizinisch) · 191 (Polizei) in Thailand · 112 in Europa.",
                      "Schreiben Sie in einem Satz, was passiert ist.",
                      "Wenn möglich, gehen Sie zu anderen Menschen."],
                     "Wo sind Sie, und ist jemand bei Ihnen?"),
        "general": _set("Gehen wir das Schritt für Schritt an.",
                        ["Schreiben Sie in einem Satz, worum es wirklich geht.",
                         "Notieren Sie, was Sie heute tun können – auch etwas Kleines.",
                         "Wählen Sie einen einzigen Schritt für die nächsten 24 Stunden."],
                        "Was belastet Sie gerade am meisten?"),
    },
    "pt": {
        "crisis": _set("Eu te escuto, e obrigada por me contar.",
                       ["Na Tailândia, ligue 1323 (saúde mental, 24 h). Em perigo agora: 1669.",
                        "Não fique sozinho(a) — conte a uma pessoa de confiança que você não está bem.",
                        "Brasil: CVV 188 (24 h) · Portugal: 112 · outros países: findahelpline.com"],
                       "Você está em segurança agora?"),
        "medical": _set("É uma emergência — ligue primeiro.",
                        ["Ligue 1669 agora (Tailândia) · SAMU 192 no Brasil · 112 em Portugal. Diga o endereço e os sintomas.",
                         "Se não respira ou não responde: pressione forte o centro do peito, 100 a 120 vezes por minuto.",
                         "Não dê água nem comida. Guarde a embalagem do remédio para mostrar ao médico."],
                        "Tem alguém com a pessoa agora?"),
        "violence": _set("Não é culpa sua. Você merece estar em segurança.",
                         ["Em perigo agora: 191 (polícia tailandesa) · 190 no Brasil · 112 em Portugal.",
                          "Vá primeiro para um lugar seguro: vizinho, casa de amigos, um lugar com gente.",
                          "Guarde fotos dos ferimentos e mensagens como prova. Brasil: Central da Mulher 180."],
                         "Você está em segurança agora?"),
        "help": _set("Estou aqui. Me conte o que está acontecendo.",
                     ["Perigo ou ferimento agora: 1669 (médico) · 191 (polícia) na Tailândia · 192/190 no Brasil.",
                      "Escreva em uma frase o que aconteceu.",
                      "Se puder, vá para perto de outras pessoas."],
                     "Onde você está, e tem alguém com você?"),
        "general": _set("Vamos por partes, um passo de cada vez.",
                        ["Escreva em uma frase o que está acontecendo de verdade.",
                         "Liste o que você pode fazer hoje, mesmo que seja algo pequeno.",
                         "Escolha uma única ação para as próximas 24 horas."],
                        "O que mais está pesando para você agora?"),
    },
    "it": {
        "crisis": _set("Ti ascolto, e grazie per avermelo detto.",
                       ["In Thailandia chiama il 1323 (salute mentale, 24 ore). In pericolo ora: 1669.",
                        "Non restare da solo/a — di' a una persona di cui ti fidi che non stai bene.",
                        "Italia: 112 · Telefono Amico 02 2327 2327 · altri paesi: findahelpline.com"],
                       "Sei al sicuro in questo momento?"),
        "medical": _set("È un'emergenza — prima chiama.",
                        ["Chiama ora il 1669 (Thailandia) · 112 in Europa. Di' l'indirizzo e i sintomi.",
                         "Se non respira o non risponde: premi forte al centro del petto, 100–120 volte al minuto.",
                         "Non dare acqua né cibo. Conserva la confezione del farmaco per il medico."],
                        "C'è qualcuno con la persona adesso?"),
        "violence": _set("Non è colpa tua. Meriti di essere al sicuro.",
                         ["In pericolo ora: 191 (polizia thailandese) · 112 in Europa.",
                          "Vai prima in un posto sicuro: un vicino, un amico, un luogo con gente.",
                          "Conserva foto delle ferite e messaggi come prova. Italia: numero antiviolenza 1522."],
                         "Sei al sicuro adesso?"),
        "help": _set("Sono qui. Dimmi cosa sta succedendo.",
                     ["Pericolo o ferite adesso: 1669 (medico) · 191 (polizia) in Thailandia · 112 in Europa.",
                      "Scrivi in una frase cosa è successo.",
                      "Se puoi, avvicinati ad altre persone."],
                     "Dove sei, e c'è qualcuno con te?"),
        "general": _set("Affrontiamolo un passo alla volta.",
                        ["Scrivi in una frase cosa sta succedendo davvero.",
                         "Elenca cosa puoi fare oggi, anche una cosa piccola.",
                         "Scegli una sola azione per le prossime 24 ore."],
                        "Cosa ti pesa di più in questo momento?"),
    },
    "ru": {
        "crisis": _set("Я слышу вас, спасибо, что рассказали.",
                       ["В Таиланде звоните 1323 (психологическая помощь, круглосуточно). Если опасность сейчас — 1669.",
                        "Не оставайтесь одни — скажите человеку, которому доверяете, что вам плохо.",
                        "Россия: 112 · телефон доверия 8-800-2000-122 · другие страны: findahelpline.com"],
                       "Вы сейчас в безопасности?"),
        "medical": _set("Это экстренная ситуация — сначала позвоните.",
                        ["Звоните 1669 сейчас (Таиланд) · 112 в России и Европе. Назовите адрес и симптомы.",
                         "Если не дышит или не реагирует: сильно надавливайте на центр груди, 100–120 раз в минуту.",
                         "Не давайте воду и еду. Сохраните упаковку лекарства для врача."],
                        "Кто-то сейчас рядом с человеком?"),
        "violence": _set("Это не ваша вина. Вы имеете право на безопасность.",
                         ["Если опасность сейчас: 191 (полиция Таиланда) · 112 в России и Европе.",
                          "Сначала уйдите в безопасное место: к соседям, друзьям, туда, где есть люди.",
                          "Сохраните фото травм и сообщения как доказательства. Помощь в Таиланде 24 ч: 1300."],
                         "Вы сейчас в безопасности?"),
        "help": _set("Я здесь. Расскажите, что происходит.",
                     ["Опасность или травма сейчас: 1669 (скорая) · 191 (полиция) в Таиланде · 112.",
                      "Напишите одним предложением, что случилось.",
                      "Если можете, идите туда, где есть другие люди."],
                     "Где вы сейчас, и есть ли кто-то рядом?"),
        "general": _set("Давайте разберёмся шаг за шагом.",
                        ["Напишите одним предложением, что на самом деле происходит.",
                         "Перечислите, что можно сделать сегодня — даже что-то маленькое.",
                         "Выберите одно действие на ближайшие 24 часа."],
                        "Что сейчас тяготит вас больше всего?"),
    },
    "uk": {
        "crisis": _set("Я чую вас, дякую, що розповіли.",
                       ["У Таїланді телефонуйте 1323 (психологічна допомога, цілодобово). Якщо небезпека зараз — 1669.",
                        "Не залишайтеся на самоті — скажіть людині, якій довіряєте, що вам погано.",
                        "Україна: 112 · Lifeline Ukraine 7333 · інші країни: findahelpline.com"],
                       "Ви зараз у безпеці?"),
        "medical": _set("Це невідкладна ситуація — спершу зателефонуйте.",
                        ["Телефонуйте 1669 зараз (Таїланд) · 103 або 112 в Україні. Назвіть адресу й симптоми.",
                         "Якщо не дихає або не реагує: сильно натискайте на центр грудей, 100–120 разів на хвилину.",
                         "Не давайте води чи їжі. Збережіть упаковку ліків для лікаря."],
                        "Хтось зараз поруч із людиною?"),
        "violence": _set("Це не ваша провина. Ви маєте право на безпеку.",
                         ["Якщо небезпека зараз: 191 (поліція Таїланду) · 102 або 112 в Україні.",
                          "Спершу йдіть у безпечне місце: до сусідів, друзів, туди, де є люди.",
                          "Збережіть фото травм і повідомлення як докази. Допомога в Таїланді 24 год: 1300."],
                         "Ви зараз у безпеці?"),
        "help": _set("Я тут. Розкажіть, що відбувається.",
                     ["Небезпека чи травма зараз: 1669 (швидка) · 191 (поліція) в Таїланді · 112.",
                      "Напишіть одним реченням, що сталося.",
                      "Якщо можете, підіть туди, де є інші люди."],
                     "Де ви зараз, і чи є хтось поруч?"),
        "general": _set("Розберімося крок за кроком.",
                        ["Напишіть одним реченням, що насправді відбувається.",
                         "Перелічіть, що можна зробити сьогодні — навіть щось маленьке.",
                         "Оберіть одну дію на найближчі 24 години."],
                        "Що вас зараз найбільше гнітить?"),
    },
    "pl": {
        "crisis": _set("Słyszę cię i dziękuję, że mi to mówisz.",
                       ["W Tajlandii zadzwoń pod 1323 (zdrowie psychiczne, całą dobę). W niebezpieczeństwie teraz: 1669.",
                        "Nie zostawaj sam/sama — powiedz zaufanej osobie, że nie jest dobrze.",
                        "Polska: 112 · telefon zaufania 116 123 · inne kraje: findahelpline.com"],
                       "Czy jesteś teraz bezpieczny/bezpieczna?"),
        "medical": _set("To nagły wypadek — najpierw zadzwoń.",
                        ["Zadzwoń teraz pod 1669 (Tajlandia) · 112 w Europie. Podaj adres i objawy.",
                         "Jeśli nie oddycha lub nie reaguje: uciskaj mocno środek klatki piersiowej, 100–120 razy na minutę.",
                         "Nie podawaj wody ani jedzenia. Zachowaj opakowanie leku dla lekarza."],
                        "Czy ktoś jest teraz przy tej osobie?"),
        "violence": _set("To nie twoja wina. Masz prawo być bezpieczny/bezpieczna.",
                         ["W niebezpieczeństwie teraz: 191 (policja w Tajlandii) · 112 w Europie.",
                          "Najpierw idź w bezpieczne miejsce: do sąsiada, przyjaciół, tam, gdzie są ludzie.",
                          "Zachowaj zdjęcia obrażeń i wiadomości jako dowody. Polska: Niebieska Linia 800 120 002."],
                         "Czy jesteś teraz bezpieczny/bezpieczna?"),
        "help": _set("Jestem tu. Powiedz, co się dzieje.",
                     ["Niebezpieczeństwo lub uraz teraz: 1669 (medyczny) · 191 (policja) w Tajlandii · 112.",
                      "Napisz w jednym zdaniu, co się stało.",
                      "Jeśli możesz, idź tam, gdzie są inni ludzie."],
                     "Gdzie jesteś i czy ktoś jest z tobą?"),
        "general": _set("Zróbmy to krok po kroku.",
                        ["Napisz w jednym zdaniu, o co naprawdę chodzi.",
                         "Wypisz, co możesz zrobić dzisiaj — nawet coś małego.",
                         "Wybierz jeden krok na najbliższe 24 godziny."],
                        "Co najbardziej cię teraz przytłacza?"),
    },
    "nl": {
        "crisis": _set("Ik hoor je, en dank je dat je het vertelt.",
                       ["In Thailand: bel 1323 (geestelijke gezondheid, 24 uur). Nu in gevaar: 1669.",
                        "Blijf niet alleen — vertel iemand die je vertrouwt dat het niet goed gaat.",
                        "Nederland: 113 (0800-0113) · België: 1813 · noodnummer 112 · elders: findahelpline.com"],
                       "Ben je nu veilig?"),
        "medical": _set("Dit is een noodgeval — bel eerst.",
                        ["Bel nu 1669 (Thailand) · 112 in Europa. Geef het adres en de klachten door.",
                         "Ademt iemand niet of reageert niet: druk hard op het midden van de borst, 100–120 keer per minuut.",
                         "Geef geen water of eten. Bewaar de verpakking van het medicijn voor de arts."],
                        "Is er nu iemand bij de persoon?"),
        "violence": _set("Het is niet jouw schuld. Je verdient het om veilig te zijn.",
                         ["Nu in gevaar: 191 (politie Thailand) · 112 in Europa.",
                          "Ga eerst naar een veilige plek: buren, vrienden, een plek met mensen.",
                          "Bewaar foto's van verwondingen en berichten als bewijs. Nederland: Veilig Thuis 0800-2000."],
                         "Ben je nu veilig?"),
        "help": _set("Ik ben er. Vertel wat er gebeurt.",
                     ["Nu gevaar of letsel: 1669 (medisch) · 191 (politie) in Thailand · 112.",
                      "Schrijf in één zin wat er gebeurd is.",
                      "Ga als het kan in de buurt van andere mensen."],
                     "Waar ben je, en is er iemand bij je?"),
        "general": _set("Laten we het stap voor stap bekijken.",
                        ["Schrijf in één zin waar het echt om gaat.",
                         "Schrijf op wat je vandaag kunt doen, ook iets kleins.",
                         "Kies één stap voor de komende 24 uur."],
                        "Wat weegt nu het zwaarst voor je?"),
    },
    "sw": {
        "crisis": _set("Ninakusikia, na asante kwa kuniambia.",
                       ["Ukiwa Thailand piga 1323 (afya ya akili, saa 24). Ukiwa hatarini sasa: 1669.",
                        "Usikae peke yako — mwambie mtu unayemwamini kwamba hauko sawa.",
                        "Kenya: 999 au 112 · Tanzania: 112 · nchi nyingine: findahelpline.com"],
                       "Uko salama sasa hivi?"),
        "medical": _set("Hii ni dharura — piga simu kwanza.",
                        ["Piga 1669 sasa (Thailand) · Kenya 999 au 112. Taja anwani na dalili.",
                         "Kama hapumui au haitikii: bonyeza kwa nguvu katikati ya kifua mara 100–120 kwa dakika.",
                         "Usimpe maji wala chakula. Hifadhi pakiti ya dawa umwonyeshe daktari."],
                        "Kuna mtu yeyote na mgonjwa sasa?"),
        "violence": _set("Si kosa lako. Unastahili kuwa salama.",
                         ["Ukiwa hatarini sasa: 191 (polisi wa Thailand) · Kenya 999 au 112.",
                          "Kwanza nenda mahali salama: kwa jirani, kwa rafiki, au mahali penye watu.",
                          "Hifadhi picha za majeraha na jumbe kama ushahidi. Kenya: 1195 (msaada wa ukatili wa kijinsia)."],
                         "Uko salama sasa?"),
        "help": _set("Niko hapa. Niambie kinachoendelea.",
                     ["Hatari au jeraha sasa: 1669 (matibabu) · 191 (polisi) Thailand · Kenya 999.",
                      "Andika kwa sentensi moja kilichotokea.",
                      "Ukiweza, nenda karibu na watu wengine."],
                     "Uko wapi sasa, na kuna mtu pamoja nawe?"),
        "general": _set("Tuchukue hatua moja baada ya nyingine.",
                        ["Andika kwa sentensi moja kinachoendelea kweli.",
                         "Orodhesha unachoweza kufanya leo, hata kitu kidogo.",
                         "Chagua hatua moja tu kwa saa 24 zijazo."],
                        "Ni nini kinakulemea zaidi sasa hivi?"),
    },
    "am": {
        "crisis": _set("እሰማሃለሁ፣ ስለነገርከኝ አመሰግናለሁ።",
                       ["በታይላንድ 1323 ይደውሉ (የአእምሮ ጤና፣ 24 ሰዓት)። አሁን አደጋ ላይ ከሆኑ 1669 ይደውሉ።",
                        "ብቻዎን አይሁኑ — ለሚያምኑት ሰው ደህና እንዳልሆኑ ይንገሩ።",
                        "በሌላ አገር ከሆኑ የአካባቢውን የአደጋ ጊዜ ቁጥር ይደውሉ ወይም findahelpline.com ይጠቀሙ።"],
                       "አሁን ደህንነትዎ የተጠበቀ ነው?"),
        "medical": _set("ይህ አስቸኳይ ሁኔታ ነው — መጀመሪያ ይደውሉ።",
                        ["አሁኑኑ 1669 ይደውሉ (ታይላንድ) ወይም የአካባቢውን የአምቡላንስ ቁጥር። አድራሻውን እና ምልክቶቹን ይናገሩ።",
                         "የማይተነፍስ ወይም የማይመልስ ከሆነ፦ የደረቱን መሃል በደቂቃ 100–120 ጊዜ አጥብቀው ይጫኑ።",
                         "ውሃ ወይም ምግብ አይስጡ። የወሰደውን መድኃኒት እሽግ ለሐኪሙ ያስቀምጡ።"],
                        "አሁን ከታማሚው ጋር ሰው አለ?"),
        "violence": _set("ይህ የእርስዎ ጥፋት አይደለም። ደህንነትዎ ሊጠበቅ ይገባል።",
                         ["አሁን አደጋ ላይ ከሆኑ 191 (የታይላንድ ፖሊስ) ይደውሉ።",
                          "መጀመሪያ ወደ ደህንነቱ የተጠበቀ ቦታ ይሂዱ፦ ጎረቤት፣ የጓደኛ ቤት ወይም ሰው ያለበት ቦታ።",
                          "የጉዳቱን ፎቶዎች እና መልእክቶች እንደ ማስረጃ ያስቀምጡ። በታይላንድ የ24 ሰዓት እርዳታ፦ 1300።"],
                         "አሁን ደህና ነዎት?"),
        "help": _set("እዚህ ነኝ። ምን እየሆነ እንዳለ ይንገሩኝ።",
                     ["አሁን አደጋ ወይም ጉዳት ካለ፦ 1669 (ሕክምና) · 191 (ፖሊስ) በታይላንድ።",
                      "የሆነውን በአንድ ዓረፍተ ነገር ይጻፉ።",
                      "ከቻሉ ወደ ሌሎች ሰዎች አቅራቢያ ይሂዱ።"],
                     "አሁን የት ነዎት፣ ከእርስዎ ጋር ሰው አለ?"),
        "general": _set("አንድ በአንድ እንየው።",
                        ["እየሆነ ያለውን በአንድ ዓረፍተ ነገር ይጻፉ።",
                         "ዛሬ ማድረግ የሚችሉትን ይዘርዝሩ፣ ትንሽ ነገር ቢሆንም።",
                         "ለሚቀጥሉት 24 ሰዓታት አንድ እርምጃ ብቻ ይምረጡ።"],
                        "አሁን በጣም የሚያስጨንቅዎት ምንድን ነው?"),
    },
    "ha": {
        "crisis": _set("Ina jin ka, kuma na gode da ka gaya mini.",
                       ["A Thailand ka kira 1323 (lafiyar kwakwalwa, awa 24). Idan kana cikin haɗari yanzu: 1669.",
                        "Kada ka zauna kai kaɗai — gaya wa wanda ka amince da shi cewa ba ka da lafiya.",
                        "Najeriya: 112 · sauran ƙasashe: findahelpline.com"],
                       "Kana cikin aminci yanzu?"),
        "medical": _set("Wannan gaggawa ce — ka kira waya da farko.",
                        ["Ka kira 1669 yanzu (Thailand) · Najeriya 112. Faɗi adireshi da alamun cutar.",
                         "Idan baya numfashi ko baya amsawa: danna tsakiyar ƙirji da ƙarfi sau 100–120 a minti ɗaya.",
                         "Kada ka ba shi ruwa ko abinci. Ajiye kwalin maganin don likita ya gani."],
                        "Akwai wani tare da mara lafiyar yanzu?"),
        "violence": _set("Ba laifinka ba ne. Ka cancanci zama cikin aminci.",
                         ["Idan kana cikin haɗari yanzu: 191 ('yan sandan Thailand) · Najeriya 112.",
                          "Da farko ka je wuri mai aminci: maƙwabci, gidan aboki, ko wurin da mutane suke.",
                          "Ajiye hotunan raunuka da saƙonni a matsayin shaida. Taimako na awa 24 a Thailand: 1300."],
                         "Kana cikin aminci yanzu?"),
        "help": _set("Ina nan. Gaya mini abin da ke faruwa.",
                     ["Haɗari ko rauni yanzu: 1669 (lafiya) · 191 ('yan sanda) a Thailand · Najeriya 112.",
                      "Rubuta abin da ya faru a jumla ɗaya.",
                      "Idan za ka iya, je kusa da wasu mutane."],
                     "Ina kake yanzu, kuma akwai wani tare da kai?"),
        "general": _set("Mu bi shi mataki-mataki.",
                        ["Rubuta abin da ke faruwa a jumla ɗaya.",
                         "Lissafa abin da za ka iya yi yau, ko da ƙarami ne.",
                         "Zaɓi mataki ɗaya kawai na awa 24 masu zuwa."],
                        "Me ya fi damunka yanzu?"),
    },
    "yo": {
        "crisis": _set("Mo gbọ́ ọ, ẹ ṣé tí o sọ fún mi.",
                       ["Ní Thailand, pe 1323 (ìlera ọpọlọ, wákàtí 24). Tí o bá wà nínú ewu báyìí: 1669.",
                        "Má ṣe dá wà — sọ fún ẹnì kan tí o fọkàn tán pé ara rẹ kò yá.",
                        "Nàìjíríà: 112 · àwọn orílẹ̀-èdè mìíràn: findahelpline.com"],
                       "Ṣé o wà láìléwu báyìí?"),
        "medical": _set("Pàjáwìrì ni èyí — kọ́kọ́ pe fóònù.",
                        ["Pe 1669 báyìí (Thailand) · Nàìjíríà 112. Sọ àdírẹ́sì àti àmì àìsàn.",
                         "Tí kò bá ń mí tàbí kò dáhùn: tẹ àárín àyà ní agbára, ìgbà 100–120 ní ìṣẹ́jú kan.",
                         "Má fún un ní omi tàbí oúnjẹ. Pa àpò oògùn mọ́ fún dókítà."],
                        "Ṣé ẹnì kan wà pẹ̀lú aláìsàn náà báyìí?"),
        "violence": _set("Kì í ṣe ẹ̀bi rẹ. O yẹ láti wà láìléwu.",
                         ["Tí o bá wà nínú ewu báyìí: 191 (ọlọ́pàá Thailand) · Nàìjíríà 112.",
                          "Kọ́kọ́ lọ sí ibi tí ó ní ààbò: aládùúgbò, ilé ọ̀rẹ́, tàbí ibi tí èèyàn wà.",
                          "Pa fọ́tò ọgbẹ́ àti àwọn ìfiránṣẹ́ mọ́ gẹ́gẹ́ bí ẹ̀rí. Ìrànlọ́wọ́ wákàtí 24 ní Thailand: 1300."],
                         "Ṣé o wà láìléwu báyìí?"),
        "help": _set("Mo wà níbí. Sọ ohun tó ń ṣẹlẹ̀ fún mi.",
                     ["Ewu tàbí ọgbẹ́ báyìí: 1669 (ìlera) · 191 (ọlọ́pàá) ní Thailand · Nàìjíríà 112.",
                      "Kọ ohun tó ṣẹlẹ̀ ní gbólóhùn kan.",
                      "Tí o bá lè ṣe é, lọ sí ọ̀dọ̀ àwọn èèyàn mìíràn."],
                     "Níbo ni o wà báyìí, ṣé ẹnì kan wà pẹ̀lú rẹ?"),
        "general": _set("Jẹ́ ká ṣe é ní ìgbésẹ̀ kọ̀ọ̀kan.",
                        ["Kọ ohun tó ń ṣẹlẹ̀ gan-an ní gbólóhùn kan.",
                         "Kọ ohun tí o lè ṣe lónìí sílẹ̀, kódà tó bá kéré.",
                         "Yan ìgbésẹ̀ kan ṣoṣo fún wákàtí 24 tó ń bọ̀."],
                        "Kí ló ń dà ọ́ láàmú jù lọ báyìí?"),
    },
    "zu": {
        "crisis": _set("Ngiyakuzwa, futhi ngiyabonga ngokungitshela.",
                       ["E-Thailand shayela u-1323 (impilo yengqondo, amahora angu-24). Uma usengozini manje: 1669.",
                        "Ungahlali wedwa — tshela umuntu omethembayo ukuthi awukho kahle.",
                        "eNingizimu Afrika: SADAG 0800 567 567 · amaphoyisa 10111 · amanye amazwe: findahelpline.com"],
                       "Ingabe uphephile manje?"),
        "medical": _set("Lesi yisimo esiphuthumayo — shayela kuqala.",
                        ["Shayela u-1669 manje (Thailand) · eNingizimu Afrika 10177 noma 112. Sho ikheli nezimpawu.",
                         "Uma engaphefumuli noma engaphenduli: cindezela phakathi nesifuba ngamandla, izikhathi ezingu-100–120 ngomzuzu.",
                         "Ungamniki amanzi noma ukudla. Gcina iphakethe lomuthi ukuze udokotela alibone."],
                        "Ingabe kukhona umuntu nesiguli manje?"),
        "violence": _set("Akulona iphutha lakho. Ufanelwe ukuphepha.",
                         ["Uma usengozini manje: 191 (amaphoyisa aseThailand) · eNingizimu Afrika 10111.",
                          "Qala uye endaweni ephephile: kumakhelwane, kumngane, noma lapho kunabantu khona.",
                          "Gcina izithombe zokulimala nemilayezo njengobufakazi. eNingizimu Afrika: GBV Command Centre 0800 428 428."],
                         "Ingabe uphephile manje?"),
        "help": _set("Ngilapha. Ngitshele ukuthi kwenzekani.",
                     ["Ingozi noma ukulimala manje: 1669 (ezempilo) · 191 (amaphoyisa) e-Thailand · eNingizimu Afrika 10111.",
                      "Bhala ngomusho owodwa ukuthi kwenzekeni.",
                      "Uma ukwazi, sondela kwabanye abantu."],
                     "Ukuphi manje, futhi ingabe ukhona umuntu nawe?"),
        "general": _set("Masithathe isinyathelo esisodwa ngesikhathi.",
                        ["Bhala ngomusho owodwa ukuthi kwenzekani ngempela.",
                         "Bhala lokho ongakwenza namuhla, ngisho kuncane.",
                         "Khetha isinyathelo esisodwa sezinsuku ezingu-24 ezizayo."],
                        "Yini ekukhathaza kakhulu manje?"),
    },
    "af": {
        "crisis": _set("Ek hoor jou, en dankie dat jy my vertel.",
                       ["In Thailand, bel 1323 (geestesgesondheid, 24 uur). In gevaar nou: 1669.",
                        "Moenie alleen bly nie — sê vir iemand wat jy vertrou dat dit nie goed gaan nie.",
                        "Suid-Afrika: SADAG 0800 567 567 · polisie 10111 · ander lande: findahelpline.com"],
                       "Is jy nou veilig?"),
        "medical": _set("Dit is 'n noodgeval — bel eers.",
                        ["Bel nou 1669 (Thailand) · Suid-Afrika 10177 of 112. Gee die adres en die simptome.",
                         "As die persoon nie asemhaal of reageer nie: druk hard in die middel van die bors, 100–120 keer per minuut.",
                         "Moenie water of kos gee nie. Hou die medisynepakkie vir die dokter."],
                        "Is daar nou iemand by die persoon?"),
        "violence": _set("Dit is nie jou skuld nie. Jy verdien om veilig te wees.",
                         ["In gevaar nou: 191 (Thaise polisie) · Suid-Afrika 10111.",
                          "Gaan eers na 'n veilige plek: 'n buurman, vriende, of 'n plek met mense.",
                          "Hou foto's van beserings en boodskappe as bewys. Suid-Afrika: GBV Command Centre 0800 428 428."],
                         "Is jy nou veilig?"),
        "help": _set("Ek is hier. Vertel my wat aangaan.",
                     ["Gevaar of besering nou: 1669 (medies) · 191 (polisie) in Thailand · Suid-Afrika 10111.",
                      "Skryf in een sin wat gebeur het.",
                      "As jy kan, gaan na ander mense toe."],
                     "Waar is jy nou, en is iemand by jou?"),
        "general": _set("Kom ons vat dit stap vir stap.",
                        ["Skryf in een sin waaroor dit regtig gaan.",
                         "Lys wat jy vandag kan doen, al is dit iets kleins.",
                         "Kies een stap vir die volgende 24 uur."],
                        "Wat druk die swaarste op jou nou?"),
    },
    "so": {
        "crisis": _set("Waan ku maqlayaa, waadna ku mahadsan tahay inaad ii sheegtay.",
                       ["Haddii aad joogto Thailand, wac 1323 (caafimaadka maskaxda, 24 saac). Haddii aad halis ku jirto hadda: 1669.",
                        "Ha keligaa joogin — u sheeg qof aad aaminsan tahay inaadan fiicnayn.",
                        "Waddamada kale: wac lambarka degdegga ee deegaanka ama eeg findahelpline.com"],
                       "Ma ammaan baad tahay hadda?"),
        "medical": _set("Tani waa xaalad degdeg ah — marka hore wac.",
                        ["Wac 1669 hadda (Thailand) ama lambarka ambalaaska ee deegaanka. Sheeg cinwaanka iyo calaamadaha.",
                         "Haddii uusan neefsanayn ama uusan jawaabin: si xoog leh u riix bartamaha laabta, 100–120 jeer daqiiqaddii.",
                         "Ha siin biyo ama cunto. Kaydi baakadda daawada si dhakhtarku u arko."],
                        "Ma jiraa qof la jooga bukaanka hadda?"),
        "violence": _set("Qaladkaagu ma aha. Waxaad mudan tahay inaad ammaan ahaato.",
                         ["Haddii aad halis ku jirto hadda: 191 (booliska Thailand).",
                          "Marka hore aad meel ammaan ah: deriskaaga, guriga saaxiib, ama meel dad joogaan.",
                          "Kaydi sawirrada dhaawaca iyo fariimaha si ay caddayn u noqdaan. Caawimaad 24 saac ah oo Thailand ah: 1300."],
                         "Ma ammaan baad tahay hadda?"),
        "help": _set("Halkan ayaan joogaa. Ii sheeg waxa dhacaya.",
                     ["Halis ama dhaawac hadda: 1669 (caafimaad) · 191 (booliis) Thailand.",
                      "Hal weedh ku qor waxa dhacay.",
                      "Haddii aad awooddo, u dhowow dad kale."],
                     "Halkee joogtaa hadda, qof ma kula jiraa?"),
        "general": _set("Aan tallaabo tallaabo u qaadno.",
                        ["Hal weedh ku qor waxa dhab ahaan dhacaya.",
                         "Qor waxa aad maanta samayn karto, xitaa wax yar.",
                         "Dooro hal tallaabo oo keliya 24-ka saac ee soo socda."],
                        "Maxaa sida ugu badan kuu culeysiinaya hadda?"),
    },
}

# ── เรื่องทั่วไปของ 16 ภาษาเอเชีย (เรื่องด่วนอยู่ใน core/asia_replies.py) ──────────────
GENERAL_ASIA = {
    "my": ("တစ်ဆင့်ချင်း စဉ်းစားကြည့်ရအောင်။", ["ဖြစ်နေတာကို စာကြောင်းတစ်ကြောင်းတည်း ရေးပါ။", "ဒီနေ့ လုပ်နိုင်တာတွေကို ချရေးပါ — သေးသေးလေး ဖြစ်ဖြစ်။", "နောက် ၂၄ နာရီအတွက် လုပ်မယ့် အဆင့်တစ်ခုတည်း ရွေးပါ။"], "အခု အလေးဆုံးဖြစ်နေတာ ဘာလဲ။"),
    "km": ("តោះគិតម្តងមួយជំហាន។", ["សរសេរពីអ្វីដែលកំពុងកើតឡើង ក្នុងមួយប្រយោគ។", "សរសេររឿងដែលអ្នកអាចធ្វើបានថ្ងៃនេះ ទោះតូចក៏ដោយ។", "ជ្រើសរើសជំហានតែមួយ សម្រាប់ ២៤ ម៉ោងខាងមុខ។"], "ឥឡូវនេះ អ្វីដែលធ្វើឲ្យអ្នកពិបាកចិត្តជាងគេ?"),
    "lo": ("ມາຄ່ອຍໆຄິດເທື່ອລະຂັ້ນ.", ["ຂຽນສິ່ງທີ່ກຳລັງເກີດຂຶ້ນໃນປະໂຫຍກດຽວ.", "ຂຽນສິ່ງທີ່ເຮັດໄດ້ມື້ນີ້ ເຖິງຈະເປັນເລື່ອງນ້ອຍກໍຕາມ.", "ເລືອກຂັ້ນຕອນດຽວສຳລັບ 24 ຊົ່ວໂມງຂ້າງໜ້າ."], "ຕອນນີ້ເລື່ອງໃດທີ່ໜັກໃຈທີ່ສຸດ?"),
    "vi": ("Mình cùng sắp xếp từng bước nhé.", ["Viết một câu về chuyện đang thật sự xảy ra.", "Liệt kê những gì bạn làm được hôm nay, dù là việc nhỏ.", "Chọn một bước duy nhất cho 24 giờ tới."], "Điều gì đang đè nặng bạn nhất lúc này?"),
    "id": ("Kita urai pelan-pelan, satu langkah dulu.", ["Tulis dalam satu kalimat apa yang sebenarnya terjadi.", "Catat apa yang bisa kamu lakukan hari ini, walau kecil.", "Pilih satu langkah saja untuk 24 jam ke depan."], "Apa yang paling membebanimu sekarang?"),
    "ms": ("Mari kita susun satu langkah demi satu langkah.", ["Tulis dalam satu ayat apa yang sebenarnya berlaku.", "Senaraikan apa yang awak boleh buat hari ini, walaupun kecil.", "Pilih satu langkah sahaja untuk 24 jam akan datang."], "Apa yang paling membebankan awak sekarang?"),
    "tl": ("Isa-isahin natin, hakbang-hakbang.", ["Isulat sa isang pangungusap kung ano talaga ang nangyayari.", "Ilista ang kaya mong gawin ngayong araw, kahit maliit.", "Pumili ng isang hakbang lang para sa susunod na 24 oras."], "Ano ang pinakamabigat sa iyo ngayon?"),
    "hi": ("चलिए एक-एक कदम करके देखते हैं।", ["एक वाक्य में लिखें कि असल में क्या हो रहा है।", "आज आप क्या कर सकते हैं, उसकी सूची बनाएँ — चाहे छोटा ही क्यों न हो।", "अगले 24 घंटों के लिए सिर्फ़ एक कदम चुनें।"], "अभी आपको सबसे ज़्यादा क्या परेशान कर रहा है?"),
    "ne": ("एक-एक कदम गरेर हेरौं।", ["वास्तवमा के भइरहेको छ, एक वाक्यमा लेख्नुहोस्।", "आज गर्न सकिने कुराहरू लेख्नुहोस्, सानै भए पनि।", "अर्को २४ घण्टाका लागि एउटा मात्र कदम छान्नुहोस्।"], "अहिले तपाईंलाई सबैभन्दा बढी के ले गाह्रो बनाइरहेको छ?"),
    "bn": ("চলুন এক এক ধাপ করে দেখি।", ["আসলে কী হচ্ছে তা এক বাক্যে লিখুন।", "আজ কী করতে পারেন তার তালিকা করুন — ছোট হলেও।", "আগামী ২৪ ঘণ্টার জন্য শুধু একটি পদক্ষেপ বেছে নিন।"], "এখন আপনাকে সবচেয়ে বেশি কী ভারী লাগছে?"),
    "ur": ("آئیے ایک ایک قدم کر کے دیکھتے ہیں۔", ["ایک جملے میں لکھیں کہ اصل میں کیا ہو رہا ہے۔", "آج آپ کیا کر سکتے ہیں اس کی فہرست بنائیں، چاہے چھوٹا ہی ہو۔", "اگلے 24 گھنٹوں کے لیے صرف ایک قدم چنیں۔"], "اس وقت آپ کو سب سے زیادہ کیا پریشان کر رہا ہے؟"),
    "ta": ("ஒவ்வொரு படியாகப் பார்ப்போம்.", ["உண்மையில் என்ன நடக்கிறது என்பதை ஒரு வாக்கியத்தில் எழுதுங்கள்.", "இன்று செய்யக்கூடியவற்றை பட்டியலிடுங்கள், சிறியதாக இருந்தாலும்.", "அடுத்த 24 மணி நேரத்திற்கு ஒரே ஒரு படியைத் தேர்ந்தெடுங்கள்."], "இப்போது உங்களை அதிகம் அழுத்துவது எது?"),
    "si": ("අපි පියවරෙන් පියවර බලමු.", ["ඇත්තටම මොකද වෙන්නේ කියලා එක වාක්‍යයකින් ලියන්න.", "අද කරන්න පුළුවන් දේවල් ලියන්න, පොඩි දෙයක් වුණත්.", "ඉදිරි පැය 24 සඳහා එක පියවරක් විතරක් තෝරන්න."], "දැන් ඔබට වැඩියෙන්ම බරක් වෙලා තියෙන්නේ මොකක්ද?"),
    "fa": ("بیایید قدم به قدم جلو برویم.", ["در یک جمله بنویسید واقعاً چه اتفاقی افتاده.", "کارهایی را که امروز می‌توانید انجام دهید بنویسید، حتی کوچک.", "فقط یک قدم برای ۲۴ ساعت آینده انتخاب کنید."], "الان چه چیزی بیشتر از همه آزارتان می‌دهد؟"),
    "ar": ("لنرتّب الأمر خطوة بخطوة.", ["اكتب في جملة واحدة ما الذي يحدث فعلًا.", "اكتب ما يمكنك فعله اليوم، حتى لو كان صغيرًا.", "اختر خطوة واحدة فقط للساعات الـ24 القادمة."], "ما الذي يثقل عليك أكثر الآن؟"),
    "tr": ("Adım adım bakalım.", ["Gerçekte ne olduğunu tek cümleyle yaz.", "Bugün yapabileceklerini yaz, küçük bile olsa.", "Önümüzdeki 24 saat için tek bir adım seç."], "Şu an seni en çok ne zorluyor?"),
}

# ── เดาภาษาของภาษาใหม่ ───────────────────────────────────────────────────
_ETHIOPIC = re.compile(r"[ሀ-፿]")
_UKR = re.compile(r"[іїєґІЇЄҐ]")
_CYR = re.compile(r"[Ѐ-ӿ]")
# คำที่บอกภาษาได้ชัด — ต้องเจออย่างน้อย 2 คำ (หรือ 1 คำที่เฉพาะมาก) กันข้อความอังกฤษถูกเดาผิด
_WORDS = {
    "fr": r"frappe|mari|mère|mourir|respire|je|j'ai|ne|pas|mon|ma|mes|est|suis|veux|avec|pour|mais|très|aujourd'hui|ça|c'est|qu'|ai|au|secours|aide",
    "de": r"sterben|atmet|schlägt|mann|mutter|ich|nicht|mein|meine|ist|bin|und|mit|habe|kann|will|heute|sehr|aber|was|hilfe|mich|mir",
    "pt": r"quero|morrer|respira|marido|bate|mãe|eu|não|meu|minha|estou|quero|com|muito|hoje|mas|você|tenho|socorro|está|sou",
    "it": r"morire|respira|marito|picchia|madre|io|non|mio|mia|sono|voglio|con|molto|oggi|ma|ho|aiuto|perché|sto|che",
    "pl": r"umrzeć|oddycha|mąż|bije|ratunku|mama|jestem|nie|mój|moja|mam|chcę|bardzo|dzisiaj|ale|się|pomocy|mnie|jak",
    "nl": r"dood|ademt|slaat|mij|moeder|ik|niet|mijn|ben|wil|met|heel|vandaag|maar|het|een|help|hulp|heb|kan",
    "sw": r"hapumui|ananipiga|kufa|mimi|nina|sina|sitaki|kufa|nataka|leo|sana|lakini|na|wangu|yangu|msaada|nisaidie|mume|mama|anapumua",
    "ha": r"mutu|numfashi|duka|taimaka|mijina|ina|ba|na|kuma|yau|sosai|amma|taimako|mijina|mahaifiyata|mutuwa|so",
    "yo": r"mo|kò|mi|ni|lónìí|ṣùgbọ́n|ràn|lọ́wọ́|ọkọ|ìyá|kú|fẹ́",
    "zu": r"akaphefumuli|uyangishaya|ngisize|ukufa|ngi|angi|ngiya|umama|umyeni|namuhla|kakhulu|kodwa|ngisize|siza|ukufa|ngifuna",
    "af": r"doodgaan|asem|slaan|ek|nie|my|is|wil|met|baie|vandag|maar|help|asseblief|het|kan",
    "so": r"garaacaa|neefsanayo|dhiman|caawi|waxaan|ma|aan|hooyo|ninkayga|maanta|aad|laakiin|i\s+caawi|caawimaad|dhiman|rabaa",
}
_WORD_RX = {k: re.compile(r"(?<![\w'])(?:" + v + r")(?![\w'])", re.I) for k, v in _WORDS.items()}
_EN_WORDS = re.compile(r"(?<![\w'])(?:i|the|and|my|is|am|not|to|you|it|what|how|with|for|but|today)(?![\w'])", re.I)


_YO = re.compile(r"[ọẹṣ]")
_VI_ONLY = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯ]")
_UK_WORDS = re.compile(r"померти|дихає|допоможіть|чоловік|втомився|дуже|роботі|мене\s+б")
_ES = re.compile(r"(?<![\w'])(?:yo|no|mi|estoy|muy|hoy|pero|quiero|tengo|es|el|la|los|las|y|de|en|con)(?![\w'])", re.I)


def world_lang(text, min_hits: int = 2) -> str | None:
    """ภาษาที่มีคำตอบสำเร็จรูปในไฟล์นี้หรือ asia_replies — ไม่รู้จักคืน None
    min_hits=1 ใช้ตอนรู้แล้วว่าเป็นเรื่องด่วนภาษาอื่น (ข้อความมักสั้น เช่น "hilfe")"""
    t = str(text or "")
    if _YO.search(t) and not _VI_ONLY.search(t):      # โยรูบาใช้ ọ ẹ ṣ — อย่าเดาเป็นเวียดนาม
        return "yo"
    a = asia_lang(t)
    if a:
        return a
    if _ETHIOPIC.search(t):
        return "am"
    if _CYR.search(t):
        return "uk" if (_UKR.search(t) or _UK_WORDS.search(t)) else "ru"
    scores = {k: len(rx.findall(t)) for k, rx in _WORD_RX.items()}
    best = max(scores, key=scores.get)
    other = max(len(_EN_WORDS.findall(t)), len(_ES.findall(t)))
    # เรื่องด่วน (min_hits=1): รู้แล้วว่าไม่ใช่อังกฤษ คะแนนเท่ากันก็พอ ("i caawi" มีคำว่า i)
    if scores[best] >= min_hits and (scores[best] > other or (min_hits == 1 and scores[best] == other)):
        return best
    return None


def reply_for(lang: str, kind: str):
    if lang in WORLD_REPLY:
        return WORLD_REPLY[lang].get(kind)
    if kind == "general":
        return GENERAL_ASIA.get(lang)
    return ASIA_REPLY.get(lang, {}).get(kind)


def compose_world(lang: str, kind: str, status: str, sign: str, footer: bool = True) -> str | None:
    """คำตอบในภาษาของผู้ใช้ — ไม่มีภาษาหรือชนิดนี้คืน None ให้ใช้ทางเดิม"""
    r = reply_for(lang, kind)
    if not r:
        return None
    opener, steps, ask = r
    body = "\n".join(f"{i + 1}) {s}" for i, s in enumerate(steps))
    tag = "\n· Answered from the system's equations — no AI used" if footer else ""
    return f"{opener}\n\n{status}\n\n{body}\n\n{ask}\n\n{sign}" + tag


# ══════════════════════════════════════════════════════════════════
# รอบ "ทำภาษาที่เหลือ": กรีก โรมาเนีย สวีเดน ฮีบรู มองโกเลีย คาซัค อุซเบก
# (ฮาวายและภาษาพื้นเมืองออสเตรเลีย: ผู้พูดเกือบทั้งหมดอ่านอังกฤษได้ และคำแนะนำทางการแพทย์ที่แปลเองเสี่ยงผิด
#  จึงใช้คำตอบภาษาอังกฤษที่มีเบอร์ออสเตรเลีย + 13YARN สายด่วนของชาวอะบอริจินและช่องแคบทอร์เรส แทน)
# ══════════════════════════════════════════════════════════════════
WORLD_REPLY.update({
    "el": {
        "crisis": _set("Σε ακούω, και σε ευχαριστώ που μου το είπες.",
                       ["Στην Ταϊλάνδη κάλεσε το 1323 (ψυχική υγεία, 24 ώρες). Αν κινδυνεύεις τώρα: 1669.",
                        "Μη μείνεις μόνος/μόνη — πες σε έναν άνθρωπο που εμπιστεύεσαι ότι δεν είσαι καλά.",
                        "Ελλάδα: γραμμή παρέμβασης για την αυτοκτονία 1018 · έκτακτη ανάγκη 112 · αλλού: findahelpline.com"],
                       "Είσαι ασφαλής αυτή τη στιγμή;"),
        "medical": _set("Είναι επείγον — τηλεφώνησε πρώτα.",
                        ["Κάλεσε τώρα το 1669 (Ταϊλάνδη) · 112 ή ΕΚΑΒ 166 στην Ελλάδα. Πες τη διεύθυνση και τα συμπτώματα.",
                         "Αν δεν αναπνέει ή δεν αντιδρά: πίεσε δυνατά στο κέντρο του στήθους, 100–120 φορές το λεπτό.",
                         "Μη δώσεις νερό ή φαγητό. Κράτα τη συσκευασία του φαρμάκου για τον γιατρό."],
                        "Είναι κάποιος με τον άνθρωπο αυτή τη στιγμή;"),
        "violence": _set("Δεν φταις εσύ. Αξίζεις να είσαι ασφαλής.",
                         ["Αν κινδυνεύεις τώρα: 191 (αστυνομία Ταϊλάνδης) · 100 ή 112 στην Ελλάδα.",
                          "Πήγαινε πρώτα κάπου ασφαλές: σε γείτονα, σε φίλους, σε μέρος με κόσμο.",
                          "Κράτα φωτογραφίες τραυμάτων και μηνύματα ως αποδείξεις. Ελλάδα: γραμμή SOS 15900."],
                         "Είσαι ασφαλής τώρα;"),
        "help": _set("Είμαι εδώ. Πες μου τι συμβαίνει.",
                     ["Κίνδυνος ή τραυματισμός τώρα: 1669 (ιατρικό) · 191 (αστυνομία) στην Ταϊλάνδη · 112.",
                      "Γράψε σε μία πρόταση τι έγινε.",
                      "Αν μπορείς, πήγαινε κοντά σε άλλους ανθρώπους."],
                     "Πού είσαι τώρα, και είναι κάποιος μαζί σου;"),
        "general": _set("Ας το πάρουμε βήμα βήμα.",
                        ["Γράψε σε μία πρόταση τι πραγματικά συμβαίνει.",
                         "Κατέγραψε τι μπορείς να κάνεις σήμερα, ακόμα και κάτι μικρό.",
                         "Διάλεξε ένα μόνο βήμα για τις επόμενες 24 ώρες."],
                        "Τι σε βαραίνει περισσότερο αυτή τη στιγμή;"),
    },
    "ro": {
        "crisis": _set("Te aud și îți mulțumesc că mi-ai spus.",
                       ["În Thailanda sună la 1323 (sănătate mintală, 24 de ore). Dacă ești în pericol acum: 1669.",
                        "Nu rămâne singur/singură — spune unei persoane de încredere că nu ești bine.",
                        "România: 112 · Alianța Română de Prevenție a Suicidului 0800 801 200 · în alte țări: findahelpline.com"],
                       "Ești în siguranță acum?"),
        "medical": _set("Este o urgență — sună mai întâi.",
                        ["Sună acum la 1669 (Thailanda) · 112 în Europa. Spune adresa și simptomele.",
                         "Dacă nu respiră sau nu răspunde: apasă puternic în mijlocul pieptului, de 100–120 de ori pe minut.",
                         "Nu da apă sau mâncare. Păstrează ambalajul medicamentului pentru medic."],
                        "Este cineva lângă persoană acum?"),
        "violence": _set("Nu este vina ta. Meriți să fii în siguranță.",
                         ["Dacă ești în pericol acum: 191 (poliția din Thailanda) · 112 în Europa.",
                          "Mergi mai întâi într-un loc sigur: la un vecin, la prieteni, unde sunt oameni.",
                          "Păstrează fotografii cu rănile și mesajele ca dovezi. România: linia pentru victimele violenței 0800 500 333."],
                         "Ești în siguranță acum?"),
        "help": _set("Sunt aici. Spune-mi ce se întâmplă.",
                     ["Pericol sau rănire acum: 1669 (medical) · 191 (poliție) în Thailanda · 112.",
                      "Scrie într-o propoziție ce s-a întâmplat.",
                      "Dacă poți, du-te lângă alți oameni."],
                     "Unde ești acum și este cineva cu tine?"),
        "general": _set("Hai să luăm lucrurile pas cu pas.",
                        ["Scrie într-o propoziție ce se întâmplă de fapt.",
                         "Notează ce poți face azi, chiar și ceva mic.",
                         "Alege un singur pas pentru următoarele 24 de ore."],
                        "Ce te apasă cel mai tare acum?"),
    },
    "sv": {
        "crisis": _set("Jag hör dig, och tack för att du berättar.",
                       ["I Thailand: ring 1323 (psykisk hälsa, dygnet runt). Om du är i fara nu: 1669.",
                        "Var inte ensam — berätta för någon du litar på att du inte mår bra.",
                        "Sverige: Självmordslinjen 90101 · nödnummer 112 · andra länder: findahelpline.com"],
                       "Är du i säkerhet just nu?"),
        "medical": _set("Det här är ett nödläge — ring först.",
                        ["Ring 1669 nu (Thailand) · 112 i Europa. Säg adressen och symtomen.",
                         "Om personen inte andas eller inte svarar: tryck hårt mitt på bröstet, 100–120 gånger per minut.",
                         "Ge inte vatten eller mat. Spara förpackningen till läkemedlet åt läkaren."],
                        "Är någon hos personen just nu?"),
        "violence": _set("Det är inte ditt fel. Du förtjänar att vara trygg.",
                         ["Om du är i fara nu: 191 (polisen i Thailand) · 112 i Europa.",
                          "Gå först till en säker plats: en granne, vänner, en plats med folk.",
                          "Spara bilder på skador och meddelanden som bevis. Sverige: Kvinnofridslinjen 020-50 50 50."],
                         "Är du i säkerhet nu?"),
        "help": _set("Jag är här. Berätta vad som händer.",
                     ["Fara eller skada nu: 1669 (sjukvård) · 191 (polis) i Thailand · 112.",
                      "Skriv i en mening vad som hände.",
                      "Om du kan, gå till andra människor."],
                     "Var är du nu, och är någon med dig?"),
        "general": _set("Vi tar det steg för steg.",
                        ["Skriv i en mening vad det egentligen handlar om.",
                         "Skriv ner vad du kan göra i dag, även något litet.",
                         "Välj ett enda steg för de kommande 24 timmarna."],
                        "Vad tynger dig mest just nu?"),
    },
    "he": {
        "crisis": _set("אני שומעת אותך, ותודה שסיפרת לי.",
                       ["בתאילנד התקשרו ל־1323 (בריאות הנפש, 24 שעות). אם יש סכנה עכשיו: 1669.",
                        "אל תישארו לבד — ספרו לאדם שאתם סומכים עליו שלא טוב לכם.",
                        "בישראל: ער״ן 1201 · מד״א 101 · במדינות אחרות: findahelpline.com"],
                       "האם אתם בטוחים עכשיו?"),
        "medical": _set("זה מצב חירום — קודם כול מתקשרים.",
                        ["התקשרו עכשיו ל־1669 (תאילנד) · מד״א 101 בישראל. מסרו כתובת ותסמינים.",
                         "אם לא נושם או לא מגיב: לחצו חזק במרכז החזה, 100–120 פעמים בדקה.",
                         "אל תתנו מים או אוכל. שמרו את אריזת התרופה כדי להראות לרופא."],
                        "האם מישהו נמצא עכשיו ליד האדם?"),
        "violence": _set("זו לא אשמתך. מגיע לך להיות בטוח/ה.",
                         ["אם יש סכנה עכשיו: 191 (משטרת תאילנד) · 100 בישראל.",
                          "לכו קודם למקום בטוח: שכנים, חברים, מקום שיש בו אנשים.",
                          "שמרו תמונות של פציעות והודעות כראיה. בישראל: קו חירום לנפגעות אלימות 118."],
                         "האם אתם בטוחים עכשיו?"),
        "help": _set("אני כאן. ספרו לי מה קורה.",
                     ["סכנה או פציעה עכשיו: 1669 (רפואה) · 191 (משטרה) בתאילנד · 101/100 בישראל.",
                      "כתבו במשפט אחד מה קרה.",
                      "אם אפשר, התקרבו לאנשים אחרים."],
                     "איפה אתם עכשיו, והאם מישהו איתכם?"),
        "general": _set("בואו ניקח את זה צעד אחר צעד.",
                        ["כתבו במשפט אחד מה באמת קורה.",
                         "רשמו מה אפשר לעשות היום, אפילו משהו קטן.",
                         "בחרו צעד אחד בלבד ל־24 השעות הקרובות."],
                        "מה הכי מכביד עליכם עכשיו?"),
    },
    "mn": {
        "crisis": _set("Би таныг сонсож байна, хэлсэнд баярлалаа.",
                       ["Тайландад 1323 (сэтгэцийн эрүүл мэнд, 24 цаг) руу залгаарай. Одоо аюулд байвал: 1669.",
                        "Ганцаараа бүү бай — итгэдэг нэг хүндээ сайнгүй байгаагаа хэлээрэй.",
                        "Монголд: түргэн тусламж 103 · цагдаа 102 · бусад улсад: findahelpline.com"],
                       "Та яг одоо аюулгүй байна уу?"),
        "medical": _set("Энэ яаралтай байдал — эхлээд залгаарай.",
                        ["Одоо 1669 руу залга (Тайланд) · Монголд 103. Хаяг, шинж тэмдгийг хэл.",
                         "Амьсгалахгүй эсвэл хариу өгөхгүй бол: цээжний голыг минутад 100–120 удаа хүчтэй дар.",
                         "Ус, хоол бүү өг. Уусан эмийн хайрцгийг эмчид үзүүлэхээр хадгал."],
                        "Одоо өвчтөний дэргэд хэн нэгэн байна уу?"),
        "violence": _set("Энэ таны буруу биш. Та аюулгүй байх ёстой.",
                         ["Одоо аюулд байвал: 191 (Тайландын цагдаа) · Монголд 102.",
                          "Эхлээд аюулгүй газар оч: хөрш, найзын гэр, хүн олонтой газар.",
                          "Гэмтлийн зураг, мессежүүдээ нотлох баримт болгон хадгал. Тайландад 24 цагийн тусламж: 1300."],
                         "Та одоо аюулгүй байна уу?"),
        "help": _set("Би энд байна. Юу болж байгааг хэлээрэй.",
                     ["Одоо аюул эсвэл гэмтэл байвал: 1669 (эмнэлэг) · 191 (цагдаа) Тайландад · Монголд 103/102.",
                      "Юу болсныг нэг өгүүлбэрээр бич.",
                      "Боломжтой бол бусад хүмүүсийн дэргэд оч."],
                     "Та одоо хаана байна, хажууд тань хэн нэгэн байна уу?"),
        "general": _set("Алхам алхмаар авч үзье.",
                        ["Юу болж байгааг нэг өгүүлбэрээр бич.",
                         "Өнөөдөр хийж чадах зүйлсээ жагсаа, жижиг ч байсан.",
                         "Дараагийн 24 цагт хийх ганц алхмыг сонго."],
                        "Одоо таныг хамгийн их юу дарамталж байна вэ?"),
    },
    "kk": {
        "crisis": _set("Мен сізді тыңдап отырмын, айтқаныңызға рахмет.",
                       ["Таиландта 1323 нөміріне қоңырау шалыңыз (психикалық денсаулық, тәулік бойы). Қазір қауіп болса: 1669.",
                        "Жалғыз қалмаңыз — сенетін бір адамға өзіңізді жаман сезініп жүргеніңізді айтыңыз.",
                        "Қазақстанда: 112 · жедел жәрдем 103 · басқа елдерде: findahelpline.com"],
                       "Сіз қазір қауіпсізсіз бе?"),
        "medical": _set("Бұл шұғыл жағдай — алдымен қоңырау шалыңыз.",
                        ["Қазір 1669 нөміріне қоңырау шалыңыз (Таиланд) · Қазақстанда 103 немесе 112. Мекенжай мен белгілерді айтыңыз.",
                         "Тыныс алмаса немесе жауап бермесе: кеуденің ортасын минутына 100–120 рет қатты басыңыз.",
                         "Су не тамақ бермеңіз. Ішкен дәрінің қорабын дәрігерге көрсету үшін сақтаңыз."],
                        "Қазір науқастың жанында біреу бар ма?"),
        "violence": _set("Бұл сіздің кінәңіз емес. Сіз қауіпсіз болуға лайықсыз.",
                         ["Қазір қауіп болса: 191 (Таиланд полициясы) · Қазақстанда 102 немесе 112.",
                          "Алдымен қауіпсіз жерге барыңыз: көршіге, достарыңызға, адам көп жерге.",
                          "Жарақат суреттері мен хабарламаларды дәлел ретінде сақтаңыз. Таиландта тәулік бойы көмек: 1300."],
                         "Сіз қазір қауіпсізсіз бе?"),
        "help": _set("Мен осындамын. Не болып жатқанын айтыңыз.",
                     ["Қазір қауіп не жарақат болса: 1669 (медициналық) · 191 (полиция) Таиландта · Қазақстанда 112.",
                      "Не болғанын бір сөйлеммен жазыңыз.",
                      "Мүмкін болса, басқа адамдардың қасына барыңыз."],
                     "Қазір қайдасыз, қасыңызда біреу бар ма?"),
        "general": _set("Қадам-қадаммен қарастырайық.",
                        ["Не болып жатқанын бір сөйлеммен жазыңыз.",
                         "Бүгін не істей алатыныңызды жазыңыз, кішкентай болса да.",
                         "Келесі 24 сағатқа бір ғана қадам таңдаңыз."],
                        "Қазір сізді ең көп не мазалап тұр?"),
    },
    "uz": {
        "crisis": _set("Sizni eshityapman, aytganingiz uchun rahmat.",
                       ["Tailandda 1323 raqamiga qo'ng'iroq qiling (ruhiy salomatlik, 24 soat). Hozir xavf bo'lsa: 1669.",
                        "Yolg'iz qolmang — ishongan bir odamingizga o'zingizni yomon his qilayotganingizni ayting.",
                        "O'zbekistonda: tez yordam 103 · militsiya 102 · boshqa davlatlarda: findahelpline.com"],
                       "Hozir xavfsiz joydamisiz?"),
        "medical": _set("Bu shoshilinch holat — avval qo'ng'iroq qiling.",
                        ["Hozir 1669 ga qo'ng'iroq qiling (Tailand) · O'zbekistonda 103. Manzil va belgilarni ayting.",
                         "Nafas olmasa yoki javob bermasa: ko'krakning o'rtasini daqiqasiga 100–120 marta qattiq bosing.",
                         "Suv yoki ovqat bermang. Ichgan dorining qutisini shifokorga ko'rsatish uchun saqlang."],
                        "Hozir bemorning yonida kimdir bormi?"),
        "violence": _set("Bu sizning aybingiz emas. Siz xavfsiz bo'lishga haqlisiz.",
                         ["Hozir xavf bo'lsa: 191 (Tailand politsiyasi) · O'zbekistonda 102.",
                          "Avval xavfsiz joyga boring: qo'shni, do'stlar uyi yoki odam ko'p joy.",
                          "Jarohat suratlari va xabarlarni dalil sifatida saqlang. Tailandda 24 soatlik yordam: 1300."],
                         "Hozir xavfsizmisiz?"),
        "help": _set("Men shu yerdaman. Nima bo'layotganini ayting.",
                     ["Hozir xavf yoki jarohat bo'lsa: 1669 (tibbiy) · 191 (politsiya) Tailandda · O'zbekistonda 103/102.",
                      "Nima bo'lganini bitta gap bilan yozing.",
                      "Iloji bo'lsa, boshqa odamlar yoniga boring."],
                     "Hozir qayerdasiz, yoningizda kimdir bormi?"),
        "general": _set("Keling, qadamma-qadam ko'rib chiqamiz.",
                        ["Aslida nima bo'layotganini bitta gap bilan yozing.",
                         "Bugun nima qila olishingizni yozing, kichik bo'lsa ham.",
                         "Keyingi 24 soat uchun bitta qadamni tanlang."],
                        "Hozir sizni eng ko'p nima qiynayapti?"),
    },
})

_WORD_RX.update({k: re.compile(r"(?<![\w'])(?:" + v + r")(?![\w'])", re.I) for k, v in {
    "ro": r"vreau|să|mor|mama|nu|respiră|soțul|bate|ajutor|sunt|foarte|obosit|azi|astăzi|și|mă|eu",
    "sv": r"jag|inte|vill|dö|andas|mamma|min|man|slår|mig|hjälp|är|mycket|trött|idag|och",
    "uz": r"men|o'lmoqchiman|o'lishni|xohlayman|onam|nafas|olmayapti|erim|uradi|meni|yordam|bering|juda|charchadim|bugun|ishda",
}.items()})
_GREEK = re.compile(r"[Ͱ-Ͽ]")
_HEBREW = re.compile(r"[֐-׿]")
_KK = re.compile(r"[әғқңұһӘҒҚҢҰҺ]")
_UZ_CYR = re.compile(r"[ўҳЎҲ]")
_MN = re.compile(r"[өүӨҮ]|байна|туслаарай|ээж|намайг|амьсгал|өнөөдөр|ядарч")
_KK_WORDS = re.compile(r"келеді|анам|тыныс|алмайды|мені|көмек|бүгін|шаршадым|өлгім|ұрады")
_RO_ONLY = re.compile(r"[șțȘȚ]|\bsă\b|\bvreau\b|\bsoțul\b|\brespiră\b", re.I)
_world_lang_base = world_lang


def world_lang(text, min_hits: int = 2) -> str | None:  # noqa: F811 — ขยายตัวเดิมด้วยภาษารอบนี้
    t = str(text or "")
    if _GREEK.search(t):
        return "el"
    if _HEBREW.search(t):
        return "he"
    if _CYR.search(t):
        if _UZ_CYR.search(t):
            return "uz"
        if _KK.search(t) or _KK_WORDS.search(t):
            return "kk"
        if _MN.search(t):
            return "mn"
    if _RO_ONLY.search(t):                       # โรมาเนียมี ă เหมือนเวียดนาม — ตรวจก่อน
        return "ro"
    return _world_lang_base(t, min_hits)


# ══════════════════════════════════════════════════════════════════
# รอบ "ทำภาษาที่เหลือให้ครบ": เช็ก สโลวัก ฮังการี ฟินแลนด์ เดนมาร์ก นอร์เวย์
# โครเอเชีย/เซอร์เบีย/บอสเนีย (ใช้ชุดเดียวกัน) บัลแกเรีย จอร์เจีย อาร์เมเนีย
# สร้างจากตารางวลี 25 ช่องต่อภาษา (ลำดับเดียวกับ 5 ชนิด × เปิด/3 ขั้น/คำถาม)
# ══════════════════════════════════════════════════════════════════
_KINDS = ("crisis", "medical", "violence", "help", "general")


def _from_table(rows):
    rows = list(rows)
    assert len(rows) == 25
    return {k: (rows[i * 5], rows[i * 5 + 1:i * 5 + 4], rows[i * 5 + 4]) for i, k in enumerate(_KINDS)}


WORLD_REPLY.update({lg: _from_table(rows) for lg, rows in {
    "cs": ["Slyším tě a děkuji, že jsi mi to řekl/a.",
           "V Thajsku volej 1323 (duševní zdraví, nonstop). Pokud jsi v nebezpečí teď: 1669.",
           "Nezůstávej sám/sama — řekni člověku, kterému věříš, že ti není dobře.",
           "Česko: Linka první psychické pomoci 116 123 · tísňová linka 112 · jinde: findahelpline.com",
           "Jsi teď v bezpečí?",
           "Je to naléhavé — nejdřív volej.",
           "Volej hned 1669 (Thajsko) · 155 nebo 112 v Česku. Řekni adresu a příznaky.",
           "Pokud nedýchá nebo nereaguje: stlačuj silně střed hrudníku 100–120krát za minutu.",
           "Nedávej vodu ani jídlo. Schovej obal od léku pro lékaře.",
           "Je teď někdo u toho člověka?",
           "Není to tvoje vina. Zasloužíš si být v bezpečí.",
           "Pokud jsi v nebezpečí teď: 191 (thajská policie) · 158 nebo 112 v Česku.",
           "Jdi nejdřív na bezpečné místo: k sousedům, k přátelům, mezi lidi.",
           "Uschovej fotky zranění a zprávy jako důkaz. Česko: Bílý kruh bezpečí 116 006.",
           "Jsi teď v bezpečí?",
           "Jsem tady. Řekni mi, co se děje.",
           "Nebezpečí nebo zranění teď: 1669 (zdravotní) · 191 (policie) v Thajsku · 112.",
           "Napiš jednou větou, co se stalo.",
           "Jestli můžeš, jdi mezi jiné lidi.",
           "Kde teď jsi a je s tebou někdo?",
           "Vezmeme to krok za krokem.",
           "Napiš jednou větou, o co doopravdy jde.",
           "Sepiš, co můžeš udělat dnes, i když je to něco malého.",
           "Vyber jediný krok na příštích 24 hodin.",
           "Co tě teď nejvíc tíží?"],
    "sk": ["Počujem ťa a ďakujem, že si mi to povedal/a.",
           "V Thajsku volaj 1323 (duševné zdravie, nonstop). Ak si v nebezpečenstve teraz: 1669.",
           "Nezostávaj sám/sama — povedz človeku, ktorému veríš, že ti nie je dobre.",
           "Slovensko: Linka dôvery 0800 500 333 · tiesňová linka 112 · inde: findahelpline.com",
           "Si teraz v bezpečí?",
           "Je to naliehavé — najprv volaj.",
           "Volaj hneď 1669 (Thajsko) · 155 alebo 112 na Slovensku. Povedz adresu a príznaky.",
           "Ak nedýcha alebo nereaguje: stláčaj silno stred hrudníka 100–120-krát za minútu.",
           "Nedávaj vodu ani jedlo. Odlož obal od lieku pre lekára.",
           "Je teraz niekto pri tom človeku?",
           "Nie je to tvoja vina. Zaslúžiš si byť v bezpečí.",
           "Ak si v nebezpečenstve teraz: 191 (thajská polícia) · 158 alebo 112 na Slovensku.",
           "Choď najprv na bezpečné miesto: k susedom, k priateľom, medzi ľudí.",
           "Odlož fotky zranení a správy ako dôkaz. Slovensko: linka pre ženy 0800 212 212.",
           "Si teraz v bezpečí?",
           "Som tu. Povedz mi, čo sa deje.",
           "Nebezpečenstvo alebo zranenie teraz: 1669 (zdravotné) · 191 (polícia) v Thajsku · 112.",
           "Napíš jednou vetou, čo sa stalo.",
           "Ak môžeš, choď medzi iných ľudí.",
           "Kde teraz si a je s tebou niekto?",
           "Poďme na to krok za krokom.",
           "Napíš jednou vetou, o čo naozaj ide.",
           "Spíš, čo môžeš urobiť dnes, aj keď je to niečo malé.",
           "Vyber jediný krok na nasledujúcich 24 hodín.",
           "Čo ťa teraz najviac ťaží?"],
    "hu": ["Hallak téged, és köszönöm, hogy elmondtad.",
           "Thaiföldön hívd az 1323-at (lelki egészség, 0–24). Ha most veszélyben vagy: 1669.",
           "Ne maradj egyedül — mondd el valakinek, akiben megbízol, hogy nem vagy jól.",
           "Magyarország: Lelki Elsősegély 116 123 · segélyhívó 112 · máshol: findahelpline.com",
           "Most biztonságban vagy?",
           "Ez vészhelyzet — előbb telefonálj.",
           "Hívd most az 1669-et (Thaiföld) · 112 Magyarországon. Mondd meg a címet és a tüneteket.",
           "Ha nem lélegzik vagy nem reagál: nyomd erősen a mellkas közepét, percenként 100–120-szor.",
           "Ne adj vizet vagy ételt. Őrizd meg a gyógyszer dobozát az orvosnak.",
           "Van most valaki a beteg mellett?",
           "Nem a te hibád. Megérdemled, hogy biztonságban legyél.",
           "Ha most veszélyben vagy: 191 (thai rendőrség) · 112 Magyarországon.",
           "Menj először biztonságos helyre: szomszédhoz, barátokhoz, emberek közé.",
           "Őrizd meg a sérülésekről készült fotókat és az üzeneteket bizonyítéknak. Magyarország: OKIT 06 80 20 55 20.",
           "Most biztonságban vagy?",
           "Itt vagyok. Mondd el, mi történik.",
           "Veszély vagy sérülés most: 1669 (mentő) · 191 (rendőrség) Thaiföldön · 112.",
           "Írd le egy mondatban, mi történt.",
           "Ha tudsz, menj más emberek közelébe.",
           "Hol vagy most, és van veled valaki?",
           "Vegyük lépésről lépésre.",
           "Írd le egy mondatban, miről szól igazán.",
           "Írd össze, mit tudsz ma megtenni, akár valami kicsit is.",
           "Válassz egyetlen lépést a következő 24 órára.",
           "Mi nyomaszt most a legjobban?"],
    "fi": ["Kuulen sinua, ja kiitos että kerroit.",
           "Thaimaassa soita 1323 (mielenterveys, 24 h). Jos olet vaarassa nyt: 1669.",
           "Älä jää yksin — kerro jollekulle, johon luotat, ettet voi hyvin.",
           "Suomi: Kriisipuhelin 09 2525 0111 · hätänumero 112 · muualla: findahelpline.com",
           "Oletko nyt turvassa?",
           "Tämä on hätätilanne — soita ensin.",
           "Soita heti 1669 (Thaimaa) · 112 Suomessa. Kerro osoite ja oireet.",
           "Jos hän ei hengitä tai ei reagoi: paina lujaa rintakehän keskeltä 100–120 kertaa minuutissa.",
           "Älä anna vettä tai ruokaa. Säilytä lääkepakkaus lääkäriä varten.",
           "Onko joku nyt hänen luonaan?",
           "Se ei ole sinun syysi. Ansaitset olla turvassa.",
           "Jos olet vaarassa nyt: 191 (Thaimaan poliisi) · 112 Suomessa.",
           "Mene ensin turvalliseen paikkaan: naapuriin, ystävälle, ihmisten pariin.",
           "Säilytä kuvat vammoista ja viestit todisteiksi. Suomi: Nollalinja 080 005 005.",
           "Oletko nyt turvassa?",
           "Olen tässä. Kerro, mitä tapahtuu.",
           "Vaara tai vamma nyt: 1669 (ensiapu) · 191 (poliisi) Thaimaassa · 112.",
           "Kirjoita yhdellä lauseella, mitä tapahtui.",
           "Jos pystyt, mene muiden ihmisten luo.",
           "Missä olet nyt, ja onko joku kanssasi?",
           "Otetaan tämä askel kerrallaan.",
           "Kirjoita yhdellä lauseella, mistä on oikeasti kyse.",
           "Listaa, mitä voit tehdä tänään, vaikka jotain pientä.",
           "Valitse yksi askel seuraaville 24 tunnille.",
           "Mikä painaa sinua eniten juuri nyt?"],
    "da": ["Jeg hører dig, og tak fordi du fortæller mig det.",
           "I Thailand: ring 1323 (psykisk sundhed, døgnet rundt). Er du i fare nu: 1669.",
           "Bliv ikke alene — fortæl en, du stoler på, at du ikke har det godt.",
           "Danmark: Livslinien 70 201 201 · alarm 112 · andre lande: findahelpline.com",
           "Er du i sikkerhed lige nu?",
           "Det er en nødsituation — ring først.",
           "Ring 1669 nu (Thailand) · 112 i Danmark. Sig adressen og symptomerne.",
           "Hvis personen ikke trækker vejret eller ikke reagerer: tryk hårdt midt på brystet, 100–120 gange i minuttet.",
           "Giv ikke vand eller mad. Gem medicinpakken til lægen.",
           "Er der nogen hos personen lige nu?",
           "Det er ikke din skyld. Du fortjener at være i sikkerhed.",
           "Er du i fare nu: 191 (thailandsk politi) · 112 i Danmark.",
           "Gå først et sikkert sted hen: en nabo, venner, et sted med mennesker.",
           "Gem billeder af skader og beskeder som bevis. Danmark: Lev Uden Vold 1888.",
           "Er du i sikkerhed nu?",
           "Jeg er her. Fortæl mig, hvad der sker.",
           "Fare eller skade nu: 1669 (sundhed) · 191 (politi) i Thailand · 112.",
           "Skriv i én sætning, hvad der skete.",
           "Hvis du kan, så gå hen til andre mennesker.",
           "Hvor er du nu, og er der nogen hos dig?",
           "Lad os tage det et skridt ad gangen.",
           "Skriv i én sætning, hvad det egentlig handler om.",
           "Skriv ned, hvad du kan gøre i dag, også noget småt.",
           "Vælg ét skridt for de næste 24 timer.",
           "Hvad tynger dig mest lige nu?"],
    "no": ["Jeg hører deg, og takk for at du forteller meg det.",
           "I Thailand: ring 1323 (psykisk helse, døgnåpent). Er du i fare nå: 1669.",
           "Ikke vær alene — si til noen du stoler på at du ikke har det bra.",
           "Norge: Mental Helse 116 123 · ambulanse 113 · andre land: findahelpline.com",
           "Er du trygg akkurat nå?",
           "Dette er en nødsituasjon — ring først.",
           "Ring 1669 nå (Thailand) · 113 i Norge. Si adressen og symptomene.",
           "Hvis personen ikke puster eller ikke reagerer: trykk hardt midt på brystet, 100–120 ganger i minuttet.",
           "Ikke gi vann eller mat. Ta vare på medisinpakken til legen.",
           "Er noen hos personen nå?",
           "Det er ikke din skyld. Du fortjener å være trygg.",
           "Er du i fare nå: 191 (thailandsk politi) · 112 i Norge.",
           "Gå først til et trygt sted: en nabo, venner, et sted med folk.",
           "Ta vare på bilder av skader og meldinger som bevis. Norge: Krisesentersekretariatet / 116 006.",
           "Er du trygg nå?",
           "Jeg er her. Fortell meg hva som skjer.",
           "Fare eller skade nå: 1669 (helse) · 191 (politi) i Thailand · 112/113 i Norge.",
           "Skriv i én setning hva som skjedde.",
           "Hvis du kan, gå bort til andre mennesker.",
           "Hvor er du nå, og er noen med deg?",
           "La oss ta det ett steg om gangen.",
           "Skriv i én setning hva det egentlig handler om.",
           "Skriv ned hva du kan gjøre i dag, også noe lite.",
           "Velg ett steg for de neste 24 timene.",
           "Hva tynger deg mest akkurat nå?"],
    "sh": ["Čujem te i hvala ti što si mi rekao/rekla.",
           "U Tajlandu nazovi 1323 (mentalno zdravlje, 0–24). Ako si sada u opasnosti: 1669.",
           "Nemoj ostati sam/sama — reci nekome kome vjeruješ da ti nije dobro.",
           "Hrvatska 112 · Srbija 194 (hitna) / 192 (policija) · BiH 124 · drugdje: findahelpline.com",
           "Jesi li sada na sigurnom?",
           "Ovo je hitno — prvo nazovi.",
           "Nazovi odmah 1669 (Tajland) · 112 u Hrvatskoj · 194 u Srbiji. Reci adresu i simptome.",
           "Ako ne diše ili ne reagira: snažno pritišći sredinu prsnog koša, 100–120 puta u minuti.",
           "Ne daj vodu ni hranu. Sačuvaj kutiju lijeka za liječnika.",
           "Je li netko sada uz tu osobu?",
           "Nisi ti kriv/kriva. Zaslužuješ biti siguran/sigurna.",
           "Ako si sada u opasnosti: 191 (tajlandska policija) · 112 u Hrvatskoj · 192 u Srbiji.",
           "Prvo idi na sigurno mjesto: kod susjeda, prijatelja, među ljude.",
           "Sačuvaj slike ozljeda i poruke kao dokaz. U Tajlandu pomoć 0–24: 1300.",
           "Jesi li sada na sigurnom?",
           "Tu sam. Reci mi što se događa.",
           "Opasnost ili ozljeda sada: 1669 (hitna) · 191 (policija) u Tajlandu · 112.",
           "Napiši u jednoj rečenici što se dogodilo.",
           "Ako možeš, idi među druge ljude.",
           "Gdje si sada i je li netko s tobom?",
           "Idemo korak po korak.",
           "Napiši u jednoj rečenici o čemu se zapravo radi.",
           "Zapiši što možeš učiniti danas, makar nešto malo.",
           "Odaberi samo jedan korak za sljedeća 24 sata.",
           "Što te sada najviše muči?"],
    "bg": ["Чувам те и благодаря, че ми каза.",
           "В Тайланд се обади на 1323 (психично здраве, денонощно). Ако си в опасност сега: 1669.",
           "Не оставай сам/сама — кажи на човек, на когото имаш доверие, че не си добре.",
           "България: спешен телефон 112 · други държави: findahelpline.com",
           "В безопасност ли си сега?",
           "Това е спешно — първо се обади.",
           "Обади се сега на 1669 (Тайланд) · 112 в България. Кажи адреса и симптомите.",
           "Ако не диша или не реагира: натискай силно в средата на гърдите, 100–120 пъти в минута.",
           "Не давай вода или храна. Запази опаковката на лекарството за лекаря.",
           "Има ли някой при човека сега?",
           "Не е твоя вината. Заслужаваш да си в безопасност.",
           "Ако си в опасност сега: 191 (тайландска полиция) · 112 в България.",
           "Първо отиди на безопасно място: при съсед, приятели, където има хора.",
           "Запази снимки на нараняванията и съобщенията като доказателство. Помощ в Тайланд 24 ч: 1300.",
           "В безопасност ли си сега?",
           "Тук съм. Кажи ми какво се случва.",
           "Опасност или нараняване сега: 1669 (медицинска) · 191 (полиция) в Тайланд · 112.",
           "Напиши с едно изречение какво се случи.",
           "Ако можеш, отиди при други хора.",
           "Къде си сега и има ли някой с теб?",
           "Нека да го вземем стъпка по стъпка.",
           "Напиши с едно изречение за какво всъщност става дума.",
           "Запиши какво можеш да направиш днес, дори нещо малко.",
           "Избери само една стъпка за следващите 24 часа.",
           "Какво те тежи най-много сега?"],
    "ka": ["მესმის შენი და მადლობა, რომ მითხარი.",
           "ტაილანდში დარეკე 1323-ზე (ფსიქიკური ჯანმრთელობა, 24 საათი). თუ ახლა საფრთხეში ხარ: 1669.",
           "მარტო ნუ დარჩები — უთხარი ვინმეს, ვისაც ენდობი, რომ კარგად არ ხარ.",
           "საქართველო: 112 · სხვა ქვეყნებში: findahelpline.com",
           "ახლა უსაფრთხოდ ხარ?",
           "ეს გადაუდებელი შემთხვევაა — ჯერ დარეკე.",
           "დარეკე ახლავე 1669-ზე (ტაილანდი) · 112 საქართველოში. თქვი მისამართი და სიმპტომები.",
           "თუ არ სუნთქავს ან არ რეაგირებს: ძლიერად დააწექი მკერდის შუაგულს, წუთში 100–120-ჯერ.",
           "ნუ მისცემ წყალს ან საჭმელს. შეინახე წამლის შეფუთვა ექიმისთვის.",
           "ახლა ვინმე არის ავადმყოფთან?",
           "ეს შენი ბრალი არ არის. იმსახურებ, რომ უსაფრთხოდ იყო.",
           "თუ ახლა საფრთხეში ხარ: 191 (ტაილანდის პოლიცია) · 112 საქართველოში.",
           "ჯერ წადი უსაფრთხო ადგილას: მეზობელთან, მეგობართან, სადაც ხალხია.",
           "შეინახე დაზიანებების ფოტოები და შეტყობინებები მტკიცებულებად. ტაილანდში 24-საათიანი დახმარება: 1300.",
           "ახლა უსაფრთხოდ ხარ?",
           "აქ ვარ. მითხარი, რა ხდება.",
           "საფრთხე ან დაზიანება ახლა: 1669 (სამედიცინო) · 191 (პოლიცია) ტაილანდში · 112.",
           "ერთი წინადადებით დაწერე, რა მოხდა.",
           "თუ შეგიძლია, სხვა ადამიანებთან ახლოს წადი.",
           "სად ხარ ახლა და ვინმე არის შენთან?",
           "მოდი ნაბიჯ-ნაბიჯ განვიხილოთ.",
           "ერთი წინადადებით დაწერე, რა ხდება სინამდვილეში.",
           "ჩამოწერე, რისი გაკეთება შეგიძლია დღეს, თუნდაც პატარა რამ.",
           "აირჩიე მხოლოდ ერთი ნაბიჯი მომდევნო 24 საათისთვის.",
           "რა გაწუხებს ყველაზე მეტად ახლა?"],
    "hy": ["Լսում եմ քեզ, և շնորհակալ եմ, որ ասացիր։",
           "Թաիլանդում զանգիր 1323 (հոգեկան առողջություն, շուրջօրյա)։ Եթե հիմա վտանգի մեջ ես՝ 1669։",
           "Մենակ մի մնա — ասա մեկին, ում վստահում ես, որ լավ չես։",
           "Հայաստան՝ 911 կամ 112 · այլ երկրներում՝ findahelpline.com",
           "Հիմա ապահո՞վ ես։",
           "Սա շտապ դեպք է — նախ զանգիր։",
           "Զանգիր հիմա 1669 (Թաիլանդ) · 911 Հայաստանում։ Ասա հասցեն և ախտանիշները։",
           "Եթե չի շնչում կամ չի արձագանքում՝ ուժեղ սեղմիր կրծքավանդակի մեջտեղը, րոպեում 100–120 անգամ։",
           "Ջուր կամ ուտելիք մի տուր։ Պահիր դեղի տուփը բժշկի համար։",
           "Հիմա ինչ-որ մեկը կա՞ հիվանդի կողքին։",
           "Սա քո մեղքը չէ։ Դու արժանի ես ապահով լինելու։",
           "Եթե հիմա վտանգի մեջ ես՝ 191 (Թաիլանդի ոստիկանություն) · 911 Հայաստանում։",
           "Նախ գնա ապահով տեղ՝ հարևանի, ընկերների մոտ կամ մարդաշատ վայր։",
           "Պահիր վնասվածքների լուսանկարները և հաղորդագրությունները որպես ապացույց։ Թաիլանդում շուրջօրյա օգնություն՝ 1300։",
           "Հիմա ապահո՞վ ես։",
           "Ես այստեղ եմ։ Ասա, թե ինչ է կատարվում։",
           "Վտանգ կամ վնասվածք հիմա՝ 1669 (բժշկական) · 191 (ոստիկանություն) Թաիլանդում · 911։",
           "Մեկ նախադասությամբ գրիր, թե ինչ պատահեց։",
           "Եթե կարող ես, գնա ուրիշ մարդկանց մոտ։",
           "Որտե՞ղ ես հիմա, և ինչ-որ մեկը կա՞ քեզ հետ։",
           "Եկ քայլ առ քայլ նայենք։",
           "Մեկ նախադասությամբ գրիր, թե իրականում ինչ է կատարվում։",
           "Գրիր, թե ինչ կարող ես անել այսօր, թեկուզ փոքր բան։",
           "Ընտրիր միայն մեկ քայլ հաջորդ 24 ժամվա համար։",
           "Ի՞նչն է քեզ հիմա ամենաշատը ծանրացնում։"],
}.items()})

# "ช่วยด้วย" คำเดียวในจีน ญี่ปุ่น เกาหลี สเปน — เดิมได้คำตอบทั่วไป ("ลองเรียงเรื่องทีละขั้น")
HELP_MAIN = {
    "zh": ("我在这里。告诉我发生了什么。",
           ["现在有危险或受伤：在泰国拨打 1669（急救）· 191（警察）· 中国大陆 120 / 110。",
            "用一句话写下发生了什么。", "如果可以，先到有其他人的地方。"], "你现在在哪里？身边有人吗？"),
    "ja": ("ここにいます。何が起きているか教えてください。",
           ["今、危険やけががあるなら：タイでは 1669（救急）· 191（警察）、日本では 119 / 110。",
            "何があったか一文で書いてください。", "できれば、ほかの人がいる場所へ移動してください。"], "今どこにいますか？そばに誰かいますか？"),
    "ko": ("여기 있어요. 무슨 일이 있는지 말해 주세요.",
           ["지금 위험하거나 다쳤다면: 태국에서는 1669(응급) · 191(경찰), 한국에서는 119 / 112.",
            "무슨 일이 있었는지 한 문장으로 써 주세요.", "가능하면 다른 사람들이 있는 곳으로 가세요."], "지금 어디에 있고, 곁에 누가 있나요?"),
    "es": ("Estoy aquí. Cuéntame qué está pasando.",
           ["Si hay peligro o heridas ahora: en Tailandia 1669 (médico) · 191 (policía) · 112 en España · 911 en México y EE. UU.",
            "Escribe en una frase qué pasó.", "Si puedes, acércate a otras personas."], "¿Dónde estás ahora y hay alguien contigo?"),
}

_CS = re.compile(r"[řěůŘĚŮ]")
_SK = re.compile(r"[ľĺŕôĽĹŔÔ]")
_HU = re.compile(r"[őűŐŰ]")
_DANO = re.compile(r"[æøÆØ]")
_SH = re.compile(r"[čćđČĆĐ]")
_SR_CYR = re.compile(r"[ђјљњћџЂЈЉЊЋЏ]")
_BG = re.compile(r"ъ|искам\s+да|не\s+диша|бие\s+ме|помощ|съм\b|днес")
_PL = re.compile(r"[ąęłśźżĄĘŁŚŹŻ]")
_HU_W = re.compile(r"\b(?:akarok|halni|lélegzik|férjem|segítség|nagyon|fáradt|vagyok|munkában)\b", re.I)
_SK_W = re.compile(r"\b(?:nedýcha|zomrieť|ma\s+bije|veľmi|neviem|pomôžte|som\s+dnes)\b", re.I)
_CS_W = re.compile(r"\b(?:pomozte|nedýchá|umřít|mě\s+bije|nevím|jsem\s+dnes)\b", re.I)
_KA = re.compile(r"[Ⴀ-ჿ]")
_HY = re.compile(r"[԰-֏]")
_NO_W = re.compile(r"\b(?:hjelp|puster|veldig|ikkje|meg|deg|slår\s+meg|kjempe)\b", re.I)
_DA_W = re.compile(r"\b(?:hjælp|vejret|meget|træt|mand|mig)\b", re.I)   # ไม่ใช้ mig/dig — สวีเดนก็ใช้
_WORD_RX.update({k: re.compile(r"(?<![\w'])(?:" + v + r")(?![\w'])", re.I) for k, v in {
    "cs": r"chci|umřít|nedýchá|manžel|mě|bije|pomoc|jsem|velmi|unavený|dnes|nevím|co|dělat",
    "sk": r"chcem|zomrieť|nedýcha|manžel|ma|bije|pomoc|som|veľmi|unavený|dnes|neviem|čo|robiť",
    "hu": r"meg|akarok|halni|anyám|nem|lélegzik|férjem|ver|segítség|nagyon|fáradt|vagyok|ma|munkában",
    "fi": r"minä|haluan|kuolla|äiti|ei|hengitä|mieheni|lyö|minua|apua|olen|todella|väsynyt|tänään|töissä",
    "sh": r"želim|umrijeti|umreti|mama|ne|diše|muž|me|tuče|upomoć|pomoć|jako|umoran|danas|sam",
}.items()})
_world_lang_prev = world_lang


def world_lang(text, min_hits: int = 2) -> str | None:  # noqa: F811 — ขยายด้วยภาษายุโรปที่เหลือ
    t = str(text or "")
    if _KA.search(t):
        return "ka"
    if _HY.search(t):
        return "hy"
    if _CYR.search(t):
        if _SR_CYR.search(t):
            return "sh"
        if _BG.search(t) and not re.search(r"[ыэё]", t):
            return "bg"
    if _VI_ONLY.search(t):                       # เวียดนามมี ô เหมือนสโลวัก — ให้ตัวเดิมตัดสิน
        return _world_lang_prev(t, min_hits)
    if _PL.search(t):                            # ą ę ł ś ź ż — โปแลนด์ (อย่าให้ ć ทำให้เดาเป็นโครเอเชีย)
        return "pl"
    if _HU.search(t) or _HU_W.search(t):          # "meg" ซ้ำกับนอร์เวย์ — ตรวจฮังการีก่อน
        return "hu"
    if _SK.search(t) or _SK_W.search(t):
        return "sk"
    if _CS.search(t) or _CS_W.search(t):
        return "cs"
    if _DANO.search(t) or _NO_W.search(t) or re.search(r"\b(?:jeg|hjælp|vejret|træt|mand)\b", t, re.I):
        n, d = len(_NO_W.findall(t)), len(_DA_W.findall(t))
        if n or d or _DANO.search(t):
            return "no" if n > d else "da"
    if _SH.search(t) and not re.search(r"[ăâîșț]", t):
        return "sh"
    return _world_lang_prev(t, min_hits)


def help_main(lang: str):
    return HELP_MAIN.get(lang)
