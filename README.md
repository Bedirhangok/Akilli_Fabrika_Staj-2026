# 🤖 bgok-patrol-vision-2026

**Fabrika Nesne Algılama + Aktif Hedef Takibi**

> Staj Projesi — Bedirhan Gök · BTÜ · 03_Gama Grubu · 2026

---

## 📌 Proje Tanımı

Robot köpek üstündeki pan-tilt kameranın **"gözü"**: sahnedeki kritik nesneleri tespit eder ve seçilen hedefi kadrajda tutmak için pan-tilt kontrolüne yön sinyali üretir.

**Amaç:**
- Fabrika ortamı nesnelerini (insan, forklift, KKD/baret-yelek, engel) **gerçek zamanlı** tespit etmek
- Tespit edilen hedefi izleyip kadraj merkezinden sapmayı `(dx, dy)` piksel ofseti olarak KONTROL modülünün PID döngüsüne beslemek (kapalı çevrim aktif takip)
- Çıktı: ≥15 Hz `vision/target_offset` mesajı (MQTT)

---

## 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Tespit | YOLOv8 / YOLOv11 |
| Takip | ByteTrack / Hybrid-SORT (CSRT/KCF + periyodik YOLO re-init) |
| Görüntü | OpenCV |
| Haberleşme | MQTT (Mosquitto broker) |
| Eğitim | Google Colab (T4 GPU) |
| Çıkarım | Edge cihaz |
| Dil | Python 3.10+ |

---

## 📦 Veri Setleri

| Set | Konu | Kaynak |
|-----|------|--------|
| COCO | İnsan (person) | Hazır ağırlıklar |
| SH17 | KKD (baret/yelek) — 8.099 görüntü, 17 sınıf | [GitHub](https://github.com/ahmadmughees/SH17dataset) |
| LOCO | Forklift, palet, transpalet | [TUM-FML](https://github.com/tum-fml/loco) |
| Kendi | Pan-tilt kamera kayıtları | — |

---

## 📁 Klasör Yapısı

```
bgok-patrol-vision-2026/
├── infra/
│   ├── publisher.py          # MQTT frame yayıncı (İP1)
│   ├── subscriber.py         # Test abonesi (İP1)
│   ├── recorder.py           # Kayıt aracı (İP2)
│   └── replayer.py           # Replay aracı (İP2)
├── vision/
│   ├── detector.py           # YOLO tespiti (İP3+)
│   ├── tracker.py            # Hibrit tracker (İP8)
│   └── offset_publisher.py   # target_offset yayıncı (İP10)
├── docs/
│   ├── target_offset_schema.md  # Şema sözleşmesi (İP4)
│   └── literature_summary.md   # Literatür özeti (İP5)
├── data/                     # Veri setleri (gitignore'da)
├── models/                   # Eğitilmiş ağırlıklar (gitignore'da)
├── daily_log.md              # Günlük ilerleme kaydı
└── README.md
```

---

## 🗓️ Haftalık Plan

| Hafta | Tarih | Odak |
|:---:|---|---|
| H1 | 27–31 Tem | Altyapı + literatür + şema dondurma |
| H2 | 3–7 Ağu | Canlı tespit + SH17 fine-tune |
| H3 | 10–14 Ağu | Hibrit tracker + ofset zinciri |
| H4 | 17–21 Ağu | MQTT yayını + 🎉 Kapalı çevrim |
| H5 | 24–28 Ağu | Çoklu sınıf + dayanıklılık |
| H6 | 31 Ağu–4 Eyl | Ablation + demo + final rapor |

---

## 📡 MQTT Şemaları

### `camera/frame` (yayıncı → tüm modüller)
```json
{ "ts": 1722000000.123, "frame": "<base64 JPEG>" }
```

### `vision/target_offset` (bu modül → KONTROL)
```json
{
  "ts": 1722000000.456,
  "track_id": 1,
  "class": "person",
  "conf": 0.92,
  "dx": -45,
  "dy": 12,
  "frame_w": 640,
  "frame_h": 480
}
```

---

## 🚀 Başlarken

```bash
# Ortam kurulumu
conda create -n patrol-vision python=3.10
conda activate patrol-vision
pip install ultralytics opencv-python paho-mqtt

# Mosquitto broker başlat
mosquitto

# Frame yayıncıyı başlat
python infra/publisher.py

# Test abonesi (başka terminal)
python infra/subscriber.py
```

---

## 📋 İş Paketleri

Detaylı iş paketleri için: [Bedirhan_is_paketleri.md](docs/is_paketleri.md)

| # | Hafta | Paket | Durum |
|---|:---:|-------|:---:|
| İP1 | H1 | Ortak altyapı (broker + yayıncı) | ⬜ |
| İP2 | H1 | Kayıt/replay aracı | ⬜ |
| İP3 | H1 | İlk YOLO tespiti | ⬜ |
| İP4 | H1 | `target_offset` şema dondur | ⬜ |
| İP5 | H1 | Mini literatür | ⬜ |
| İP6 | H2 | Canlı insan tespiti ≥10 FPS | ⬜ |
| İP7 | H2 | SH17 fine-tune (mAP tablosu) | ⬜ |
| İP8 | H3 | Hibrit tracker | ⬜ |
| İP9 | H3 | Hedef seçimi + (dx,dy) | ⬜ |
| İP10 | H4 | MQTT ofset yayını ≥15 Hz | ⬜ |
| İP11 | H4 | Takip metriği (MOTA/IDF1) | ⬜ |
| İP12 | H4 | 🎉 Kapalı çevrim | ⬜ |
| İP13 | H5 | Çoklu sınıf genişleme | ⬜ |
| İP14 | H5 | Zor koşullar (ışık/titreşim) | ⬜ |
| İP15 | H6 | Yanlış alarm ayarı | ⬜ |
| İP16 | H6 | Ablation + final teslim | ⬜ |

---

## ⚠️ Önemli Notlar

- **Fabrika görüntüsü repoya yüklenmez** — sadece açık/sentetik veri
- Commit formatı: `İPx: kısa açıklama` (örn. `İP1: mosquitto publisher calisiyor`)
- Takıldığında → 2 saat kural → not düş, danışmana sor
- **İP10 ve İP12 feda edilemez** — modülün varlık sebebi bunlar

---

*Çatı proje: Pan-Tilt Devriye Robotu · Grup: 03_Gama · BTÜ · 2026*
