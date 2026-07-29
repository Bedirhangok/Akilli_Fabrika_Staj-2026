"""
detector.py — YOLOv8 kullanarak ilk tespit scripti.
İP3: İlk Tespit

Kullanım:
    # İnternetten otomatik test resmi indirip tespit yapar:
    python vision/detector.py
    
    # Kendi resminle test etmek için:
    python vision/detector.py --input resim.jpg
"""

import argparse
import os
import sys
import urllib.request
from ultralytics import YOLO

# ─── Ayarlar ───────────────────────────────────────────────
DEFAULT_MODEL = "yolov8n.pt"  # Nano model (hızlı ve hafif)
TEST_IMAGE_URL = "https://ultralytics.com/images/bus.jpg"  # Örnek test resmi
# ────────────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 İlk Tespit Scripti")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Kullanılacak model ağırlığı")
    parser.add_argument("--input", default=None, help="Giriş resminin yolu (Yoksa örnek resim indirilir)")
    parser.add_argument("--output-dir", default="output", help="Sonuçların kaydedileceği klasör")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence (güven) eşiği")
    return parser.parse_args()


def download_test_image(dest_path):
    print(f"[YOLO] Örnek test resmi indiriliyor: {TEST_IMAGE_URL}")
    try:
        urllib.request.urlretrieve(TEST_IMAGE_URL, dest_path)
        print(f"[YOLO] Resim kaydedildi: {dest_path}")
        return True
    except Exception as e:
        print(f"[HATA] Test resmi indirilemedi: {e}")
        return False


def main():
    args = parse_args()
    
    # Output klasörünü oluştur
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Giriş resmi belirlenmemişse örnek resmi indir
    if args.input is None:
        input_image = os.path.join(args.output_dir, "test_bus.jpg")
        if not os.path.exists(input_image):
            if not download_test_image(input_image):
                sys.exit(1)
    else:
        input_image = args.input
        if not os.path.exists(input_image):
            print(f"[HATA] Giriş dosyası bulunamadı: {input_image}")
            sys.exit(1)
            
    # YOLO modelini yükle (ağırlık yoksa otomatik indirir)
    print(f"[YOLO] Model yükleniyor: {args.model}")
    try:
        model = YOLO(args.model)
    except Exception as e:
        print(f"[HATA] Model yüklenemedi: {e}")
        sys.exit(1)
        
    print(f"[YOLO] Görsel üzerinde çıkarım yapılıyor: {input_image}")
    
    # Görsel üzerinde tespit yap
    results = model.predict(
        source=input_image,
        conf=args.conf,
        save=True,              # Sonucu kaydet
        project=args.output_dir,# Kayıt klasörü projesi
        name="detection_run",   # Kayıt alt klasörü
        exist_ok=True           # Üzerine yaz
    )
    
    # Sonuçların nereye kaydedildiğini ekrana yaz
    save_dir = results[0].save_dir
    print("\n" + "="*50)
    print(f"[BAŞARILI] Tespit tamamlandı!")
    print(f"[BİLGİ] Kutulu görsel şuraya kaydedildi: {save_dir}")
    print("="*50)


if __name__ == "__main__":
    main()
