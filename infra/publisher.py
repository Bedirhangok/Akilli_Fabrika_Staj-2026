"""
publisher.py — Webcam → MQTT frame yayıncı
İP1: Ortak altyapı

Kullanım:
    python infra/publisher.py
    python infra/publisher.py --source 0          # webcam (varsayılan)
    python infra/publisher.py --source video.mp4  # video dosyası
    python infra/publisher.py --fps 30            # FPS sınırı
"""

import cv2
import paho.mqtt.client as mqtt
import base64
import json
import time
import argparse
import sys

# ─── Ayarlar ───────────────────────────────────────────────
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC       = "camera/frame"
QUALITY     = 80       # JPEG kalitesi (0-100), düşürdükçe bant genişliği azalır
# ────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(description="Webcam → MQTT frame yayıncı")
    parser.add_argument("--source", default=0,
                        help="Kaynak: 0=webcam, 1=ikinci kamera, video.mp4")
    parser.add_argument("--fps", type=float, default=30,
                        help="Hedef FPS (varsayılan: 30)")
    parser.add_argument("--host", default=BROKER_HOST,
                        help="MQTT broker adresi")
    parser.add_argument("--port", type=int, default=BROKER_PORT,
                        help="MQTT broker portu")
    parser.add_argument("--topic", default=TOPIC,
                        help="Yayın topic'i")
    parser.add_argument("--width", type=int, default=640,
                        help="Frame genişliği (px)")
    parser.add_argument("--height", type=int, default=480,
                        help="Frame yüksekliği (px)")
    return parser.parse_args()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Broker'a bağlandı: {userdata['host']}:{userdata['port']}")
    else:
        print(f"[MQTT] Bağlantı hatası, kod: {rc}")
        sys.exit(1)


def on_disconnect(client, userdata, rc):
    print(f"[MQTT] Bağlantı kesildi (kod: {rc}) — yeniden bağlanılıyor...")


def main():
    args = parse_args()

    # Kaynak: sayı ise int'e çevir (webcam index)
    source = args.source
    try:
        source = int(source)
    except (ValueError, TypeError):
        pass  # video dosyası — string kalır

    # ── MQTT bağlantısı ──
    client = mqtt.Client(userdata={"host": args.host, "port": args.port})
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()

    # ── Kamera / video aç ──
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[HATA] Kaynak açılamadı: {source}")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    frame_interval = 1.0 / args.fps
    frame_count    = 0
    dropped        = 0
    print(f"[YAYINcı] Kaynak={source} | {args.width}x{args.height} | "
          f"Hedef {args.fps} FPS | Topic={args.topic}")
    print("  Durdurmak için Ctrl+C")

    try:
        while True:
            t0 = time.time()

            ret, frame = cap.read()
            if not ret:
                if isinstance(source, str):
                    print("[BİLGİ] Video bitti — döngüye alınıyor...")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    print("[UYARI] Frame okunamadı, atlanıyor...")
                    dropped += 1
                    continue

            # JPEG encode → base64
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, QUALITY]
            _, buf = cv2.imencode(".jpg", frame, encode_params)

            payload = {
                "ts":       time.time(),           # Unix zaman damgası (saniye)
                "frame_w":  frame.shape[1],
                "frame_h":  frame.shape[0],
                "seq":      frame_count,
                "frame":    base64.b64encode(buf).decode("ascii"),
            }

            result = client.publish(args.topic, json.dumps(payload), qos=0)
            frame_count += 1

            # FPS istatistik (her 100 frame'de bir)
            if frame_count % 100 == 0:
                fps_actual = 100 / (time.time() - t0 + 1e-9) if frame_count == 100 else None
                print(f"[İSTATİSTİK] Gönderilen={frame_count} | Atlanan={dropped}")

            # FPS limitle
            elapsed = time.time() - t0
            sleep_t = frame_interval - elapsed
            if sleep_t > 0:
                time.sleep(sleep_t)

    except KeyboardInterrupt:
        print(f"\n[YAYINcı] Durduruldu. Toplam frame: {frame_count}, atlanan: {dropped}")
    finally:
        cap.release()
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
