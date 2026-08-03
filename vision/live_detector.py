"""
live_detector.py — Canlı Kamera veya Videodan YOLOv8 ile İnsan Tespiti
İP6: Canlı İnsan Tespiti

Kullanım:
    # Web kamerası ile başlatmak için (Varsayılan):
    python vision/live_detector.py
    
    # Belirli bir video dosyası ile başlatmak için:
    python vision/live_detector.py --source video.mp4
"""

import cv2
import argparse
import time
import sys
from ultralytics import YOLO

# ─── Ayarlar ───────────────────────────────────────────────
DEFAULT_MODEL = "yolov8n.pt"
PERSON_CLASS_ID = 0  # COCO veri setinde "person" (insan) sınıfı ID'si 0'dır.
# ────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 Canlı İnsan Tespiti")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="YOLO model ağırlıkları (.pt)")
    parser.add_argument("--source", default="0", help="Kamera indexi (örn: 0) veya video dosya yolu")
    parser.add_argument("--conf", type=float, default=0.4, help="Güven (confidence) eşiği")
    parser.add_argument("--width", type=int, default=640, help="Kamera genişliği")
    parser.add_argument("--height", type=int, default=480, help="Kamera yüksekliği")
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Kaynak kameraysa int'e çevir
    source = args.source
    try:
        source = int(source)
    except ValueError:
        pass  # Video dosyası yolu
        
    # YOLO modelini yükle
    print(f"[YOLO] Model yükleniyor: {args.model}")
    try:
        model = YOLO(args.model)
    except Exception as e:
        print(f"[HATA] Model yüklenemedi: {e}")
        sys.exit(1)
        
    # Kamera / Video kaynağını aç
    print(f"[YAYIN] Görüntü kaynağı açılıyor: {source}")
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[HATA] Görüntü kaynağı açılamadı!")
        sys.exit(1)
        
    # Kamera çözünürlüğünü ayarla (Sadece fiziksel kameralar için geçerlidir)
    if isinstance(source, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        
    print("[BİLGİ] Canlı tespit başladı. Kapatmak için görüntü penceresindeyken 'q' tuşuna bas.")
    
    # FPS hesaplama değişkenleri
    prev_time = 0
    fps = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # Video bittiyse başa sar
                if isinstance(source, str):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    print("[UYARI] Kamera karesi okunamadı!")
                    break
                    
            # YOLO Çıkarımı
            # Sadece performansı artırmak için `classes=[0]` parametresiyle YOLO'nun sadece insanları çıkarmasını sağlıyoruz.
            results = model.predict(source=frame, conf=args.conf, classes=[PERSON_CLASS_ID], verbose=False)
            
            # Algılanan nesneleri çerçeve içine al
            annotated_frame = frame.copy()
            
            if len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    # Koordinatları al [x1, y1, x2, y2]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    # İnsan etrafına yeşil kutu çiz
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Etiket ekle
                    label = f"Insan: {conf:.2f}"
                    cv2.putText(annotated_frame, label, (x1, max(y1 - 10, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                
            # FPS Hesapla
            curr_time = time.time()
            time_diff = curr_time - prev_time
            if time_diff > 0:
                fps = 1.0 / time_diff
            prev_time = curr_time
            
            # FPS bilgisini sol üst köşeye yazdır
            cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        
            # Sonucu ekranda göster
            cv2.imshow("YOLOv8 Canli Insan Tespiti (Kapatmak icin 'q')", annotated_frame)
            
            # 'q' tuşuna basıldığında döngüden çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n[BİLGİ] Kullanıcı tarafından durduruldu.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[BİLGİ] Kaynaklar serbest bırakıldı, pencere kapatıldı.")


if __name__ == "__main__":
    main()
