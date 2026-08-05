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
import json
import paho.mqtt.client as mqtt
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
    parser.add_argument("--mqtt-host", default="localhost", help="MQTT broker adresi")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT broker portu")
    parser.add_argument("--topic", default="vision/target_offset", help="MQTT yayın topic'i")
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
    
    # MQTT İstemci Kurulumu
    client = mqtt.Client()
    try:
        client.connect(args.mqtt_host, args.mqtt_port, 60)
        client.loop_start()
        print(f"[MQTT] {args.mqtt_host}:{args.mqtt_port} adresine bağlanıldı. Topic: {args.topic}")
    except Exception as e:
        print(f"[MQTT HATA] Broker'a bağlanılamadı: {e}")
        # Bağlanamazsa da program devam etsin diye sys.exit koymuyoruz
    
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
            # Eğittiğimiz yeni modelin tüm sınıflarını görebilmek için sınıf kısıtlaması (classes=...) yapmıyoruz.
            # predict yerine track kullanıyoruz (Tracker: bytetrack otomatik çalışır)
            results = model.track(source=frame, conf=args.conf, persist=True, verbose=False)
            
            # Algılanan nesneleri çerçeve içine al
            annotated_frame = frame.copy()
            frame_h, frame_w = annotated_frame.shape[:2]
            
            best_target = None
            highest_conf = -1.0
            
            if len(results) > 0 and results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes
                for i, box in enumerate(boxes):
                    # Koordinatları al [x1, y1, x2, y2]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    track_id = int(boxes.id[i]) if boxes.id is not None else -1
                    
                    # Hedef seçimi: Şimdilik en yüksek güven oranına sahip nesneyi ana hedef kabul ediyoruz
                    if conf > highest_conf:
                        highest_conf = conf
                        best_target = {
                            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                            "conf": conf, "cls_name": cls_name, "track_id": track_id
                        }
                    
                    # Etrafına yeşil kutu çiz
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Dinamik Sınıf Etiketi ekle (ID ile birlikte)
                    label = f"ID:{track_id} {cls_name}: {conf:.2f}"
                    cv2.putText(annotated_frame, label, (x1, max(y1 - 10, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                
            # Eğer sahnede takip edilen bir hedef varsa ofset hesapla ve yayınla
            if best_target is not None:
                x1, y1, x2, y2 = best_target["x1"], best_target["y1"], best_target["x2"], best_target["y2"]
                
                # Hedef merkezi
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # Kadraj merkezi
                frame_cx = int(frame_w / 2)
                frame_cy = int(frame_h / 2)
                
                # Sapma (dx, dy)
                dx = cx - frame_cx
                dy = cy - frame_cy
                
                # Hedefin üzerine merkez noktasını ve sapmayı çiz (Robotun gözü)
                cv2.circle(annotated_frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.line(annotated_frame, (frame_cx, frame_cy), (cx, cy), (255, 0, 0), 2)
                cv2.putText(annotated_frame, f"dx:{dx} dy:{dy}", (cx + 10, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # MQTT Mesajı Oluştur ve Yayınla
                payload = {
                    "ts": time.time(),
                    "track_id": best_target["track_id"],
                    "class": best_target["cls_name"],
                    "conf": best_target["conf"],
                    "dx": dx,
                    "dy": dy,
                    "frame_w": frame_w,
                    "frame_h": frame_h
                }
                client.publish(args.topic, json.dumps(payload), qos=0)
            else:
                # Hedef yoksa Bekleme Modu (track_id: -1 gönder)
                payload = {
                    "ts": time.time(), "track_id": -1, "class": "", "conf": 0.0,
                    "dx": 0, "dy": 0, 
                    "frame_w": frame_w if 'frame_w' in locals() else args.width, 
                    "frame_h": frame_h if 'frame_h' in locals() else args.height
                }
                try:
                    client.publish(args.topic, json.dumps(payload), qos=0)
                except:
                    pass
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
        try:
            client.loop_stop()
            client.disconnect()
        except:
            pass
        print("[BİLGİ] Kaynaklar serbest bırakıldı, pencere kapatıldı.")


if __name__ == "__main__":
    main()
