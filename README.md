# Valorant Chat Translator (TR → EN)

Oyun içi sohbete yazdığınız **Türkçe** metni tek tuşla (varsayılan **F8**) seçip kopyalar,
bir LLM ile **rekabetçi Valorant terminolojisine** uygun şekilde İngilizceye çevirir ve
geri yapıştırır. Enter'a siz basarsınız.

```
Chat'e yaz  ─►  F8  ─►  [seç + kopyala]  ─►  çeviri  ─►  [İngilizcesi yapışır]  ─►  Enter
                                             │
                        yerel sözlük (0 ms) ─┤ sık kalıplar API'ye hiç gitmez
                        önbellek     (0 ms) ─┤ aynı cümlenin tekrarı
                        API       (~1–2 sn) ─┘ geri kalan her şey
```

Sağlayıcı bağımsızdır: OpenAI uyumlu her endpoint çalışır (Xiaomi MiMo, DeepSeek, ...).

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
4. **`config.ini`** dosyasını açın ve API anahtarınızı yazın:
   ```ini
   [api]
   key = sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   (Sağlayıcı seçimi için aşağıdaki **Sağlayıcı seçimi** tablosuna bakın.)
5. **Kurulumu doğrulayın** — oyuna girmeden anahtar/model/endpoint testi:
   ```bat
   .venv\Scripts\python.exe check_api.py
   ```
6. **`run.bat`** dosyasına çift tıklayın. (Yönetici izni ister — **Evet** deyin; oyuna giriş gönderebilmek için gerekli.)

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
| `api.key` | API anahtarı | — |
| `api.base_url` | Sağlayıcı endpoint'i (OpenAI uyumlu her sağlayıcı) | `https://api.xiaomimimo.com/v1` |
| `api.model` | Model | `mimo-v2.6-flash` |
| `api.temperature` | Düşük = daha tutarlı/sabit çıktı (bkz. sıcaklık kıyası) | `0.3` |
| `api.max_tokens` | Yanıt sınırı; dar tutmak modelin gevezelemesini engeller | `256` |
| `translation.source_lang` / `target_lang` | Çeviri yönü | `Turkish` → `English` |
| `hotkey.translate` | Kısayol (`f8`, `f9`, `ctrl+space`, `alt+x`...) | `f8` |
| `hotkey.suppress` | Tuşu oyuna iletme | `true` |
| `behavior.auto_send` | Çeviri sonrası otomatik Enter | `false` |
| `behavior.restore_clipboard` | İşlem sonrası eski panoyu geri yükle | `true` |
| `behavior.play_sound` | Sesli geri bildirim | `true` |
| `behavior.use_local_dict` | Sık kalıpları API'siz, anlık çevir (`callouts.py`) | `true` |
| `behavior.cache` | Aynı cümlenin tekrarını önbellekten ver | `true` |

### Sağlayıcı seçimi

OpenAI uyumlu her sağlayıcı çalışır — `base_url` + `model` değiştirmek yeterli:

| Sağlayıcı | `base_url` | `model` |
|---|---|---|
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` — **oyun içi için en hızlı**, bkz. ölçüm |
| Xiaomi MiMo | `https://api.xiaomimimo.com/v1` | `mimo-v2.6-pro` (MiMo'nun en hızlısı), `mimo-v2.6-flash` |

> MiMo'nun model adları noktalıdır (`mimo-v2.6-flash`, `mimo-v2-flash` **değil**).
> Geçerli listeyi `check_api.py` yazdırır; `mimo-v2.5-*` modelleri kullanımdan
> kaldırılıyor.

Anahtar/endpoint/model üçlüsünün gerçekten çalıştığını **oyuna girmeden** doğrulamak için:

```bat
.venv\Scripts\python.exe check_api.py
```

Bu araç anahtarı doğrular, sağlayıcıdaki **kullanılabilir modelleri listeler**, gerçek
prompt'la tek cümle çevirip gecikmeyi ölçer ve yerel sözlüğü sınar.

### Çeviri kalitesi nasıl sağlanıyor?

`translator.py` içindeki sistem promptu, modele **rekabetçi Valorant comms** tonu verir:
ajan/harita/silah isimleri korunur, Türkçe oyun argosu → İngilizce callout sözlüğüyle
eşlenir (örn. *“iki kişi A geliyor”* → **“2 pushing A”**, *“spike ektim”* → **“planted”**),
çıktı kısa ve net tutulur. Promptu kendi takım jargonunuza göre düzenleyebilirsiniz.

### Gecikme nasıl düşürülüyor?

Oyun içinde 2 saniye uzun bir süre. Üç katmanlı bir yol izlenir — en hızlısı önce:

| Katman | Gecikme | Kapsam (`tests/` korpusunda ölçülmüş, 837 gerçek mesaj) |
|---|---|---|
| **Yerel sözlük** (`callouts.py`) | **0 ms** | **%18,5** — 341 kalıp |
| **Önbellek** | **0 ms** | Aynı cümlenin tekrarı (comms çok tekrar eder) |
| **API** | sağlayıcıya göre | Geri kalan ~%80 — serbest cümleler |

Sözlük kapsamı kategoriye göre çok değişir, çünkü kalıplar **gerçek korpustan**
çıkarıldı (oyuncuların varsaydığım değil, gerçekten yazdığı biçimler — `smoke at`,
`a gelin`, `ulti var`):

| Kategori | Kapsam |
|---|---|
| `korunacak-kelime` (`op`, `eco`, `full buy`, `drop`...) | %100 |
| `kisa-komut` (`a boş`, `defuse bas`, `heal at`...) | %81 |
| `kisa-komut-2` (tek kelimelik emirler) | %60 |
| Uzun taktik cümleler | %0 — API'ye gider, doğrusu da bu |

Ayrıca her çeviride yeni TCP+TLS el sıkışması yapılmaz: tek bir `requests.Session`
bağlantıyı canlı tutar ve açılışta bir kez ısıtılır (çağrı başına ~200–400 ms).

Yerel sözlük **tutucu** tutulur: yalnızca tek anlamlı kalıplar girer. Tek başına
çok anlamlı tek kelimeler (`çık`, `kur`, `vur`, `bırak`) bilerek dışarıda —
yanlış bir anlık cevap, yavaş ama doğru bir cevaptan kötüdür. Kendi jargonunuzu
tabloya ekleyebilirsiniz (anahtarlar `normalize()` geçmiş halde: küçük harf,
Türkçe harfler ASCII'ye katlanmış, noktalama atılmış).

### Sağlayıcı gecikmesi (ölçülmüş)

Oyun içi kullanılabilirliği **medyan değil, kuyruk** belirler: 2 sn medyan iyi
görünür ama her 10 çağrıdan biri 10 sn sürerse araç işe yaramaz. Aşağıdaki
ölçüm **sıralı** isteklerle yapıldı (oyunda tek seferde tek istek olur):

| Model | medyan | p90 | en kötü |
|---|---|---|---|
| `deepseek-chat` (bkz. `benchmark_results.md`) | **1282 ms** | — | **1516 ms** |
| `mimo-v2.6-pro` | 3781 ms | — | 11629 ms |
| `mimo-v2.6-flash` | 5109 ms | 9724 ms | 14097 ms |
| `mimo-v2.6-pro-ultraspeed` | 8159 ms | — | 27831 ms |

DeepSeek yalnızca ~3x daha hızlı değil, **öngörülebilir**: en kötüsü 1,5 sn.
MiMo modellerinin kuyruğu 11–28 sn'ye çıkıyor, ki oyun ortasında kullanılamaz.
Çeviri kalitesi üç MiMo modelinde de birbirine yakın, yani `pro-ultraspeed`'in
adı yanıltıcı — ölçümde en yavaşı o.

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

### Büyük ölçekli toplu test

`batch_translate.py`, `tests/phrases.txt` içindeki yüzlerce gerçek oyun-içi mesajı
**eşzamanlı** çevirir (tekrarlar önbelleğe alınır), gecikme ölçer, sorunlu çıktıları
(Türkçe sızıntısı / boş / aşırı uzun) otomatik işaretler ve tümünü `tests/results.md`'ye yazar:

```bat
.venv\Scripts\python.exe batch_translate.py
```

Kendi dosyanızla da çalışır (ör. taktiksel set): `batch_translate.py tests/tactical_phrases.txt`

Son toplu ölçüm: **790 satır / 770 benzersiz çağrı, ort. ~1.2 sn gecikme, 0 otomatik işaret.**
Karmaşık taktiksel cümlelerde (oyala / zaman kazan / bait / default okuma) kalite **~9.7/10**.

### Sıcaklık kıyası

`temp_compare.py` aynı cümleyi farklı sıcaklıklarda tekrar tekrar çevirip çıktı kararlılığını ölçer
(`tests/temp_compare.md`). Sonuç: kalite 0.3 / 0.7 / 1.0'da **eşit**, ama **0.3 en tutarlı**
(aynı cümlede en sık çıktı oranı %60 vs 1.0'da %29). Bu yüzden varsayılan `temperature = 0.3`.

---

## Sorun giderme

| Sorun | Çözüm |
|---|---|
| Oyunda hiçbir şey olmuyor | `run.bat`'i **yönetici olarak** çalıştırın. Vanguard yüksek yetkide çalıştığı için şart. |
| Tam ekranda çalışmıyor | Oyunu **Kenarlıksız Pencere (Borderless)** moduna alın. |
| “Pano boş” uyarısı | Önce sohbete metin yazın; F8'e sohbet kutusu **odaktayken** basın. |
| F8 oyunda başka şey yapıyor | `config.ini`'de `suppress = true` olsun veya başka kısayol seçin. |
| 401 hatası | API anahtarı yanlış, ya da anahtar `base_url` ile uyuşmuyor → `check_api.py` çalıştırın. |
| 402 hatası | Sağlayıcıdaki bakiyeniz bitmiş. |
| 404 hatası | `base_url` veya `model` adı yanlış → `check_api.py` kullanılabilir modelleri listeler. |
| 429 hatası | Hız sınırı; birkaç saniye bekleyin. |
| Çeviri yavaş | Sağlayıcıya bağlı — bkz. **Sağlayıcı gecikmesi (ölçülmüş)**. MiMo'da kuyruk 11–28 sn'ye çıkabiliyor; en hızlı seçenek `deepseek-chat`. Sık kullandığınız kalıpları `callouts.py`'ye eklemek o satırları tamamen API'den çıkarır (0 ms). |

---

## Güvenlik

- **API anahtarınızı asla paylaşmayın / commit etmeyin.** `config.ini` `.gitignore` ile hariç tutulur;
  repoda yalnızca `config.example.ini` (yer tutucu) bulunur.
- Anahtarınız bir yerde açığa çıktıysa (sohbete yapıştırmak, ekran paylaşımı, log) **hemen yenileyin**:
  MiMo → <https://platform.xiaomimimo.com> · DeepSeek → <https://platform.deepseek.com/api_keys>
- `check_api.py` anahtarı ekrana yazmaz, yalnızca maskeler (`sk-abc...1234`).

## Lisans

MIT — bkz. [LICENSE](LICENSE).
