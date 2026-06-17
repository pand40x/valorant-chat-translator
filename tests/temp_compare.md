# Sicaklik Tutarlilik Kiyasi

- Kaynak: `tactical_phrases.txt`  |  47 cumle, her biri 4 kez, model `deepseek-chat`

| sicaklik | benzersiz/cumle | mode payi | tam-ayni % | gecikme |
|---|---|---|---|---|
| 0.3 | 2.49 | 60% | 17% | 1318 ms |
| 0.7 | 3.45 | 38% | 0% | 1305 ms |
| 1.0 | 3.85 | 29% | 0% | 1317 ms |

## Ornek varyantlar

**TR:** site girdiklerinde görünmeyin, sadece saklanın, zaman kazanıp oyalayın

- temp 0.3 (4 farkli):
    - Don't show when they enter site, just hide, stall and waste time.
    - When they enter site, stay hidden, just stall and waste time.
    - When they enter site, stay hidden. Just hide, waste time and stall.
    - Don't peek when they enter site, just hide and stall for time.

- temp 0.7 (4 farkli):
    - When they enter site, stay hidden, just hide and stall, waste their time.
    - Don't peek when they enter site, just hide, waste time and stall.
    - When they enter site, don't show yourselves, just hide, stall and waste their time.
    - Don't peek when they enter site, just hide and stall.

- temp 1.0 (4 farkli):
    - hide when they enter site, just stay hidden and stall for time
    - Hide when they enter site, just stall and waste their time.
    - Don't show when they enter site, just hide and waste time stalling.
    - When they enter site, stay hidden, just stall and waste time.

**TR:** adam siteye girdi ama acele etme, onu içeride tut, rotasyon yetişene kadar ölme

- temp 0.3 (1 farkli):
    - enemy entered site, don't rush, keep him inside, don't die until rotation arrives

- temp 0.7 (4 farkli):
    - enemy entered site, don't rush, keep him inside, don't die until rotate arrives
    - enemy entered site, don't rush, keep him inside, stall until rotate arrives, don't die
    - He went into site but don't rush, hold him inside, stall until rotation arrives.
    - enemy entered site, don't rush, keep him inside, don't die until rotation comes

- temp 1.0 (4 farkli):
    - One guy entered site, don't rush, keep him inside, don't die until rotation arrives.
    - one guy entered site, don't rush, hold him inside, don't die until rotate gets here
    - One guy's on site, don't rush—hold him inside, don't die until the rotate arrives.
    - one's on site, don't rush, keep him inside and don't die until rotation arrives

**TR:** ilk 30 saniye bilgi toplayalım, agresif çıkmadan onların hatasını bekleyelim

- temp 0.3 (4 farkli):
    - Let's gather info first 30 seconds, play slow and wait for their mistake.
    - Let's gather info first 30 seconds, wait for their mistake without peeking.
    - Let's gather info first 30s, play slow and wait for their mistake.
    - Let's gather info first 30 seconds, play passive and wait for their mistake.

- temp 0.7 (3 farkli):
    - Let's gather info first 30 seconds, wait for their mistake without peeking.
    - Let's gather info first 30 seconds, wait for their mistake without peeking aggressive.
    - Let's gather info first 30 sec, don't peek early, wait for their mistake

- temp 1.0 (4 farkli):
    - Let's get info first 30 seconds, wait for their mistake without peeking.
    - Let's gather info first 30, wait for their mistake without peeking.
    - Let's info gather first 30s, play off their mistakes
    - Let's gather info first 30 secs, play slow and wait for their mistake

**TR:** ben flank'i bekliyorum, siz spike'a oynayın, arkadan gelen olursa söylerim

- temp 0.3 (4 farkli):
    - I'm watching flank, you play the spike, I'll call if someone comes behind.
    - I'm watching flank, you play spike, I'll call if someone comes behind.
    - I'm watching flank, you play the spike, I'll call if someone comes from behind.
    - I'll watch flank, you play spike, I'll call if someone comes from behind.

- temp 0.7 (4 farkli):
    - I'm watching flank, you play spike, I'll call if someone comes behind
    - I'm holding flank, you play the spike, I'll call if someone comes behind.
    - I'm watching flank, you play spike, I'll call if someone comes behind.
    - I'm watching flank, you play the spike, I'll call out if someone comes from behind.

- temp 1.0 (4 farkli):
    - I'll watch flank, you play spike, I'll call out anyone coming from behind.
    - I'll watch flank, you play the spike, I'll call out if anyone comes from behind.
    - I'm watching flank, you play spike, I'll call if someone comes behind.
    - I'm holding flank, play the spike, I'll call if anyone comes from behind.

**TR:** flank'ten ayak sesi geliyor, bir kişi dönüp baksın diğerleri spike'a oynasın

- temp 0.3 (3 farkli):
    - Footsteps flank, one check it, rest play spike.
    - footsteps flank, one check it rest play spike
    - footsteps flank, one check it, rest play spike

- temp 0.7 (4 farkli):
    - footsteps flank, someone check it the rest play spike
    - Footsteps flank, someone check it, rest play spike.
    - footsteps flank, someone check it, rest play spike
    - Footsteps flank, one turn and check, rest play spike.

- temp 1.0 (4 farkli):
    - Footsteps on flank, someone check it, rest play spike.
    - footsteps flank, one guy check it, rest play spike
    - Footsteps flank, one guy check it, rest play spike
    - footsteps flank, one check it rest play spike

**TR:** yarım satın alma yapmayalım, ya tam force ya tam save, ortada kalmayalım

- temp 0.3 (2 farkli):
    - Don't half-buy, either full force or full save, no in-between.
    - don't half buy, either full force or full save, don't get stuck in between

- temp 0.7 (4 farkli):
    - Don't half-buy, full force or full save, no middle ground.
    - don't half buy, either full force or full save, no in-between
    - Don't half-buy, either full force or full save. No in-between.
    - Don't half-buy. Either full force or full save. No in-between.

- temp 1.0 (4 farkli):
    - Let's not half buy. Either full force or full save, no in-between.
    - Don't half-buy, either full force or full save.
    - Don't half-buy. Either full force or full save. No in-between.
    - Don't half buy, either full force or full save. No in-between buys.
