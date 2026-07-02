#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valorant Chat Translator
------------------------
Oyun chat'ine yazdiginiz metni kisayola (varsayilan F8) basinca secip kopyalar,
DeepSeek ile rekabetci VALORANT terminolojisine uygun sekilde cevirir ve geri yapistirir.

Akis:
  F8 -> Ctrl+A + Ctrl+C (yazdigini sec/kopyala)
     -> DeepSeek ile ceviri (TR -> EN)
     -> panoya yaz
     -> Ctrl+A + Ctrl+V (Ingilizcesini yapistir)
  Enter'a SIZ basarsiniz (auto_send kapaliyken).

Kullanim:
  1) config.ini icine DeepSeek API anahtarinizi yazin.
  2) run.bat ile calistirin (yonetici olarak onerilir).
  3) Oyunda chat'i acin, Turkce yazin, F8'e basin -> Ingilizcesi yapisir.
"""

import os
import sys
import time
import threading
import configparser

# UTF-8 konsol (Windows cp1252 karakter sorunlarini onler)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _die(msg):
    print(msg)
    try:
        input("\nKapatmak icin Enter'a basin...")
    except Exception:
        pass
    sys.exit(1)


# --- Bagimliliklar -----------------------------------------------------------
try:
    import requests
except ImportError:
    _die("[HATA] 'requests' kurulu degil. Once setup.bat calistirin.")

try:
    import pyperclip
except ImportError:
    _die("[HATA] 'pyperclip' kurulu degil. Once setup.bat calistirin.")

try:
    import keyboard
except ImportError:
    _die("[HATA] 'keyboard' kurulu degil. Once setup.bat calistirin.")

try:
    import winsound  # sadece Windows
    _HAS_SOUND = True
except ImportError:
    _HAS_SOUND = False

from prompt import build_system_prompt as _shared_build_prompt


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.ini")
LOG_PATH = os.path.join(HERE, "translator.log")
SENTINEL = "\x00__VALO_TR_SENTINEL__\x00"


def _log(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(time.strftime("%H:%M:%S") + "  " + str(msg) + "\n")
    except Exception:
        pass


# --- Yardimcilar -------------------------------------------------------------
def _to_bool(v, default):
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on", "evet", "acik")


def _to_float(v, default):
    try:
        return float(str(v).strip())
    except Exception:
        return default


def load_config():
    if not os.path.exists(CONFIG_PATH):
        _die("[HATA] config.ini bulunamadi.\n"
             "config.example.ini dosyasini 'config.ini' olarak kopyalayip API anahtarinizi girin.")
    cp = configparser.ConfigParser(inline_comment_prefixes=(";", "#"))
    cp.read(CONFIG_PATH, encoding="utf-8")

    def get(section, key, fallback=None):
        try:
            return cp.get(section, key)
        except Exception:
            return fallback

    cfg = {
        "api_key": (get("api", "key", "") or os.environ.get("DEEPSEEK_API_KEY", "")).strip(),
        "base_url": (get("api", "base_url", "https://api.deepseek.com") or "").strip().rstrip("/"),
        "model": (get("api", "model", "deepseek-chat") or "deepseek-chat").strip(),
        "timeout": _to_float(get("api", "timeout", "20"), 20.0),
        "temperature": _to_float(get("api", "temperature", "1.0"), 1.0),
        "source": (get("translation", "source_lang", "Turkish") or "Turkish").strip(),
        "target": (get("translation", "target_lang", "English") or "English").strip(),
        "hotkey": (get("hotkey", "translate", "f8") or "f8").strip().lower(),
        "suppress": _to_bool(get("hotkey", "suppress", "true"), True),
        "auto_send": _to_bool(get("behavior", "auto_send", "false"), False),
        "restore_clipboard": _to_bool(get("behavior", "restore_clipboard", "true"), True),
        "play_sound": _to_bool(get("behavior", "play_sound", "true"), True),
        # ince ayar gecikmeleri (saniye)
        "key_delay": 0.04,
        "copy_timeout": 1.2,
    }
    if not cfg["api_key"] or cfg["api_key"].startswith("sk-YOUR"):
        _die("[HATA] DeepSeek API anahtari ayarlanmamis.\n"
             "config.ini -> [api] key = sk-... satirini doldurun.")
    return cfg


# --- Ceviri ------------------------------------------------------------------
def build_system_prompt(cfg):
    # Sistem promptu prompt.py icinde tutulur (translator + benchmark ayni promptu kullanir).
    return _shared_build_prompt(cfg["source"], cfg["target"])


def translate(text, cfg):
    url = cfg["base_url"] + "/chat/completions"
    headers = {
        "Authorization": "Bearer " + cfg["api_key"],
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": build_system_prompt(cfg)},
            {"role": "user", "content": text},
        ],
        "temperature": cfg["temperature"],
        "max_tokens": 512,
        "stream": False,
    }
    last_err = None
    for _ in range(2):  # kisa bir tekrar denemesi (ag dalgalanmalari icin)
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=cfg["timeout"])
            if r.status_code == 401:
                raise RuntimeError("API anahtari gecersiz (401). config.ini kontrol edin.")
            if r.status_code == 402:
                raise RuntimeError("Bakiye yetersiz (402). DeepSeek hesabinizi kontrol edin.")
            r.raise_for_status()
            data = r.json()
            out = data["choices"][0]["message"]["content"].strip()
            return out.strip().strip('"').strip("'").strip()
        except Exception as e:
            last_err = e
            time.sleep(0.4)
    raise last_err


# --- Pano + tus simulasyonu --------------------------------------------------
def grab_selection(cfg):
    """Chat kutusundaki metni sec + kopyala ve panodan oku (sentinel ile dogrula)."""
    try:
        pyperclip.copy(SENTINEL)
    except Exception:
        pass
    keyboard.send("ctrl+a")
    time.sleep(cfg["key_delay"])
    keyboard.send("ctrl+c")
    deadline = time.time() + cfg["copy_timeout"]
    while time.time() < deadline:
        time.sleep(0.02)
        try:
            val = pyperclip.paste()
        except Exception:
            val = None
        if val and val != SENTINEL:
            return val
    return None


def paste_text(text, cfg):
    pyperclip.copy(text)
    time.sleep(cfg["key_delay"])
    keyboard.send("ctrl+a")
    time.sleep(cfg["key_delay"])
    keyboard.send("ctrl+v")
    time.sleep(cfg["key_delay"])
    if cfg["auto_send"]:
        time.sleep(0.05)
        keyboard.send("enter")


def beep_ok(cfg):
    if cfg["play_sound"] and _HAS_SOUND:
        try:
            winsound.Beep(880, 90)
        except Exception:
            pass


def beep_err(cfg):
    if cfg["play_sound"] and _HAS_SOUND:
        try:
            winsound.Beep(300, 170)
        except Exception:
            pass


def beep_ready(cfg):
    # Acilista "hazirim" bildirimi: iki yukselen ton. Boylece arka planda
    # calistigini (pencere olmadan) duyarak anlarsiniz.
    if cfg["play_sound"] and _HAS_SOUND:
        try:
            winsound.Beep(660, 120)
            winsound.Beep(990, 160)
        except Exception:
            pass


def _restore(original, cfg):
    if cfg["restore_clipboard"] and original is not None and original != SENTINEL:
        try:
            pyperclip.copy(original)
        except Exception:
            pass


# --- Ana islem ---------------------------------------------------------------
_busy = threading.Lock()


def do_translate(cfg):
    _log("hotkey fired")
    if not _busy.acquire(blocking=False):
        _log("busy, skipped")
        return  # zaten bir ceviri suruyor
    try:
        try:
            original = pyperclip.paste()
        except Exception:
            original = None

        src = grab_selection(cfg)
        _log("grabbed: " + repr(src))
        if not src or not src.strip():
            print("[!] Pano bos - cevrilecek metin yok. (Chat'e yazdiniz mi?)")
            beep_err(cfg)
            _restore(original, cfg)
            return
        src = src.strip()
        print("[TR] " + src)

        t0 = time.time()
        try:
            out = translate(src, cfg)
        except Exception as e:
            print("[X] Ceviri hatasi: " + str(e))
            beep_err(cfg)
            _restore(original, cfg)
            return
        if not out:
            print("[X] Bos ceviri dondu.")
            beep_err(cfg)
            _restore(original, cfg)
            return

        ms = int((time.time() - t0) * 1000)
        print("[EN] " + out + "  ({} ms)".format(ms))
        _log("translated: " + repr(out) + " ({} ms)".format(ms))
        paste_text(out, cfg)
        beep_ok(cfg)

        if cfg["restore_clipboard"]:
            time.sleep(0.35)
            _restore(original, cfg)
    finally:
        _busy.release()


def main():
    cfg = load_config()
    _log("=== started, waiting for hotkey: " + cfg["hotkey"] + " ===")
    print("=" * 58)
    print("  VALORANT Chat Translator  ({} -> {})".format(cfg["source"], cfg["target"]))
    print("=" * 58)
    print("  Model     : " + cfg["model"])
    print("  Kisayol   : " + cfg["hotkey"].upper() + "  (chat'e yaz -> bas -> Ingilizcesi yapisir)")
    print("  Auto-send : " + ("ACIK" if cfg["auto_send"] else "KAPALI (Enter'a kendin bas)"))
    print("  Cikis     : Ctrl+C  veya  bu pencereyi kapat")
    print("-" * 58)
    print("  UYARI: Valorant'in Vanguard anti-hile sistemi sentetik giris/")
    print("  global klavye hook'unu tespit edebilir. Kullanim tamamen kendi")
    print("  sorumlulugunuzdadir. Ayrinti icin README.md.")
    print("=" * 58)
    print("Hazir. {} bekleniyor...\n".format(cfg["hotkey"].upper()))

    try:
        keyboard.add_hotkey(
            cfg["hotkey"],
            lambda: threading.Thread(target=do_translate, args=(cfg,), daemon=True).start(),
            suppress=cfg["suppress"],
        )
        _log("hotkey registered OK (suppress=%s)" % cfg["suppress"])
        beep_ready(cfg)
    except Exception as e:
        _log("HOTKEY REGISTER FAILED: " + str(e))
        _die("[HATA] Kisayol kaydedilemedi: {}\n"
             "Yonetici olarak calistirmayi deneyin.".format(e))

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass
    print("\nKapatiliyor...")


if __name__ == "__main__":
    main()
