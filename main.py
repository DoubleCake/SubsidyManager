# main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_ui import MainUI
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())