# -*- coding: utf-8 -*-
"""
Sicaklik (temperature) tutarlilik kiyasi.
Ayni cumleyi her sicaklikta RUNS kez cevirir; cikti ne kadar degisiyor olcer.
Dusuk temp -> daha sabit (deterministik) cikti beklenir.

Olculenler (her sicaklik icin):
  - benzersiz cikti / cumle (1.0 = hep ayni, RUNS = hepsi farkli)
  - mode payi  (en sik ciktinin orani; 1.0 = tam tutarli)
  - tam tutarli cumle yuzdesi (RUNS denemenin hepsi ayni)
  - ortalama gecikme

Calistirma:  python temp_compare.py [phrases.txt]
"""
import os
import re
import sys
import statistics
import configparser
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import requests
from prompt import build_system_prompt

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PHRASES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "tests", "tactical_phrases.txt")
OUT = os.path.join(HERE, "tests", "temp_compare.md")
TEMPS = [0.3, 0.7, 1.0]
RUNS = 4
WORKERS = 12


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
    }


def read_phrases(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s)
    return out


def translate(text, cfg, system, temp):
    url = cfg["base"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + cfg["key"], "Content-Type": "application/json"}
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
        "temperature": temp,
        "max_tokens": 200,
        "stream": False,
    }
    import time
    t0 = time.time()
    for _ in range(3):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            out = r.json()["choices"][0]["message"]["content"].strip()
            return out.strip().strip('"').strip("'").strip(), (time.time() - t0) * 1000.0
        except Exception:
            time.sleep(0.6)
    return "[HATA]", 0.0


def norm(s):
    return re.sub(r"[^\wçşğıöü]+", " ", s.lower(), flags=re.UNICODE).strip()


def main():
    cfg = load_cfg()
    if not cfg["key"] or cfg["key"].startswith("sk-YOUR"):
        print("[HATA] config.ini icinde API anahtari yok.")
        sys.exit(1)

    system = build_system_prompt("Turkish", "English")
    phrases = read_phrases(PHRASES)
    tasks = [(p, t, r) for p in phrases for t in TEMPS for r in range(RUNS)]
    print("Cumle: {}  |  Sicaklik: {}  |  Tekrar: {}  |  Toplam cagri: {}".format(
        len(phrases), TEMPS, RUNS, len(tasks)))
    print("Eszamanli ({} worker)...".format(WORKERS))

    def work(task):
        p, t, r = task
        out, ms = translate(p, cfg, system, t)
        return (p, t, out, ms)

    res = {}  # (phrase, temp) -> list of (out, ms)
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for p, t, out, ms in ex.map(work, tasks):
            res.setdefault((p, t), []).append((out, ms))
            done += 1
            if done % 80 == 0:
                print("  {}/{}...".format(done, len(tasks)))

    # Sicaklik basina toplulastir
    stats = {}
    for t in TEMPS:
        distincts, modeshares, lats, identical = [], [], [], 0
        for p in phrases:
            outs = [o for o, _ in res[(p, t)]]
            lats += [m for _, m in res[(p, t)]]
            normed = [norm(o) for o in outs]
            c = Counter(normed)
            d = len(c)
            distincts.append(d)
            modeshares.append(max(c.values()) / len(normed))
            if d == 1:
                identical += 1
        stats[t] = {
            "distinct": statistics.mean(distincts),
            "mode": statistics.mean(modeshares),
            "identical_pct": 100.0 * identical / len(phrases),
            "lat": statistics.mean(lats),
        }

    print("\n" + "=" * 64)
    print("TUTARLILIK KIYASI  ({} cumle, her biri {} kez)".format(len(phrases), RUNS))
    print("-" * 64)
    print("  sicaklik | benzersiz/cumle | mode payi | tam-ayni % | gecikme")
    for t in TEMPS:
        s = stats[t]
        print("    {:<5}  |      {:.2f}       |   {:.0%}    |    {:>4.0f}%   | {:.0f}ms".format(
            t, s["distinct"], s["mode"], s["identical_pct"], s["lat"]))

    # Ornek cumleler: her sicaklikta varyantlar
    sample_idx = [i for i in (0, 8, 16, 24, 32, 40) if i < len(phrases)]
    print("\n--- Ornek varyantlar ---")
    for i in sample_idx:
        p = phrases[i]
        print("\nTR: {}".format(p))
        for t in TEMPS:
            uniq = []
            for o, _ in res[(p, t)]:
                if o not in uniq:
                    uniq.append(o)
            print("  temp {}: {} farkli".format(t, len(uniq)))
            for u in uniq:
                print("     - {}".format(u))

    # md yaz
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# Sicaklik Tutarlilik Kiyasi\n\n")
        f.write("- Kaynak: `{}`  |  {} cumle, her biri {} kez, model `{}`\n\n".format(
            os.path.basename(PHRASES), len(phrases), RUNS, cfg["model"]))
        f.write("| sicaklik | benzersiz/cumle | mode payi | tam-ayni % | gecikme |\n")
        f.write("|---|---|---|---|---|\n")
        for t in TEMPS:
            s = stats[t]
            f.write("| {} | {:.2f} | {:.0%} | {:.0f}% | {:.0f} ms |\n".format(
                t, s["distinct"], s["mode"], s["identical_pct"], s["lat"]))
        f.write("\n## Ornek varyantlar\n")
        for i in sample_idx:
            p = phrases[i]
            f.write("\n**TR:** {}\n".format(p))
            for t in TEMPS:
                uniq = []
                for o, _ in res[(p, t)]:
                    if o not in uniq:
                        uniq.append(o)
                f.write("\n- temp {} ({} farkli):\n".format(t, len(uniq)))
                for u in uniq:
                    f.write("    - {}\n".format(u))
    print("\nKaydedildi: " + OUT)


if __name__ == "__main__":
    main()
