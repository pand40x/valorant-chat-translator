# -*- coding: utf-8 -*-
"""
Anlik yerel callout sozlugu.
----------------------------
Oyun ici comms'in buyuk bolumu ayni kisa kaliplardan olusur ("rotate", "spike
ektim", "iki kisi a"). Bunlari API'ye sormak gereksiz: ag gecikmesi 1-3 sn,
oysa cevap zaten sabit. Burada SADECE yuksek guvenli, tek anlamli ve sik
kullanilan kaliplar tutulur; tam eslesme olursa ceviri 0 ms'de doner.

Emin olunmayan hicbir sey buraya girmez -> eslesme yoksa API'ye dusulur
(translator.py icindeki akis bunu kendisi yapar). Yanlis bir anlik cevap,
yavas ama dogru bir cevaptan cok daha kotudur.

Cikti bicimi prompt.py ile ayni: tamami kucuk harf, noktalama yok.
"""

# Turkce harfleri ASCII'ye katlama tablosu: kullanici "spıke ektım" da yazsa
# "spike ektim" ile ayni anahtara dusmeli.
_FOLD = str.maketrans({
    "ı": "i", "İ": "i", "I": "i", "i": "i",
    "ş": "s", "Ş": "s",
    "ğ": "g", "Ğ": "g",
    "ü": "u", "Ü": "u",
    "ö": "o", "Ö": "o",
    "ç": "c", "Ç": "c",
    "â": "a", "Â": "a",
    "î": "i", "Î": "i",
    "û": "u", "Û": "u",
})

_STRIP = ".,!?;:'\"`´’‘“”()[]{}*_-–—/\\|…"


def normalize(text):
    """Arama anahtari uret: kucuk harf, Turkce harfler katlanmis, noktalama
    atilmis, ic bosluklar teke indirilmis."""
    if not text:
        return ""
    s = text.translate(_FOLD).lower()
    s = "".join((" " if ch in _STRIP else ch) for ch in s)
    return " ".join(s.split())


# --- Sozluk ------------------------------------------------------------------
# Anahtarlar normalize() gecmis halde yazilir (kucuk, ASCII, noktalamasiz).
# Degerler dogrudan chat'e yapistirilacak nihai Ingilizce callout'tur.
_TABLE = {
    # --- Spike ---
    "spike ektim": "planted",
    "ektim": "planted",
    "diktim": "planted",
    "spike dikildi": "spike planted",
    "spike nerede": "where is the spike",
    "spike bende": "i have the spike",
    "spike bende var": "i have the spike",
    "spike at": "drop the spike",
    "spike ver": "drop the spike",
    "sokuyorum": "defusing",
    "sokmaya basladim": "defusing",
    "defuse ediyorum": "defusing",
    "sok": "defuse",
    "sokun": "defuse it",
    "durdur": "stop the defuse",
    "durdurun": "stop the defuse",
    "yarim sok": "half defuse",
    "yarim sokun": "half defuse",
    "yarim biraktim": "left it on half",

    # --- Rotasyon / konum ---
    "rotasyon": "rotate",
    "rotate": "rotate",
    "donun": "rotate",
    "don": "rotate",
    "geri don": "rotate back",
    "geri donun": "rotate back",
    "rotasyon a": "rotate a",
    "rotasyon b": "rotate b",
    "rotasyon c": "rotate c",
    "a ya don": "rotate a",
    "b ye don": "rotate b",
    "c ye don": "rotate c",
    "mid e don": "rotate mid",
    "mide don": "rotate mid",

    # --- Saldiri / savunma ---
    "basalim": "lets push",
    "basin": "push",
    "bas": "push",
    "gidelim": "lets go",
    "git": "go",
    "gidin": "go",
    "a basalim": "lets push a",
    "b basalim": "lets push b",
    "c basalim": "lets push c",
    "mid basalim": "lets push mid",
    "a ya basalim": "lets push a",
    "b ye basalim": "lets push b",
    "tutun": "hold",
    "tut": "hold",
    "savunun": "hold",
    "bekleyin": "wait",
    "bekle": "wait",
    "biraz bekleyin": "hold up",
    "dur": "stop",
    "durun": "stop",
    "geri cekil": "fall back",
    "geri cekilin": "fall back",
    "kacin": "fall back",
    "yavas": "slow it down",
    "yavaslayin": "slow it down",
    "acele etmeyin": "no rush",
    "hizli": "fast",
    "hizli gidelim": "lets go fast",
    "rush": "rush",
    "default": "default",
    "default oynayalim": "lets play default",
    "split": "lets split",
    "yayilin": "spread out",
    "toplanin": "group up",
    "beraber gidelim": "lets go together",

    # --- Dusman sayisi / durum ---
    "tek kaldi": "1 left",
    "bir kaldi": "1 left",
    "iki kaldi": "2 left",
    "uc kaldi": "3 left",
    "dort kaldi": "4 left",
    "hepsi burada": "all of them here",
    "kimse yok": "nobody here",
    "burada kimse yok": "nobody here",
    "bos": "its clear",
    "temiz": "clear",
    "temizlendi": "cleared",
    "dusuk": "hes low",
    "dusuk can": "hes low",
    "cani dusuk": "hes low",
    "oldu": "down",
    "gitti": "down",
    "aldim": "got one",
    "birini aldim": "got one",
    "ikisini aldim": "got two",
    "trade al": "trade me",
    "trade alin": "trade me",
    "arkadan": "from behind",
    "arkada": "behind us",
    "arkamizda": "behind us",
    "flank var": "flank",
    "flank geliyor": "flank incoming",
    "lurk var": "someone lurking",

    # --- Ekonomi ---
    "save": "save",
    "save edelim": "lets save",
    "save atalim": "lets save",
    "eco": "eco",
    "eco atalim": "lets eco",
    "force": "force",
    "force atalim": "force buy",
    "full al": "full buy",
    "full alalim": "full buy",
    "para yok": "no money",
    "param yok": "i have no money",
    "silah at": "drop me a gun",
    "bana silah at": "drop me a gun",
    "silah atar misin": "can you drop me a gun",
    "silaha ihtiyacim var": "i need a gun",
    "silah alabilir miyim": "can i get a gun",
    "kalkan al": "buy shield",
    "util alin": "buy util",

    # --- Yetenek / ulti ---
    "ulti hazir": "ult ready",
    "ultim hazir": "my ult is ready",
    "ultim var": "i have ult",
    "ultim yok": "no ult",
    "ulti kullandi": "he used ult",
    "ulti at": "use your ult",
    "flas at": "flash",
    "flas atin": "flash",
    "flas lazim": "need a flash",
    "duman at": "smoke",
    "duman atin": "smoke it",
    "duman lazim": "need smoke",
    "molotof at": "molly it",
    "molotof lazim": "need a molly",
    "util yok": "no util",
    "util bitti": "out of util",
    "drone at": "drone it",
    "recon at": "recon it",
    "wall at": "wall it",

    # --- Yardim / bilgi ---
    "yardim": "need backup",
    "yardim edin": "need backup",
    "destek lazim": "need backup",
    "yalnizim": "im alone here",
    "tek basimayim": "im alone here",
    "ben varim": "im up",
    "geliyorum": "coming",
    "geldim": "im here",
    "buradayim": "im here",
    "hazirim": "im ready",
    "hazir misiniz": "you ready",
    "bilmiyorum": "i dont know",
    "gormedim": "didnt see",
    "goremedim": "couldnt see",

    # --- Oyun akisi ---
    "sus": "chill",
    "sakin": "chill",
    "sakin olun": "chill",
    "iyi oyun": "good game",
    "gg": "gg",
    "iyi atis": "nice shot",
    "guzel": "nice",
    "harika": "nice one",
    "sorun yok": "no worries",
    "benim hatam": "my bad",
    "benim hatamdi": "my bad",
    "ozur": "sorry",
    "tamam": "ok",
    "olur": "ok",
    "evet": "yes",
    "hayir": "no",
    "tesekkurler": "thanks",
    "sagol": "thanks",

    # --- Ajan secimi ---
    "ben dolarim": "i can fill",
    "dolduruyorum": "i can fill",
    "flexliyorum": "i can flex",
    "smoke lazim": "need a controller",
    "smokeci yok": "need a controller",
    "kontrolcu lazim": "need a controller",
    "sentinel lazim": "need a sentinel",
    "initiator lazim": "need an initiator",
    "acici lazim": "need an initiator",
    "herkes duelist": "too many duelists",
    "duelist doldu": "too many duelists",
    "cok duelist var": "too many duelists",
    "rol secin": "pick by role",
    "doclayin": "dodge",
    "dodge atin": "dodge",
    "comp bozuk": "bad comp",
    "compu bozmayin": "dont grief the comp",
}

# --- Korpustan gelen kaliplar -----------------------------------------------
# Yukaridaki tablo elle yazilmisti ve gercek kullanimi iyi temsil etmiyordu:
# tests/phrases.txt uzerinde olculen kapsam yalnizca %5 cikti. Asagidaki
# kaliplar dogrudan o korpustan (gercek oyun-ici mesajlar) cikarildi -- yani
# oyuncularin GERCEKTEN yazdigi bicimler. Ornegin "duman at" degil "smoke at",
# "gidelim" degil "a gelin".
#
# Hala tutucu: tek basina cok anlamli olan tek kelimeler (cik, kur, vur, birak,
# alma, verme, sustur, kir) BILEREK dışarida birakildi -- onlar API'ye gider.
_TABLE_CORPUS = {
    # --- Site cagrisi / durum ---
    "a gelin": "come a",
    "b gelin": "come b",
    "c gelin": "come c",
    "mid gelin": "come mid",
    "a bos": "a is clear",
    "b bos": "b is clear",
    "c bos": "c is clear",
    "mid bos": "mid is clear",
    "a dolu": "a is stacked",
    "b dolu": "b is stacked",
    "c dolu": "c is stacked",
    "site temiz": "site clear",
    "site dolu": "site is stacked",
    "rush a": "rush a",
    "rush b": "rush b",
    "rush c": "rush c",
    "donelim": "lets rotate",
    "main kontrol": "control main",

    # --- Hareket / tempo ---
    "yuruyun": "walk",
    "cikma": "dont peek",
    "peek atma": "dont peek",
    "bakmayin": "dont look",
    "sessiz gidin": "go quiet",
    "ses yapma": "dont make noise",
    "yavas oynayin": "play slow",
    "hizli girelim": "lets go fast",
    "beraber cikalim": "lets swing together",
    "tek tek cikmayin": "dont go one by one",
    "odaklanin": "focus up",
    "gir": "go in",
    "kos": "run",
    "yuru": "walk",
    "saklan": "hide",
    "kac": "run",
    "koru": "hold",
    "oyna": "play",
    "bak": "check",

    # --- Util (oyuncular Ingilizce terimi Turkce fiille kullaniyor) ---
    "smoke at": "smoke it",
    "smoke bekle": "wait for smoke",
    "flash at": "flash",
    "molly at": "molly it",
    "nade at": "nade it",
    "heal at": "heal me",
    "res at": "res me",
    "trap kur": "set a trap",
    "fake at": "fake it",
    "flashliyorum": "im flashing",
    "ulti var": "i have ult",
    "ulti ac": "use your ult",
    "ulti sakla": "save your ult",
    "cam bak": "check window",
    "info ver": "give info",

    # --- Spike ---
    "spike dustu": "spike dropped",
    "spike al": "pick up the spike",
    "spike sende": "you have the spike",
    "plant at": "plant it",
    "plant kur": "plant it",
    "defuse bas": "defuse it",
    "yari defuse": "half defuse",
    "full defuse": "full defuse",
    "fake defuse": "fake defuse",

    # --- Ekonomi ---
    "save alin": "save",
    "eco yapalim": "lets eco",
    "silahi kurtar": "save your gun",
    "vandal alicam": "ill buy vandal",
    "phantom ver": "drop me a phantom",
    "drop var mi": "anyone have a drop",
    "heal var mi": "anyone have heal",

    # --- Dusman bilgisi ---
    "iki kisi": "2 of them",
    "uc kisi": "3 of them",
    "dort kisi": "4 of them",
    "low hp": "low hp",
    "cok low": "really low",
    "80 vurdum": "hit him for 80",
    "kir oldum": "im broken",
    "ses aldim": "heard something",
    "tradele": "trade him",
    "trade yok": "no trade",
    "arkaya bak": "watch behind",
    "arkanda": "behind you",
    "yakinda": "close by",
    "flank geliyo": "flank incoming",
    "op var": "they have op",
    "op a cikma": "dont peek the op",

    # --- Lokasyon ---
    "solda": "left",
    "sagda": "right",
    "kosede": "in the corner",
    "markette": "market",
    "main de": "main",
    "linkte": "link",
    "defaultta": "default",
    "shortta biri": "one short",
    "longda biri": "one long",
    "heaven var": "one heaven",
    "ct var": "one ct",
    "garage var": "one garage",
    "elbow var": "one elbow",

    # --- Zaman ---
    "zamani oynayin": "play the clock",
    "zaman var": "we have time",
    "zaman yok": "no time",

    # --- Sosyal ---
    "nt": "nt",
    "wp": "wp",
}
_TABLE.update(_TABLE_CORPUS)


# Zaten standart Ingilizce oyun terimi olan tek kelimeler: oldugu gibi doner.
# (prompt.py ayni kurali modele de soyluyor; burada API'ye hic gitmeden hallediyoruz.)
_PASSTHROUGH = {
    "op", "eco", "force", "save", "smoke", "flash", "rush", "peek", "lurk",
    "flank", "clutch", "retake", "default", "entry", "drone", "recon", "wall",
    "molly", "heaven", "hell", "short", "long", "main", "ct", "mid", "spawn",
    "plant", "spike", "defuse", "rotate", "push", "hold", "trade", "util",
    "ult", "gg", "ff", "a", "b", "c", "one", "two", "three", "low", "down",
    # korpustan: korunacak-kelime kategorisinde gecen, oldugu gibi kalmasi gerekenler
    "full buy", "drop", "fake", "swing", "post plant", "nt", "wp", "stack",
    "bonus", "save", "info", "trade", "lurk", "dry", "stall", "bait",
}


def lookup(text, source="Turkish", target="English"):
    """Anlik karsilik varsa dondur, yoksa None (-> API'ye dusulur).

    Yalnizca TR -> EN icin calisir; baska dil cifti yapilandirilmissa sozluk
    devre disi kalir ki yanlis dilde cevap uretmeyelim.
    """
    if source.strip().lower() != "turkish" or target.strip().lower() != "english":
        return None

    key = normalize(text)
    if not key:
        return None

    hit = _TABLE.get(key)
    if hit:
        return hit

    if key in _PASSTHROUGH:
        return key

    return None


def size():
    """Sozlukteki kalip sayisi (acilis ekraninda gosterilir)."""
    return len(_TABLE) + len(_PASSTHROUGH)
