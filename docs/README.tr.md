# Warehouse Vision Counting System

**Diller:** [العربية](../README.md) · [English](README.en.md) · [Français](README.fr.md) · [Español](README.es.md) · [Türkçe](README.tr.md) · [中文](README.zh-CN.md)

Depo hattından geçen kolileri ve paletleri saymak için çevrimdışı çalışan,
denetlenebilir bir çekirdek. MVP, takip gözlemlerini `IN/OUT` yön olaylarına
dönüştürür, yinelenen sayımları engeller ve kanıt metadatasını SQLite'ta saklar.

## Hızlı başlangıç

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m warehouse_counting.demo
```

Çekirdek Python 3.11+ ve standart kütüphane ile çalışır. Canlı kamera, gösterge
paneli ve üretim doğruluğu yol haritasındadır.

## Mevcut kapsam

Tek sayım hattı, `carton` ve `pallet` nesneleri, güven ve sınıf filtreleri,
yinelenen olayların engellenmesi, SQLite kalıcılığı ve açık palet kapasitesi
kuralları. Mevcut videolar kabul testi değil, destekleyici eğitim verisidir.

## Topluluğa katılın

Geliştiricileri, araştırmacıları, depo uzmanlarını ve çevirmenleri katkıya davet
ediyoruz. [`CONTRIBUTING.md`](../CONTRIBUTING.md) dosyasını okuyun, Issue açın
ve küçük, test edilmiş Pull Request gönderin.

## Lisans

MIT — [`LICENSE`](../LICENSE).
