from PyQt4 import QtCore, QtGui
from basicwindow import BasicWindow
from pidwindow import PIDWindow

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None): # Here starts class instance
        super(MainWindow, self).__init__(parent) # Calling constructor MainWindow

        self.createUI()
        self.connectHandlers()
        self.show()

    def connectHandlers(self): # More comfortable to handle in function
        self.btnBasicTest.clicked.connect(self.onBasicTest)
        self.btnPIDRegulator.clicked.connect(self.onPIDRegulator)
        self.btnLQRController.clicked.connect(self.onLQRController)
        self.btnExit.clicked.connect(self.onExit)
        self.actionAbout.triggered.connect(self.onAbout)

    def onExit(self):
        mbResult = QtGui.QMessageBox.question(self, 'Extract',
                                            "Are you sure?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if mbResult == QtGui.QMessageBox.Yes:
            print("Successful Closed Application")
            QtCore.QCoreApplication.instance().quit()

    def onAbout(self):
        QtGui.QMessageBox.about(self, 'About',
                                "This program was created by Artjom Smolov 153154IASM "
                                "for (A-lab)TTU purpose. Tallinn, 2017.")

    def onPIDRegulator(self):
        wndBasic = PIDWindow(self)
        wndBasic.setModal(True)
        wndBasic.show()

    def onBasicTest(self):
        wndBasic = BasicWindow(self)
        wndBasic.setModal(True)
        wndBasic.show()

    def onLQRController(self):
        QtGui.QMessageBox.about(self, "Info", "Not implemented!")

    def createUI(self):
        self.setWindowTitle("Application")
        self.resize(176, 266)

        # Create status bar
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)

        # Create menu
        self.menuBar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menuBar)
        self.actionAbout = QtGui.QAction(self)
        self.actionAbout.setText("&About")
        self.menuAbout = QtGui.QMenu(self.menuBar)
        self.menuAbout.setAutoFillBackground(False)
        self.menuAbout.setTitle("&File")
        self.menuAbout.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuAbout.menuAction())

        # Create layout
        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.gridLayout = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout.setMargin(11)
        self.gridLayout.setSpacing(6)

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setMargin(11)
        self.verticalLayout.setSpacing(6)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)

        self.groupBox = QtGui.QGroupBox(self.centralWidget)
        self.groupBox.setTitle("Control Options")
        self.verticalLayout.addWidget(self.groupBox)

        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setMargin(11)
        self.verticalLayout_2.setSpacing(6)

        # Create buttons
        self.btnBasicTest = QtGui.QPushButton(self.groupBox)
        self.btnBasicTest.setText("Basic Test")
        self.verticalLayout_2.addWidget(self.btnBasicTest)

        self.btnPIDRegulator = QtGui.QPushButton(self.groupBox)
        self.btnPIDRegulator.setText("PID Regulator")
        self.verticalLayout_2.addWidget(self.btnPIDRegulator)

        self.btnLQRController = QtGui.QPushButton(self.groupBox)
        self.btnLQRController.setText("LQR Controller")
        self.verticalLayout_2.addWidget(self.btnLQRController)

        self.btnExit = QtGui.QPushButton(self.groupBox)
        self.btnExit.setText("Exit")
        self.verticalLayout_2.addWidget(self.btnExit)