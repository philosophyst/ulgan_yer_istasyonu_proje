class KomutIsleyici:
    def __init__(self):
        self.komutlar = {
            "RESET": "Roket yönü sıfırlandı.",
            "BAGLANTI": "Bağlantı sağlandı.",
            "TEST": "Test komutu çalıştı.",
            "DURUM": "Sistem durumu iyi.",
            "ISIK": "LED ışığı açıldı.",
            "KAMERA": "Kamera başlatıldı.",
            "GPS": "GPS verisi alınıyor.",
            "BASLAT": "Görev başlatıldı.",
            "DUR": "Görev durduruldu.",
            "YENIDEN": "Yeniden başlatılıyor."
        }

    def isle(self, komut):
        sonuc = []
        parcali = komut.upper().split(",")
        for k in parcali:
            k = k.strip()
            if k in self.komutlar:
                sonuc.append(f"[OK] {k} → {self.komutlar[k]}")
            else:
                sonuc.append(f"[ERR] {k} tanınmadı.")
        return "\n".join(sonuc)
