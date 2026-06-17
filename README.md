# Valorant Chat Translator (TR → EN)

Oyun içi sohbete yazdığınız **Türkçe** metni tek tuşla (varsayılan **F8**) seçip kopyalar,
DeepSeek ile **rekabetçi Valorant terminolojisine** uygun şekilde İngilizceye çevirir ve
geri yapıştırır. Enter'a siz basarsınız.

```
Chat'e yaz  ─►  F8  ─►  [seç + kopyala]  ─►  DeepSeek çeviri  ─►  [İngilizcesi yapışır]  ─►  Enter
```

---

## ⚠️ Önemli uyarı — Anti-hile (Vanguard)

Valorant, **kernel seviyesinde** çalışan **Vanguard** anti-hile sistemini kullanır. Bu araç:

- Global bir **klavye hook**'u kurar (F8'i dinlemek için), ve
- Oyuna **sentetik tuş girişi** gönderir (Ctrl+A / Ctrl+C / Ctrl+V).

Bu iki davranış teorik olarak Vanguard tarafından tespit edilebilir. Pano tabanlı çeviri
araçları yaygın kullanılsa da, **hesabınıza yönelik bir işlem yapılmayacağının garantisi
yoktur.** Bu aracı kullanmak **tamamen kendi sorumluluğunuzdadır.** Riski azaltmak için:

- `auto_send = false` bırakın (otomatik mesaj göndermek daha "bot" gibi görünür).
- Makro/tuş tekrarı gibi şeyler için kullanmayın; sadece çeviri için.

Kabul etmiyorsanız bu aracı kullanmayın.

---

## Kurulum (Windows)

1. **Python 3** kurun: <https://www.python.org/downloads/>
   Kurulumda **“Add python.exe to PATH”** kutusunu işaretleyin.
2. Bu klasörü Windows PC'ye indirin (repo'yu klonlayın veya ZIP indirin).
3. **`setup.bat`** dosyasına çift tıklayın. (Sanal ortam kurar, paketleri yükler, `config.ini` oluşturur.)
4. **`config.ini`** dosyasını açın ve DeepSeek API anahtarınızı yazın:
   ```ini
   [api]
   key = sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
5. **`run.bat`** dosyasına çift tıklayın. (Yönetici izni ister — **Evet** deyin; oyuna giriş gönderebilmek için gerekli.)

> İsterseniz tek dosyalık `.exe` için `build.bat` çalıştırın → `dist\ValorantTranslator.exe`.
> (config.ini'yi exe ile aynı klasöre koyun.)

---

## Kullanım

1. `run.bat` açık dursun (siyah konsol penceresi).
2. Valorant'ta sohbeti açın (örn. `Enter` veya takım sohbeti `Shift+Enter`).
3. **Türkçe** yazın, göndermeden **F8**'e basın.
4. Kısa süre sonra Türkçe metin **İngilizcesiyle değişir** → kontrol edip **Enter**'a basın.

Başarıda tiz, hatada pes bir bip sesi duyarsınız. Konsolda `[TR]` ve `[EN]` satırları görünür.

---

## Yapılandırma (`config.ini`)

| Ayar | Açıklama | Varsayılan |
|---|---|---|
| `api.key` | DeepSeek API anahtarı | — |
| `api.model` | Model | `deepseek-chat` |
| `api.temperature` | Yaratıcılık (1.0 tutarlı, 1.3 DeepSeek çeviri önerisi) | `1.0` |
| `translation.source_lang` / `target_lang` | Çeviri yönü | `Turkish` → `English` |
| `hotkey.translate` | Kısayol (`f8`, `f9`, `ctrl+space`...) | `f8` |
| `hotkey.suppress` | Tuşu oyuna iletme | `true` |
| `behavior.auto_send` | Çeviri sonrası otomatik Enter | `false` |
| `behavior.restore_clipboard` | İşlem sonrası eski panoyu geri yükle | `true` |
| `behavior.play_sound` | Sesli geri bildirim | `true` |

### Çeviri kalitesi nasıl sağlanıyor?

`translator.py` içindeki sistem promptu, modele **rekabetçi Valorant comms** tonu verir:
ajan/harita/silah isimleri korunur, Türkçe oyun argosu → İngilizce callout sözlüğüyle
eşlenir (örn. *“iki kişi A geliyor”* → **“2 pushing A”**, *“spike ektim”* → **“planted”**),
çıktı kısa ve net tutulur. Promptu kendi takım jargonunuza göre düzenleyebilirsiniz.

---

## Benchmark (çeviri kalitesi testi)

`benchmark.py`, aracın **gerçek prompt'uyla** 9 kategoride 24 gerçekçi Valorant mesajını
çevirir, gecikme ölçer ve sonuçları `benchmark_results.md`'ye yazar:

```bat
.venv\Scripts\python.exe benchmark.py
```

Son ölçüm: genel **~9.5/10** çeviri kalitesi, ortalama **~1.3 sn** gecikme. Prompt'u
(`prompt.py`) düzenleyip benchmark'ı tekrar çalıştırarak kendi jargonunuza göre kaliteyi
ölçebilirsiniz (`prompt.py` hem aracı hem benchmark'ı besler).

---

## Sorun giderme

| Sorun | Çözüm |
|---|---|
| Oyunda hiçbir şey olmuyor | `run.bat`'i **yönetici olarak** çalıştırın. Vanguard yüksek yetkide çalıştığı için şart. |
| Tam ekranda çalışmıyor | Oyunu **Kenarlıksız Pencere (Borderless)** moduna alın. |
| “Pano boş” uyarısı | Önce sohbete metin yazın; F8'e sohbet kutusu **odaktayken** basın. |
| F8 oyunda başka şey yapıyor | `config.ini`'de `suppress = true` olsun veya başka kısayol seçin. |
| 401 hatası | API anahtarı yanlış → `config.ini`'yi kontrol edin. |
| 402 hatası | DeepSeek bakiyeniz bitmiş. |
| Çeviri yavaş | Normal; ağ + API gecikmesi 1–3 sn olabilir. |

---

## Güvenlik

- **API anahtarınızı asla paylaşmayın / commit etmeyin.** `config.ini` `.gitignore` ile hariç tutulur;
  repoda yalnızca `config.example.ini` (yer tutucu) bulunur.
- Anahtarınız bir yerde açığa çıktıysa <https://platform.deepseek.com/api_keys> üzerinden **yenileyin**.

## Lisans

MIT — bkz. [LICENSE](LICENSE).
