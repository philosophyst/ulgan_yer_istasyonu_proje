import sys
import csv
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QWidget, QComboBox, QFrame, QTextEdit
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import Qt, QThread, pyqtSignal


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


class YerIstasyonu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ULGAN Yer İstasyonu")
        self.setGeometry(50, 50, 1400, 800)
        self.setMinimumSize(1200, 700)

        self.temp_series = QLineSeries()
        self.alt_series = QLineSeries()
        self.press_series = QLineSeries()
        self.volt_series = QLineSeries()

        for seri in [self.temp_series, self.alt_series, self.press_series, self.volt_series]:
            seri.setUseOpenGL(True)

        self.komut_isleyici = KomutIsleyici()

        self.init_ui()
        self.baslat_veri_izleme()

    def init_ui(self):
        # Üst Panel
        logo = QLabel()
        logo.setPixmap(QPixmap("icons/img.png").scaled(80, 80, Qt.KeepAspectRatio))

        self.label_packet = QLabel("Packet: 0")
        self.label_mission = QLabel("Mission: 00:00")
        for lbl in [self.label_packet, self.label_mission]:
            lbl.setFont(QFont("Arial", 12))

        top_grid = QGridLayout()
        top_grid.addWidget(logo, 0, 0)
        top_grid.addWidget(self.label_packet, 0, 1)
        top_grid.addWidget(self.label_mission, 0, 2)

        # Grafikler
        self.temp_chart = self.olustur_grafik("Temperature", self.temp_series)
        self.alt_chart = self.olustur_grafik("Altitude", self.alt_series)
        self.press_chart = self.olustur_grafik("Pressure", self.press_series)
        self.volt_chart = self.olustur_grafik("Voltage", self.volt_series)

        grafikler = QGridLayout()
        grafikler.addWidget(self.temp_chart, 0, 0)
        grafikler.addWidget(self.alt_chart, 0, 1)
        grafikler.addWidget(self.press_chart, 1, 0)
        grafikler.addWidget(self.volt_chart, 1, 1)

        charts_frame = QFrame()
        charts_frame.setLayout(grafikler)

        # Konsol
        self.console_input = QComboBox()
        self.console_input.setEditable(True)
        self.console_input.setFont(QFont("Consolas", 11))

        komut_gonder_btn = QPushButton("Komut Gönder")
        komut_gonder_btn.clicked.connect(self.komut_gonder)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 11))

        konsol_layout = QVBoxLayout()
        konsol_layout.addWidget(QLabel("Konsol"))
        konsol_layout.addWidget(self.console_input)
        konsol_layout.addWidget(komut_gonder_btn)
        konsol_layout.addWidget(self.console_output)

        konsol_frame = QFrame()
        konsol_frame.setLayout(konsol_layout)
        konsol_frame.setFixedWidth(300)

        # Roket ve Reset
        roket_layout = QVBoxLayout()
        roket_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        reset_btn = QPushButton("Reset")
        reset_btn.setFixedWidth(80)
        reset_btn.setStyleSheet("background-color: #8B0000; color: white;")  # Tema uyumlu koyu kırmızı
        reset_btn.clicked.connect(lambda: self.console_output.append("> RESET\n[OK] Roket yönü sıfırlandı.\n"))

        roket = QLabel()
        roket.setPixmap(QPixmap("assets/img.png").scaled(80, 160, Qt.KeepAspectRatio))
        roket.setAlignment(Qt.AlignRight)

        roket_layout.addWidget(reset_btn, alignment=Qt.AlignRight)
        roket_layout.addWidget(roket, alignment=Qt.AlignRight)

        # Ana düzen
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_grid)

        orta_layout = QHBoxLayout()
        orta_layout.addWidget(charts_frame, 4)
        orta_layout.addWidget(konsol_frame, 1)

        main_layout.addLayout(orta_layout)
        main_layout.addLayout(roket_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def olustur_grafik(self, baslik, seri):
        chart = QChart()
        chart.addSeries(seri)
        chart.setTitle(baslik)
        chart.createDefaultAxes()
        chart.legend().hide()

        y_axis = QValueAxis()
        y_axis.setLabelFormat("%.2f")
        y_axis.setRange(0, 100)  # Gerekirse dinamik ayarlanabilir
        chart.setAxisY(y_axis, seri)

        x_axis = QValueAxis()
        x_axis.setLabelFormat("%d")
        x_axis.setTickCount(10)
        x_axis.setRange(0, 50)
        chart.setAxisX(x_axis, seri)

        return QChartView(chart)

    def baslat_veri_izleme(self):
        self.veri_thread = VeriOkuyucuThread()
        self.veri_thread.veri_okundu.connect(self.veri_guncelle)
        self.veri_thread.start()

    def veri_guncelle(self, temp, alt, press, volt, index):
        self.temp_series.append(index, temp)
        self.alt_series.append(index, alt)
        self.press_series.append(index, press)
        self.volt_series.append(index, volt)

        self.label_packet.setText(f"Packet: {index + 1}")
        self.label_mission.setText(f"Mission: 00:00:{str(index+1).zfill(2)}")

    def komut_gonder(self):
        komut = self.console_input.currentText()
        yanit = self.komut_isleyici.isle(komut)
        self.console_output.append(f"> {komut}\n{yanit}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("dark_red_theme.qss", "r") as f:
        app.setStyleSheet(f.read())
    pencere = YerIstasyonu()
    pencere.show()
    sys.exit(app.exec_())