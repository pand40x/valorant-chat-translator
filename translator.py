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
import ctypes
import threading
import subprocess
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
import callouts


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
        # Chat satiri kisa; dar tutmak modelin gevezelemesini de engeller.
        "max_tokens": int(_to_float(get("api", "max_tokens", "256"), 256.0)),
        "source": (get("translation", "source_lang", "Turkish") or "Turkish").strip(),
        "target": (get("translation", "target_lang", "English") or "English").strip(),
        "hotkey": (get("hotkey", "translate", "f8") or "f8").strip().lower(),
        "suppress": _to_bool(get("hotkey", "suppress", "true"), True),
        "auto_send": _to_bool(get("behavior", "auto_send", "false"), False),
        "restore_clipboard": _to_bool(get("behavior", "restore_clipboard", "true"), True),
        "play_sound": _to_bool(get("behavior", "play_sound", "true"), True),
        # Sik kaliplari API'ye hic gitmeden anlik cevir (callouts.py).
        "use_local_dict": _to_bool(get("behavior", "use_local_dict", "true"), True),
        # Ayni cumlenin ikinci cevirisini onbellekten ver.
        "cache": _to_bool(get("behavior", "cache", "true"), True),
        # ince ayar gecikmeleri (saniye)
        "key_delay": 0.04,
        "copy_timeout": 1.2,
    }
    if not cfg["api_key"] or cfg["api_key"].startswith("sk-YOUR"):
        _die("[HATA] DeepSeek API anahtari ayarlanmamis.\n"
             "config.ini -> [api] key = sk-... satirini doldurun.")
    return cfg


# --- Ceviri ------------------------------------------------------------------
# Tek bir HTTP oturumu: her F8'de yeni TCP+TLS el sikismasi yapmak oyun ici
# gecikmeye 200-400 ms ekliyordu. Session baglantiyi canli tutar (keep-alive),
# acilista da bir kez isitilir (_prewarm) -> ilk ceviri de hizli olur.
_SESSION = requests.Session()
_SESSION.headers.update({"Content-Type": "application/json",
                         "Connection": "keep-alive"})

# Sistem promptu her cagrida yeniden kurulmasin (buyuk bir f-string).
_PROMPT_CACHE = {}

# Ceviri onbellegi: oyun ici comms agir sekilde tekrar eder ("rotate", "2 a").
# Ayni cumle ikinci kez 0 ms'de doner ve token harcamaz.
_CACHE = {}
_CACHE_MAX = 500
_CACHE_LOCK = threading.Lock()

# Saglayiciya ozel ince ayar parametreleri 400/422 ile reddedilirse bir daha
# gonderilmez (DeepSeek "thinking" destekler, OpenAI uyumlu digerleri etmeyebilir).
_SEND_EXTRAS = True


def build_system_prompt(cfg):
    # Sistem promptu prompt.py icinde tutulur (translator + benchmark ayni promptu kullanir).
    key = (cfg["source"], cfg["target"])
    if key not in _PROMPT_CACHE:
        _PROMPT_CACHE[key] = _shared_build_prompt(cfg["source"], cfg["target"])
    return _PROMPT_CACHE[key]


def _cache_get(text, cfg):
    with _CACHE_LOCK:
        return _CACHE.get((text, cfg["model"], cfg["source"], cfg["target"]))


def _cache_put(text, cfg, out):
    with _CACHE_LOCK:
        if len(_CACHE) >= _CACHE_MAX:
            # En eskiyi at (dict ekleme sirasini korur -> basit FIFO yeter).
            _CACHE.pop(next(iter(_CACHE)), None)
        _CACHE[(text, cfg["model"], cfg["source"], cfg["target"])] = out


def _extras_for(cfg):
    """Saglayiciya gore hiz ayari. Bilinmeyen saglayiciya bos sozluk doner."""
    if "deepseek" in cfg["base_url"].lower():
        # Oyun sohbeti icin uzun dusunme yerine hizli, dogrudan ceviri.
        return {"thinking": {"type": "disabled"}}
    return {}


def _build_payload(text, cfg, with_extras=True):
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": build_system_prompt(cfg)},
            {"role": "user", "content": text},
        ],
        "temperature": cfg["temperature"],
        "max_tokens": cfg["max_tokens"],
        "stream": False,
    }
    if with_extras:
        payload.update(_extras_for(cfg))
    return payload


def _post(text, cfg, with_extras):
    url = cfg["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + cfg["api_key"]}
    r = _SESSION.post(url, headers=headers,
                      json=_build_payload(text, cfg, with_extras),
                      timeout=cfg["timeout"])
    if r.status_code == 401:
        raise RuntimeError("API anahtari gecersiz (401). config.ini -> [api] key kontrol edin.")
    if r.status_code == 402:
        raise RuntimeError("Bakiye yetersiz (402). Saglayici hesabinizi kontrol edin.")
    if r.status_code == 404:
        raise RuntimeError("Endpoint/model bulunamadi (404). base_url ve model adini kontrol edin "
                           "(check_api.py yardimci olur).")
    if r.status_code == 429:
        raise RuntimeError("Hiz siniri (429). Birkac saniye sonra tekrar deneyin.")
    return r


def translate(text, cfg):
    global _SEND_EXTRAS

    # 1) Onbellek
    if cfg["cache"]:
        hit = _cache_get(text, cfg)
        if hit:
            _log("cache hit")
            return hit

    last_err = None
    for attempt in range(2):  # kisa bir tekrar denemesi (ag dalgalanmalari icin)
        try:
            r = _post(text, cfg, _SEND_EXTRAS)

            # Saglayici ince ayar parametresini kabul etmiyorsa birakip tekrar dene.
            if r.status_code in (400, 422) and _SEND_EXTRAS and _extras_for(cfg):
                _log("extras reddedildi (%s) -> sade payload'a gecildi" % r.status_code)
                _SEND_EXTRAS = False
                r = _post(text, cfg, False)

            r.raise_for_status()
            data = r.json()
            out = data["choices"][0]["message"]["content"].strip()
            out = out.strip().strip('"').strip("'").strip()
            if out and cfg["cache"]:
                _cache_put(text, cfg, out)
            return out
        except Exception as e:
            last_err = e
            # Anahtar/bakiye/model hatasinda tekrar denemek anlamsiz.
            if isinstance(e, RuntimeError):
                break
            if attempt == 0:
                time.sleep(0.4)
    raise last_err


def _prewarm(cfg):
    """Acilista TLS el sikismasini pesinen yap: ilk F8 de hizli olsun."""
    try:
        _SESSION.get(cfg["base_url"] + "/models",
                     headers={"Authorization": "Bearer " + cfg["api_key"]},
                     timeout=5)
        _log("prewarm OK (baglanti isitildi)")
    except Exception as e:
        _log("prewarm atlandi: %r" % (e,))


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
_last_fire = 0.0  # son "hotkey fired" ani (bekci bununla hook'un canli olup olmadigini anlar)


def do_translate(cfg):
    global _last_fire
    _last_fire = time.time()
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
        # Sik kullanilan kisa kaliplar: API'ye hic gitmeden, 0 ms'de.
        out = None
        if cfg["use_local_dict"]:
            out = callouts.lookup(src, cfg["source"], cfg["target"])
            if out:
                _log("local dict hit: " + repr(out))

        if not out:
            try:
                out = translate(src, cfg)
            except Exception as e:
                _log("translation error: " + repr(e))
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


# --- Hook bekcisi (self-heal) --------------------------------------------------
# Oyun tam yuk altindayken Windows (LowLevelHooksTimeout) ve/veya Vanguard,
# dusuk seviyeli klavye hook'unu sessizce dusurebiliyor: surec ayakta kalir ama
# F8 sagirlasir. Bekci, kisayolu hook'tan bagimsiz olarak GetAsyncKeyState ile
# izler (bu bir sorgudur, hook degildir; sokulemez). Hook bir basisi kacirirsa
# ceviriyi yine de tetikler ve hook'u tazelemek icin sureci kendini yeniden
# baslatir. Sonuc: hook olse bile F8 calismaya devam eder.
_VK = {
    # Fonksiyon tuslari
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75,
    "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "f13": 0x7C, "f14": 0x7D, "f15": 0x7E, "f16": 0x7F,
    # Ozel tuslar
    "space": 0x20, "tab": 0x09, "enter": 0x0D, "return": 0x0D, "esc": 0x1B,
    "escape": 0x1B, "backspace": 0x08, "insert": 0x2D, "ins": 0x2D,
    "delete": 0x2E, "del": 0x2E, "home": 0x24, "end": 0x23,
    "page up": 0x21, "pageup": 0x21, "page down": 0x22, "pagedown": 0x22,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "caps lock": 0x14, "scroll lock": 0x91, "pause": 0x13,
    # Noktalama / sembol
    "`": 0xC0, "-": 0xBD, "=": 0xBB, "[": 0xDB, "]": 0xDD, "\\": 0xDC,
    ";": 0xBA, "'": 0xDE, ",": 0xBC, ".": 0xBE, "/": 0xBF,
    # Numpad
    "num 0": 0x60, "num 1": 0x61, "num 2": 0x62, "num 3": 0x63, "num 4": 0x64,
    "num 5": 0x65, "num 6": 0x66, "num 7": 0x67, "num 8": 0x68, "num 9": 0x69,
    "num *": 0x6A, "num +": 0x6B, "num -": 0x6D, "num .": 0x6E, "num /": 0x6F,
}
# Harf ve rakamlar: VK kodlari ASCII ile ayni.
for _c in "abcdefghijklmnopqrstuvwxyz0123456789":
    _VK[_c] = ord(_c.upper())

# Degistirici tuslar (kombinasyonlarda ayrica sorgulanir).
_VK_MOD = {
    "ctrl": 0x11, "control": 0x11,
    "shift": 0x10,
    "alt": 0x12, "menu": 0x12,
    "win": 0x5B, "windows": 0x5B, "cmd": 0x5B,
}


def _parse_hotkey(hotkey):
    """'ctrl+space' -> ([0x11], 0x20). Cozulemezse None.

    Eskiden yalnizca F1-F12 taninirdi; baska bir kisayol secen kullanicida
    bekci sessizce devre disi kaliyordu (yani hook olunce F8 tamamen sagirdi).
    """
    parts = [p.strip().lower() for p in str(hotkey).split("+") if p.strip()]
    if not parts:
        return None
    mods, main = [], None
    for p in parts:
        if p in _VK_MOD:
            mods.append(_VK_MOD[p])
        elif p in _VK:
            if main is not None:
                return None  # iki ana tus -> desteklenmiyor
            main = _VK[p]
        else:
            return None  # taninmayan parca
    if main is None:
        return None
    return mods, main


def _self_restart():
    _log("self-restart: hook sagirlasti, surec tazeleniyor")
    try:
        env = dict(os.environ)
        env["VALO_TR_RESPAWN"] = "1"  # yeniden dogan kopya "hazirim" bip'ini calmasin
        subprocess.Popen([sys.executable, os.path.abspath(__file__)], cwd=HERE, env=env)
    except Exception as e:
        _log("self-restart BASARISIZ: %s" % e)
        return
    os._exit(0)


def _watchdog(cfg):
    parsed = _parse_hotkey(cfg["hotkey"])
    if parsed is None:
        _log("watchdog: %r cozulemedi, bekci devre disi" % cfg["hotkey"])
        return
    mods, vk = parsed
    user32 = ctypes.windll.user32
    was_down = False
    while True:
        time.sleep(0.03)
        try:
            down = bool(user32.GetAsyncKeyState(vk) & 0x8000)
            # Kombinasyonda degistiricilerin de basili olmasi gerekir.
            if down and mods:
                down = all(bool(user32.GetAsyncKeyState(m) & 0x8000) for m in mods)
        except Exception:
            continue
        if down and not was_down:
            press_ts = time.time()
            time.sleep(0.35)  # hook'a ates etme firsati taniyalim
            if _last_fire < press_ts:
                # Hook bu basisi gormedi -> sagir. Ceviriyi biz tetikleyelim,
                # bitince de hook'u tazelemek icin yeniden baslayalim.
                _log("watchdog: hook %s'i kacirdi -> yedek tetik + tazeleme" % cfg["hotkey"])
                t = threading.Thread(target=do_translate, args=(cfg,), daemon=True)
                t.start()
                t.join(timeout=30)
                time.sleep(0.5)
                _self_restart()
        was_down = down


def main():
    cfg = load_config()
    _log("=== started, waiting for hotkey: " + cfg["hotkey"] + " ===")
    print("=" * 58)
    print("  VALORANT Chat Translator  ({} -> {})".format(cfg["source"], cfg["target"]))
    print("=" * 58)
    print("  Model     : " + cfg["model"])
    print("  Sunucu    : " + cfg["base_url"])
    print("  Kisayol   : " + cfg["hotkey"].upper() + "  (chat'e yaz -> bas -> Ingilizcesi yapisir)")
    print("  Auto-send : " + ("ACIK" if cfg["auto_send"] else "KAPALI (Enter'a kendin bas)"))
    print("  Yerel szl : " + ("ACIK ({} kalip, 0 ms)".format(callouts.size())
                              if cfg["use_local_dict"] else "KAPALI"))
    print("  Onbellek  : " + ("ACIK" if cfg["cache"] else "KAPALI"))
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
        if not os.environ.get("VALO_TR_RESPAWN"):
            beep_ready(cfg)
    except Exception as e:
        _log("HOTKEY REGISTER FAILED: " + str(e))
        _die("[HATA] Kisayol kaydedilemedi: {}\n"
             "Yonetici olarak calistirmayi deneyin.".format(e))

    threading.Thread(target=_watchdog, args=(cfg,), daemon=True).start()
    _log("watchdog armed (GetAsyncKeyState yedegi aktif)")

    # TLS el sikismasini pesinen yap -> ilk ceviri de hizli olsun.
    threading.Thread(target=_prewarm, args=(cfg,), daemon=True).start()

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass
    print("\nKapatiliyor...")


if __name__ == "__main__":
    main()
