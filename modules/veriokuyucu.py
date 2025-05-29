import csv
import time
from PyQt5.QtCore import QThread, pyqtSignal

class VeriOkuyucuThread(QThread):
    veri_okundu = pyqtSignal(float, float, float, float, int)

    def run(self):
        with open("data/telemetry_data.csv", "r", encoding="utf-8") as dosya:
            reader = csv.reader(dosya)
            next(reader)
            sayac = 0
            for satir in reader:
                temp = float(satir[3])
                alt = float(satir[4])
                press = float(satir[5])
                volt = float(satir[6])
                self.veri_okundu.emit(temp, alt, press, volt, sayac)
                time.sleep(1)
                sayac += 1
