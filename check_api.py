#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API self-testi.
---------------
config.ini'deki anahtar / base_url / model uclusunun gercekten calistigini
dogrular. Saglayici degistirdikten sonra (DeepSeek -> Mimo gibi) once bunu
calistirin: oyun icinde "neden bir sey olmuyor" diye ugrasmaktan kurtarir.

Calistirma:
  .venv\\Scripts\\python.exe check_api.py

Yaptigi sira:
  1) config.ini okunur (anahtar ekrana YAZILMAZ, sadece maskelenir)
  2) GET /models      -> anahtar gecerli mi, hangi modeller var
  3) POST /chat/...   -> gercek prompt'la tek cumle cevrilir, gecikme olculur
  4) Yerel sozluk     -> callouts.py birkac ornekle sinanir (API gerektirmez)
"""

import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import requests
except ImportError:
    print("[HATA] 'requests' kurulu degil. Once setup.bat calistirin.")
    sys.exit(1)

import configparser

from prompt import build_system_prompt
import callouts


def mask(key):
    if not key:
        return "(bos)"
    if len(key) <= 10:
        return key[:3] + "***"
    return key[:6] + "..." + key[-4:]


def load():
    path = os.path.join(HERE, "config.ini")
    if not os.path.exists(path):
        print("[HATA] config.ini yok. config.example.ini dosyasini kopyalayin.")
        sys.exit(1)
    cp = configparser.ConfigParser(inline_comment_prefixes=(";", "#"))
    cp.read(path, encoding="utf-8")

    def get(s, k, d=None):
        try:
            return cp.get(s, k)
        except Exception:
            return d

    return {
        "key": (get("api", "key", "") or os.environ.get("DEEPSEEK_API_KEY", "")).strip(),
        "base_url": (get("api", "base_url", "https://api.deepseek.com") or "").strip().rstrip("/"),
        "model": (get("api", "model", "deepseek-chat") or "").strip(),
        "timeout": float(get("api", "timeout", "20") or 20),
        "temperature": float(get("api", "temperature", "0.3") or 0.3),
        "source": (get("translation", "source_lang", "Turkish") or "Turkish").strip(),
        "target": (get("translation", "target_lang", "English") or "English").strip(),
    }


def main():
    cfg = load()
    print("=" * 60)
    print("  API self-testi")
    print("=" * 60)
    print("  base_url : " + cfg["base_url"])
    print("  model    : " + cfg["model"])
    print("  anahtar  : " + mask(cfg["key"]))
    print("  yon      : {} -> {}".format(cfg["source"], cfg["target"]))
    print("-" * 60)

    if not cfg["key"] or cfg["key"].startswith("sk-YOUR"):
        print("[X] API anahtari ayarlanmamis.")
        print("    config.ini -> [api] key = ... satirini doldurun.")
        return 1

    sess = requests.Session()
    auth = {"Authorization": "Bearer " + cfg["key"]}
    ok = True

    # --- 1) Modeller ---------------------------------------------------------
    print("\n[1/3] GET /models ...")
    try:
        r = sess.get(cfg["base_url"] + "/models", headers=auth, timeout=10)
        if r.status_code == 401:
            print("  [X] 401 - anahtar gecersiz (yanlis anahtar ya da yanlis base_url).")
            return 1
        r.raise_for_status()
        names = [m.get("id", "?") for m in r.json().get("data", [])]
        print("  [OK] anahtar gecerli. {} model bulundu:".format(len(names)))
        for n in names[:25]:
            mark = "  <-- config.ini'deki" if n == cfg["model"] else ""
            print("       - " + n + mark)
        if names and cfg["model"] not in names:
            print("  [!] UYARI: '{}' listede yok. Yukaridakilerden birini".format(cfg["model"]))
            print("      config.ini -> [api] model satirina yazin.")
            ok = False
    except Exception as e:
        print("  [!] Model listesi alinamadi: {}".format(e))
        print("      (bazi saglayicilar /models sunmaz; bu tek basina hata degil)")

    # --- 2) Gercek ceviri ----------------------------------------------------
    print("\n[2/3] POST /chat/completions ...")
    probe = "iki kisi a geliyor spike ektim"
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": build_system_prompt(cfg["source"], cfg["target"])},
            {"role": "user", "content": probe},
        ],
        "temperature": cfg["temperature"],
        "max_tokens": 256,
        "stream": False,
    }
    try:
        t0 = time.time()
        r = sess.post(cfg["base_url"] + "/chat/completions", headers=auth,
                      json=payload, timeout=cfg["timeout"])
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 402:
            print("  [X] 402 - bakiye yetersiz.")
            return 1
        if r.status_code == 404:
            print("  [X] 404 - endpoint/model yok. base_url ve model adini kontrol edin.")
            return 1
        if r.status_code >= 400:
            print("  [X] HTTP {} - {}".format(r.status_code, r.text[:300]))
            return 1
        out = r.json()["choices"][0]["message"]["content"].strip()
        print("  [OK] {} ms".format(ms))
        print("       [TR] " + probe)
        print("       [EN] " + out)
        if ms > 3000:
            print("  [!] Gecikme yuksek. Oyun ici icin daha hizli/kucuk bir model deneyin.")
    except Exception as e:
        print("  [X] Istek basarisiz: {}".format(e))
        return 1

    # --- 3) Yerel sozluk -----------------------------------------------------
    print("\n[3/3] Yerel sozluk (API'siz, 0 ms) ...")
    samples = ["spike ektim", "rotasyon", "bana silah at", "tek kaldi", "op"]
    for s in samples:
        hit = callouts.lookup(s, cfg["source"], cfg["target"])
        print("       {:<16} -> {}".format(s, hit if hit else "(API'ye dusulur)"))
    print("  [OK] {} kalip yuklu.".format(callouts.size()))

    print("\n" + "=" * 60)
    print("  SONUC: " + ("her sey hazir, run.bat ile baslatabilirsiniz."
                         if ok else "calisiyor ama yukaridaki UYARI'yi giderin."))
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
