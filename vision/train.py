"""
train.py — SH17 Veri Seti ile YOLOv8 Fine-Tune Eğitimi (Colab Uyumlu)
İP7: SH17 Fine-Tune

Kullanım (Google Colab hücresinde):
    !python vision/train.py --epochs 20 --batch 16
"""

import os
import sys
import argparse
import yaml

def install_and_import(package, import_name=None):
    if import_name is None:
        import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"[BİLGİ] '{package}' kütüphanesi kurulu değil, kuruluyor...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Gerekli paketlerin kurulu olduğundan emin ol (Colab'da kagglehub yüklü gelmeyebilir)
install_and_import("kagglehub")
install_and_import("ultralytics")

import kagglehub
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 SH17 Fine-Tune Eğitimi")
    parser.add_argument("--epochs", type=int, default=20, help="Eğitim devir (epoch) sayısı (Varsayılan: 20)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (Varsayılan: 16)")
    parser.add_argument("--imgsz", type=int, default=640, help="Görüntü boyutu (Varsayılan: 640)")
    parser.add_argument("--model", default="yolov8n.pt", help="Başlangıç modeli (yolov8n.pt, yolov8s.pt vb.)")
    return parser.parse_args()

def main():
    args = parse_args()
    
    print("\n" + "="*50)
    print("🚀 YOLOv8 SH17 FINE-TUNE EĞİTİMİ BAŞLIYOR")
    print("="*50 + "\n")
    
    # ── 1. Veri Setini Kaggle'dan İndir ──
    print("[1/4] Veri seti indiriliyor (mughees/sh17-dataset)...")
    dataset_path = kagglehub.dataset_download("mughees/sh17-dataset")
    print(f"[BİLGİ] Veri seti şuraya indirildi: {dataset_path}")
    
    # ── 2. Veri Seti Yapısını İncele ve Klasörleri Bul ──
    # İndirilen klasörün altındaki yapıyı tarayalım. Genelde 'train' ve 'val' klasörleri bulunur.
    train_dir = os.path.join(dataset_path, "train")
    val_dir = os.path.join(dataset_path, "val")
    
    # Eğer doğrudan alt klasörler yoksa, altındaki klasörleri kontrol et
    if not os.path.exists(train_dir):
        # Klasör içeriğine bak
        subdirs = [os.path.join(dataset_path, d) for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
        if len(subdirs) == 1:
            # Tek bir ana klasör varsa onun içine gir
            dataset_path = subdirs[0]
            train_dir = os.path.join(dataset_path, "train")
            val_dir = os.path.join(dataset_path, "val")
            
    print(f"[BİLGİ] Eğitim klasörü: {train_dir}")
    print(f"[BİLGİ] Doğrulama klasörü: {val_dir}")
    
    # ── 3. Dinamik dataset.yaml Dosyası Oluştur ──
    print("[2/4] dataset.yaml dosyası hazırlanıyor...")
    
    # SH17 Veri Setinin 17 Sınıfı (Resmi sınıf listesi)
    classes = [
        "person", "vest", "blue helmet", "red helmet", "yellow helmet", 
        "white helmet", "no vest", "no helmet", "safety belt", "gloves", 
        "boots", "goggles", "mask", "hearing protection", "kneepads", 
        "hard hat", "other helmet"
    ]
    
    yaml_data = {
        "path": dataset_path,      # Ana veri seti yolu
        "train": "train/images",   # Eğitim resimlerinin göreceli yolu
        "val": "val/images",       # Doğrulama resimlerinin göreceli yolu
        "names": {i: name for i, name in enumerate(classes)}
    }
    
    yaml_filename = "sh17_colab.yaml"
    with open(yaml_filename, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False)
    
    print(f"[BAŞARILI] {yaml_filename} başarıyla oluşturuldu.")
    
    # ── 4. YOLO modelini yükle ──
    print(f"[3/4] Başlangıç modeli yükleniyor: {args.model}")
    model = YOLO(args.model)
    
    # ── 5. Eğitimi Başlat ──
    print(f"[4/4] Eğitim başlıyor! (Epochs: {args.epochs}, Batch: {args.batch}, Imgsz: {args.imgsz})")
    
    # Colab'da GPU olup olmadığını doğrulamak için device=0 (varsa) veya cpu seçilir
    import torch
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"[BİLGİ] Kullanılan donanım: {device} ({'GPU Aktif' if device == 0 else 'CPU - Dikkat: Yavaş çalışabilir'})")
    
    results = model.train(
        data=yaml_filename,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=device,
        project="sh17_training",
        name="yolov8_sh17_run",
        exist_ok=True
    )
    
    print("\n" + "="*50)
    print("🎉 EĞİTİM BAŞARIYLA TAMAMLANDI!")
    print(f"[BİLGİ] En iyi ağırlıklar şuraya kaydedildi: sh17_training/yolov8_sh17_run/weights/best.pt")
    print("="*50)

if __name__ == "__main__":
    main()
