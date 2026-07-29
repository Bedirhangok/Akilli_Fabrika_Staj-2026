# 📡 MQTT target_offset İletişim Sözleşmesi (v1.0)
**Modül:** VİZYON → KONTROL  
**Tarih:** 30.07.2026  
**Durum:** Donduruldu (Frozen) ❄️

Bu belge, **Fabrika Nesne Algılama + Aktif Hedef Takibi (VİZYON)** modülü tarafından üretilen ve **Pan-Tilt Kontrol (KONTROL)** modülü tarafından tüketilecek olan hedef sapma mesaj şemasını tanımlar.

---

## 📬 MQTT Topic
- **Topic:** `vision/target_offset`
- **QoS:** `0` (En düşük gecikme için)
- **Frekans:** `≥15 Hz` (Canlı kamera akışına göre hedeflenen: 30 Hz)

---

## 📄 Mesaj Şeması (JSON)

Her mesaj aşağıdaki formatta tek satırlık bir JSON objesi olmalıdır:

```json
{
  "ts": 1722300000.123,
  "track_id": 1,
  "class": "person",
  "conf": 0.92,
  "dx": -45,
  "dy": 12,
  "frame_w": 640,
  "frame_h": 480
}
```

### 🗂️ Alan Açıklamaları

| Alan Adı | Tip | Açıklama | Örnek |
|:---|:---:|:---|:---:|
| `ts` | float | Mesajın oluşturulduğu anın Unix Zaman Damgası (saniye cinsinden Epoch). Uçtan uca gecikmeyi ölçmek için kullanılır. | `1722300000.123` |
| `track_id` | int | Takip edilen nesnenin eşsiz ID'si (Tracker ID). Hedef kaybolup tekrar bulunmadığı sürece bu ID sabit kalmalıdır. | `1` |
| `class` | string | Algılanan nesnenin sınıfı. v1 için sadece `"person"` (insan) desteklenir. İleride `"forklift"`, `"helmet"`, `"vest"`, `"obstacle"` eklenecektir. | `"person"` |
| `conf` | float | Tespitin güven skoru (`0.0` ile `1.0` arasında). | `0.92` |
| `dx` | int | Nesne merkezinin kadraj merkezine göre yatay piksel sapması. `(Nesne_X - Kadraj_X_Merkez)` | `-45` |
| `dy` | int | Nesne merkezinin kadraj merkezine göre dikey piksel sapması. `(Nesne_Y - Kadraj_Y_Merkez)` | `12` |
| `frame_w` | int | İşlenen video karesinin piksel genişliği. | `640` |
| `frame_h` | int | İşlenen video karesinin piksel yüksekliği. | `480` |

---

## 🎯 dx ve dy Koordinat Ekseni Detayları

Yön kontrollerinin (Pan/Tilt) PID döngüsüne doğru beslenebilmesi için eksen yönleri aşağıdaki gibidir:

1. **Kadraj Merkezi:**
   - $X_{merkez} = \text{frame\_w} / 2$
   - $Y_{merkez} = \text{frame\_h} / 2$
2. **Yatay Eksen (dx - Pan sapması):**
   - Eğer nesne merkezde ise: `dx = 0`
   - Nesne kadrajın **solunda** ise: `dx < 0` (Örn: `-50` px) -> *Pan motoru sola dönmeli*
   - Nesne kadrajın **sağında** ise: `dx > 0` (Örn: `+50` px) -> *Pan motoru sağa dönmeli*
3. **Dikey Eksen (dy - Tilt sapması):**
   - Eğer nesne merkezde ise: `dy = 0`
   - Nesne kadrajın **yukarısında** ise: `dy < 0` (Örn: `-30` px) -> *Tilt motoru yukarı/aşağı (kalibrasyona göre) hareket etmeli*
   - Nesne kadrajın **aşasında** ise: `dy > 0` (Örn: `+30` px)

---

## ⚠️ Bekleme Modu (Hedef Yoksa)

Sahnede takip edilen aktif bir hedef yoksa, KONTROL modülünün motorları durdurması veya arama moduna geçmesi için VİZYON modülü **mesaj yayınlamayı durdurur** veya `track_id: -1` gönderir. KONTROL modülü 1 saniyeden uzun süre mesaj almazsa hedefi kayıp kabul etmelidir.
