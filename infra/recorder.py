"""
recorder.py — MQTT yayınlarını zaman damgalı olarak kaydeder.
İP2: Kayıt/Replay Aracı

Kullanım:
    python infra/recorder.py --output session.jsonl
"""

import paho.mqtt.client as mqtt
import json
import time
import argparse
import sys
import os

# ─── Ayarlar ───────────────────────────────────────────────
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPICS      = [("camera/frame", 0)]  # Kaydedilecek topic'ler ve QoS'leri
# ────────────────────────────────────────────────────────────

record_file = None
message_count = 0


def parse_args():
    parser = argparse.ArgumentParser(description="MQTT Zaman Damgalı Mesaj Kaydedici")
    parser.add_argument("--host", default=BROKER_HOST, help="MQTT broker host")
    parser.add_argument("--port", type=int, default=BROKER_PORT, help="MQTT broker port")
    parser.add_argument("--output", default="session.jsonl", help="Kayıt dosyası (.jsonl)")
    return parser.parse_args()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Broker'a bağlandı. Topic'lere abone olunuyor...")
        for topic, qos in TOPICS:
            client.subscribe(topic, qos=qos)
            print(f"       Abone olundu: {topic}")
    else:
        print(f"[MQTT] Bağlantı hatası: {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    global message_count, record_file
    
    # Gelen mesajı zaman damgasıyla paketle
    record_entry = {
        "rel_time": time.time() - userdata["start_time"], # Göreceli zaman (saniye)
        "topic": msg.topic,
        "payload": msg.payload.decode("utf-8") # JSON string olarak kaydet
    }
    
    # JSON lines formatında dosyaya yaz
    record_file.write(json.dumps(record_entry) + "\n")
    record_file.flush()
    
    message_count += 1
    if message_count % 30 == 0:
        print(f"[KAYIT] {message_count} mesaj kaydedildi...")


def main():
    global record_file
    args = parse_args()
    
    # Çıktı klasörünü kontrol et
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    print(f"[KAYIT] Mesajlar '{args.output}' dosyasına kaydedilecek.")
    record_file = open(args.output, "w", encoding="utf-8")
    
    userdata = {
        "start_time": time.time()
    }
    
    client = mqtt.Client(userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(args.host, args.port, keepalive=60)
    except ConnectionRefusedError:
        print(f"[HATA] Broker'a bağlanılamadı. Mosquitto çalışıyor mu?")
        sys.exit(1)
        
    print("[KAYIT] Dinleme başladı. Durdurmak için Ctrl+C tuşlarına bas.")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n[KAYIT] Durduruldu. Toplam kaydedilen mesaj: {message_count}")
    finally:
        record_file.close()
        client.disconnect()


if __name__ == "__main__":
    main()
