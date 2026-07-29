# 📚 Mini Literatür Özeti — Algılama & Takip
**Modül:** VİZYON  
**Tarih:** 30.07.2026  
**Hazırlayan:** Bedirhan Gök

Bu doküman, projemizin temelini oluşturan nesne algılama (YOLO), nesne takibi (Tracking-by-Detection) ve aktif kamera yönlendirme (Active Vision) konularında incelenen 10 akademik yayının özetini içermektedir.

---

## 🔍 İncelenen Makaleler Tablosu

| # | Makale Adı | Yazar & Yıl | Ana Yöntem / Katkı | Projedeki Yeri / Önemi |
|---|---|---|---|---|
| 1 | **YOLOv8 / Ultralytics** | Jocher et al. (2023) | En son sürüm tek-aşama (single-stage) nesne detektörü. Çapa-bağımsız (anchor-free) mimari. | Gerçek zamanlı insan, forklift ve KKD tespiti için omurga (backbone) modelimiz. |
| 2 | **ByteTrack: Multi-Object Tracking by Associating Every Detection Box** | Zhang et al. (ECCV 2022) | Güven eşiği düşük (low-score) tespitleri de takip işlemine katarak veri kaybını azaltan MOT algoritması. | Hibrit takip yapımızda YOLO çıktılarını birleştirmek ve ID tutarlılığını sağlamak için kullanılacak. |
| 3 | **Observation-Centric SORT (OC-SORT)** | Cao et al. (2023) | Nesnelerin geçici olarak kaybolduğu durumlardaki (occlusion) Kalman filtresi sapmalarını düzelten tracker. | Fabrika ortamında forkliftlerin veya kolonların arkasından geçen insanların ID'sini kaybetmemek için referans. |
| 4 | **Slicing Aided Hyper Inference (SAHI)** | Akyon et al. (2022) | Büyük çözünürlüklü görüntülerde küçük nesnelerin (örn. uzaktaki baretler) tespiti için dilimleme tabanlı çıkarım yöntemi. | Pan-tilt kameranın uzak mesafelerdeki KKD / baret ve yelekleri kaçırmaması için gerekirse entegre edilecek. |
| 5 | **SH17 Dataset for Safety Helmet Detection** | Mughees et al. (2024) | İş güvenliği ekipmanları (baret, yelek) tespiti için 8099 görsel ve 17 sınıf içeren özel veri seti. | H2'de Colab üzerinde YOLO modelini fine-tune etmek için kullanacağımız temel veri seti. |
| 6 | **Pointer Meters in the Wild: A Robust Benchmark** | Nature Sci. Reports (2024) | Saha koşullarında (ışık yansımaları, eğik açılar) analog göstergelerin ibre açılarının tespiti. | Reşit'in projesindeki analog gösterge okuma (GÖSTERGE) modülü için metodolojik temel. |
| 7 | **EfficientAD: Accurate Visual Anomaly Detection** | WACV (2024) | Edge cihazlarında hızlı çalışabilen hafif görsel anomali tespit mimarisi. | Özgür'ün projesindeki anomali tespit (ANOMALİ) modülünde PatchCore yerine edge performansı için referans. |
| 8 | **STAPLE: Sum of Template and Pixel-wise Learners** | Bertinetto et al. (CVPR 2016) | Renk histogramı ve HOG özelliklerini birleştiren hızlı korelasyon tracker (correlation tracker). | İP8'de geliştireceğimiz "YOLO + OpenCV Tracker" hibrit yaklaşımındaki (P20 deseni) OpenCV izleme omurgası. |
| 9 | **Active Visual Tracking with PID Control** | Various | Kadraj merkezinden piksel sapmasını (dx, dy) kullanarak kamera motorlarını yönlendiren kapalı çevrim kontrol makaleleri. | İP12'de yapacağımız visual tracking → PID → pan-tilt motor kontrol hattının kurumsal teorisi. |
| 10 | **LOCO: Logistics Objects in Context** | TUM-FML (2020) | Forklift, palet ve transpalet gibi depo/lojistik araçlarını içeren veri seti. | Fabrika ortamındaki forklift ve engelleri tespit etmek için kullanacağımız veri seti. |

---

## 💡 Projemize Yansımaları ve Yol Haritası

1. **Çıkarım Hızı (FPS):** Edge cihazda çalışacağımız için YOLOv8-Nano/Small ve hafif bir OpenCV tracker birleşimi (STAPLE/KCF/CSRT) ile **≥15 FPS** hedefine ulaşabileceğimiz doğrulandı.
2. **Kapanma (Occlusion) Çözümü:** İP8'deki tracker implementasyonunda, nesnenin önüne bir şey geldiğinde Kalman filtresi veya korelasyon tracker'ı ile takip devam edecek, periyodik YOLO taraması ile konum doğrulaması yapılacaktır.
3. **Koordinasyon:** GÖSTERGE (Reşit) ve ANOMALİ (Özgür) projelerinin metodolojileri de incelenerek, ekip içi mimari uyumluluk (örneğin MQTT üzerinden frame paylaşımı) optimize edilmiştir.
