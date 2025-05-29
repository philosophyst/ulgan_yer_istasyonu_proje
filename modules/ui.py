from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QWidget, QComboBox, QTextEdit, QTabWidget
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import os

from modules.veriokuyucu import VeriOkuyucuThread
from modules.komutisleyici import KomutIsleyici

class YerIstasyonu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ULGAN Yer İstasyonu")
        self.setGeometry(100, 100, 1600, 900)

        self.temp_series = QLineSeries()
        self.alt_series = QLineSeries()
        self.press_series = QLineSeries()
        self.volt_series = QLineSeries()

        self.komut_isleyici = KomutIsleyici()

        self.init_ui()
        self.baslat_veri_izleme()

    def init_ui(self):
        self.tabs = QTabWidget()

        charts_tab = QWidget()
        charts_layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        logo = QLabel()
        logo.setPixmap(QPixmap("icons/img.png").scaled(40, 40, Qt.KeepAspectRatio))
        header_layout.addWidget(logo)

        self.label_mod = QLabel("Mod: S")
        self.label_rotation = QLabel("Rotation Rate: 1.1")
        self.label_packet = QLabel("Packet Count: 0")
        self.label_mission = QLabel("Mission Time: 00:00")
        self.label_satellites = QLabel("Satellites: 8")
        self.label_gps = QLabel("GPS Time: 17:12:12")
        self.label_state = QLabel("State: Ready")

        for lbl in [
            self.label_mod, self.label_rotation, self.label_packet,
            self.label_mission, self.label_satellites, self.label_gps, self.label_state
        ]:
            lbl.setStyleSheet("color: white; background-color: #222; padding: 10px; border-radius: 8px;")
            lbl.setFont(QFont("Arial", 11))
            header_layout.addWidget(lbl)

        grafik_layout = QGridLayout()
        grafik_layout.addWidget(self.grafik_olustur("ALTITUDE", self.alt_series), 0, 0)
        grafik_layout.addWidget(self.grafik_olustur("TEMPERATURE", self.temp_series), 0, 1)
        grafik_layout.addWidget(self.grafik_olustur("PRESSURE", self.press_series), 1, 0)
        grafik_layout.addWidget(self.grafik_olustur("VOLTAGE", self.volt_series), 1, 1)

        sag_panel = QVBoxLayout()
        harita = folium.Map(location=[40.98, 29.13], zoom_start=7)
        folium.Marker(location=[40.98, 29.13]).add_to(harita)
        harita_path = "map/map.html"
        harita.save(harita_path)
        self.map_view = QWebEngineView()
        self.map_view.load(QUrl.fromLocalFile(os.path.abspath(harita_path)))
        self.map_view.setMinimumHeight(300)

        roket = QLabel()
        roket.setPixmap(QPixmap("assets/img.png").scaled(150, 300, Qt.KeepAspectRatio))
        roket.setAlignment(Qt.AlignCenter)
        sag_panel.addWidget(self.map_view)
        sag_panel.addWidget(roket)

        grafik_ve_harita = QHBoxLayout()
        grafik_ve_harita.addLayout(grafik_layout, 4)
        grafik_ve_harita.addLayout(sag_panel, 1)

        charts_layout.addLayout(header_layout)
        charts_layout.addLayout(grafik_ve_harita)
        charts_tab.setLayout(charts_layout)

        telemetry_tab = QWidget()
        telemetry_layout = QVBoxLayout()
        self.label_temp = QLabel("Temperature:")
        self.label_alt = QLabel("Altitude:")
        self.label_press = QLabel("Pressure:")
        self.label_volt = QLabel("Voltage:")
        for lbl in [self.label_temp, self.label_alt, self.label_press, self.label_volt]:
            lbl.setFont(QFont("Consolas", 14))
            telemetry_layout.addWidget(lbl)

        self.telemetry_log = QTextEdit()
        self.telemetry_log.setReadOnly(True)
        telemetry_layout.addWidget(self.telemetry_log)
        telemetry_tab.setLayout(telemetry_layout)

        console_tab = QWidget()
        console_layout = QVBoxLayout()
        self.console_input = QComboBox()
        self.console_input.setEditable(True)
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        komut_gonder_btn = QPushButton("Komut Gönder")
        komut_gonder_btn.clicked.connect(self.komut_gonder)
        console_layout.addWidget(QLabel("Komut Konsolu"))
        console_layout.addWidget(self.console_input)
        console_layout.addWidget(komut_gonder_btn)
        console_layout.addWidget(self.console_output)
        console_tab.setLayout(console_layout)

        self.tabs.addTab(charts_tab, "Charts")
        self.tabs.addTab(telemetry_tab, "Telemetry")
        self.tabs.addTab(console_tab, "Console")
        self.setCentralWidget(self.tabs)

    def grafik_olustur(self, baslik, seri):
        chart = QChart()
        chart.addSeries(seri)
        chart.setTitle(baslik)
        chart.legend().hide()
        y_axis = QValueAxis()
        y_axis.setLabelFormat("%.2f")
        y_axis.setRange(0, 2000)
        chart.setAxisY(y_axis, seri)
        x_axis = QValueAxis()
        x_axis.setLabelFormat("%d")
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

        self.label_temp.setText(f"Temperature: {temp} °C")
        self.label_alt.setText(f"Altitude: {alt} m")
        self.label_press.setText(f"Pressure: {press} hPa")
        self.label_volt.setText(f"Voltage: {volt} V")

        self.telemetry_log.append(f"#{index+1} → Temp: {temp}°C, Alt: {alt}m, Press: {press}hPa, Volt: {volt}V")

        self.label_packet.setText(f"Packet Count: {index + 1}")
        self.label_mission.setText(f"Mission Time: 00:00:{str(index+1).zfill(2)}")

    def komut_gonder(self):
        komut = self.console_input.currentText()
        yanit = self.komut_isleyici.isle(komut)
        self.console_output.append(f"> {komut}\n{yanit}\n")
