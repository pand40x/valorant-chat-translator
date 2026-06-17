# -*- coding: utf-8 -*-
"""
Valorant ceviri benchmark'i.
config.ini'deki AYNI model/prompt ile gercekci Turkce Valorant mesajlarini
cevirir, gecikme olcer ve sonuclari benchmark_results.md dosyasina yazar.

Calistirma:  python benchmark.py   (veya .venv\\Scripts\\python.exe benchmark.py)
"""
import os
import sys
import time
import statistics
import configparser

import requests
from prompt import build_system_prompt

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))

# Gercekci, zorlu test seti: callout, harita-ozel lokasyon, ekonomi, yetenek,
# strateji, clutch, code-switching (TR-EN karisik), argo/yazim hatasi, sosyal.
TEST_CASES = [
    # --- Pozisyon / sayi callout ---
    {"cat": "Pozisyon/Sayi", "tr": "iki kisi A'ya yukleniyor, biri kisa biri uzun"},
    {"cat": "Pozisyon/Sayi", "tr": "mid'de bir tane var sanirim Jett, op'lu olabilir"},
    {"cat": "Pozisyon/Sayi", "tr": "uc dort kisi B'ye toplandi, rotasyon gerek hemen"},
    # --- Harita-ozel lokasyon ---
    {"cat": "Harita Lokasyon", "tr": "Ascent market'te iki kisi pusuda, dikkat catwalk"},
    {"cat": "Harita Lokasyon", "tr": "Bind hookah'tan geliyorlar, lamba kapali kimse bakmiyor"},
    {"cat": "Harita Lokasyon", "tr": "Split rafters'a Cypher kamera koymus, vent'ten gelin"},
    # --- Ekonomi ---
    {"cat": "Ekonomi", "tr": "bu round save atalim, sadece pistol alin para biriksin"},
    {"cat": "Ekonomi", "tr": "force gidiyoruz, herkes Spectre ve light shield alsin"},
    {"cat": "Ekonomi", "tr": "bana silah at param yok, full eco kaldim ya"},
    # --- Ajan yetenegi ---
    {"cat": "Ajan Yetenek", "tr": "Sova oku attim A site temiz, kimse yok girin"},
    {"cat": "Ajan Yetenek", "tr": "Killjoy ultisi var B'de, util harcatmadan girmeyin"},
    {"cat": "Ajan Yetenek", "tr": "Viper duvarini actim mid'i kesiyor, arkadan gecin"},
    # --- Strateji / round plani ---
    {"cat": "Strateji", "tr": "default oynayalim, 30 saniye bekleyip B'ye fake sonra A'ya yuklenelim"},
    {"cat": "Strateji", "tr": "ben mid lurk'e gidiyorum, siz A'dan ses verin baski yapin"},
    # --- Clutch / acil ---
    {"cat": "Clutch/Acil", "tr": "1v3 kaldim sustun lutfen, spike A'da sokuyorum sesli olmayin"},
    {"cat": "Clutch/Acil", "tr": "yardim edin retake B, ben tek kaldim canim cok dusuk"},
    {"cat": "Clutch/Acil", "tr": "cabuk trade alin beni, heaven'a peek atiyorum simdi"},
    # --- Code-switching (TR-EN karisik) ---
    {"cat": "Karisik TR-EN", "tr": "enemy mid var ben rotate ediyorum A site, cover me"},
    {"cat": "Karisik TR-EN", "tr": "op'cu var long, bait'lemeyin smoke'la push yapalim"},
    # --- Argo / kisaltma / yazim hatasi ---
    {"cat": "Argo/Yazim", "tr": "dusman bee de cok kalabalik dikkat edin yaa"},
    {"cat": "Argo/Yazim", "tr": "akkci var hevende, sen deag al ben entry girerim"},
    {"cat": "Argo/Yazim", "tr": "eko round bunlar 100% force etti gibi geliyo bana"},
    # --- Trash talk / sosyal (hafif) ---
    {"cat": "Sosyal", "tr": "ez round rakip cop resmen, gg devam edelim"},
    {"cat": "Sosyal", "tr": "iyi oynuyorsun kanka devam et, o clutch efsaneydi"},
]


def load_cfg():
    cp = configparser.ConfigParser(inline_comment_prefixes=(";", "#"))
    cp.read(os.path.join(HERE, "config.ini"), encoding="utf-8")

    def g(s, k, d):
        try:
            return cp.get(s, k)
        except Exception:
            return d

    key = (g("api", "key", "") or os.environ.get("DEEPSEEK_API_KEY", "")).strip()
    return {
        "key": key,
        "base": (g("api", "base_url", "https://api.deepseek.com") or "").strip().rstrip("/"),
        "model": (g("api", "model", "deepseek-chat") or "deepseek-chat").strip(),
        "temp": float((g("api", "temperature", "1.0") or "1.0").strip()),
    }


def translate(text, cfg, system):
    url = cfg["base"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + cfg["key"], "Content-Type": "application/json"}
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
        "temperature": cfg["temp"],
        "max_tokens": 256,
        "stream": False,
    }
    t0 = time.time()
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    out = r.json()["choices"][0]["message"]["content"].strip().strip('"').strip("'").strip()
    return out, (time.time() - t0) * 1000.0


def main():
    cfg = load_cfg()
    if not cfg["key"] or cfg["key"].startswith("sk-YOUR"):
        print("[HATA] config.ini icinde DeepSeek API anahtari yok.")
        sys.exit(1)

    system = build_system_prompt("Turkish", "English")
    print("Model: {}  |  Temp: {}  |  Vaka: {}".format(cfg["model"], cfg["temp"], len(TEST_CASES)))
    print("=" * 72)

    rows, lats = [], []
    for i, c in enumerate(TEST_CASES, 1):
        try:
            out, ms = translate(c["tr"], cfg, system)
        except Exception as e:
            out, ms = "[HATA] " + str(e), 0.0
        lats.append(ms)
        rows.append((i, c["cat"], c["tr"], out, ms))
        print("\n[{:02d}] {}  ({:.0f} ms)".format(i, c["cat"], ms))
        print("  TR: " + c["tr"])
        print("  EN: " + out)

    valid = [l for l in lats if l > 0]
    print("\n" + "=" * 72)
    if valid:
        print("Gecikme  ort:{:.0f}ms  medyan:{:.0f}ms  min:{:.0f}ms  max:{:.0f}ms".format(
            statistics.mean(valid), statistics.median(valid), min(valid), max(valid)))

    out_path = os.path.join(HERE, "benchmark_results.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Valorant Ceviri Benchmark Sonuclari\n\n")
        f.write("- Model: `{}`  |  Temperature: `{}`  |  Vaka: {}\n".format(
            cfg["model"], cfg["temp"], len(TEST_CASES)))
        if valid:
            f.write("- Gecikme: ort {:.0f} ms, medyan {:.0f} ms, min {:.0f} ms, max {:.0f} ms\n".format(
                statistics.mean(valid), statistics.median(valid), min(valid), max(valid)))
        f.write("\n| # | Kategori | Turkce | Ingilizce (cikti) | ms |\n")
        f.write("|---|---|---|---|---|\n")
        for i, cat, tr, out, ms in rows:
            f.write("| {} | {} | {} | {} | {:.0f} |\n".format(
                i, cat, tr.replace("|", "\\|"), out.replace("|", "\\|"), ms))
    print("\nKaydedildi: benchmark_results.md")


if __name__ == "__main__":
    main()
