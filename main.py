from PyQt5.QtWidgets import QApplication
from modules.ui import YerIstasyonu
from modules.komutisleyici import KomutIsleyici
from modules.veriokuyucu import VeriOkuyucuThread
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("qss/dark_red_theme.qss", "r") as f:
        app.setStyleSheet(f.read())
    pencere = YerIstasyonu()
    pencere.show()
    sys.exit(app.exec_())
