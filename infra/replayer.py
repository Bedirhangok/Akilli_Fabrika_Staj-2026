"""
replayer.py — Kayıtlı MQTT mesajlarını zaman damgalarına göre tekrar oynatır.
İP2: Kayıt/Replay Aracı

Kullanım:
    python infra/replayer.py --input session.jsonl
    python infra/replayer.py --input session.jsonl --loop  # Sürekli tekrar et
"""

import paho.mqtt.client as mqtt
import json
import time
import argparse
import sys
import os


def parse_args():
    parser = argparse.ArgumentParser(description="MQTT Zaman Damgalı Mesaj Tekrar Oynatıcı")
    parser.add_argument("--host", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--input", default="session.jsonl", help="Kayıt dosyası (.jsonl)")
    parser.add_argument("--loop", action="store_true", help="Kayıt bittiğinde başa dön")
    return parser.parse_args()


def play_session(client, filepath, loop):
    if not os.path.exists(filepath):
        print(f"[HATA] Kayıt dosyası bulunamadı: {filepath}")
        return False

    while True:
        print(f"[REPLAY] Oynatım başladı: {filepath}")
        start_time = time.time()
        message_count = 0
        
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # Oynatılması gereken zamanı bekle
                target_time = start_time + entry["rel_time"]
                now = time.time()
                delay = target_time - now
                if delay > 0:
                    time.sleep(delay)
                
                # Mesajı yayınla
                client.publish(entry["topic"], entry["payload"])
                message_count += 1
                
                if message_count % 30 == 0:
                    print(f"[REPLAY] {message_count} mesaj gönderildi...")
                    
        print(f"[REPLAY] Oynatma bitti. Gönderilen mesaj: {message_count}")
        
        if not loop:
            break
            
        print("[REPLAY] Sürekli döngü modu aktif. 2 saniye içinde tekrar başlayacak...")
        time.sleep(2)
        
    return True


def main():
    args = parse_args()
    
    client = mqtt.Client()
    
    try:
        client.connect(args.host, args.port, keepalive=60)
    except ConnectionRefusedError:
        print(f"[HATA] Broker'a bağlanılamadı. Mosquitto çalışıyor mu?")
        sys.exit(1)
        
    client.loop_start()
    
    try:
        play_session(client, args.input, args.loop)
    except KeyboardInterrupt:
        print("\n[REPLAY] Durduruldu.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
