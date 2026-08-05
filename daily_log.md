# 📓 Günlük İlerleme Kaydı — Bedirhan Gök

> Repo: `bgok-patrol-vision-2026` · Başlangıç: 27.07.2026 · Bitiş: 04.09.2026
> Commit formatı: `İPx: kısa açıklama`

---

## Hafta 2 — 3–7 Ağustos 2026

### 📅 5 Ağustos 2026 (Çarşamba)

**Aktif İş Paketleri:** İP7, İP8, İP9, İP10

**Bugün yapılanlar:**
- [x] Kaggle üzerinde `shlokraval/ppe-dataset-yolov8` veri seti ile YOLOv8 fine-tune eğitimi başarıyla tamamlandı (İP7).
- [x] Eğitilen `best.pt` ağırlığı `live_detector.py`'ye entegre edildi ve sınıf isimleri (Baret, Yelek vb.) dinamik hale getirildi.
- [x] YOLOv8'in yerleşik ByteTrack algoritması aktif edilerek Hedef Takibi (Tracker) sağlandı (İP8).
- [x] En yüksek güven skoruna sahip nesne ana hedef seçilerek kameranın tam merkezinden hedefe olan (dx, dy) sapma miktarı piksel cinsinden hesaplandı (İP9).
- [x] Hesaplanan dx, dy değerleri MQTT `vision/target_offset` kanalı üzerinden ~20 FPS (≥15 Hz hedefi aşılarak) başarıyla yayınlandı (İP10).

---

### 📅 4 Ağustos 2026 (Salı)

**Aktif İş Paketi:** İP7 — SH17 fine-tune

**Bugün yapılanlar:**
- [x] Kaggle ortamında eğitim için `vision/train.py` dosyası API anahtarı istemeyecek şekilde (otomatik ortam algılamalı) güncellendi.
- [x] SH17 veri seti Kaggle'dan kaldırıldığı için uygun alternatif olan `shlokraval/ppe-dataset-yolov8` belirlendi ve eğitime hazırlık yapıldı.

---

### 📅 3 Ağustos 2026 (Pazartesi)

**Aktif İş Paketi:** İP6 — Canlı insan tespiti

**Bugün yapılanlar:**
- [x] `vision/live_detector.py` scripti geliştirildi.
- [x] Canlı web kamerası üzerinde insan tespiti başarıyla test edildi.
- [x] İşlem hızı ortalama **~30 FPS** ölçülerek bitti kriteri (≥10 FPS) fazlasıyla sağlandı.

---

## Hafta 1 — 27–31 Temmuz 2026

### 📅 31 Temmuz 2026 (Cuma)

**Aktif İş Paketi:** İP5 — Mini literatür

**Bugün yapılanlar:**
- [x] Proje ile ilgili çeşitli makaleler ve akademik yayınlar incelendi.
- [x] İncelenen makaleler literatür özeti dokümanına eklendi.

---

### 📅 30 Temmuz 2026 (Perşembe)

**Aktif İş Paketleri:** İP1, İP2, İP3, İP4, İP5

**Bugün yapılanlar:**
- [x] GitHub repo oluşturuldu: `bgok-patrol-vision-2026`
- [x] README.md ve daily_log.md eklendi.
- [x] `infra/publisher.py` ve `infra/subscriber.py` eklendi (İP1 tamamlandı).
- [x] `infra/recorder.py` ve `infra/replayer.py` eklendi (İP2 tamamlandı).
- [x] `vision/detector.py` eklendi, YOLOv8 entegrasyonu sağlandı (İP3 tamamlandı).
- [x] `docs/target_offset_schema.md` oluşturuldu ve KONTROL modülüyle protokol donduruldu (İP4 tamamlandı).
- [x] `docs/literature_summary.md` 10 adet makale taramasıyla oluşturuldu (İP5 tamamlandı).

**Engel / Not:**
- Mosquitto yerel kurulum gerektirdiği için Windows installer indirildi, yerel olarak kurulması bekleniyor.

---

## Şablon (kopyala-yapıştır)

```
### 📅 [GÜN AY YIL]

**Aktif İş Paketi:** İPx — [isim]

**Bugün yapılanlar:**
- [ ] ...

**Engel / Not:**
- ...

**Yarın:**
- ...
```

---

## İP Durum Özeti

| İş Paketi | Başladı | Bitti | Not |
|:---:|:---:|:---:|-----|
| İP1 | 28.07 | 30.07 | Mosquitto kurulunca test edilecek |
| İP2 | 28.07 | 30.07 | Kayıt/Replay test edildi |
| İP3 | 29.07 | 30.07 | YOLOv8 entegrasyonu hazır |
| İP4 | 30.07 | 30.07 | Sözleşme donduruldu |
| İP5 | 30.07 | 30.07 | Literatür özeti eklendi |
| İP6 | 03.08 | 03.08 | Canlı insan tespiti test edildi (~30 FPS) |
| İP7 | 04.08 | 05.08 | Kaggle (PPE-YOLOv8) ile eğitildi |
| İP8 | 05.08 | 05.08 | ByteTrack ile entegre edildi |
| İP9 | 05.08 | 05.08 | Ofset ve merkez hesaplandı |
| İP10 | 05.08 | 05.08 | 20 FPS ile MQTT üzerinden yayınlandı |
| İP11 | | | |
| İP12 | | | |
| İP13 | | | |
| İP14 | | | |
| İP15 | | | |
| İP16 | | | |
