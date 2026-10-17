# ตรวจคำแปลและเบอร์ฉุกเฉิน
ไฟล์นี้สร้างอัตโนมัติจากโค้ด (`python scripts/build_translation_review.py`) — อย่าแก้ในไฟล์นี้โดยตรง
ให้เจ้าของภาษาช่วยเช็ก 3 อย่าง: ① ความหมายถูกและน้ำเสียงอ่อนโยน ② ไม่มีคำที่ทำให้ตกใจหรือดูถูก ③ เบอร์ในประเทศนั้นยังใช้ได้จริง (เทียบกับเว็บทางการ)

| ภาษา | หัวข้อ | เบอร์ที่พบ |
|---|---|---|
| Afrikaans (`af`) | 5 | 0800 428 · 0800 567 567 · 100 · 10111 · 10177 · 120 · 1323 · 1669 · 191 |
| Dansk (`da`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 191 · 70 201 201 |
| Deutsch (`de`) | 5 | 0800 111 0 111 · 0800 222 · 100 · 112 · 116 016 · 120 · 1323 · 142 · 1669 · 191 |
| Español (`es`) | 6 | 016 · 112 · 911 |
| Français (`fr`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 191 · 3114 · 911 |
| Hausa (`ha`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 191 |
| Hrvatski / Srpski / Bosanski (`sh`) | 5 | 100 · 112 · 120 · 124 · 1323 · 1669 · 191 · 192 · 194 |
| Indonesia (`id`) | 4 | 100 · 110 · 119 · 120 · 1300 · 1323 · 1669 · 191 |
| Italiano (`it`) | 5 | 02 2327 2327 · 100 · 112 · 120 · 1323 · 1669 · 191 |
| Kiswahili (`sw`) | 5 | 100 · 112 · 1195 · 120 · 1323 · 1669 · 191 · 999 |
| Magyar (`hu`) | 5 | 06 80 20 55 · 100 · 112 · 116 123 · 120 · 1323 · 1669 · 191 |
| Melayu (`ms`) | 4 | 03-7627 2929 · 100 · 120 · 1300 · 1323 · 1669 · 191 · 999 |
| Nederlands (`nl`) | 5 | 0800 · 0800-0113 · 100 · 112 · 113 · 120 · 1323 · 1669 · 1813 · 191 |
| Norsk (`no`) | 5 | 100 · 112 · 113 · 116 · 116 123 · 120 · 1323 · 1669 · 191 |
| Oʻzbek (`uz`) | 5 | 100 · 102 · 103 · 120 · 1323 · 1669 · 191 |
| Polski (`pl`) | 5 | 100 · 112 · 116 123 · 120 · 1323 · 1669 · 191 · 800 120 |
| Português (`pt`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 188 · 190 · 191 · 192 |
| Română (`ro`) | 5 | 0800 500 · 0800 801 200 · 100 · 112 · 120 · 1323 · 1669 · 191 |
| Slovenčina (`sk`) | 5 | 0800 212 · 0800 500 333 · 100 · 112 · 120 · 1323 · 155 · 158 · 1669 · 191 |
| Soomaali (`so`) | 5 | 100 · 120 · 1323 · 1669 · 191 |
| Suomi (`fi`) | 5 | 080 005 · 09 2525 0111 · 100 · 112 · 120 · 1323 · 1669 · 191 |
| Svenska (`sv`) | 5 | 020-50 50 · 100 · 112 · 120 · 1323 · 1669 · 191 · 90101 |
| Tagalog (`tl`) | 4 | 100 · 120 · 1300 · 1323 · 1553 · 1669 · 191 · 911 |
| Tiếng Việt (`vi`) | 4 | 100 · 113 · 115 · 120 · 1300 · 1323 · 1669 · 191 |
| Türkçe (`tr`) | 4 | 100 · 112 · 120 · 1300 · 1323 · 1669 · 191 |
| Yorùbá (`yo`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 191 |
| isiZulu (`zu`) | 5 | 0800 428 · 0800 567 567 · 100 · 10111 · 10177 · 120 · 1323 · 1669 · 191 |
| Čeština (`cs`) | 5 | 100 · 112 · 116 · 116 123 · 1323 · 155 · 158 · 1669 · 191 |
| Ελληνικά (`el`) | 5 | 100 · 1018 · 112 · 120 · 1323 · 166 · 1669 · 191 |
| Български (`bg`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 191 |
| Монгол (`mn`) | 5 | 100 · 102 · 103 · 120 · 1323 · 1669 · 191 |
| Русский (`ru`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 191 · 8-800-2000-122 |
| Українська (`uk`) | 5 | 100 · 102 · 103 · 112 · 120 · 1323 · 1669 · 191 · 7333 |
| Қазақ (`kk`) | 5 | 100 · 102 · 103 · 112 · 120 · 1323 · 1669 · 191 |
| Հայերեն (`hy`) | 5 | 100 · 112 · 120 · 1300 · 1323 · 1669 · 191 · 911 |
| עברית (`he`) | 5 | 100 · 101 · 120 · 1201 · 1323 · 1669 · 191 |
| اردو (`ur`) | 4 | 100 · 1122 · 120 · 1300 · 1323 · 1669 · 191 |
| العربية (`ar`) | 4 | 100 · 120 · 1300 · 1323 · 1669 · 191 |
| فارسی (`fa`) | 4 | 110 · 115 · 1300 · 1323 · 1480 · 1669 · 191 · ۱۰۰ · ۱۲۰ |
| नेपाली (`ne`) | 4 | 100 · 102 · 1166 · 1300 · 1323 · 1669 · 191 · १०० · १२० |
| हिन्दी (`hi`) | 4 | 100 · 112 · 120 · 1300 · 1323 · 14416 · 1669 · 191 |
| বাংলা (`bn`) | 4 | 1300 · 1323 · 1669 · 191 · 999 · ১০০ · ১২০ |
| தமிழ் (`ta`) | 4 | 100 · 108 · 112 · 120 · 1300 · 1323 · 14416 · 1669 · 191 |
| සිංහල (`si`) | 4 | 100 · 119 · 120 · 1300 · 1323 · 1669 · 191 · 1926 · 1990 |
| ລາວ (`lo`) | 4 | 100 · 120 · 1300 · 1323 · 1669 · 191 |
| မြန်မာ (`my`) | 4 | 1300 · 1323 · 1669 · 191 · ၁၀၀ · ၁၂၀ |
| ქართული (`ka`) | 5 | 100 · 112 · 120 · 1323 · 1669 · 191 |
| አማርኛ (`am`) | 5 | 100 · 120 · 1300 · 1323 · 1669 · 191 |
| ខ្មែរ (`km`) | 4 | 1300 · 1323 · 1669 · 191 · ១០០ · ១២០ |
| 中文 (`zh`) | 6 | 110 · 119 · 120 · 12338 · 12345 · 96110 |
| 日本語 (`ja`) | 6 | 110 · 119 · 8008 · 9110 |
| 한국어 (`ko`) | 6 | 109 · 1366 |

## Afrikaans (`af`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Ek hoor jou, en dankie dat jy my vertel.', ['In Thailand, bel 1323 (geestesgesondheid, 24 uur). In gevaar nou: 1669.', 'Moenie alleen bly nie — sê vir iemand wat jy vertrou dat dit nie goed gaan nie.', 'Suid-Afrika: SADAG 0800 567 567 · polisie 10111 · ander lande: findahelpline.com'], 'Is jy nou veilig?')
```

**medical**

```text
("Dit is 'n noodgeval — bel eers.", ['Bel nou 1669 (Thailand) · Suid-Afrika 10177 of 112. Gee die adres en die simptome.', 'As die persoon nie asemhaal of reageer nie: druk hard in die middel van die bors, 100–120 keer per minuut.', 'Moenie water of kos gee nie. Hou die medisynepakkie vir die dokter.'], 'Is daar nou iemand by die persoon?')
```

**violence**

```text
('Dit is nie jou skuld nie. Jy verdien om veilig te wees.', ['In gevaar nou: 191 (Thaise polisie) · Suid-Afrika 10111.', "Gaan eers na 'n veilige plek: 'n buurman, vriende, of 'n plek met mense.", "Hou foto's van beserings en boodskappe as bewys. Suid-Afrika: GBV Command Centre 0800 428 428."], 'Is jy nou veilig?')
```

**help**

```text
('Ek is hier. Vertel my wat aangaan.', ['Gevaar of besering nou: 1669 (medies) · 191 (polisie) in Thailand · Suid-Afrika 10111.', 'Skryf in een sin wat gebeur het.', 'As jy kan, gaan na ander mense toe.'], 'Waar is jy nou, en is iemand by jou?')
```

**general**

```text
('Kom ons vat dit stap vir stap.', ['Skryf in een sin waaroor dit regtig gaan.', 'Lys wat jy vandag kan doen, al is dit iets kleins.', 'Kies een stap vir die volgende 24 uur.'], 'Wat druk die swaarste op jou nou?')
```

## Dansk (`da`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Jeg hører dig, og tak fordi du fortæller mig det.', ['I Thailand: ring 1323 (psykisk sundhed, døgnet rundt). Er du i fare nu: 1669.', 'Bliv ikke alene — fortæl en, du stoler på, at du ikke har det godt.', 'Danmark: Livslinien 70 201 201 · alarm 112 · andre lande: findahelpline.com'], 'Er du i sikkerhed lige nu?')
```

**medical**

```text
('Det er en nødsituation — ring først.', ['Ring 1669 nu (Thailand) · 112 i Danmark. Sig adressen og symptomerne.', 'Hvis personen ikke trækker vejret eller ikke reagerer: tryk hårdt midt på brystet, 100–120 gange i minuttet.', 'Giv ikke vand eller mad. Gem medicinpakken til lægen.'], 'Er der nogen hos personen lige nu?')
```

**violence**

```text
('Det er ikke din skyld. Du fortjener at være i sikkerhed.', ['Er du i fare nu: 191 (thailandsk politi) · 112 i Danmark.', 'Gå først et sikkert sted hen: en nabo, venner, et sted med mennesker.', 'Gem billeder af skader og beskeder som bevis. Danmark: Lev Uden Vold 1888.'], 'Er du i sikkerhed nu?')
```

**help**

```text
('Jeg er her. Fortæl mig, hvad der sker.', ['Fare eller skade nu: 1669 (sundhed) · 191 (politi) i Thailand · 112.', 'Skriv i én sætning, hvad der skete.', 'Hvis du kan, så gå hen til andre mennesker.'], 'Hvor er du nu, og er der nogen hos dig?')
```

**general**

```text
('Lad os tage det et skridt ad gangen.', ['Skriv i én sætning, hvad det egentlig handler om.', 'Skriv ned, hvad du kan gøre i dag, også noget småt.', 'Vælg ét skridt for de næste 24 timer.'], 'Hvad tynger dig mest lige nu?')
```

## Deutsch (`de`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Ich höre Ihnen zu – danke, dass Sie es mir sagen.', ['In Thailand: 1323 anrufen (psychische Gesundheit, 24 Std.). Jetzt in Gefahr: 1669.', 'Bleiben Sie nicht allein – sagen Sie einer Person, der Sie vertrauen, dass es Ihnen nicht gut geht.', 'Deutschland: TelefonSeelsorge 0800 111 0 111 · Österreich: 142 · Notruf 112 · sonst: findahelpline.com'], 'Sind Sie gerade in Sicherheit?')
```

**medical**

```text
('Das ist ein Notfall – rufen Sie zuerst an.', ['Jetzt 1669 anrufen (Thailand) · 112 in Europa. Adresse und Beschwerden nennen.', 'Atmet die Person nicht oder reagiert nicht: fest in der Mitte der Brust drücken, 100–120 Mal pro Minute.', 'Kein Wasser und kein Essen geben. Die Medikamentenpackung für den Arzt aufheben.'], 'Ist gerade jemand bei der Person?')
```

**violence**

```text
('Das ist nicht Ihre Schuld. Sie haben ein Recht auf Sicherheit.', ['Jetzt in Gefahr: 191 (Polizei Thailand) · 112 in Europa · Österreich Polizei 133.', 'Gehen Sie zuerst an einen sicheren Ort: Nachbarn, Freunde, ein Ort mit Menschen.', 'Bewahren Sie Fotos von Verletzungen und Nachrichten als Beweis auf. Hilfetelefon DE: 116 016 · AT: 0800 222 555.'], 'Sind Sie jetzt in Sicherheit?')
```

**help**

```text
('Ich bin da. Erzählen Sie mir, was passiert.', ['Jetzt Gefahr oder Verletzung: 1669 (medizinisch) · 191 (Polizei) in Thailand · 112 in Europa.', 'Schreiben Sie in einem Satz, was passiert ist.', 'Wenn möglich, gehen Sie zu anderen Menschen.'], 'Wo sind Sie, und ist jemand bei Ihnen?')
```

**general**

```text
('Gehen wir das Schritt für Schritt an.', ['Schreiben Sie in einem Satz, worum es wirklich geht.', 'Notieren Sie, was Sie heute tun können – auch etwas Kleines.', 'Wählen Sie einen einzigen Schritt für die nächsten 24 Stunden.'], 'Was belastet Sie gerade am meisten?')
```

## Español (`es`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**basic**

```text
('Primero, que puedas comer hoy — eso va antes que cualquier plan.', ['Contacta hoy con los servicios sociales de tu ayuntamiento o municipio: pueden darte ayuda de emergencia para comida.', 'Busca un banco de alimentos, comedor social, Cáritas o Cruz Roja cerca de ti — suelen dar comida ese mismo día.', 'Si estás mareado o muy débil, llama al 112 (España) o al 911 (México y EE. UU.).'], '¿Dónde estás ahora y hay alguien que pueda ayudarte?')
```

**someone**

```text
('Gracias por preocuparte por esa persona — estar ahí importa más de lo que crees.', ['Pregúntale directamente: "¿Estás pensando en quitarte la vida?". Preguntar no empeora las cosas.', 'Si está en peligro o ya se hizo daño, llama ahora al 112 (España) o al 911 (México y EE. UU.).', 'Intenta que no se quede sola y aleja medicamentos, cuchillos o armas.'], '¿Esa persona está acompañada ahora mismo?')
```

**medical**

```text
('Es una emergencia — primero llama, después todo lo demás.', ['Llama ahora al 112 (España) o al 911 (México y EE. UU.) y di la dirección y los síntomas.', 'Si no respira o no responde, sigue las instrucciones del operador para hacer compresiones en el pecho.', 'No le des agua ni comida, y guarda el envase de lo que haya tomado para enseñarlo al médico.'], '¿Hay alguien con la persona ahora mismo?')
```

**violence**

```text
('No es tu culpa. Mereces estar a salvo.', ['Si estás en peligro ahora, llama al 112 (España) o al 911 (México y EE. UU.).', 'Ve primero a un lugar seguro: un vecino, familiares o amigos, o un sitio con gente.', 'Guarda pruebas (fotos de lesiones, mensajes, partes médicos). En España, el 016 atiende 24 horas y no deja rastro en la factura.'], '¿Estás en un lugar seguro ahora mismo?')
```

**disaster**

```text
('Tu seguridad es lo primero — las cosas se pueden reponer.', ['Terremoto: agáchate, cúbrete la cabeza y sujétate a una mesa; cuando pare, sal por las escaleras (no uses el ascensor).', 'Incendio o fuga de gas: no toques interruptores, cúbrete nariz y boca, sal agachado y llama al 112 / 911 desde fuera.', 'Inundación o tsunami: sube a un lugar alto ya. No camines ni conduzcas por el agua.'], '¿Dónde estás ahora y hay alguien contigo?')
```

**scam**

```text
('Esto tiene señales de estafa — no transfieras nada todavía.', ['La policía o tu banco nunca te pedirán transferir dinero a una "cuenta segura" ni tus códigos.', 'Cuelga y llama tú al número oficial para comprobarlo.', 'Si ya transferiste, llama a tu banco para bloquearlo y denuncia a la policía (112 / 911).'], '¿Ya enviaste dinero o diste algún código?')
```

## Français (`fr`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
("Je vous entends, et merci de me l'avoir dit.", ['En Thaïlande, appelez le 1323 (santé mentale, 24 h/24). En danger maintenant : 1669.', 'Ne restez pas seul·e — dites à une personne de confiance que ça ne va pas.', 'En France : 3114 (prévention du suicide) · Europe : 112 · ailleurs : findahelpline.com'], 'Êtes-vous en sécurité en ce moment ?')
```

**medical**

```text
("C'est une urgence — appelez d'abord.", ["Appelez le 1669 maintenant (Thaïlande) · 112 en Europe · 911 au Canada. Donnez l'adresse et les symptômes.", "S'il ne respire pas ou ne répond pas : appuyez fort au centre de la poitrine, 100 à 120 fois par minute.", "Ne donnez ni eau ni nourriture. Gardez l'emballage du médicament pour le médecin."], "Quelqu'un est-il avec la personne en ce moment ?")
```

**violence**

```text
("Ce n'est pas votre faute. Vous méritez d'être en sécurité.", ['En danger maintenant : 191 (police thaïlandaise) · 112 en Europe · 911 au Canada.', "Allez d'abord dans un lieu sûr : un voisin, un ami, un endroit avec du monde.", 'Gardez les photos des blessures et les messages comme preuves. Aide sociale 24 h en Thaïlande : 1300.'], 'Êtes-vous en sécurité maintenant ?')
```

**help**

```text
('Je suis là. Dites-moi ce qui se passe.', ['Danger ou blessure maintenant : 1669 (médical) · 191 (police) en Thaïlande · 112 en Europe.', "Écrivez en une phrase ce qui s'est passé.", "Si vous pouvez, rapprochez-vous d'autres personnes."], "Où êtes-vous, et quelqu'un est-il avec vous ?")
```

**general**

```text
('Prenons les choses une étape à la fois.', ['Écrivez en une phrase ce qui se passe vraiment.', "Listez ce que vous pouvez faire aujourd'hui, même quelque chose de petit.", 'Choisissez une seule action pour les prochaines 24 heures.'], "Qu'est-ce qui vous pèse le plus en ce moment ?")
```

## Hausa (`ha`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Ina jin ka, kuma na gode da ka gaya mini.', ['A Thailand ka kira 1323 (lafiyar kwakwalwa, awa 24). Idan kana cikin haɗari yanzu: 1669.', 'Kada ka zauna kai kaɗai — gaya wa wanda ka amince da shi cewa ba ka da lafiya.', 'Najeriya: 112 · sauran ƙasashe: findahelpline.com'], 'Kana cikin aminci yanzu?')
```

**medical**

```text
('Wannan gaggawa ce — ka kira waya da farko.', ['Ka kira 1669 yanzu (Thailand) · Najeriya 112. Faɗi adireshi da alamun cutar.', 'Idan baya numfashi ko baya amsawa: danna tsakiyar ƙirji da ƙarfi sau 100–120 a minti ɗaya.', 'Kada ka ba shi ruwa ko abinci. Ajiye kwalin maganin don likita ya gani.'], 'Akwai wani tare da mara lafiyar yanzu?')
```

**violence**

```text
('Ba laifinka ba ne. Ka cancanci zama cikin aminci.', ["Idan kana cikin haɗari yanzu: 191 ('yan sandan Thailand) · Najeriya 112.", 'Da farko ka je wuri mai aminci: maƙwabci, gidan aboki, ko wurin da mutane suke.', 'Ajiye hotunan raunuka da saƙonni a matsayin shaida. Taimako na awa 24 a Thailand: 1300.'], 'Kana cikin aminci yanzu?')
```

**help**

```text
('Ina nan. Gaya mini abin da ke faruwa.', ["Haɗari ko rauni yanzu: 1669 (lafiya) · 191 ('yan sanda) a Thailand · Najeriya 112.", 'Rubuta abin da ya faru a jumla ɗaya.', 'Idan za ka iya, je kusa da wasu mutane.'], 'Ina kake yanzu, kuma akwai wani tare da kai?')
```

**general**

```text
('Mu bi shi mataki-mataki.', ['Rubuta abin da ke faruwa a jumla ɗaya.', 'Lissafa abin da za ka iya yi yau, ko da ƙarami ne.', 'Zaɓi mataki ɗaya kawai na awa 24 masu zuwa.'], 'Me ya fi damunka yanzu?')
```

## Hrvatski / Srpski / Bosanski (`sh`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Čujem te i hvala ti što si mi rekao/rekla.', ['U Tajlandu nazovi 1323 (mentalno zdravlje, 0–24). Ako si sada u opasnosti: 1669.', 'Nemoj ostati sam/sama — reci nekome kome vjeruješ da ti nije dobro.', 'Hrvatska 112 · Srbija 194 (hitna) / 192 (policija) · BiH 124 · drugdje: findahelpline.com'], 'Jesi li sada na sigurnom?')
```

**medical**

```text
('Ovo je hitno — prvo nazovi.', ['Nazovi odmah 1669 (Tajland) · 112 u Hrvatskoj · 194 u Srbiji. Reci adresu i simptome.', 'Ako ne diše ili ne reagira: snažno pritišći sredinu prsnog koša, 100–120 puta u minuti.', 'Ne daj vodu ni hranu. Sačuvaj kutiju lijeka za liječnika.'], 'Je li netko sada uz tu osobu?')
```

**violence**

```text
('Nisi ti kriv/kriva. Zaslužuješ biti siguran/sigurna.', ['Ako si sada u opasnosti: 191 (tajlandska policija) · 112 u Hrvatskoj · 192 u Srbiji.', 'Prvo idi na sigurno mjesto: kod susjeda, prijatelja, među ljude.', 'Sačuvaj slike ozljeda i poruke kao dokaz. U Tajlandu pomoć 0–24: 1300.'], 'Jesi li sada na sigurnom?')
```

**help**

```text
('Tu sam. Reci mi što se događa.', ['Opasnost ili ozljeda sada: 1669 (hitna) · 191 (policija) u Tajlandu · 112.', 'Napiši u jednoj rečenici što se dogodilo.', 'Ako možeš, idi među druge ljude.'], 'Gdje si sada i je li netko s tobom?')
```

**general**

```text
('Idemo korak po korak.', ['Napiši u jednoj rečenici o čemu se zapravo radi.', 'Zapiši što možeš učiniti danas, makar nešto malo.', 'Odaberi samo jedan korak za sljedeća 24 sata.'], 'Što te sada najviše muči?')
```

## Indonesia (`id`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Aku mendengarmu, dan terima kasih sudah bercerita.', ['Di Thailand, telepon 1323 (kesehatan jiwa, 24 jam). Jika dalam bahaya sekarang, segera telepon 1669.', 'Jangan sendirian. Beri tahu satu orang yang kamu percaya bahwa kamu sedang tidak baik-baik saja.', 'Di luar Thailand, cari layanan bantuan di findahelpline.com (Indonesia: 119 ext 8).'], 'Apakah kamu aman sekarang?')
```

**medical**

```text
('Ini keadaan darurat — telepon dulu.', ['Telepon 1669 sekarang (di Indonesia: 119), sebutkan alamat dan gejalanya.', 'Jika tidak bernapas atau tidak merespons: tekan kuat di tengah dada 100–120 kali per menit, ikuti petunjuk petugas di telepon.', 'Jangan beri minum atau makan. Simpan kemasan obat yang diminum untuk ditunjukkan ke dokter.'], 'Apakah ada orang yang menemani pasien sekarang?')
```

**violence**

```text
('Ini bukan salahmu. Kamu berhak untuk aman.', ['Jika dalam bahaya sekarang, telepon 191 (polisi Thailand; di Indonesia: 110).', 'Pergi dulu ke tempat aman: tetangga, rumah teman, atau tempat ramai.', 'Kamu bisa telepon 1300 (bantuan sosial 24 jam). Simpan foto luka dan pesan sebagai bukti.'], 'Apakah kamu aman sekarang?')
```

**help**

```text
('Aku di sini. Ceritakan apa yang sedang terjadi.', ['Jika dalam bahaya atau terluka sekarang: 1669 (medis) · 191 (polisi)', 'Tulis dalam satu kalimat apa yang terjadi.', 'Kalau bisa, pergilah ke dekat orang lain.'], 'Kamu di mana sekarang, dan apakah ada orang bersamamu?')
```

## Italiano (`it`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Ti ascolto, e grazie per avermelo detto.', ['In Thailandia chiama il 1323 (salute mentale, 24 ore). In pericolo ora: 1669.', "Non restare da solo/a — di' a una persona di cui ti fidi che non stai bene.", 'Italia: 112 · Telefono Amico 02 2327 2327 · altri paesi: findahelpline.com'], 'Sei al sicuro in questo momento?')
```

**medical**

```text
("È un'emergenza — prima chiama.", ["Chiama ora il 1669 (Thailandia) · 112 in Europa. Di' l'indirizzo e i sintomi.", 'Se non respira o non risponde: premi forte al centro del petto, 100–120 volte al minuto.', 'Non dare acqua né cibo. Conserva la confezione del farmaco per il medico.'], "C'è qualcuno con la persona adesso?")
```

**violence**

```text
('Non è colpa tua. Meriti di essere al sicuro.', ['In pericolo ora: 191 (polizia thailandese) · 112 in Europa.', 'Vai prima in un posto sicuro: un vicino, un amico, un luogo con gente.', 'Conserva foto delle ferite e messaggi come prova. Italia: numero antiviolenza 1522.'], 'Sei al sicuro adesso?')
```

**help**

```text
('Sono qui. Dimmi cosa sta succedendo.', ['Pericolo o ferite adesso: 1669 (medico) · 191 (polizia) in Thailandia · 112 in Europa.', 'Scrivi in una frase cosa è successo.', 'Se puoi, avvicinati ad altre persone.'], "Dove sei, e c'è qualcuno con te?")
```

**general**

```text
('Affrontiamolo un passo alla volta.', ['Scrivi in una frase cosa sta succedendo davvero.', 'Elenca cosa puoi fare oggi, anche una cosa piccola.', 'Scegli una sola azione per le prossime 24 ore.'], 'Cosa ti pesa di più in questo momento?')
```

## Kiswahili (`sw`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Ninakusikia, na asante kwa kuniambia.', ['Ukiwa Thailand piga 1323 (afya ya akili, saa 24). Ukiwa hatarini sasa: 1669.', 'Usikae peke yako — mwambie mtu unayemwamini kwamba hauko sawa.', 'Kenya: 999 au 112 · Tanzania: 112 · nchi nyingine: findahelpline.com'], 'Uko salama sasa hivi?')
```

**medical**

```text
('Hii ni dharura — piga simu kwanza.', ['Piga 1669 sasa (Thailand) · Kenya 999 au 112. Taja anwani na dalili.', 'Kama hapumui au haitikii: bonyeza kwa nguvu katikati ya kifua mara 100–120 kwa dakika.', 'Usimpe maji wala chakula. Hifadhi pakiti ya dawa umwonyeshe daktari.'], 'Kuna mtu yeyote na mgonjwa sasa?')
```

**violence**

```text
('Si kosa lako. Unastahili kuwa salama.', ['Ukiwa hatarini sasa: 191 (polisi wa Thailand) · Kenya 999 au 112.', 'Kwanza nenda mahali salama: kwa jirani, kwa rafiki, au mahali penye watu.', 'Hifadhi picha za majeraha na jumbe kama ushahidi. Kenya: 1195 (msaada wa ukatili wa kijinsia).'], 'Uko salama sasa?')
```

**help**

```text
('Niko hapa. Niambie kinachoendelea.', ['Hatari au jeraha sasa: 1669 (matibabu) · 191 (polisi) Thailand · Kenya 999.', 'Andika kwa sentensi moja kilichotokea.', 'Ukiweza, nenda karibu na watu wengine.'], 'Uko wapi sasa, na kuna mtu pamoja nawe?')
```

**general**

```text
('Tuchukue hatua moja baada ya nyingine.', ['Andika kwa sentensi moja kinachoendelea kweli.', 'Orodhesha unachoweza kufanya leo, hata kitu kidogo.', 'Chagua hatua moja tu kwa saa 24 zijazo.'], 'Ni nini kinakulemea zaidi sasa hivi?')
```

## Magyar (`hu`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Hallak téged, és köszönöm, hogy elmondtad.', ['Thaiföldön hívd az 1323-at (lelki egészség, 0–24). Ha most veszélyben vagy: 1669.', 'Ne maradj egyedül — mondd el valakinek, akiben megbízol, hogy nem vagy jól.', 'Magyarország: Lelki Elsősegély 116 123 · segélyhívó 112 · máshol: findahelpline.com'], 'Most biztonságban vagy?')
```

**medical**

```text
('Ez vészhelyzet — előbb telefonálj.', ['Hívd most az 1669-et (Thaiföld) · 112 Magyarországon. Mondd meg a címet és a tüneteket.', 'Ha nem lélegzik vagy nem reagál: nyomd erősen a mellkas közepét, percenként 100–120-szor.', 'Ne adj vizet vagy ételt. Őrizd meg a gyógyszer dobozát az orvosnak.'], 'Van most valaki a beteg mellett?')
```

**violence**

```text
('Nem a te hibád. Megérdemled, hogy biztonságban legyél.', ['Ha most veszélyben vagy: 191 (thai rendőrség) · 112 Magyarországon.', 'Menj először biztonságos helyre: szomszédhoz, barátokhoz, emberek közé.', 'Őrizd meg a sérülésekről készült fotókat és az üzeneteket bizonyítéknak. Magyarország: OKIT 06 80 20 55 20.'], 'Most biztonságban vagy?')
```

**help**

```text
('Itt vagyok. Mondd el, mi történik.', ['Veszély vagy sérülés most: 1669 (mentő) · 191 (rendőrség) Thaiföldön · 112.', 'Írd le egy mondatban, mi történt.', 'Ha tudsz, menj más emberek közelébe.'], 'Hol vagy most, és van veled valaki?')
```

**general**

```text
('Vegyük lépésről lépésre.', ['Írd le egy mondatban, miről szól igazán.', 'Írd össze, mit tudsz ma megtenni, akár valami kicsit is.', 'Válassz egyetlen lépést a következő 24 órára.'], 'Mi nyomaszt most a legjobban?')
```

## Melayu (`ms`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Saya dengar awak, dan terima kasih kerana memberitahu saya.', ['Di Thailand, telefon 1323 (kesihatan mental, 24 jam). Jika dalam bahaya sekarang, segera telefon 1669.', 'Jangan bersendirian. Beritahu seorang yang awak percaya bahawa awak tidak okey.', 'Di luar Thailand, cari talian bantuan di findahelpline.com (Malaysia: Befrienders 03-7627 2929).'], 'Adakah awak selamat sekarang?')
```

**medical**

```text
('Ini kecemasan — telefon dahulu.', ['Telefon 1669 sekarang (di Malaysia: 999), beritahu alamat dan simptom.', 'Jika tidak bernafas atau tidak sedar: tekan kuat di tengah dada 100–120 kali seminit, ikut arahan pegawai di telefon.', 'Jangan beri minuman atau makanan. Simpan bungkusan ubat yang diambil untuk ditunjukkan kepada doktor.'], 'Adakah sesiapa bersama pesakit sekarang?')
```

**violence**

```text
('Ini bukan salah awak. Awak berhak untuk selamat.', ['Jika dalam bahaya sekarang, telefon 191 (polis Thailand; di Malaysia: 999).', 'Pergi dahulu ke tempat selamat: jiran, rumah kawan, atau tempat ramai orang.', 'Awak boleh telefon 1300 (bantuan sosial 24 jam). Simpan gambar kecederaan dan mesej sebagai bukti.'], 'Adakah awak selamat sekarang?')
```

**help**

```text
('Saya di sini. Ceritakan apa yang sedang berlaku.', ['Jika dalam bahaya atau cedera sekarang: 1669 (perubatan) · 191 (polis)', 'Tulis dalam satu ayat apa yang berlaku.', 'Jika boleh, pergi dekat dengan orang lain.'], 'Awak di mana sekarang, dan adakah sesiapa bersama awak?')
```

## Nederlands (`nl`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Ik hoor je, en dank je dat je het vertelt.', ['In Thailand: bel 1323 (geestelijke gezondheid, 24 uur). Nu in gevaar: 1669.', 'Blijf niet alleen — vertel iemand die je vertrouwt dat het niet goed gaat.', 'Nederland: 113 (0800-0113) · België: 1813 · noodnummer 112 · elders: findahelpline.com'], 'Ben je nu veilig?')
```

**medical**

```text
('Dit is een noodgeval — bel eerst.', ['Bel nu 1669 (Thailand) · 112 in Europa. Geef het adres en de klachten door.', 'Ademt iemand niet of reageert niet: druk hard op het midden van de borst, 100–120 keer per minuut.', 'Geef geen water of eten. Bewaar de verpakking van het medicijn voor de arts.'], 'Is er nu iemand bij de persoon?')
```

**violence**

```text
('Het is niet jouw schuld. Je verdient het om veilig te zijn.', ['Nu in gevaar: 191 (politie Thailand) · 112 in Europa.', 'Ga eerst naar een veilige plek: buren, vrienden, een plek met mensen.', "Bewaar foto's van verwondingen en berichten als bewijs. Nederland: Veilig Thuis 0800-2000."], 'Ben je nu veilig?')
```

**help**

```text
('Ik ben er. Vertel wat er gebeurt.', ['Nu gevaar of letsel: 1669 (medisch) · 191 (politie) in Thailand · 112.', 'Schrijf in één zin wat er gebeurd is.', 'Ga als het kan in de buurt van andere mensen.'], 'Waar ben je, en is er iemand bij je?')
```

**general**

```text
('Laten we het stap voor stap bekijken.', ['Schrijf in één zin waar het echt om gaat.', 'Schrijf op wat je vandaag kunt doen, ook iets kleins.', 'Kies één stap voor de komende 24 uur.'], 'Wat weegt nu het zwaarst voor je?')
```

## Norsk (`no`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Jeg hører deg, og takk for at du forteller meg det.', ['I Thailand: ring 1323 (psykisk helse, døgnåpent). Er du i fare nå: 1669.', 'Ikke vær alene — si til noen du stoler på at du ikke har det bra.', 'Norge: Mental Helse 116 123 · ambulanse 113 · andre land: findahelpline.com'], 'Er du trygg akkurat nå?')
```

**medical**

```text
('Dette er en nødsituasjon — ring først.', ['Ring 1669 nå (Thailand) · 113 i Norge. Si adressen og symptomene.', 'Hvis personen ikke puster eller ikke reagerer: trykk hardt midt på brystet, 100–120 ganger i minuttet.', 'Ikke gi vann eller mat. Ta vare på medisinpakken til legen.'], 'Er noen hos personen nå?')
```

**violence**

```text
('Det er ikke din skyld. Du fortjener å være trygg.', ['Er du i fare nå: 191 (thailandsk politi) · 112 i Norge.', 'Gå først til et trygt sted: en nabo, venner, et sted med folk.', 'Ta vare på bilder av skader og meldinger som bevis. Norge: Krisesentersekretariatet / 116 006.'], 'Er du trygg nå?')
```

**help**

```text
('Jeg er her. Fortell meg hva som skjer.', ['Fare eller skade nå: 1669 (helse) · 191 (politi) i Thailand · 112/113 i Norge.', 'Skriv i én setning hva som skjedde.', 'Hvis du kan, gå bort til andre mennesker.'], 'Hvor er du nå, og er noen med deg?')
```

**general**

```text
('La oss ta det ett steg om gangen.', ['Skriv i én setning hva det egentlig handler om.', 'Skriv ned hva du kan gjøre i dag, også noe lite.', 'Velg ett steg for de neste 24 timene.'], 'Hva tynger deg mest akkurat nå?')
```

## Oʻzbek (`uz`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Sizni eshityapman, aytganingiz uchun rahmat.', ["Tailandda 1323 raqamiga qo'ng'iroq qiling (ruhiy salomatlik, 24 soat). Hozir xavf bo'lsa: 1669.", "Yolg'iz qolmang — ishongan bir odamingizga o'zingizni yomon his qilayotganingizni ayting.", "O'zbekistonda: tez yordam 103 · militsiya 102 · boshqa davlatlarda: findahelpline.com"], 'Hozir xavfsiz joydamisiz?')
```

**medical**

```text
("Bu shoshilinch holat — avval qo'ng'iroq qiling.", ["Hozir 1669 ga qo'ng'iroq qiling (Tailand) · O'zbekistonda 103. Manzil va belgilarni ayting.", "Nafas olmasa yoki javob bermasa: ko'krakning o'rtasini daqiqasiga 100–120 marta qattiq bosing.", "Suv yoki ovqat bermang. Ichgan dorining qutisini shifokorga ko'rsatish uchun saqlang."], 'Hozir bemorning yonida kimdir bormi?')
```

**violence**

```text
("Bu sizning aybingiz emas. Siz xavfsiz bo'lishga haqlisiz.", ["Hozir xavf bo'lsa: 191 (Tailand politsiyasi) · O'zbekistonda 102.", "Avval xavfsiz joyga boring: qo'shni, do'stlar uyi yoki odam ko'p joy.", 'Jarohat suratlari va xabarlarni dalil sifatida saqlang. Tailandda 24 soatlik yordam: 1300.'], 'Hozir xavfsizmisiz?')
```

**help**

```text
("Men shu yerdaman. Nima bo'layotganini ayting.", ["Hozir xavf yoki jarohat bo'lsa: 1669 (tibbiy) · 191 (politsiya) Tailandda · O'zbekistonda 103/102.", "Nima bo'lganini bitta gap bilan yozing.", "Iloji bo'lsa, boshqa odamlar yoniga boring."], 'Hozir qayerdasiz, yoningizda kimdir bormi?')
```

**general**

```text
("Keling, qadamma-qadam ko'rib chiqamiz.", ["Aslida nima bo'layotganini bitta gap bilan yozing.", "Bugun nima qila olishingizni yozing, kichik bo'lsa ham.", 'Keyingi 24 soat uchun bitta qadamni tanlang.'], "Hozir sizni eng ko'p nima qiynayapti?")
```

## Polski (`pl`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Słyszę cię i dziękuję, że mi to mówisz.', ['W Tajlandii zadzwoń pod 1323 (zdrowie psychiczne, całą dobę). W niebezpieczeństwie teraz: 1669.', 'Nie zostawaj sam/sama — powiedz zaufanej osobie, że nie jest dobrze.', 'Polska: 112 · telefon zaufania 116 123 · inne kraje: findahelpline.com'], 'Czy jesteś teraz bezpieczny/bezpieczna?')
```

**medical**

```text
('To nagły wypadek — najpierw zadzwoń.', ['Zadzwoń teraz pod 1669 (Tajlandia) · 112 w Europie. Podaj adres i objawy.', 'Jeśli nie oddycha lub nie reaguje: uciskaj mocno środek klatki piersiowej, 100–120 razy na minutę.', 'Nie podawaj wody ani jedzenia. Zachowaj opakowanie leku dla lekarza.'], 'Czy ktoś jest teraz przy tej osobie?')
```

**violence**

```text
('To nie twoja wina. Masz prawo być bezpieczny/bezpieczna.', ['W niebezpieczeństwie teraz: 191 (policja w Tajlandii) · 112 w Europie.', 'Najpierw idź w bezpieczne miejsce: do sąsiada, przyjaciół, tam, gdzie są ludzie.', 'Zachowaj zdjęcia obrażeń i wiadomości jako dowody. Polska: Niebieska Linia 800 120 002.'], 'Czy jesteś teraz bezpieczny/bezpieczna?')
```

**help**

```text
('Jestem tu. Powiedz, co się dzieje.', ['Niebezpieczeństwo lub uraz teraz: 1669 (medyczny) · 191 (policja) w Tajlandii · 112.', 'Napisz w jednym zdaniu, co się stało.', 'Jeśli możesz, idź tam, gdzie są inni ludzie.'], 'Gdzie jesteś i czy ktoś jest z tobą?')
```

**general**

```text
('Zróbmy to krok po kroku.', ['Napisz w jednym zdaniu, o co naprawdę chodzi.', 'Wypisz, co możesz zrobić dzisiaj — nawet coś małego.', 'Wybierz jeden krok na najbliższe 24 godziny.'], 'Co najbardziej cię teraz przytłacza?')
```

## Português (`pt`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Eu te escuto, e obrigada por me contar.', ['Na Tailândia, ligue 1323 (saúde mental, 24 h). Em perigo agora: 1669.', 'Não fique sozinho(a) — conte a uma pessoa de confiança que você não está bem.', 'Brasil: CVV 188 (24 h) · Portugal: 112 · outros países: findahelpline.com'], 'Você está em segurança agora?')
```

**medical**

```text
('É uma emergência — ligue primeiro.', ['Ligue 1669 agora (Tailândia) · SAMU 192 no Brasil · 112 em Portugal. Diga o endereço e os sintomas.', 'Se não respira ou não responde: pressione forte o centro do peito, 100 a 120 vezes por minuto.', 'Não dê água nem comida. Guarde a embalagem do remédio para mostrar ao médico.'], 'Tem alguém com a pessoa agora?')
```

**violence**

```text
('Não é culpa sua. Você merece estar em segurança.', ['Em perigo agora: 191 (polícia tailandesa) · 190 no Brasil · 112 em Portugal.', 'Vá primeiro para um lugar seguro: vizinho, casa de amigos, um lugar com gente.', 'Guarde fotos dos ferimentos e mensagens como prova. Brasil: Central da Mulher 180.'], 'Você está em segurança agora?')
```

**help**

```text
('Estou aqui. Me conte o que está acontecendo.', ['Perigo ou ferimento agora: 1669 (médico) · 191 (polícia) na Tailândia · 192/190 no Brasil.', 'Escreva em uma frase o que aconteceu.', 'Se puder, vá para perto de outras pessoas.'], 'Onde você está, e tem alguém com você?')
```

**general**

```text
('Vamos por partes, um passo de cada vez.', ['Escreva em uma frase o que está acontecendo de verdade.', 'Liste o que você pode fazer hoje, mesmo que seja algo pequeno.', 'Escolha uma única ação para as próximas 24 horas.'], 'O que mais está pesando para você agora?')
```

## Română (`ro`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Te aud și îți mulțumesc că mi-ai spus.', ['În Thailanda sună la 1323 (sănătate mintală, 24 de ore). Dacă ești în pericol acum: 1669.', 'Nu rămâne singur/singură — spune unei persoane de încredere că nu ești bine.', 'România: 112 · Alianța Română de Prevenție a Suicidului 0800 801 200 · în alte țări: findahelpline.com'], 'Ești în siguranță acum?')
```

**medical**

```text
('Este o urgență — sună mai întâi.', ['Sună acum la 1669 (Thailanda) · 112 în Europa. Spune adresa și simptomele.', 'Dacă nu respiră sau nu răspunde: apasă puternic în mijlocul pieptului, de 100–120 de ori pe minut.', 'Nu da apă sau mâncare. Păstrează ambalajul medicamentului pentru medic.'], 'Este cineva lângă persoană acum?')
```

**violence**

```text
('Nu este vina ta. Meriți să fii în siguranță.', ['Dacă ești în pericol acum: 191 (poliția din Thailanda) · 112 în Europa.', 'Mergi mai întâi într-un loc sigur: la un vecin, la prieteni, unde sunt oameni.', 'Păstrează fotografii cu rănile și mesajele ca dovezi. România: linia pentru victimele violenței 0800 500 333.'], 'Ești în siguranță acum?')
```

**help**

```text
('Sunt aici. Spune-mi ce se întâmplă.', ['Pericol sau rănire acum: 1669 (medical) · 191 (poliție) în Thailanda · 112.', 'Scrie într-o propoziție ce s-a întâmplat.', 'Dacă poți, du-te lângă alți oameni.'], 'Unde ești acum și este cineva cu tine?')
```

**general**

```text
('Hai să luăm lucrurile pas cu pas.', ['Scrie într-o propoziție ce se întâmplă de fapt.', 'Notează ce poți face azi, chiar și ceva mic.', 'Alege un singur pas pentru următoarele 24 de ore.'], 'Ce te apasă cel mai tare acum?')
```

## Slovenčina (`sk`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Počujem ťa a ďakujem, že si mi to povedal/a.', ['V Thajsku volaj 1323 (duševné zdravie, nonstop). Ak si v nebezpečenstve teraz: 1669.', 'Nezostávaj sám/sama — povedz človeku, ktorému veríš, že ti nie je dobre.', 'Slovensko: Linka dôvery 0800 500 333 · tiesňová linka 112 · inde: findahelpline.com'], 'Si teraz v bezpečí?')
```

**medical**

```text
('Je to naliehavé — najprv volaj.', ['Volaj hneď 1669 (Thajsko) · 155 alebo 112 na Slovensku. Povedz adresu a príznaky.', 'Ak nedýcha alebo nereaguje: stláčaj silno stred hrudníka 100–120-krát za minútu.', 'Nedávaj vodu ani jedlo. Odlož obal od lieku pre lekára.'], 'Je teraz niekto pri tom človeku?')
```

**violence**

```text
('Nie je to tvoja vina. Zaslúžiš si byť v bezpečí.', ['Ak si v nebezpečenstve teraz: 191 (thajská polícia) · 158 alebo 112 na Slovensku.', 'Choď najprv na bezpečné miesto: k susedom, k priateľom, medzi ľudí.', 'Odlož fotky zranení a správy ako dôkaz. Slovensko: linka pre ženy 0800 212 212.'], 'Si teraz v bezpečí?')
```

**help**

```text
('Som tu. Povedz mi, čo sa deje.', ['Nebezpečenstvo alebo zranenie teraz: 1669 (zdravotné) · 191 (polícia) v Thajsku · 112.', 'Napíš jednou vetou, čo sa stalo.', 'Ak môžeš, choď medzi iných ľudí.'], 'Kde teraz si a je s tebou niekto?')
```

**general**

```text
('Poďme na to krok za krokom.', ['Napíš jednou vetou, o čo naozaj ide.', 'Spíš, čo môžeš urobiť dnes, aj keď je to niečo malé.', 'Vyber jediný krok na nasledujúcich 24 hodín.'], 'Čo ťa teraz najviac ťaží?')
```

## Soomaali (`so`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Waan ku maqlayaa, waadna ku mahadsan tahay inaad ii sheegtay.', ['Haddii aad joogto Thailand, wac 1323 (caafimaadka maskaxda, 24 saac). Haddii aad halis ku jirto hadda: 1669.', 'Ha keligaa joogin — u sheeg qof aad aaminsan tahay inaadan fiicnayn.', 'Waddamada kale: wac lambarka degdegga ee deegaanka ama eeg findahelpline.com'], 'Ma ammaan baad tahay hadda?')
```

**medical**

```text
('Tani waa xaalad degdeg ah — marka hore wac.', ['Wac 1669 hadda (Thailand) ama lambarka ambalaaska ee deegaanka. Sheeg cinwaanka iyo calaamadaha.', 'Haddii uusan neefsanayn ama uusan jawaabin: si xoog leh u riix bartamaha laabta, 100–120 jeer daqiiqaddii.', 'Ha siin biyo ama cunto. Kaydi baakadda daawada si dhakhtarku u arko.'], 'Ma jiraa qof la jooga bukaanka hadda?')
```

**violence**

```text
('Qaladkaagu ma aha. Waxaad mudan tahay inaad ammaan ahaato.', ['Haddii aad halis ku jirto hadda: 191 (booliska Thailand).', 'Marka hore aad meel ammaan ah: deriskaaga, guriga saaxiib, ama meel dad joogaan.', 'Kaydi sawirrada dhaawaca iyo fariimaha si ay caddayn u noqdaan. Caawimaad 24 saac ah oo Thailand ah: 1300.'], 'Ma ammaan baad tahay hadda?')
```

**help**

```text
('Halkan ayaan joogaa. Ii sheeg waxa dhacaya.', ['Halis ama dhaawac hadda: 1669 (caafimaad) · 191 (booliis) Thailand.', 'Hal weedh ku qor waxa dhacay.', 'Haddii aad awooddo, u dhowow dad kale.'], 'Halkee joogtaa hadda, qof ma kula jiraa?')
```

**general**

```text
('Aan tallaabo tallaabo u qaadno.', ['Hal weedh ku qor waxa dhab ahaan dhacaya.', 'Qor waxa aad maanta samayn karto, xitaa wax yar.', 'Dooro hal tallaabo oo keliya 24-ka saac ee soo socda.'], 'Maxaa sida ugu badan kuu culeysiinaya hadda?')
```

## Suomi (`fi`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Kuulen sinua, ja kiitos että kerroit.', ['Thaimaassa soita 1323 (mielenterveys, 24 h). Jos olet vaarassa nyt: 1669.', 'Älä jää yksin — kerro jollekulle, johon luotat, ettet voi hyvin.', 'Suomi: Kriisipuhelin 09 2525 0111 · hätänumero 112 · muualla: findahelpline.com'], 'Oletko nyt turvassa?')
```

**medical**

```text
('Tämä on hätätilanne — soita ensin.', ['Soita heti 1669 (Thaimaa) · 112 Suomessa. Kerro osoite ja oireet.', 'Jos hän ei hengitä tai ei reagoi: paina lujaa rintakehän keskeltä 100–120 kertaa minuutissa.', 'Älä anna vettä tai ruokaa. Säilytä lääkepakkaus lääkäriä varten.'], 'Onko joku nyt hänen luonaan?')
```

**violence**

```text
('Se ei ole sinun syysi. Ansaitset olla turvassa.', ['Jos olet vaarassa nyt: 191 (Thaimaan poliisi) · 112 Suomessa.', 'Mene ensin turvalliseen paikkaan: naapuriin, ystävälle, ihmisten pariin.', 'Säilytä kuvat vammoista ja viestit todisteiksi. Suomi: Nollalinja 080 005 005.'], 'Oletko nyt turvassa?')
```

**help**

```text
('Olen tässä. Kerro, mitä tapahtuu.', ['Vaara tai vamma nyt: 1669 (ensiapu) · 191 (poliisi) Thaimaassa · 112.', 'Kirjoita yhdellä lauseella, mitä tapahtui.', 'Jos pystyt, mene muiden ihmisten luo.'], 'Missä olet nyt, ja onko joku kanssasi?')
```

**general**

```text
('Otetaan tämä askel kerrallaan.', ['Kirjoita yhdellä lauseella, mistä on oikeasti kyse.', 'Listaa, mitä voit tehdä tänään, vaikka jotain pientä.', 'Valitse yksi askel seuraaville 24 tunnille.'], 'Mikä painaa sinua eniten juuri nyt?')
```

## Svenska (`sv`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Jag hör dig, och tack för att du berättar.', ['I Thailand: ring 1323 (psykisk hälsa, dygnet runt). Om du är i fara nu: 1669.', 'Var inte ensam — berätta för någon du litar på att du inte mår bra.', 'Sverige: Självmordslinjen 90101 · nödnummer 112 · andra länder: findahelpline.com'], 'Är du i säkerhet just nu?')
```

**medical**

```text
('Det här är ett nödläge — ring först.', ['Ring 1669 nu (Thailand) · 112 i Europa. Säg adressen och symtomen.', 'Om personen inte andas eller inte svarar: tryck hårt mitt på bröstet, 100–120 gånger per minut.', 'Ge inte vatten eller mat. Spara förpackningen till läkemedlet åt läkaren.'], 'Är någon hos personen just nu?')
```

**violence**

```text
('Det är inte ditt fel. Du förtjänar att vara trygg.', ['Om du är i fara nu: 191 (polisen i Thailand) · 112 i Europa.', 'Gå först till en säker plats: en granne, vänner, en plats med folk.', 'Spara bilder på skador och meddelanden som bevis. Sverige: Kvinnofridslinjen 020-50 50 50.'], 'Är du i säkerhet nu?')
```

**help**

```text
('Jag är här. Berätta vad som händer.', ['Fara eller skada nu: 1669 (sjukvård) · 191 (polis) i Thailand · 112.', 'Skriv i en mening vad som hände.', 'Om du kan, gå till andra människor.'], 'Var är du nu, och är någon med dig?')
```

**general**

```text
('Vi tar det steg för steg.', ['Skriv i en mening vad det egentligen handlar om.', 'Skriv ner vad du kan göra i dag, även något litet.', 'Välj ett enda steg för de kommande 24 timmarna.'], 'Vad tynger dig mest just nu?')
```

## Tagalog (`tl`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Naririnig kita, at salamat sa pagsasabi mo sa akin.', ['Sa Thailand, tumawag sa 1323 (mental health, 24 oras). Kung nasa panganib ka ngayon, tumawag agad sa 1669.', 'Huwag kang mag-isa. Sabihin sa isang taong pinagkakatiwalaan mo na hindi ka okay.', 'Kung nasa labas ng Thailand, maghanap ng hotline sa findahelpline.com (Pilipinas: NCMH 1553).'], 'Ligtas ka ba ngayon?')
```

**medical**

```text
('Emergency ito — tumawag muna.', ['Tumawag sa 1669 ngayon (sa Pilipinas: 911), sabihin ang address at mga sintomas.', 'Kung hindi humihinga o hindi tumutugon: diinan nang malakas ang gitna ng dibdib, 100–120 beses kada minuto, sundin ang operator sa telepono.', 'Huwag painumin o pakainin. Itago ang lalagyan ng gamot na ininom para maipakita sa doktor.'], 'May kasama ba ang pasyente ngayon?')
```

**violence**

```text
('Hindi mo ito kasalanan. Karapat-dapat kang maging ligtas.', ['Kung nasa panganib ka ngayon, tumawag sa 191 (pulis sa Thailand; sa Pilipinas: 911).', 'Pumunta muna sa ligtas na lugar: kapitbahay, bahay ng kaibigan, o lugar na maraming tao.', 'Pwede kang tumawag sa 1300 (tulong panlipunan, 24 oras). Itago ang mga litrato ng sugat at mga mensahe bilang ebidensya.'], 'Ligtas ka ba ngayon?')
```

**help**

```text
('Nandito ako. Sabihin mo kung ano ang nangyayari.', ['Kung may panganib o sugatan ngayon: 1669 (medikal) · 191 (pulis)', 'Isulat sa isang pangungusap kung ano ang nangyari.', 'Kung kaya, lumapit sa ibang tao.'], 'Nasaan ka ngayon, at may kasama ka ba?')
```

## Tiếng Việt (`vi`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Mình nghe bạn, và cảm ơn bạn đã nói ra.', ['Ở Thái Lan, gọi 1323 (sức khỏe tâm thần, 24 giờ). Nếu đang gặp nguy hiểm, gọi ngay 1669.', 'Đừng ở một mình. Hãy nói với một người bạn tin tưởng rằng bạn đang không ổn.', 'Nếu ở ngoài Thái Lan, tìm đường dây hỗ trợ tại findahelpline.com (Việt Nam: cấp cứu 115).'], 'Bây giờ bạn có đang an toàn không?')
```

**medical**

```text
('Đây là tình huống khẩn cấp — hãy gọi điện trước.', ['Gọi ngay 1669 (ở Việt Nam: 115), nói rõ địa chỉ và triệu chứng.', 'Nếu không thở hoặc gọi không tỉnh: ấn mạnh giữa ngực 100–120 lần/phút, làm theo hướng dẫn qua điện thoại.', 'Không cho uống nước hay ăn. Giữ lại vỏ thuốc đã uống để cho bác sĩ xem.'], 'Bây giờ có ai ở cạnh người bệnh không?')
```

**violence**

```text
('Đây không phải lỗi của bạn. Bạn xứng đáng được an toàn.', ['Nếu đang nguy hiểm, gọi ngay 191 (cảnh sát Thái Lan; ở Việt Nam: 113).', 'Đến nơi an toàn trước: hàng xóm, nhà bạn bè, hoặc nơi đông người.', 'Có thể gọi 1300 (hỗ trợ xã hội 24 giờ). Giữ ảnh vết thương và tin nhắn làm bằng chứng.'], 'Bây giờ bạn có an toàn không?')
```

**help**

```text
('Mình ở đây. Hãy kể cho mình chuyện gì đang xảy ra.', ['Nếu đang nguy hiểm hoặc bị thương: 1669 (cấp cứu) · 191 (cảnh sát)', 'Viết một câu ngắn kể chuyện gì đã xảy ra.', 'Nếu được, hãy đến gần những người khác.'], 'Bạn đang ở đâu, có ai ở cùng không?')
```

## Türkçe (`tr`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Seni duyuyorum, anlattığın için teşekkür ederim.', ["Tayland'daysan 1323'ü (ruh sağlığı, 24 saat) ara. Şu an tehlikedeysen hemen 1669'u ara.", 'Yalnız kalma. Güvendiğin birine iyi olmadığını söyle.', "Tayland dışındaysan findahelpline.com'dan yardım hattı bul (Türkiye: 112)."], 'Şu an güvende misin?')
```

**medical**

```text
('Bu bir acil durum — önce ara.', ["Hemen 1669'u ara (Türkiye'de: 112), adresi ve belirtileri söyle.", 'Nefes almıyorsa veya tepki vermiyorsa: göğsün ortasına dakikada 100–120 kez güçlüce bastır, telefondaki görevlinin talimatlarını izle.', 'Su ya da yiyecek verme. İçtiği ilacın kutusunu doktora göstermek için sakla.'], 'Şu an hastanın yanında biri var mı?')
```

**violence**

```text
('Bu senin suçun değil. Güvende olmayı hak ediyorsun.', ["Şu an tehlikedeysen 191'i (Tayland polisi; Türkiye'de: 112) ara.", 'Önce güvenli bir yere git: komşu, arkadaş evi ya da kalabalık bir yer.', "1300'ü (sosyal yardım, 24 saat) arayabilirsin. Yaraların fotoğraflarını ve mesajları kanıt olarak sakla."], 'Şu an güvende misin?')
```

**help**

```text
('Buradayım. Ne olduğunu anlat.', ['Şu an tehlike veya yaralanma varsa: 1669 (sağlık) · 191 (polis)', 'Ne olduğunu tek cümleyle yaz.', 'Mümkünse başka insanların yanına git.'], 'Şu an neredesin, yanında biri var mı?')
```

## Yorùbá (`yo`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Mo gbọ́ ọ, ẹ ṣé tí o sọ fún mi.', ['Ní Thailand, pe 1323 (ìlera ọpọlọ, wákàtí 24). Tí o bá wà nínú ewu báyìí: 1669.', 'Má ṣe dá wà — sọ fún ẹnì kan tí o fọkàn tán pé ara rẹ kò yá.', 'Nàìjíríà: 112 · àwọn orílẹ̀-èdè mìíràn: findahelpline.com'], 'Ṣé o wà láìléwu báyìí?')
```

**medical**

```text
('Pàjáwìrì ni èyí — kọ́kọ́ pe fóònù.', ['Pe 1669 báyìí (Thailand) · Nàìjíríà 112. Sọ àdírẹ́sì àti àmì àìsàn.', 'Tí kò bá ń mí tàbí kò dáhùn: tẹ àárín àyà ní agbára, ìgbà 100–120 ní ìṣẹ́jú kan.', 'Má fún un ní omi tàbí oúnjẹ. Pa àpò oògùn mọ́ fún dókítà.'], 'Ṣé ẹnì kan wà pẹ̀lú aláìsàn náà báyìí?')
```

**violence**

```text
('Kì í ṣe ẹ̀bi rẹ. O yẹ láti wà láìléwu.', ['Tí o bá wà nínú ewu báyìí: 191 (ọlọ́pàá Thailand) · Nàìjíríà 112.', 'Kọ́kọ́ lọ sí ibi tí ó ní ààbò: aládùúgbò, ilé ọ̀rẹ́, tàbí ibi tí èèyàn wà.', 'Pa fọ́tò ọgbẹ́ àti àwọn ìfiránṣẹ́ mọ́ gẹ́gẹ́ bí ẹ̀rí. Ìrànlọ́wọ́ wákàtí 24 ní Thailand: 1300.'], 'Ṣé o wà láìléwu báyìí?')
```

**help**

```text
('Mo wà níbí. Sọ ohun tó ń ṣẹlẹ̀ fún mi.', ['Ewu tàbí ọgbẹ́ báyìí: 1669 (ìlera) · 191 (ọlọ́pàá) ní Thailand · Nàìjíríà 112.', 'Kọ ohun tó ṣẹlẹ̀ ní gbólóhùn kan.', 'Tí o bá lè ṣe é, lọ sí ọ̀dọ̀ àwọn èèyàn mìíràn.'], 'Níbo ni o wà báyìí, ṣé ẹnì kan wà pẹ̀lú rẹ?')
```

**general**

```text
('Jẹ́ ká ṣe é ní ìgbésẹ̀ kọ̀ọ̀kan.', ['Kọ ohun tó ń ṣẹlẹ̀ gan-an ní gbólóhùn kan.', 'Kọ ohun tí o lè ṣe lónìí sílẹ̀, kódà tó bá kéré.', 'Yan ìgbésẹ̀ kan ṣoṣo fún wákàtí 24 tó ń bọ̀.'], 'Kí ló ń dà ọ́ láàmú jù lọ báyìí?')
```

## isiZulu (`zu`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Ngiyakuzwa, futhi ngiyabonga ngokungitshela.', ['E-Thailand shayela u-1323 (impilo yengqondo, amahora angu-24). Uma usengozini manje: 1669.', 'Ungahlali wedwa — tshela umuntu omethembayo ukuthi awukho kahle.', 'eNingizimu Afrika: SADAG 0800 567 567 · amaphoyisa 10111 · amanye amazwe: findahelpline.com'], 'Ingabe uphephile manje?')
```

**medical**

```text
('Lesi yisimo esiphuthumayo — shayela kuqala.', ['Shayela u-1669 manje (Thailand) · eNingizimu Afrika 10177 noma 112. Sho ikheli nezimpawu.', 'Uma engaphefumuli noma engaphenduli: cindezela phakathi nesifuba ngamandla, izikhathi ezingu-100–120 ngomzuzu.', 'Ungamniki amanzi noma ukudla. Gcina iphakethe lomuthi ukuze udokotela alibone.'], 'Ingabe kukhona umuntu nesiguli manje?')
```

**violence**

```text
('Akulona iphutha lakho. Ufanelwe ukuphepha.', ['Uma usengozini manje: 191 (amaphoyisa aseThailand) · eNingizimu Afrika 10111.', 'Qala uye endaweni ephephile: kumakhelwane, kumngane, noma lapho kunabantu khona.', 'Gcina izithombe zokulimala nemilayezo njengobufakazi. eNingizimu Afrika: GBV Command Centre 0800 428 428.'], 'Ingabe uphephile manje?')
```

**help**

```text
('Ngilapha. Ngitshele ukuthi kwenzekani.', ['Ingozi noma ukulimala manje: 1669 (ezempilo) · 191 (amaphoyisa) e-Thailand · eNingizimu Afrika 10111.', 'Bhala ngomusho owodwa ukuthi kwenzekeni.', 'Uma ukwazi, sondela kwabanye abantu.'], 'Ukuphi manje, futhi ingabe ukhona umuntu nawe?')
```

**general**

```text
('Masithathe isinyathelo esisodwa ngesikhathi.', ['Bhala ngomusho owodwa ukuthi kwenzekani ngempela.', 'Bhala lokho ongakwenza namuhla, ngisho kuncane.', 'Khetha isinyathelo esisodwa sezinsuku ezingu-24 ezizayo.'], 'Yini ekukhathaza kakhulu manje?')
```

## Čeština (`cs`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Slyším tě a děkuji, že jsi mi to řekl/a.', ['V Thajsku volej 1323 (duševní zdraví, nonstop). Pokud jsi v nebezpečí teď: 1669.', 'Nezůstávej sám/sama — řekni člověku, kterému věříš, že ti není dobře.', 'Česko: Linka první psychické pomoci 116 123 · tísňová linka 112 · jinde: findahelpline.com'], 'Jsi teď v bezpečí?')
```

**medical**

```text
('Je to naléhavé — nejdřív volej.', ['Volej hned 1669 (Thajsko) · 155 nebo 112 v Česku. Řekni adresu a příznaky.', 'Pokud nedýchá nebo nereaguje: stlačuj silně střed hrudníku 100–120krát za minutu.', 'Nedávej vodu ani jídlo. Schovej obal od léku pro lékaře.'], 'Je teď někdo u toho člověka?')
```

**violence**

```text
('Není to tvoje vina. Zasloužíš si být v bezpečí.', ['Pokud jsi v nebezpečí teď: 191 (thajská policie) · 158 nebo 112 v Česku.', 'Jdi nejdřív na bezpečné místo: k sousedům, k přátelům, mezi lidi.', 'Uschovej fotky zranění a zprávy jako důkaz. Česko: Bílý kruh bezpečí 116 006.'], 'Jsi teď v bezpečí?')
```

**help**

```text
('Jsem tady. Řekni mi, co se děje.', ['Nebezpečí nebo zranění teď: 1669 (zdravotní) · 191 (policie) v Thajsku · 112.', 'Napiš jednou větou, co se stalo.', 'Jestli můžeš, jdi mezi jiné lidi.'], 'Kde teď jsi a je s tebou někdo?')
```

**general**

```text
('Vezmeme to krok za krokem.', ['Napiš jednou větou, o co doopravdy jde.', 'Sepiš, co můžeš udělat dnes, i když je to něco malého.', 'Vyber jediný krok na příštích 24 hodin.'], 'Co tě teď nejvíc tíží?')
```

## Ελληνικά (`el`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Σε ακούω, και σε ευχαριστώ που μου το είπες.', ['Στην Ταϊλάνδη κάλεσε το 1323 (ψυχική υγεία, 24 ώρες). Αν κινδυνεύεις τώρα: 1669.', 'Μη μείνεις μόνος/μόνη — πες σε έναν άνθρωπο που εμπιστεύεσαι ότι δεν είσαι καλά.', 'Ελλάδα: γραμμή παρέμβασης για την αυτοκτονία 1018 · έκτακτη ανάγκη 112 · αλλού: findahelpline.com'], 'Είσαι ασφαλής αυτή τη στιγμή;')
```

**medical**

```text
('Είναι επείγον — τηλεφώνησε πρώτα.', ['Κάλεσε τώρα το 1669 (Ταϊλάνδη) · 112 ή ΕΚΑΒ 166 στην Ελλάδα. Πες τη διεύθυνση και τα συμπτώματα.', 'Αν δεν αναπνέει ή δεν αντιδρά: πίεσε δυνατά στο κέντρο του στήθους, 100–120 φορές το λεπτό.', 'Μη δώσεις νερό ή φαγητό. Κράτα τη συσκευασία του φαρμάκου για τον γιατρό.'], 'Είναι κάποιος με τον άνθρωπο αυτή τη στιγμή;')
```

**violence**

```text
('Δεν φταις εσύ. Αξίζεις να είσαι ασφαλής.', ['Αν κινδυνεύεις τώρα: 191 (αστυνομία Ταϊλάνδης) · 100 ή 112 στην Ελλάδα.', 'Πήγαινε πρώτα κάπου ασφαλές: σε γείτονα, σε φίλους, σε μέρος με κόσμο.', 'Κράτα φωτογραφίες τραυμάτων και μηνύματα ως αποδείξεις. Ελλάδα: γραμμή SOS 15900.'], 'Είσαι ασφαλής τώρα;')
```

**help**

```text
('Είμαι εδώ. Πες μου τι συμβαίνει.', ['Κίνδυνος ή τραυματισμός τώρα: 1669 (ιατρικό) · 191 (αστυνομία) στην Ταϊλάνδη · 112.', 'Γράψε σε μία πρόταση τι έγινε.', 'Αν μπορείς, πήγαινε κοντά σε άλλους ανθρώπους.'], 'Πού είσαι τώρα, και είναι κάποιος μαζί σου;')
```

**general**

```text
('Ας το πάρουμε βήμα βήμα.', ['Γράψε σε μία πρόταση τι πραγματικά συμβαίνει.', 'Κατέγραψε τι μπορείς να κάνεις σήμερα, ακόμα και κάτι μικρό.', 'Διάλεξε ένα μόνο βήμα για τις επόμενες 24 ώρες.'], 'Τι σε βαραίνει περισσότερο αυτή τη στιγμή;')
```

## Български (`bg`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Чувам те и благодаря, че ми каза.', ['В Тайланд се обади на 1323 (психично здраве, денонощно). Ако си в опасност сега: 1669.', 'Не оставай сам/сама — кажи на човек, на когото имаш доверие, че не си добре.', 'България: спешен телефон 112 · други държави: findahelpline.com'], 'В безопасност ли си сега?')
```

**medical**

```text
('Това е спешно — първо се обади.', ['Обади се сега на 1669 (Тайланд) · 112 в България. Кажи адреса и симптомите.', 'Ако не диша или не реагира: натискай силно в средата на гърдите, 100–120 пъти в минута.', 'Не давай вода или храна. Запази опаковката на лекарството за лекаря.'], 'Има ли някой при човека сега?')
```

**violence**

```text
('Не е твоя вината. Заслужаваш да си в безопасност.', ['Ако си в опасност сега: 191 (тайландска полиция) · 112 в България.', 'Първо отиди на безопасно място: при съсед, приятели, където има хора.', 'Запази снимки на нараняванията и съобщенията като доказателство. Помощ в Тайланд 24 ч: 1300.'], 'В безопасност ли си сега?')
```

**help**

```text
('Тук съм. Кажи ми какво се случва.', ['Опасност или нараняване сега: 1669 (медицинска) · 191 (полиция) в Тайланд · 112.', 'Напиши с едно изречение какво се случи.', 'Ако можеш, отиди при други хора.'], 'Къде си сега и има ли някой с теб?')
```

**general**

```text
('Нека да го вземем стъпка по стъпка.', ['Напиши с едно изречение за какво всъщност става дума.', 'Запиши какво можеш да направиш днес, дори нещо малко.', 'Избери само една стъпка за следващите 24 часа.'], 'Какво те тежи най-много сега?')
```

## Монгол (`mn`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Би таныг сонсож байна, хэлсэнд баярлалаа.', ['Тайландад 1323 (сэтгэцийн эрүүл мэнд, 24 цаг) руу залгаарай. Одоо аюулд байвал: 1669.', 'Ганцаараа бүү бай — итгэдэг нэг хүндээ сайнгүй байгаагаа хэлээрэй.', 'Монголд: түргэн тусламж 103 · цагдаа 102 · бусад улсад: findahelpline.com'], 'Та яг одоо аюулгүй байна уу?')
```

**medical**

```text
('Энэ яаралтай байдал — эхлээд залгаарай.', ['Одоо 1669 руу залга (Тайланд) · Монголд 103. Хаяг, шинж тэмдгийг хэл.', 'Амьсгалахгүй эсвэл хариу өгөхгүй бол: цээжний голыг минутад 100–120 удаа хүчтэй дар.', 'Ус, хоол бүү өг. Уусан эмийн хайрцгийг эмчид үзүүлэхээр хадгал.'], 'Одоо өвчтөний дэргэд хэн нэгэн байна уу?')
```

**violence**

```text
('Энэ таны буруу биш. Та аюулгүй байх ёстой.', ['Одоо аюулд байвал: 191 (Тайландын цагдаа) · Монголд 102.', 'Эхлээд аюулгүй газар оч: хөрш, найзын гэр, хүн олонтой газар.', 'Гэмтлийн зураг, мессежүүдээ нотлох баримт болгон хадгал. Тайландад 24 цагийн тусламж: 1300.'], 'Та одоо аюулгүй байна уу?')
```

**help**

```text
('Би энд байна. Юу болж байгааг хэлээрэй.', ['Одоо аюул эсвэл гэмтэл байвал: 1669 (эмнэлэг) · 191 (цагдаа) Тайландад · Монголд 103/102.', 'Юу болсныг нэг өгүүлбэрээр бич.', 'Боломжтой бол бусад хүмүүсийн дэргэд оч.'], 'Та одоо хаана байна, хажууд тань хэн нэгэн байна уу?')
```

**general**

```text
('Алхам алхмаар авч үзье.', ['Юу болж байгааг нэг өгүүлбэрээр бич.', 'Өнөөдөр хийж чадах зүйлсээ жагсаа, жижиг ч байсан.', 'Дараагийн 24 цагт хийх ганц алхмыг сонго.'], 'Одоо таныг хамгийн их юу дарамталж байна вэ?')
```

## Русский (`ru`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Я слышу вас, спасибо, что рассказали.', ['В Таиланде звоните 1323 (психологическая помощь, круглосуточно). Если опасность сейчас — 1669.', 'Не оставайтесь одни — скажите человеку, которому доверяете, что вам плохо.', 'Россия: 112 · телефон доверия 8-800-2000-122 · другие страны: findahelpline.com'], 'Вы сейчас в безопасности?')
```

**medical**

```text
('Это экстренная ситуация — сначала позвоните.', ['Звоните 1669 сейчас (Таиланд) · 112 в России и Европе. Назовите адрес и симптомы.', 'Если не дышит или не реагирует: сильно надавливайте на центр груди, 100–120 раз в минуту.', 'Не давайте воду и еду. Сохраните упаковку лекарства для врача.'], 'Кто-то сейчас рядом с человеком?')
```

**violence**

```text
('Это не ваша вина. Вы имеете право на безопасность.', ['Если опасность сейчас: 191 (полиция Таиланда) · 112 в России и Европе.', 'Сначала уйдите в безопасное место: к соседям, друзьям, туда, где есть люди.', 'Сохраните фото травм и сообщения как доказательства. Помощь в Таиланде 24 ч: 1300.'], 'Вы сейчас в безопасности?')
```

**help**

```text
('Я здесь. Расскажите, что происходит.', ['Опасность или травма сейчас: 1669 (скорая) · 191 (полиция) в Таиланде · 112.', 'Напишите одним предложением, что случилось.', 'Если можете, идите туда, где есть другие люди.'], 'Где вы сейчас, и есть ли кто-то рядом?')
```

**general**

```text
('Давайте разберёмся шаг за шагом.', ['Напишите одним предложением, что на самом деле происходит.', 'Перечислите, что можно сделать сегодня — даже что-то маленькое.', 'Выберите одно действие на ближайшие 24 часа.'], 'Что сейчас тяготит вас больше всего?')
```

## Українська (`uk`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Я чую вас, дякую, що розповіли.', ['У Таїланді телефонуйте 1323 (психологічна допомога, цілодобово). Якщо небезпека зараз — 1669.', 'Не залишайтеся на самоті — скажіть людині, якій довіряєте, що вам погано.', 'Україна: 112 · Lifeline Ukraine 7333 · інші країни: findahelpline.com'], 'Ви зараз у безпеці?')
```

**medical**

```text
('Це невідкладна ситуація — спершу зателефонуйте.', ['Телефонуйте 1669 зараз (Таїланд) · 103 або 112 в Україні. Назвіть адресу й симптоми.', 'Якщо не дихає або не реагує: сильно натискайте на центр грудей, 100–120 разів на хвилину.', 'Не давайте води чи їжі. Збережіть упаковку ліків для лікаря.'], 'Хтось зараз поруч із людиною?')
```

**violence**

```text
('Це не ваша провина. Ви маєте право на безпеку.', ['Якщо небезпека зараз: 191 (поліція Таїланду) · 102 або 112 в Україні.', 'Спершу йдіть у безпечне місце: до сусідів, друзів, туди, де є люди.', 'Збережіть фото травм і повідомлення як докази. Допомога в Таїланді 24 год: 1300.'], 'Ви зараз у безпеці?')
```

**help**

```text
('Я тут. Розкажіть, що відбувається.', ['Небезпека чи травма зараз: 1669 (швидка) · 191 (поліція) в Таїланді · 112.', 'Напишіть одним реченням, що сталося.', 'Якщо можете, підіть туди, де є інші люди.'], 'Де ви зараз, і чи є хтось поруч?')
```

**general**

```text
('Розберімося крок за кроком.', ['Напишіть одним реченням, що насправді відбувається.', 'Перелічіть, що можна зробити сьогодні — навіть щось маленьке.', 'Оберіть одну дію на найближчі 24 години.'], 'Що вас зараз найбільше гнітить?')
```

## Қазақ (`kk`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Мен сізді тыңдап отырмын, айтқаныңызға рахмет.', ['Таиландта 1323 нөміріне қоңырау шалыңыз (психикалық денсаулық, тәулік бойы). Қазір қауіп болса: 1669.', 'Жалғыз қалмаңыз — сенетін бір адамға өзіңізді жаман сезініп жүргеніңізді айтыңыз.', 'Қазақстанда: 112 · жедел жәрдем 103 · басқа елдерде: findahelpline.com'], 'Сіз қазір қауіпсізсіз бе?')
```

**medical**

```text
('Бұл шұғыл жағдай — алдымен қоңырау шалыңыз.', ['Қазір 1669 нөміріне қоңырау шалыңыз (Таиланд) · Қазақстанда 103 немесе 112. Мекенжай мен белгілерді айтыңыз.', 'Тыныс алмаса немесе жауап бермесе: кеуденің ортасын минутына 100–120 рет қатты басыңыз.', 'Су не тамақ бермеңіз. Ішкен дәрінің қорабын дәрігерге көрсету үшін сақтаңыз.'], 'Қазір науқастың жанында біреу бар ма?')
```

**violence**

```text
('Бұл сіздің кінәңіз емес. Сіз қауіпсіз болуға лайықсыз.', ['Қазір қауіп болса: 191 (Таиланд полициясы) · Қазақстанда 102 немесе 112.', 'Алдымен қауіпсіз жерге барыңыз: көршіге, достарыңызға, адам көп жерге.', 'Жарақат суреттері мен хабарламаларды дәлел ретінде сақтаңыз. Таиландта тәулік бойы көмек: 1300.'], 'Сіз қазір қауіпсізсіз бе?')
```

**help**

```text
('Мен осындамын. Не болып жатқанын айтыңыз.', ['Қазір қауіп не жарақат болса: 1669 (медициналық) · 191 (полиция) Таиландта · Қазақстанда 112.', 'Не болғанын бір сөйлеммен жазыңыз.', 'Мүмкін болса, басқа адамдардың қасына барыңыз.'], 'Қазір қайдасыз, қасыңызда біреу бар ма?')
```

**general**

```text
('Қадам-қадаммен қарастырайық.', ['Не болып жатқанын бір сөйлеммен жазыңыз.', 'Бүгін не істей алатыныңызды жазыңыз, кішкентай болса да.', 'Келесі 24 сағатқа бір ғана қадам таңдаңыз.'], 'Қазір сізді ең көп не мазалап тұр?')
```

## Հայերեն (`hy`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('Լսում եմ քեզ, և շնորհակալ եմ, որ ասացիր։', ['Թաիլանդում զանգիր 1323 (հոգեկան առողջություն, շուրջօրյա)։ Եթե հիմա վտանգի մեջ ես՝ 1669։', 'Մենակ մի մնա — ասա մեկին, ում վստահում ես, որ լավ չես։', 'Հայաստան՝ 911 կամ 112 · այլ երկրներում՝ findahelpline.com'], 'Հիմա ապահո՞վ ես։')
```

**medical**

```text
('Սա շտապ դեպք է — նախ զանգիր։', ['Զանգիր հիմա 1669 (Թաիլանդ) · 911 Հայաստանում։ Ասա հասցեն և ախտանիշները։', 'Եթե չի շնչում կամ չի արձագանքում՝ ուժեղ սեղմիր կրծքավանդակի մեջտեղը, րոպեում 100–120 անգամ։', 'Ջուր կամ ուտելիք մի տուր։ Պահիր դեղի տուփը բժշկի համար։'], 'Հիմա ինչ-որ մեկը կա՞ հիվանդի կողքին։')
```

**violence**

```text
('Սա քո մեղքը չէ։ Դու արժանի ես ապահով լինելու։', ['Եթե հիմա վտանգի մեջ ես՝ 191 (Թաիլանդի ոստիկանություն) · 911 Հայաստանում։', 'Նախ գնա ապահով տեղ՝ հարևանի, ընկերների մոտ կամ մարդաշատ վայր։', 'Պահիր վնասվածքների լուսանկարները և հաղորդագրությունները որպես ապացույց։ Թաիլանդում շուրջօրյա օգնություն՝ 1300։'], 'Հիմա ապահո՞վ ես։')
```

**help**

```text
('Ես այստեղ եմ։ Ասա, թե ինչ է կատարվում։', ['Վտանգ կամ վնասվածք հիմա՝ 1669 (բժշկական) · 191 (ոստիկանություն) Թաիլանդում · 911։', 'Մեկ նախադասությամբ գրիր, թե ինչ պատահեց։', 'Եթե կարող ես, գնա ուրիշ մարդկանց մոտ։'], 'Որտե՞ղ ես հիմա, և ինչ-որ մեկը կա՞ քեզ հետ։')
```

**general**

```text
('Եկ քայլ առ քայլ նայենք։', ['Մեկ նախադասությամբ գրիր, թե իրականում ինչ է կատարվում։', 'Գրիր, թե ինչ կարող ես անել այսօր, թեկուզ փոքր բան։', 'Ընտրիր միայն մեկ քայլ հաջորդ 24 ժամվա համար։'], 'Ի՞նչն է քեզ հիմա ամենաշատը ծանրացնում։')
```

## עברית (`he`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('אני שומעת אותך, ותודה שסיפרת לי.', ['בתאילנד התקשרו ל־1323 (בריאות הנפש, 24 שעות). אם יש סכנה עכשיו: 1669.', 'אל תישארו לבד — ספרו לאדם שאתם סומכים עליו שלא טוב לכם.', 'בישראל: ער״ן 1201 · מד״א 101 · במדינות אחרות: findahelpline.com'], 'האם אתם בטוחים עכשיו?')
```

**medical**

```text
('זה מצב חירום — קודם כול מתקשרים.', ['התקשרו עכשיו ל־1669 (תאילנד) · מד״א 101 בישראל. מסרו כתובת ותסמינים.', 'אם לא נושם או לא מגיב: לחצו חזק במרכז החזה, 100–120 פעמים בדקה.', 'אל תתנו מים או אוכל. שמרו את אריזת התרופה כדי להראות לרופא.'], 'האם מישהו נמצא עכשיו ליד האדם?')
```

**violence**

```text
('זו לא אשמתך. מגיע לך להיות בטוח/ה.', ['אם יש סכנה עכשיו: 191 (משטרת תאילנד) · 100 בישראל.', 'לכו קודם למקום בטוח: שכנים, חברים, מקום שיש בו אנשים.', 'שמרו תמונות של פציעות והודעות כראיה. בישראל: קו חירום לנפגעות אלימות 118.'], 'האם אתם בטוחים עכשיו?')
```

**help**

```text
('אני כאן. ספרו לי מה קורה.', ['סכנה או פציעה עכשיו: 1669 (רפואה) · 191 (משטרה) בתאילנד · 101/100 בישראל.', 'כתבו במשפט אחד מה קרה.', 'אם אפשר, התקרבו לאנשים אחרים.'], 'איפה אתם עכשיו, והאם מישהו איתכם?')
```

**general**

```text
('בואו ניקח את זה צעד אחר צעד.', ['כתבו במשפט אחד מה באמת קורה.', 'רשמו מה אפשר לעשות היום, אפילו משהו קטן.', 'בחרו צעד אחד בלבד ל־24 השעות הקרובות.'], 'מה הכי מכביד עליכם עכשיו?')
```

## اردو (`ur`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('میں آپ کی بات سن رہی ہوں، اور بتانے کا شکریہ۔', ['تھائی لینڈ میں 1323 (ذہنی صحت، 24 گھنٹے) پر کال کریں۔ ابھی خطرہ ہو تو فوراً 1669 پر کال کریں۔', 'اکیلے نہ رہیں۔ کسی بھروسے والے شخص کو بتائیں کہ آپ ٹھیک نہیں ہیں۔', 'تھائی لینڈ سے باہر ہوں تو findahelpline.com پر ہیلپ لائن تلاش کریں (پاکستان: 1122)۔'], 'کیا آپ ابھی محفوظ ہیں؟')
```

**medical**

```text
('یہ ایمرجنسی ہے — پہلے کال کریں۔', ['ابھی 1669 پر کال کریں (پاکستان میں: 1122)، پتہ اور علامات بتائیں۔', 'اگر سانس نہیں لے رہے یا جواب نہیں دے رہے: سینے کے بیچ میں زور سے دبائیں، ایک منٹ میں 100–120 بار، فون پر دی گئی ہدایات پر عمل کریں۔', 'پانی یا کھانا نہ دیں۔ جو دوا لی ہے اس کا پیکٹ ڈاکٹر کو دکھانے کے لیے رکھیں۔'], 'کیا ابھی مریض کے پاس کوئی ہے؟')
```

**violence**

```text
('یہ آپ کی غلطی نہیں ہے۔ آپ کو محفوظ رہنے کا حق ہے۔', ['ابھی خطرہ ہو تو 191 (تھائی پولیس؛ پاکستان میں: 15) پر کال کریں۔', 'پہلے کسی محفوظ جگہ جائیں: پڑوسی، دوست کا گھر، یا جہاں لوگ ہوں۔', '1300 (سماجی مدد، 24 گھنٹے) پر کال کر سکتے ہیں۔ چوٹ کی تصاویر اور پیغامات ثبوت کے طور پر رکھیں۔'], 'کیا آپ ابھی محفوظ ہیں؟')
```

**help**

```text
('میں یہاں ہوں۔ بتائیں کیا ہو رہا ہے۔', ['ابھی خطرہ یا چوٹ ہو تو: 1669 (طبی) · 191 (پولیس)', 'ایک جملے میں لکھیں کہ کیا ہوا۔', 'ہو سکے تو دوسرے لوگوں کے قریب جائیں۔'], 'آپ ابھی کہاں ہیں، اور کیا کوئی آپ کے ساتھ ہے؟')
```

## العربية (`ar`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('أنا أسمعك، وشكرًا لأنك أخبرتني.', ['في تايلاند اتصل بـ 1323 (الصحة النفسية، 24 ساعة). إذا كنت في خطر الآن، اتصل فورًا بـ 1669.', 'لا تبقَ وحدك. أخبر شخصًا تثق به أنك لست بخير.', 'خارج تايلاند ابحث عن خط مساعدة في findahelpline.com.'], 'هل أنت في أمان الآن؟')
```

**medical**

```text
('هذه حالة طارئة — اتصل أولًا.', ['اتصل الآن بـ 1669 وأخبرهم بالعنوان والأعراض.', 'إذا كان لا يتنفس أو لا يستجيب: اضغط بقوة في وسط الصدر 100–120 مرة في الدقيقة، واتبع تعليمات الموظف على الهاتف.', 'لا تعطه ماءً أو طعامًا، واحتفظ بعلبة الدواء الذي تناوله لتريها للطبيب.'], 'هل يوجد أحد مع المريض الآن؟')
```

**violence**

```text
('هذا ليس خطأك. من حقك أن تكون في أمان.', ['إذا كنت في خطر الآن، اتصل بـ 191 (شرطة تايلاند).', 'اذهب أولًا إلى مكان آمن: جار، بيت صديق، أو مكان فيه ناس.', 'يمكنك الاتصال بـ 1300 (المساعدة الاجتماعية، 24 ساعة). احتفظ بصور الإصابات والرسائل كدليل.'], 'هل أنت في أمان الآن؟')
```

**help**

```text
('أنا هنا. أخبرني ماذا يحدث.', ['إذا كان هناك خطر أو إصابة الآن: 1669 (طبي) · 191 (شرطة)', 'اكتب في جملة واحدة ماذا حدث.', 'إن استطعت، اقترب من أشخاص آخرين.'], 'أين أنت الآن، وهل معك أحد؟')
```

## فارسی (`fa`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('حرف شما را می\u200cشنوم و ممنون که گفتید.', ['در تایلند با 1323 (سلامت روان، ۲۴ ساعته) تماس بگیرید. اگر الان در خطر هستید، فوراً با 1669 تماس بگیرید.', 'تنها نمانید. به یک نفر که به او اعتماد دارید بگویید حالتان خوب نیست.', 'اگر بیرون از تایلند هستید، در findahelpline.com خط کمک پیدا کنید (ایران: 1480).'], 'آیا الان در امان هستید؟')
```

**medical**

```text
('این یک وضعیت اورژانسی است — اول تماس بگیرید.', ['همین الان با 1669 تماس بگیرید (در ایران: 115) و آدرس و علائم را بگویید.', 'اگر نفس نمی\u200cکشد یا جواب نمی\u200cدهد: وسط قفسه سینه را محکم فشار دهید، دقیقه\u200cای ۱۰۰ تا ۱۲۰ بار، طبق راهنمایی پشت تلفن.', 'آب یا غذا ندهید. بسته داروی مصرف\u200cشده را برای نشان دادن به پزشک نگه دارید.'], 'الان کسی کنار بیمار هست؟')
```

**violence**

```text
('این تقصیر شما نیست. شما حق دارید در امان باشید.', ['اگر الان در خطر هستید با 191 (پلیس تایلند؛ در ایران: 110) تماس بگیرید.', 'اول به جای امن بروید: همسایه، خانه دوست، یا جای شلوغ.', 'می\u200cتوانید با 1300 (کمک اجتماعی، ۲۴ ساعته) تماس بگیرید. عکس جراحت\u200cها و پیام\u200cها را به عنوان مدرک نگه دارید.'], 'آیا الان در امان هستید؟')
```

**help**

```text
('من اینجا هستم. بگویید چه اتفاقی افتاده.', ['اگر الان در خطر یا زخمی هستید: 1669 (پزشکی) · 191 (پلیس)', 'در یک جمله بنویسید چه شده.', 'اگر می\u200cتوانید، نزدیک آدم\u200cهای دیگر بروید.'], 'الان کجا هستید و کسی با شما هست؟')
```

## नेपाली (`ne`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('म तपाईंको कुरा सुनिरहेको छु, भन्नुभएकोमा धन्यवाद।', ['थाइल्याण्डमा 1323 (मानसिक स्वास्थ्य, २४ घण्टा) मा फोन गर्नुहोस्। अहिले खतरा छ भने तुरुन्तै 1669 मा फोन गर्नुहोस्।', 'एक्लै नबस्नुहोस्। भरोसा लाग्ने एक जनालाई तपाईं ठीक हुनुहुन्न भनेर भन्नुहोस्।', 'थाइल्याण्ड बाहिर हुनुहुन्छ भने findahelpline.com मा हेल्पलाइन खोज्नुहोस् (नेपाल: 1166)।'], 'के तपाईं अहिले सुरक्षित हुनुहुन्छ?')
```

**medical**

```text
('यो आपतकालीन अवस्था हो — पहिले फोन गर्नुहोस्।', ['अहिले नै 1669 मा फोन गर्नुहोस् (नेपालमा: 102), ठेगाना र लक्षण बताउनुहोस्।', 'सास फेरेको छैन वा बोलाउँदा जवाफ दिँदैन भने: छातीको बीचमा बलियोसँग थिच्नुहोस्, मिनेटमा १००–१२० पटक, फोनमा दिइएको निर्देशन मान्नुहोस्।', 'पानी वा खाना नदिनुहोस्। खाएको औषधिको प्याकेट डाक्टरलाई देखाउन राख्नुहोस्।'], 'अहिले बिरामीको साथमा कोही हुनुहुन्छ?')
```

**violence**

```text
('यो तपाईंको गल्ती होइन। तपाईं सुरक्षित रहन योग्य हुनुहुन्छ।', ['अहिले खतरा छ भने 191 (थाइल्याण्ड प्रहरी; नेपालमा: 100) मा फोन गर्नुहोस्।', 'पहिले सुरक्षित ठाउँमा जानुहोस्: छिमेकी, साथीको घर, वा मान्छे धेरै भएको ठाउँ।', '1300 (सामाजिक सहायता, २४ घण्टा) मा फोन गर्न सक्नुहुन्छ। चोटका फोटो र सन्देशहरू प्रमाणको रूपमा राख्नुहोस्।'], 'के तपाईं अहिले सुरक्षित हुनुहुन्छ?')
```

**help**

```text
('म यहाँ छु। के भइरहेको छ भन्नुहोस्।', ['अहिले खतरा वा चोट छ भने: 1669 (मेडिकल) · 191 (प्रहरी)', 'के भयो एक वाक्यमा लेख्नुहोस्।', 'सकिन्छ भने अरू मान्छेको नजिक जानुहोस्।'], 'तपाईं अहिले कहाँ हुनुहुन्छ, साथमा कोही छ?')
```

## हिन्दी (`hi`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('मैं आपकी बात सुन रही हूँ, और बताने के लिए धन्यवाद।', ['थाईलैंड में 1323 (मानसिक स्वास्थ्य, 24 घंटे) पर कॉल करें। अभी खतरा हो तो तुरंत 1669 पर कॉल करें।', 'अकेले न रहें। किसी भरोसेमंद व्यक्ति को बताएँ कि आप ठीक नहीं हैं।', 'थाईलैंड के बाहर हों तो findahelpline.com पर हेल्पलाइन खोजें (भारत: Tele-MANAS 14416)।'], 'क्या आप अभी सुरक्षित हैं?')
```

**medical**

```text
('यह आपातकाल है — पहले कॉल करें।', ['अभी 1669 पर कॉल करें (भारत में: 112), पता और लक्षण बताएँ।', 'अगर साँस नहीं ले रहे या जवाब नहीं दे रहे: छाती के बीच में ज़ोर से दबाएँ, मिनट में 100–120 बार, फ़ोन पर दिए निर्देश मानें।', 'पानी या खाना न दें। जो दवा ली है उसका पैकेट डॉक्टर को दिखाने के लिए रखें।'], 'क्या अभी मरीज़ के पास कोई है?')
```

**violence**

```text
('यह आपकी गलती नहीं है। आपको सुरक्षित रहने का हक़ है।', ['अभी खतरा हो तो 191 (थाईलैंड पुलिस; भारत में: 112) पर कॉल करें।', 'पहले किसी सुरक्षित जगह जाएँ: पड़ोसी, दोस्त का घर, या जहाँ लोग हों।', '1300 (सामाजिक सहायता, 24 घंटे) पर कॉल कर सकते हैं। चोट की तस्वीरें और संदेश सबूत के तौर पर रखें।'], 'क्या आप अभी सुरक्षित हैं?')
```

**help**

```text
('मैं यहाँ हूँ। बताइए क्या हो रहा है।', ['अभी खतरा या चोट हो तो: 1669 (मेडिकल) · 191 (पुलिस)', 'एक वाक्य में लिखें कि क्या हुआ।', 'हो सके तो दूसरे लोगों के पास जाएँ।'], 'आप अभी कहाँ हैं, और क्या कोई आपके साथ है?')
```

## বাংলা (`bn`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('আমি আপনার কথা শুনছি, আর বলার জন্য ধন্যবাদ।', ['থাইল্যান্ডে 1323 (মানসিক স্বাস্থ্য, ২৪ ঘণ্টা) নম্বরে ফোন করুন। এখন বিপদে থাকলে সঙ্গে সঙ্গে 1669 নম্বরে ফোন করুন।', 'একা থাকবেন না। বিশ্বাস করেন এমন একজনকে বলুন যে আপনি ভালো নেই।', 'থাইল্যান্ডের বাইরে থাকলে findahelpline.com-এ হেল্পলাইন খুঁজুন (বাংলাদেশ: 999)।'], 'আপনি কি এখন নিরাপদ?')
```

**medical**

```text
('এটা জরুরি অবস্থা — আগে ফোন করুন।', ['এখনই 1669 নম্বরে ফোন করুন (বাংলাদেশে: 999), ঠিকানা আর উপসর্গ বলুন।', 'শ্বাস না নিলে বা ডাকলে সাড়া না দিলে: বুকের মাঝখানে জোরে চাপ দিন, মিনিটে ১০০–১২০ বার, ফোনের নির্দেশ মেনে চলুন।', 'পানি বা খাবার দেবেন না। যে ওষুধ খেয়েছে তার প্যাকেট ডাক্তারকে দেখানোর জন্য রেখে দিন।'], 'এখন রোগীর পাশে কেউ আছে?')
```

**violence**

```text
('এটা আপনার দোষ নয়। আপনার নিরাপদে থাকার অধিকার আছে।', ['এখন বিপদে থাকলে 191 (থাই পুলিশ; বাংলাদেশে: 999) নম্বরে ফোন করুন।', 'আগে নিরাপদ জায়গায় যান: প্রতিবেশী, বন্ধুর বাড়ি, বা যেখানে লোকজন আছে।', '1300 (সামাজিক সহায়তা, ২৪ ঘণ্টা) নম্বরে ফোন করতে পারেন। আঘাতের ছবি আর মেসেজ প্রমাণ হিসেবে রাখুন।'], 'আপনি কি এখন নিরাপদ?')
```

**help**

```text
('আমি এখানে আছি। কী হচ্ছে বলুন।', ['এখন বিপদ বা আঘাত থাকলে: 1669 (চিকিৎসা) · 191 (পুলিশ)', 'কী হয়েছে এক বাক্যে লিখুন।', 'পারলে অন্য মানুষের কাছে যান।'], 'আপনি এখন কোথায়, সঙ্গে কেউ আছে?')
```

## தமிழ் (`ta`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('நான் உங்களைக் கேட்கிறேன், சொன்னதற்கு நன்றி.', ['தாய்லாந்தில் 1323 (மனநலம், 24 மணி நேரம்) அழைக்கவும். இப்போது ஆபத்தில் இருந்தால் உடனே 1669 அழைக்கவும்.', 'தனியாக இருக்காதீர்கள். நம்பிக்கையான ஒருவரிடம் நீங்கள் நலமாக இல்லை என்று சொல்லுங்கள்.', 'தாய்லாந்துக்கு வெளியே இருந்தால் findahelpline.com இல் உதவி எண்ணைத் தேடுங்கள் (இந்தியா: 14416).'], 'நீங்கள் இப்போது பாதுகாப்பாக இருக்கிறீர்களா?')
```

**medical**

```text
('இது அவசர நிலை — முதலில் அழையுங்கள்.', ['இப்போதே 1669 அழைத்து முகவரியும் அறிகுறிகளும் சொல்லுங்கள் (இந்தியா: 108).', 'மூச்சு விடவில்லை அல்லது பதில் இல்லை என்றால்: மார்பின் நடுவில் வலுவாக அழுத்துங்கள், நிமிடத்திற்கு 100–120 முறை, தொலைபேசி வழிகாட்டலைப் பின்பற்றுங்கள்.', 'தண்ணீர் அல்லது உணவு கொடுக்காதீர்கள். சாப்பிட்ட மருந்தின் அட்டையை மருத்துவரிடம் காட்ட வைத்திருங்கள்.'], 'இப்போது நோயாளியுடன் யாராவது இருக்கிறார்களா?')
```

**violence**

```text
('இது உங்கள் தவறு அல்ல. நீங்கள் பாதுகாப்பாக இருக்கத் தகுதியானவர்.', ['இப்போது ஆபத்து என்றால் 191 (தாய்லாந்து போலீஸ்; இந்தியா: 112) அழைக்கவும்.', 'முதலில் பாதுகாப்பான இடத்திற்குச் செல்லுங்கள்: அண்டை வீட்டார், நண்பர் வீடு, அல்லது மக்கள் உள்ள இடம்.', '1300 (சமூக உதவி, 24 மணி நேரம்) அழைக்கலாம். காயங்களின் புகைப்படங்களையும் செய்திகளையும் ஆதாரமாக வைத்திருங்கள்.'], 'நீங்கள் இப்போது பாதுகாப்பாக இருக்கிறீர்களா?')
```

**help**

```text
('நான் இங்கே இருக்கிறேன். என்ன நடக்கிறது என்று சொல்லுங்கள்.', ['இப்போது ஆபத்து அல்லது காயம் என்றால்: 1669 (மருத்துவம்) · 191 (போலீஸ்)', 'என்ன நடந்தது என்று ஒரு வாக்கியத்தில் எழுதுங்கள்.', 'முடிந்தால் மற்றவர்கள் அருகில் செல்லுங்கள்.'], 'நீங்கள் இப்போது எங்கே இருக்கிறீர்கள், உடன் யாராவது இருக்கிறார்களா?')
```

## සිංහල (`si`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('මම ඔබට ඇහුම්කන් දෙනවා, කිව්වට ස්තූතියි.', ['තායිලන්තයේ 1323 (මානසික සෞඛ්\u200dය, පැය 24) අමතන්න. දැන් අනතුරක නම් වහාම 1669 අමතන්න.', 'තනියම ඉන්න එපා. ඔබ විශ්වාස කරන කෙනෙකුට ඔබ හොඳින් නැති බව කියන්න.', 'තායිලන්තයෙන් පිටත නම් findahelpline.com හි උදව් අංක සොයන්න (ශ්\u200dරී ලංකාව: 1926).'], 'ඔබ දැන් ආරක්ෂිතද?')
```

**medical**

```text
('මෙය හදිසි අවස්ථාවක් — මුලින්ම අමතන්න.', ['දැන්ම 1669 අමතා ලිපිනය සහ රෝග ලක්ෂණ කියන්න (ශ්\u200dරී ලංකාව: 1990).', 'හුස්ම ගන්නේ නැත්නම් හෝ ප්\u200dරතිචාර නැත්නම්: පපුවේ මැද තදින් තද කරන්න, විනාඩියට 100–120 වතාවක්, දුරකථන උපදෙස් අනුගමනය කරන්න.', 'වතුර හෝ කෑම දෙන්න එපා. ගත් බෙහෙත් පැකට්ටුව වෛද්\u200dයවරයාට පෙන්වන්න තියාගන්න.'], 'දැන් රෝගියා ළඟ කවුරුහරි ඉන්නවාද?')
```

**violence**

```text
('මෙය ඔබේ වරදක් නොවේ. ඔබට ආරක්ෂිතව සිටීමට අයිතියක් තිබේ.', ['දැන් අනතුරක නම් 191 (තායි පොලිසිය; ශ්\u200dරී ලංකාව: 119) අමතන්න.', 'මුලින්ම ආරක්ෂිත තැනකට යන්න: අසල්වැසියා, මිතුරෙකුගේ නිවස, හෝ මිනිසුන් සිටින තැනක්.', '1300 (සමාජ සහාය, පැය 24) අමතන්න පුළුවන්. තුවාලවල ඡායාරූප සහ පණිවිඩ සාක්ෂි ලෙස තියාගන්න.'], 'ඔබ දැන් ආරක්ෂිතද?')
```

**help**

```text
('මම මෙතන ඉන්නවා. මොකද වෙන්නේ කියන්න.', ['දැන් අනතුරක් හෝ තුවාලයක් නම්: 1669 (වෛද්\u200dය) · 191 (පොලිසිය)', 'මොකද වුණේ කියලා එක වාක්\u200dයයකින් ලියන්න.', 'පුළුවන් නම් වෙනත් අය ළඟට යන්න.'], 'ඔබ දැන් කොහෙද, ළඟ කවුරුහරි ඉන්නවාද?')
```

## ລາວ (`lo`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('ຂອບໃຈທີ່ບອກຂ້ອຍ. ຂ້ອຍກຳລັງຟັງເຈົ້າຢູ່.', ['ຢູ່ປະເທດໄທ ໂທ 1323 (ສຸຂະພາບຈິດ 24 ຊົ່ວໂມງ). ຖ້າມີອັນຕະລາຍຕອນນີ້ ໂທ 1669 ທັນທີ.', 'ຢ່າຢູ່ຄົນດຽວ. ບອກຄົນທີ່ເຈົ້າໄວ້ໃຈໜຶ່ງຄົນວ່າຕອນນີ້ບໍ່ໄຫວ.', 'ຖ້າຢູ່ນອກປະເທດໄທ ຊອກເບີຊ່ວຍເຫຼືອໄດ້ທີ່ findahelpline.com.'], 'ຕອນນີ້ເຈົ້າປອດໄພບໍ?')
```

**medical**

```text
('ນີ້ແມ່ນເຫດສຸກເສີນ — ໂທກ່ອນ.', ['ໂທ 1669 ດຽວນີ້ ແລະບອກທີ່ຢູ່ກັບອາການ.', 'ຖ້າບໍ່ຫາຍໃຈ ຫຼືເອີ້ນແລ້ວບໍ່ຕອບ: ກົດກາງໜ້າເອິກແຮງໆ 100–120 ເທື່ອຕໍ່ນາທີ ຕາມທີ່ເຈົ້າໜ້າທີ່ບອກທາງໂທລະສັບ.', 'ຢ່າໃຫ້ນ້ຳ ຫຼືອາຫານ. ເກັບກ່ອງຢາທີ່ກິນໄວ້ໃຫ້ທ່ານໝໍເບິ່ງ.'], 'ຕອນນີ້ມີໃຜຢູ່ກັບຄົນເຈັບບໍ?')
```

**violence**

```text
('ນີ້ບໍ່ແມ່ນຄວາມຜິດຂອງເຈົ້າ. ເຈົ້າຄວນໄດ້ຮັບຄວາມປອດໄພ.', ['ຖ້າມີອັນຕະລາຍຕອນນີ້ ໂທ 191 (ຕຳຫຼວດ) ທັນທີ.', 'ໄປບ່ອນທີ່ປອດໄພກ່ອນ — ເພື່ອນບ້ານ ເຮືອນໝູ່ ຫຼືບ່ອນທີ່ມີຄົນຫຼາຍ.', 'ໂທ 1300 (ຊ່ວຍເຫຼືອສັງຄົມ 24 ຊົ່ວໂມງ) ໄດ້. ເກັບຮູບບາດແຜ ແລະຂໍ້ຄວາມໄວ້ເປັນຫຼັກຖານ.'], 'ຕອນນີ້ເຈົ້າປອດໄພບໍ?')
```

**help**

```text
('ຂ້ອຍຢູ່ນີ້. ບອກມາເລີຍວ່າເກີດຫຍັງຂຶ້ນ.', ['ຖ້າມີອັນຕະລາຍ ຫຼືບາດເຈັບຕອນນີ້ — 1669 (ການແພດ) · 191 (ຕຳຫຼວດ)', 'ຂຽນບອກສິ່ງທີ່ເກີດຂຶ້ນໃນປະໂຫຍກດຽວ.', 'ຖ້າເປັນໄປໄດ້ ໄປຢູ່ໃກ້ຄົນອື່ນ.'], 'ຕອນນີ້ເຈົ້າຢູ່ໃສ ແລະມີໃຜຢູ່ນຳບໍ?')
```

## မြန်မာ (`my`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('ပြောပြတာ ကျေးဇူးတင်ပါတယ်။ ကျွန်မ နားထောင်နေပါတယ်။', ['ထိုင်းနိုင်ငံမှာ 1323 (စိတ်ကျန်းမာရေး၊ ၂၄ နာရီ) ကို ဖုန်းဆက်ပါ။ အခု အန္တရာယ်ရှိရင် 1669 ကို ချက်ချင်းခေါ်ပါ။', 'တစ်ယောက်တည်း မနေပါနဲ့။ ယုံကြည်ရတဲ့ တစ်ယောက်ယောက်ကို အခု မကောင်းဘူးလို့ ပြောပါ။', 'ထိုင်းပြင်ပမှာဆိုရင် findahelpline.com မှာ အကူအညီဖုန်းနံပါတ် ရှာနိုင်ပါတယ်။'], 'အခု လုံခြုံတဲ့နေရာမှာ ရှိလား။')
```

**medical**

```text
('ဒါက အရေးပေါ်ပါ — အရင်ဆုံး ဖုန်းဆက်ပါ။', ['အခုပဲ 1669 ကို ခေါ်ပြီး လိပ်စာနဲ့ ရောဂါလက္ခဏာကို ပြောပါ။', 'အသက်မရှူရင် ဒါမှမဟုတ် ခေါ်လို့ မထူးရင် ရင်ဘတ်အလယ်ကို တစ်မိနစ် ၁၀၀–၁၂၀ ကြိမ် ပြင်းပြင်း ဖိပါ — ဖုန်းထဲက ညွှန်ကြားချက်အတိုင်း လုပ်ပါ။', 'ရေ၊ အစားအစာ မပေးပါနဲ့။ သောက်ထားတဲ့ ဆေးဗူးကို ဆရာဝန်ပြဖို့ သိမ်းထားပါ။'], 'လူနာဘေးမှာ အခု တစ်ယောက်ယောက် ရှိလား။')
```

**violence**

```text
('ဒါ သင့်အပြစ် မဟုတ်ပါဘူး။ သင် လုံခြုံစွာ နေပိုင်ခွင့်ရှိပါတယ်။', ['အခု အန္တရာယ်ရှိရင် 191 (ရဲ) ကို ချက်ချင်း ခေါ်ပါ။', 'လုံခြုံတဲ့ နေရာကို အရင်သွားပါ — အိမ်နီးချင်း၊ သူငယ်ချင်းအိမ်၊ လူများတဲ့နေရာ။', '1300 (၂၄ နာရီ လူမှုအကူအညီ) ကို ခေါ်နိုင်ပါတယ်။ ဒဏ်ရာဓာတ်ပုံ၊ မက်ဆေ့ချ်တွေကို သက်သေအဖြစ် သိမ်းထားပါ။'], 'အခု လုံခြုံလား။')
```

**help**

```text
('ကျွန်မ ဒီမှာ ရှိပါတယ်။ ဘာဖြစ်နေလဲ ပြောပြပါ။', ['အခု အန္တရာယ် ဒါမှမဟုတ် ဒဏ်ရာရှိရင် — 1669 (ဆေး) · 191 (ရဲ)', 'ဘာဖြစ်သွားလဲ တစ်ကြောင်းတည်း ရေးပြပါ။', 'ဖြစ်နိုင်ရင် တခြားလူတွေ အနားကို သွားပါ။'], 'အခု ဘယ်မှာလဲ၊ ဘေးမှာ တစ်ယောက်ယောက် ရှိလား။')
```

## ქართული (`ka`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('მესმის შენი და მადლობა, რომ მითხარი.', ['ტაილანდში დარეკე 1323-ზე (ფსიქიკური ჯანმრთელობა, 24 საათი). თუ ახლა საფრთხეში ხარ: 1669.', 'მარტო ნუ დარჩები — უთხარი ვინმეს, ვისაც ენდობი, რომ კარგად არ ხარ.', 'საქართველო: 112 · სხვა ქვეყნებში: findahelpline.com'], 'ახლა უსაფრთხოდ ხარ?')
```

**medical**

```text
('ეს გადაუდებელი შემთხვევაა — ჯერ დარეკე.', ['დარეკე ახლავე 1669-ზე (ტაილანდი) · 112 საქართველოში. თქვი მისამართი და სიმპტომები.', 'თუ არ სუნთქავს ან არ რეაგირებს: ძლიერად დააწექი მკერდის შუაგულს, წუთში 100–120-ჯერ.', 'ნუ მისცემ წყალს ან საჭმელს. შეინახე წამლის შეფუთვა ექიმისთვის.'], 'ახლა ვინმე არის ავადმყოფთან?')
```

**violence**

```text
('ეს შენი ბრალი არ არის. იმსახურებ, რომ უსაფრთხოდ იყო.', ['თუ ახლა საფრთხეში ხარ: 191 (ტაილანდის პოლიცია) · 112 საქართველოში.', 'ჯერ წადი უსაფრთხო ადგილას: მეზობელთან, მეგობართან, სადაც ხალხია.', 'შეინახე დაზიანებების ფოტოები და შეტყობინებები მტკიცებულებად. ტაილანდში 24-საათიანი დახმარება: 1300.'], 'ახლა უსაფრთხოდ ხარ?')
```

**help**

```text
('აქ ვარ. მითხარი, რა ხდება.', ['საფრთხე ან დაზიანება ახლა: 1669 (სამედიცინო) · 191 (პოლიცია) ტაილანდში · 112.', 'ერთი წინადადებით დაწერე, რა მოხდა.', 'თუ შეგიძლია, სხვა ადამიანებთან ახლოს წადი.'], 'სად ხარ ახლა და ვინმე არის შენთან?')
```

**general**

```text
('მოდი ნაბიჯ-ნაბიჯ განვიხილოთ.', ['ერთი წინადადებით დაწერე, რა ხდება სინამდვილეში.', 'ჩამოწერე, რისი გაკეთება შეგიძლია დღეს, თუნდაც პატარა რამ.', 'აირჩიე მხოლოდ ერთი ნაბიჯი მომდევნო 24 საათისთვის.'], 'რა გაწუხებს ყველაზე მეტად ახლა?')
```

## አማርኛ (`am`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('እሰማሃለሁ፣ ስለነገርከኝ አመሰግናለሁ።', ['በታይላንድ 1323 ይደውሉ (የአእምሮ ጤና፣ 24 ሰዓት)። አሁን አደጋ ላይ ከሆኑ 1669 ይደውሉ።', 'ብቻዎን አይሁኑ — ለሚያምኑት ሰው ደህና እንዳልሆኑ ይንገሩ።', 'በሌላ አገር ከሆኑ የአካባቢውን የአደጋ ጊዜ ቁጥር ይደውሉ ወይም findahelpline.com ይጠቀሙ።'], 'አሁን ደህንነትዎ የተጠበቀ ነው?')
```

**medical**

```text
('ይህ አስቸኳይ ሁኔታ ነው — መጀመሪያ ይደውሉ።', ['አሁኑኑ 1669 ይደውሉ (ታይላንድ) ወይም የአካባቢውን የአምቡላንስ ቁጥር። አድራሻውን እና ምልክቶቹን ይናገሩ።', 'የማይተነፍስ ወይም የማይመልስ ከሆነ፦ የደረቱን መሃል በደቂቃ 100–120 ጊዜ አጥብቀው ይጫኑ።', 'ውሃ ወይም ምግብ አይስጡ። የወሰደውን መድኃኒት እሽግ ለሐኪሙ ያስቀምጡ።'], 'አሁን ከታማሚው ጋር ሰው አለ?')
```

**violence**

```text
('ይህ የእርስዎ ጥፋት አይደለም። ደህንነትዎ ሊጠበቅ ይገባል።', ['አሁን አደጋ ላይ ከሆኑ 191 (የታይላንድ ፖሊስ) ይደውሉ።', 'መጀመሪያ ወደ ደህንነቱ የተጠበቀ ቦታ ይሂዱ፦ ጎረቤት፣ የጓደኛ ቤት ወይም ሰው ያለበት ቦታ።', 'የጉዳቱን ፎቶዎች እና መልእክቶች እንደ ማስረጃ ያስቀምጡ። በታይላንድ የ24 ሰዓት እርዳታ፦ 1300።'], 'አሁን ደህና ነዎት?')
```

**help**

```text
('እዚህ ነኝ። ምን እየሆነ እንዳለ ይንገሩኝ።', ['አሁን አደጋ ወይም ጉዳት ካለ፦ 1669 (ሕክምና) · 191 (ፖሊስ) በታይላንድ።', 'የሆነውን በአንድ ዓረፍተ ነገር ይጻፉ።', 'ከቻሉ ወደ ሌሎች ሰዎች አቅራቢያ ይሂዱ።'], 'አሁን የት ነዎት፣ ከእርስዎ ጋር ሰው አለ?')
```

**general**

```text
('አንድ በአንድ እንየው።', ['እየሆነ ያለውን በአንድ ዓረፍተ ነገር ይጻፉ።', 'ዛሬ ማድረግ የሚችሉትን ይዘርዝሩ፣ ትንሽ ነገር ቢሆንም።', 'ለሚቀጥሉት 24 ሰዓታት አንድ እርምጃ ብቻ ይምረጡ።'], 'አሁን በጣም የሚያስጨንቅዎት ምንድን ነው?')
```

## ខ្មែរ (`km`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**crisis**

```text
('សូមអរគុណដែលបានប្រាប់ខ្ញុំ។ ខ្ញុំកំពុងស្តាប់អ្នក។', ['នៅប្រទេសថៃ សូមទូរស័ព្ទ 1323 (សុខភាពផ្លូវចិត្ត ២៤ម៉ោង)។ បើមានគ្រោះថ្នាក់ឥឡូវនេះ ហៅ 1669 ភ្លាម។', 'កុំនៅម្នាក់ឯង។ ប្រាប់មនុស្សម្នាក់ដែលអ្នកទុកចិត្តថា អ្នកមិនស្រួលទេ។', 'បើនៅក្រៅប្រទេសថៃ រកលេខជំនួយបាននៅ findahelpline.com។'], 'ឥឡូវនេះ អ្នកមានសុវត្ថិភាពទេ?')
```

**medical**

```text
('នេះជាករណីបន្ទាន់ — ទូរស័ព្ទមុនសិន។', ['ហៅ 1669 ឥឡូវនេះ ហើយប្រាប់អាសយដ្ឋាន និងរោគសញ្ញា។', 'បើមិនដកដង្ហើម ឬហៅមិនដឹងខ្លួន សូមសង្កត់កណ្តាលទ្រូងឲ្យខ្លាំង ១០០–១២០ ដងក្នុងមួយនាទី តាមការណែនាំតាមទូរស័ព្ទ។', 'កុំឲ្យទឹក ឬអាហារ។ ទុកកញ្ចប់ថ្នាំដែលបានលេប ដើម្បីបង្ហាញគ្រូពេទ្យ។'], 'ឥឡូវនេះ មានអ្នកណានៅជាមួយអ្នកជំងឺទេ?')
```

**violence**

```text
('នេះមិនមែនជាកំហុសរបស់អ្នកទេ។ អ្នកសមនឹងទទួលបានសុវត្ថិភាព។', ['បើមានគ្រោះថ្នាក់ឥឡូវនេះ ហៅ 191 (ប៉ូលិស) ភ្លាម។', 'ទៅកន្លែងមានសុវត្ថិភាពជាមុន — អ្នកជិតខាង ផ្ទះមិត្តភក្តិ ឬកន្លែងមានមនុស្សច្រើន។', 'អាចហៅ 1300 (ជំនួយសង្គម ២៤ម៉ោង)។ រក្សារូបថតរបួស និងសារ ទុកជាភស្តុតាង។'], 'ឥឡូវនេះ អ្នកមានសុវត្ថិភាពទេ?')
```

**help**

```text
('ខ្ញុំនៅទីនេះ។ ប្រាប់ខ្ញុំថា មានរឿងអ្វីកើតឡើង។', ['បើមានគ្រោះថ្នាក់ ឬរបួសឥឡូវនេះ — 1669 (ពេទ្យ) · 191 (ប៉ូលិស)', 'សរសេរប្រាប់ពីអ្វីដែលកើតឡើង ក្នុងមួយប្រយោគ។', 'បើអាច សូមទៅនៅជិតមនុស្សផ្សេង។'], 'ឥឡូវអ្នកនៅឯណា ហើយមានអ្នកណានៅជាមួយទេ?')
```

## 中文 (`zh`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**basic**

```text
('先让你今天有东西吃 — 这比任何计划都重要。', ['今天就打 12345 市民服务热线，问附近的救助站、社区食堂或临时救助，说明你几天没吃饭了。', '附近的寺庙、教会、慈善机构常有免费餐 · 也可以直接去居委会/社区服务中心求助。', '如果头晕、站不稳或身体很不舒服，拨打 120。'], '你现在在哪个城市？身边有可以帮你的人吗？')
```

**someone**

```text
('谢谢你关心他/她 — 你的陪伴比你想象的更重要。', ['现在就直接问：“你是不是想结束生命？” 问出口不会让情况变糟。', '如果他/她有危险或已经伤害自己，立刻拨打 120（急救）或 110。', '尽量不要让他/她一个人待着，并把药物、刀具等收起来。'], '他/她现在和别人在一起吗？')
```

**medical**

```text
('这是紧急情况 — 先打电话，再做其他事。', ['立即拨打 120（急救），说清楚地址和症状。', '没有呼吸或叫不醒：按电话里急救人员的指导做胸外按压。', '不要喂水或食物，把吃过的药或东西的包装留着给医生看。'], '现在有人在病人身边吗？')
```

**violence**

```text
('这不是你的错，你值得安全。', ['如果现在有危险，立刻拨打 110。', '先去安全的地方：邻居、亲友家，或人多的地方。', '保留证据：伤口照片、聊天记录、就医记录。全国妇联热线 12338 可以提供帮助。'], '你现在安全吗？')
```

**disaster**

```text
('安全第一 — 东西可以再买，人最重要。', ['地震：先趴下、护住头、抓牢桌子；停止摇晃后走楼梯离开，不坐电梯。', '火灾或煤气泄漏：不要开关电器，捂住口鼻低身离开，到外面再拨打 119。', '洪水或海啸：立刻往高处走，不要涉水或开车穿过积水。'], '你现在在哪里，身边有人吗？')
```

**scam**

```text
('这很像诈骗 — 先停下，不要转账。', ['真正的警察、法院、银行不会让你转账到“安全账户”，也不会要验证码。', '挂掉电话，自己查官方号码再打回去确认。', '如果已经转账，马上打银行电话止付，并拨打 110 或反诈热线 96110。'], '你已经转账或告诉对方验证码了吗？')
```

## 日本語 (`ja`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**basic**

```text
('まず今日食べられるようにしましょう — それが何より先です。', ['市区町村の福祉窓口（生活困窮者自立支援の相談窓口）に今日連絡してください。食料の緊急支援や生活保護の相談ができます。', '近くのフードバンクや子ども食堂、社会福祉協議会でも食べ物をもらえることがあります。', 'めまいがしたり立てないほどなら、119 に電話してください。'], '今どこにいて、頼れる人はいますか？')
```

**someone**

```text
('その人のことを気にかけてくれてありがとう。あなたがそばにいることには大きな意味があります。', ['「死にたいと思っている？」とはっきり聞いてください。聞いても悪化しません。', '危険な状態やすでに自分を傷つけているなら、すぐに 119 に電話してください。', 'できるだけ一人にしないで、薬や刃物を遠ざけてください。'], 'その人は今、誰かと一緒にいますか？')
```

**medical**

```text
('緊急事態です — まず電話してください。', ['今すぐ 119 に電話し、住所と症状を伝えてください。', '呼吸がない・呼びかけに反応しない場合は、電話の指示に従って胸骨圧迫をしてください。', '水や食べ物を与えず、飲んだ薬などの容器は医師に見せるため残しておいてください。'], '今、その人のそばに誰かいますか？')
```

**violence**

```text
('あなたのせいではありません。あなたには安全でいる権利があります。', ['今危険なら、すぐに 110 に電話してください。', 'まず安全な場所へ：近所、家族や友人の家、人の多い場所。', '証拠を残してください（けがの写真、メッセージ、診断書）。DV相談ナビ #8008 で相談できます。'], '今、安全な場所にいますか？')
```

**disaster**

```text
('今は身の安全が最優先です — 物は取り戻せます。', ['地震：姿勢を低くして頭を守り、机につかまる。揺れが収まったら階段で外へ（エレベーターは使わない）。', '火事・ガス漏れ：電気のスイッチに触れず、口と鼻を覆って低い姿勢で外へ出てから 119 へ。', '津波・洪水：すぐに高い所へ。水の中を歩いたり車で進んだりしない。'], '今どこにいますか？一緒にいる人はいますか？')
```

**scam**

```text
('詐欺の可能性が高いです — 送金はいったん止めてください。', ['本物の警察や銀行が送金や暗証番号を求めることはありません。', '電話を切り、公式の番号を自分で調べてかけ直して確認してください。', 'すでに送金したら、すぐ銀行に連絡し、警察相談専用電話 #9110 か 110 へ。'], 'もう送金したり、番号を伝えたりしましたか？')
```

## 한국어 (`ko`)

- [ ] ผู้ตรวจ: ______  วันที่: ______

**basic**

```text
('오늘 먹을 것부터 해결해요 — 그게 무엇보다 먼저예요.', ['보건복지상담센터 129에 전화해서 며칠째 못 먹었다고 말하세요. 긴급 생계 지원을 안내받을 수 있어요.', '가까운 주민센터(행정복지센터)나 푸드뱅크에서도 바로 도움을 받을 수 있어요.', '어지럽거나 몸을 가누기 힘들면 119에 전화하세요.'], '지금 어디에 있고, 도와줄 사람이 있나요?')
```

**someone**

```text
('그 사람을 걱정해줘서 고마워요. 곁에 있어 주는 것이 생각보다 큰 힘이 돼요.', ['"혹시 죽고 싶은 생각이 있어?"라고 직접 물어보세요. 묻는다고 더 나빠지지 않아요.', '위험하거나 이미 자해했다면 바로 119에 전화하세요. 자살예방 상담전화 109(24시간)에서 어떻게 도울지 상담할 수 있어요.', '가능하면 혼자 두지 말고, 약이나 칼 같은 것은 치워 주세요.'], '그 사람은 지금 누군가와 함께 있나요?')
```

**medical**

```text
('응급 상황이에요 — 먼저 전화부터 해 주세요.', ['지금 바로 119에 전화해서 주소와 증상을 말해 주세요.', '숨을 쉬지 않거나 깨워도 반응이 없으면, 전화 안내에 따라 가슴압박을 해 주세요.', '물이나 음식을 주지 말고, 먹은 약이나 물건의 포장은 의사에게 보여줄 수 있게 남겨 두세요.'], '지금 환자 곁에 누가 있나요?')
```

**violence**

```text
('당신 잘못이 아니에요. 안전할 권리가 있어요.', ['지금 위험하다면 바로 112에 전화하세요.', '먼저 안전한 곳으로 가세요: 이웃, 가족이나 친구 집, 사람이 많은 곳.', '증거를 남겨 두세요(상처 사진, 메시지, 진단서). 여성긴급전화 1366(24시간)에서 도움을 받을 수 있어요.'], '지금 안전한 곳에 있나요?')
```

**disaster**

```text
('지금은 안전이 먼저예요 — 물건은 다시 마련할 수 있어요.', ['지진: 몸을 낮추고 머리를 보호하며 탁자를 잡으세요. 흔들림이 멈추면 계단으로 나가세요(엘리베이터 금지).', '화재·가스 누출: 전기 스위치를 건드리지 말고, 입과 코를 막고 낮은 자세로 나간 뒤 119에 전화하세요.', '쓰나미·홍수: 바로 높은 곳으로 가세요. 물속을 걷거나 차로 지나가지 마세요.'], '지금 어디에 있고, 함께 있는 사람이 있나요?')
```

**scam**

```text
('보이스피싱일 가능성이 높아요 — 송금하지 말고 잠깐 멈추세요.', ['진짜 경찰·검찰·은행은 "안전 계좌"로 돈을 보내라거나 인증번호를 묻지 않아요.', '전화를 끊고, 공식 번호를 직접 찾아서 다시 확인하세요.', '이미 송금했다면 바로 은행에 지급정지를 요청하고 112에 신고하세요.'], '이미 돈을 보냈거나 인증번호를 알려줬나요?')
```
