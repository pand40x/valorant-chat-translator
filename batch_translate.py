# -*- coding: utf-8 -*-
"""
Toplu ceviri benchmark'i.
tests/phrases.txt dosyasindaki tum Turkce mesajlari (kategori basliklariyla)
ESZAMANLI cevirir, gecikme olcer, sorunlu ciktiları otomatik isaretler ve
tum sonuclari tests/results.md dosyasina yazar.

Calistirma:  python batch_translate.py
"""
import os
import re
import sys
import time
import statistics
import configparser
from concurrent.futures import ThreadPoolExecutor

import requests
from prompt import build_system_prompt

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PHRASES = os.path.join(HERE, "tests", "phrases.txt")
RESULTS = os.path.join(HERE, "tests", "results.md")
WORKERS = 10
TR_CHARS = set("çÇşŞğĞıİöÖüÜ")


def load_cfg():
    cp = configparser.ConfigParser(inline_comment_prefixes=(";", "#"))
    cp.read(os.path.join(HERE, "config.ini"), encoding="utf-8")

    def g(s, k, d):
        try:
            return cp.get(s, k)
        except Exception:
            return d

    return {
        "key": (g("api", "key", "") or os.environ.get("DEEPSEEK_API_KEY", "")).strip(),
        "base": (g("api", "base_url", "https://api.deepseek.com") or "").strip().rstrip("/"),
        "model": (g("api", "model", "deepseek-chat") or "deepseek-chat").strip(),
        "temp": float((g("api", "temperature", "1.0") or "1.0").strip()),
    }


def parse_phrases(path):
    items, cat = [], "genel"
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                cat = s.lstrip("#").strip()
                continue
            items.append((cat, s))
    return items


def translate(text, cfg, system):
    url = cfg["base"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + cfg["key"], "Content-Type": "application/json"}
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
        "temperature": cfg["temp"],
        "max_tokens": 200,
        "stream": False,
    }
    for attempt in range(3):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            if r.status_code == 429:
                time.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            out = r.json()["choices"][0]["message"]["content"].strip()
            return out.strip().strip('"').strip("'").strip()
        except Exception:
            time.sleep(0.6 * (attempt + 1))
    return "[HATA]"


def norm(s):
    return re.sub(r"[^\wçşğıöü]+", "", s.lower(), flags=re.UNICODE)


def flags_for(cat, tr, out):
    fl = []
    if not out or out == "[HATA]":
        fl.append("BOS/HATA")
        return fl
    if any(c in TR_CHARS for c in out):
        fl.append("TR-LEAK")
    is_english_input = all(ord(c) < 128 for c in tr)
    if cat != "korunacak-kelime" and not is_english_input and norm(out) == norm(tr):
        fl.append("CEVRILMEMIS")
    if len(out) > 2.4 * len(tr) + 30:
        fl.append("UZUN")
    return fl


def main():
    cfg = load_cfg()
    if not cfg["key"] or cfg["key"].startswith("sk-YOUR"):
        print("[HATA] config.ini icinde API anahtari yok.")
        sys.exit(1)

    in_path = sys.argv[1] if len(sys.argv) > 1 else PHRASES
    base = os.path.basename(in_path)
    out_path = (sys.argv[2] if len(sys.argv) > 2 else
                os.path.join(os.path.dirname(in_path) or ".",
                             base.replace("phrases", "results").replace(".txt", ".md")))

    system = build_system_prompt("Turkish", "English")
    items = parse_phrases(in_path)
    uniq = sorted({tr for _, tr in items})
    show_all = len(items) <= 80
    print("Toplam satir: {}  |  Benzersiz: {}  |  Model: {}  |  Temp: {}".format(
        len(items), len(uniq), cfg["model"], cfg["temp"]))
    print("Eszamanli ceviri ({} worker)...".format(WORKERS))
    print("=" * 72)

    cache, lat = {}, {}
    t_start = time.time()

    def work(tr):
        t0 = time.time()
        out = translate(tr, cfg, system)
        return tr, out, (time.time() - t0) * 1000.0

    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for tr, out, ms in ex.map(work, uniq):
            cache[tr], lat[tr] = out, ms
            done += 1
            if done % 50 == 0:
                print("  {}/{} cevrildi...".format(done, len(uniq)))

    wall = time.time() - t_start

    # Sonuclari kategoriye gore topla
    by_cat = {}
    all_flags = []
    for cat, tr in items:
        out = cache[tr]
        fl = flags_for(cat, tr, out)
        by_cat.setdefault(cat, []).append((tr, out, lat[tr], fl))
        if fl:
            all_flags.append((cat, tr, out, fl))

    lats = list(lat.values())
    print("\n" + "=" * 72)
    print("OZET")
    print("  Duvar suresi : {:.1f} sn  ({} benzersiz cagri, {} worker)".format(wall, len(uniq), WORKERS))
    print("  Gecikme/cagri: ort {:.0f}ms  medyan {:.0f}ms  min {:.0f}ms  max {:.0f}ms".format(
        statistics.mean(lats), statistics.median(lats), min(lats), max(lats)))
    print("  Isaretli     : {} / {} satir".format(len(all_flags), len(items)))

    # Kategori basina kisa ornek
    head = "tumu" if show_all else "her birinden 2"
    print("\n--- Kategori ciktilari ({}) ---".format(head))
    for cat in by_cat:
        rows = by_cat[cat]
        print("\n[{}]  ({} satir)".format(cat, len(rows)))
        for tr, out, ms, fl in (rows if show_all else rows[:2]):
            tag = ("  <" + ",".join(fl) + ">") if fl else ""
            print("   TR: {}\n   EN: {}{}".format(tr, out, tag))

    # Tum isaretli satirlar
    if all_flags:
        print("\n--- ISARETLI SATIRLAR ({}) ---".format(len(all_flags)))
        for cat, tr, out, fl in all_flags:
            print("   [{}] <{}>  TR: {}  |  EN: {}".format(cat, ",".join(fl), tr, out))

    # sonuc dosyasi yaz
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Toplu Ceviri Sonuclari\n\n")
        f.write("- Model: `{}`  |  Temperature: `{}`\n".format(cfg["model"], cfg["temp"]))
        f.write("- Toplam satir: {}  |  Benzersiz cagri: {}\n".format(len(items), len(uniq)))
        f.write("- Gecikme/cagri: ort {:.0f} ms, medyan {:.0f} ms (duvar suresi {:.1f} sn, {} worker)\n".format(
            statistics.mean(lats), statistics.median(lats), wall, WORKERS))
        f.write("- Otomatik isaretli satir: {} / {}\n".format(len(all_flags), len(items)))
        for cat in by_cat:
            f.write("\n## {}\n\n| Turkce | Ingilizce | ms | flag |\n|---|---|---|---|\n".format(cat))
            for tr, out, ms, fl in by_cat[cat]:
                f.write("| {} | {} | {:.0f} | {} |\n".format(
                    tr.replace("|", "\\|"), out.replace("|", "\\|"), ms, " ".join(fl)))
    print("\nKaydedildi: " + out_path)


if __name__ == "__main__":
    main()
