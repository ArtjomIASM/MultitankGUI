import sys
from PyQt4.QtGui import QApplication
from mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wndMain = MainWindow()
    sys.exit(app.exec_())