"""
subscriber.py — MQTT frame abone/test scripti
İP1: Bitti kriteri — bu script frame'leri alıyorsa İP1 tamamdır!

Kullanım:
    python infra/subscriber.py
    python infra/subscriber.py --show    # frame'leri ekranda göster
    python infra/subscriber.py --save    # frame'leri dosyaya kaydet
"""

import paho.mqtt.client as mqtt
import base64
import json
import time
import argparse
import sys
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# ─── Ayarlar ───────────────────────────────────────────────
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC       = "camera/frame"
# ────────────────────────────────────────────────────────────

stats = {
    "count":    0,
    "last_ts":  None,
    "fps":      0.0,
    "latency":  [],   # ms cinsinden son 10 frame gecikmesi
}


def parse_args():
    parser = argparse.ArgumentParser(description="MQTT frame test abonesi")
    parser.add_argument("--host",  default=BROKER_HOST)
    parser.add_argument("--port",  type=int, default=BROKER_PORT)
    parser.add_argument("--topic", default=TOPIC)
    parser.add_argument("--show",  action="store_true",
                        help="Frame'leri OpenCV pencerede göster")
    parser.add_argument("--save",  action="store_true",
                        help="Frame'leri captured/ klasörüne kaydet")
    return parser.parse_args()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Bağlandı: {userdata['host']}:{userdata['port']}")
        print(f"[MQTT] Abone olundu: {userdata['topic']}")
        client.subscribe(userdata["topic"])
    else:
        print(f"[MQTT] Bağlantı hatası, kod: {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    recv_ts = time.time()

    try:
        data = json.loads(msg.payload)
    except json.JSONDecodeError:
        print("[UYARI] JSON parse hatası")
        return

    # Gecikme ölçümü
    send_ts  = data.get("ts", recv_ts)
    latency  = (recv_ts - send_ts) * 1000   # ms
    stats["latency"].append(latency)
    if len(stats["latency"]) > 10:
        stats["latency"].pop(0)

    # FPS hesabı
    if stats["last_ts"] is not None:
        dt = recv_ts - stats["last_ts"]
        stats["fps"] = 1.0 / dt if dt > 0 else 0
    stats["last_ts"] = recv_ts
    stats["count"]  += 1

    seq = data.get("seq", "?")
    w   = data.get("frame_w", "?")
    h   = data.get("frame_h", "?")
    avg_lat = sum(stats["latency"]) / len(stats["latency"])

    print(f"[FRAME #{stats['count']:05d}] seq={seq} | {w}x{h} | "
          f"FPS≈{stats['fps']:.1f} | gecikme≈{avg_lat:.1f}ms")

    # ── Opsiyonel: frame decode ──
    if userdata.get("show") or userdata.get("save"):
        if not CV2_AVAILABLE:
            print("[UYARI] OpenCV kurulu değil (pip install opencv-python)")
            return

        try:
            jpg_bytes = base64.b64decode(data["frame"])
            arr       = np.frombuffer(jpg_bytes, dtype=np.uint8)
            frame     = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"[UYARI] Frame decode hatası: {e}")
            return

        if userdata.get("show"):
            cv2.putText(frame, f"FPS: {stats['fps']:.1f} | Gecikme: {avg_lat:.0f}ms",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("MQTT Frame — ESC ile kapat", frame)
            if cv2.waitKey(1) & 0xFF == 27:   # ESC
                client.disconnect()

        if userdata.get("save"):
            import os
            os.makedirs("captured", exist_ok=True)
            fname = f"captured/frame_{stats['count']:05d}.jpg"
            cv2.imwrite(fname, frame)


def main():
    args   = parse_args()
    udata  = {
        "host":  args.host,
        "port":  args.port,
        "topic": args.topic,
        "show":  args.show,
        "save":  args.save,
    }

    client = mqtt.Client(userdata=udata)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.host, args.port, keepalive=60)
    except ConnectionRefusedError:
        print(f"[HATA] Broker'a bağlanılamadı ({args.host}:{args.port})")
        print("       Mosquitto çalışıyor mu? → 'mosquitto' komutunu başka bir terminalde çalıştır.")
        sys.exit(1)

    print(f"[ABONE] {args.topic} topic'ini dinliyor... (Ctrl+C ile dur)")
    print(f"        --show={args.show} | --save={args.save}")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n[ABONE] Durduruldu. Toplam alınan frame: {stats['count']}")
        if CV2_AVAILABLE:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
