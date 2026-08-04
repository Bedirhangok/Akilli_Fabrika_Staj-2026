"""
train.py — PPE Veri Seti ile YOLOv8 Fine-Tune Eğitimi (Colab Uyumlu)
İP7: SH17/PPE Fine-Tune

Kullanım (Google Colab hücresinde):
    !python vision/train.py --epochs 20 --batch 16
"""

import os
import sys
import argparse
import yaml
import glob

def install_and_import(package, import_name=None):
    if import_name is None:
        import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"[BİLGİ] '{package}' kütüphanesi kurulu değil, kuruluyor...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Colab'da gerekli paketleri yükleyelim
install_and_import("huggingface_hub")
install_and_import("ultralytics")

from huggingface_hub import snapshot_download
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 PPE Fine-Tune Eğitimi")
    parser.add_argument("--epochs", type=int, default=20, help="Eğitim devir (epoch) sayısı (Varsayılan: 20)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (Varsayılan: 16)")
    parser.add_argument("--imgsz", type=int, default=640, help="Görüntü boyutu (Varsayılan: 640)")
    parser.add_argument("--model", default="yolov8n.pt", help="Başlangıç modeli (yolov8n.pt, yolov8s.pt vb.)")
    parser.add_argument("--project", default="ppe_training", help="Sonuçların kaydedileceği ana klasör")
    return parser.parse_args()

def main():
    args = parse_args()
    
    print("\n" + "="*50)
    print("🚀 YOLOv8 PPE FINE-TUNE EĞİTİMİ BAŞLIYOR (HuggingFace Versiyonu)")
    print("="*50 + "\n")
    
    # ── 1. Veri Setini HuggingFace'den İndirme (API KEY GEREKTİRMEZ!) ──
    # Kaggle'ın sürekli verdiği 403 hatasını aşmak için halka açık bir HF dataseti kullanıyoruz.
    print("[1/4] HuggingFace'den PPE Veri Seti indiriliyor (jhboyo/ppe-dataset)...")
    try:
        dataset_path = snapshot_download(repo_id="jhboyo/ppe-dataset", repo_type="dataset")
        print(f"[BAŞARILI] Veri seti indirildi: {dataset_path}")
    except Exception as e:
        print(f"[HATA] HuggingFace'den veri seti indirilemedi: {e}")
        sys.exit(1)
        
    # ── 2. Dinamik YAML Bulma ve Yolu Düzeltme ──
    print("\n[2/4] dataset.yaml dosyası bulunuyor...")
    
    yaml_files = glob.glob(os.path.join(dataset_path, "**", "*.yaml"), recursive=True)
    if not yaml_files:
        print("[HATA] İndirilen veri setinde hiçbir .yaml dosyası bulunamadı!")
        sys.exit(1)
        
    original_yaml = yaml_files[0]
    print(f"[BİLGİ] {original_yaml} bulundu. Dosya yolları mutlak (absolute) hale getiriliyor...")
    
    # Yaml dosyasını oku ve train/val yollarını dataset_path ile birleştirerek kaydet
    with open(original_yaml, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)
        
    # YOLO için path'i zorunlu kıl
    yaml_data["path"] = dataset_path
    
    yaml_filename = "ppe_colab.yaml"
    with open(yaml_filename, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False)
    
    print(f"[BAŞARILI] {yaml_filename} başarıyla oluşturuldu ve yollar güncellendi.")
    
    # ── 3. YOLO modelini yükle ──
    print(f"\n[3/4] Başlangıç modeli yükleniyor: {args.model}")
    model = YOLO(args.model)
    
    # ── 4. Eğitimi Başlat ──
    print(f"\n[4/4] Eğitim başlıyor! (Epochs: {args.epochs}, Batch: {args.batch}, Imgsz: {args.imgsz})")
    
    import torch
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"[BİLGİ] Kullanılan donanım: {device} ({'GPU Aktif' if device == 0 else 'CPU - Dikkat: Yavaş çalışabilir'})")
    
    results = model.train(
        data=yaml_filename,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=device,
        project=args.project,
        name="yolov8_ppe_run",
        exist_ok=True
    )
    
    print("\n" + "="*50)
    print("🎉 EĞİTİM BAŞARIYLA TAMAMLANDI!")
    print(f"[BİLGİ] En iyi ağırlıklar şuraya kaydedildi: {args.project}/yolov8_ppe_run/weights/best.pt")
    print("="*50)

if __name__ == "__main__":
    main()
