# Toplu Ceviri Sonuclari

- Model: `deepseek-chat`  |  Temperature: `1.0`
- Toplam satir: 47  |  Benzersiz cagri: 47
- Gecikme/cagri: ort 1298 ms, medyan 1274 ms (duvar suresi 6.5 sn, 10 worker)
- Otomatik isaretli satir: 0 / 47

## oyalama-zaman-kazanma

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| site girdiklerinde görünmeyin, sadece saklanın, zaman kazanıp oyalayın | When they enter site, don't show, just hide. Stall and waste time. | 1138 |  |
| hemen peek atmayın, spike'ı ekmelerini bekleyin, rotasyon gelince beraber alırız | don't peek yet, wait for them to plant, we'll take it together when the rotate comes | 1496 |  |
| defuse'a basma, zamanı yedir, ben heaven'dan geliyorum birlikte temizleriz | Don't defuse, stall. I'm coming from heaven, we'll clear it together. | 1282 |  |
| açılışta göz göze gelmeyin, util harcatın, mümkün olduğunca geç ölün | Don't take first duels, make them waste util, die as late as you can. | 1280 |  |
| tek başına savunmaya kalkma, alanı yavaşça ver ama her köşede biraz oyala | don't try to hold alone, give up space slowly but stall a bit at every corner | 1524 |  |
| onları farklı açılardan sürekli rahatsız et, push'larını yavaşlat ama trade yeme | peek them from different angles to slow their push, just don't get traded | 1235 |  |
| spike kurulduktan sonra ortaya çıkma, zaman bizden yana, sabırlı oyna | Don't peek after spike plant, time is on our side, play patient. | 1217 |  |
| molly ve flash'ları defuse anına saklayın, son saniyede iptal ettiririz | Save molly and flash for the defuse, we cancel it last second | 1429 |  |
| adam siteye girdi ama acele etme, onu içeride tut, rotasyon yetişene kadar ölme | enemy entered site, don't rush—keep him inside, don't die until rotate arrives | 1359 |  |
| defuse'a oynuyormuş gibi yapıp geri çekil ki kit'ini boşa harcasın | Fake defuse and fall back so he wastes his kit. | 1231 |  |

## bait-feda-trade

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| ben önden girip util çekeceğim, hemen arkamdan gelip trade'leyin | I'll entry and pull util, trade me behind right away. | 1158 |  |
| duelist en önde açılışı çeksin, biz ikinci dalga temiz girelim | Duelist takes first contact, we clean up as second wave. | 1408 |  |
| lurk'ü besleyin, ben arkadan sesleri çekeyim siz ortadan basın | feed the lurk, I'll draw noise from behind, you push mid | 1243 |  |
| ilk peek'i feda etme, beraber wide swing atıp aynı anda ateş açalım | Don't peek first, wide swing together and shoot at the same time | 1193 |  |
| sentinel'i yem olarak harcamayın, info için yavaş oynasın yeter | Don't waste the sentinel as bait, just play slow for info | 1516 |  |

## default-kontrol-okuma

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| önce ortayı alalım, sonra rotasyonlarına göre zayıf siteye yükleniriz | Let's take mid first, then we'll hit the weak site based on their rotates. | 1314 |  |
| ilk 30 saniye bilgi toplayalım, agresif çıkmadan onların hatasını bekleyelim | First 30 seconds gather info, don't peek aggro, wait for their mistake. | 1274 |  |
| ekonomilerini gördük, force atmışlar, yakın dövüşe zorlayıp util'lerini boşa çıkaralım | saw their econ, they force bought, let's close the gap and waste their util | 1558 |  |
| aynı taktiği üçüncü kez yapıyorlar, bu sefer mid'i kapatıp flank'i keselim | They're doing the same play for the third time, let's smoke mid and cut the flank this time. | 1247 |  |
| spike'ı erken düşürmeyin, önce kontrolü alıp güvenli plant'a oynayalım | Don't drop spike early, clear control first then play for safe plant. | 1247 |  |
| retake'e güveniyorlar, o yüzden hızlı execute yerine yavaş yorucu bir round oynayalım | they trust their retake, so let's play a slow, draining round instead of a fast execute | 1267 |  |

## post-plant-crossfire

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| plant sonrası dağılın, biri long biri short tutsun, asla aynı yerde durmayın | After plant spread out, one hold long one hold short, never stack the same spot. | 1371 |  |
| defuse sesini duyunca hep birlikte swing atalım, tek tek gidip ölmeyelim | When you hear the defuse sound, we all swing together. Don't go one by one and die. | 1149 |  |
| spike'ı görüş alanında tutun ama açıktan oynamayın, çapraz ateş kuralım | Keep the spike in sight but don't peek open, let's set up crossfire. | 1281 |  |
| ben flank'i bekliyorum, siz spike'a oynayın, arkadan gelen olursa söylerim | I'm watching flank, you guys play the spike, I'll call if someone comes from behind. | 1319 |  |
| molly'i defuse tam yarılanınca atın ki maksimum zaman kaybettirsin | throw the molly right when the defuse is half done so it wastes max time | 1393 |  |

## retake-koordinasyon

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| geri çekilip retake'i bekleyin, util tamamlanmadan kuru girmeyin | fall back and wait for retake, don't dry peek without util | 1153 |  |
| önce yakın köşeleri temizleyelim, sonra açık alana beraber yüklenelim | clear close corners first, then we push open together | 1152 |  |
| ulti'leri retake için saklayın, hepsini aynı anda kullanıp alanı boşaltırız | save ults for retake, we pop all at once to clear site | 1305 |  |
| zaman azaldıysa risk alıp dağınık girin, bol zaman varsa sabırlı temizleyin | if time's low, spread and take risks. if plenty of time, clear patiently | 1229 |  |
| spike'ın yerini öğrenin, defuse hattını util ile kesip oradan başlayalım | Find spike, cut the defuse path with util and start from there. | 1236 |  |

## lurk-flank-bilgi

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| ben sessizce arkadan dolaşıp rotasyonlarını keseceğim, siz baskıyı koruyun | I'll sneak around and cut off their rotates, keep the pressure. | 1306 |  |
| flank'ten ayak sesi geliyor, bir kişi dönüp baksın diğerleri spike'a oynasın | footsteps flank, one check, rest play spike | 1194 |  |
| ben lurk'teyim, mid'e rotasyon atarlarsa arkadan yakalar haber veririm | I'm lurking, rotating mid if they come, I'll catch them from behind and call it. | 1238 |  |
| onları sürekli iki taraftan düşündürelim ki net karar veremesinler | keep them guessing both sides so they can't decide clearly | 1134 |  |

## clutch-karar

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| teke tek düşürmeye çalış, kalabalık açılara kuru peek atma, zamanı kullan | Try to isolate 1v1s, don't dry-peek wide angles, use the time. | 1312 |  |
| fake defuse başlat, ses gelince bırak, panikleyip açılırsa cezalandır | Start a fake defuse, stop when you hear sound, punish if they panic and peek. | 1379 |  |
| zaman varsa bekle, yoksa util harcatıp kör edip gir | if we have time, wait. if not, make them waste util and flash then go in. | 1410 |  |
| silah sesini gizle, reload yapma, köşeyi temizleyince basıp al | Hide your gunshots, don't reload, clear the corner then take it | 1456 |  |

## ekonomi-mantik

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| bu round save, ama biri sheriff'le agresif oynayıp bonus deneyebilir | This round save, but someone can play aggro with sheriff and try for bonus. | 1227 |  |
| yarım satın alma yapmayalım, ya tam force ya tam save, ortada kalmayalım | No half buys. Full force or full save. Don't sit in the middle. | 1271 |  |
| kaybedersek gelecek round full buy olur, o yüzden bu round silahları kurtaralım | Save guns this round, next is full buy if we lose. | 1188 |  |
| onların eco'su geldi, full almayın, light shield'la yakın oynamak yeterli | They're on eco, don't full buy, light shields and close range is enough. | 1254 |  |

## anti-strat-combo

| Turkce | Ingilizce | ms | flag |
|---|---|---|---|
| her round aynı yerden flash'lıyorlar, bu sefer flash'ı bekleyip patlayınca peek atalım | Every round they flash from the same spot. Wait for the flash, then peek when it pops. | 1266 |  |
| breach stun atınca neon hemen dalıyor, stun'ı duyunca geri çekilip trade kuralım | when breach stuns, neon dives right in. back off when you hear the stun and trade | 1340 |  |
| viper duvarı kalkınca hemen girmeyin, toxin azalınca girin yoksa kör savaşırsınız | don't peek until viper wall drops and toxin clears, or you fight blind | 1465 |  |
| sova recon'u plant'tan önce çekelim ki bilgi taze olsun, erken harcamayalım | Let's save Sova recon for right before plant, keep it fresh. | 1346 |  |
