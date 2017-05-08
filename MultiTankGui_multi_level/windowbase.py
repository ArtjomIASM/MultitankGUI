from PyQt4 import QtCore, QtGui
from threading import Lock
from graphdialog import GraphDialog
from transport import Transport
from config import *
import csv
import os

class WindowBase(QtGui.QDialog):
    def __init__(self, parent=None):
        super(WindowBase, self).__init__(parent)

        self.lstLabelsForData = []
        self.lstGraphDls = [None, None, None]
        self.menuBar = None
        self.stopped = False
        self.lstData = []
        self.firstSentBeforeReceive = None
        self.resetOutValuesOnSend = False

        self.saveLock = Lock()

        self.createUI()
        self.setTexts()
        self.connectHandlers()
        self.enableControls()

        self.transport = Transport(self.lstLabelsForData.__len__())
        self.transport.registerCallback(self, self.onDataReceived) # Transport

    def hideEvent(self, *args, **kwargs):
        super(WindowBase, self).hideEvent(*args, **kwargs)
        self.transport.unRegisterCallback(self)
        self.onDisconnect()
        for graphDlg in self.lstGraphDls:
            if None != graphDlg:
                graphDlg.close()

    def onDataReceived(self, lstServerData):
        if lstServerData.__len__() < self.lstLabelsForData.__len__():
            QtGui.QMessageBox.information(self, 'Error', "Provided more controls to fill with data than read from server!")
            QtCore.QCoreApplication.instance().quit()

        # Store input and output values to list for further use by Save command
        lstDataRow = []
        if None != self.firstSentBeforeReceive:
            lstDataRow.extend([formatFloat(val) for val in self.firstSentBeforeReceive[0]]) # values sent to the server
            lstDataRow.extend(self.firstSentBeforeReceive[1]) # additional values like PID.error
        else:
            nOutAndInternalColumns = len(self.getColumnNamesForSave()) - len(lstServerData)
            lstDataRow = ['0.0000'] * nOutAndInternalColumns       # Try here [0.0, 0.0, 0.0 0.0]
        lstDataRow.extend([formatFloat(val) for val in lstServerData])                      # values received from the server
        self.saveLock.acquire(True)
        try:
            self.lstData.append(lstDataRow)
        finally:
            self.saveLock.release()
        if self.resetOutValuesOnSend:
            self.firstSentBeforeReceive = None

        for i in range(self.lstLabelsForData.__len__()):
            # Choice round or float and test after in lab
            #self.lstLabelsForData[i].setText(str(round(lstServerData[i], self.ROUNDED_VALUE)))
            self.lstLabelsForData[i].setText(formatFloat(lstServerData[i]))

        self.customProcessingOnReceive(lstServerData)

    def onSendBtn(self):
        self.stopped = False
        self.onSend()

    def onSend(self):
        lstDataToSend = self.getValuesForSend()
        lstOutValuesForSave = self.getOutValuesForSave()
        if None == lstOutValuesForSave:
            lstOutValuesForSave = lstDataToSend

        nBytesSent = self.transport.doSend(lstDataToSend)
        if 0 == nBytesSent:
            QtGui.QMessageBox.information(self, 'Error', "Failed to send data")
        else:
            # Store first output values, since first received values will be correlated with first output values
            if not self.resetOutValuesOnSend or None == self.firstSentBeforeReceive:
                customData = self.getCustomDataForSave()
                self.firstSentBeforeReceive = (lstOutValuesForSave, customData)

            self.labelOnDataSent.setText(str(int(self.labelOnDataSent.text()) + nBytesSent))

    def emergencyStop(self):
        self.stopped = True

    def getCustomDataForSave(self):
        return []

    def customProcessingOnReceive(self, lstServerData):
        pass

    def getValuesForSend(self):
        pass

    def getOutValuesForSave(self):
        return None

    def updateSetPoint(self, val):
        for oGraph in self.lstGraphDls:
            if None != oGraph:
                oGraph.updateSetPoint(val)

    def onConnect(self):
        self.btnDisconnect.setEnabled(True)
        self.btnSendData.setEnabled(True)
        self.btnConnect.setEnabled(False)

        #Graph buttons start
        self.btnShowGraph1.setEnabled(True)
        self.btnShowGraph2.setEnabled(True)
        self.btnShowGraph3.setEnabled(True)

        # Graph stop buttons
        self.btnCloseGraph1.setEnabled(True)
        self.btnCloseGraph2.setEnabled(True)
        self.btnCloseGraph3.setEnabled(True)

        client = (self.lineEditClientHost.text(), int(self.lineEditClientPort.text()))
        server = (self.lineEditServerHost.text(), int(self.lineEditServerPort.text()))
        if self.transport.doConnect(client, server):
            QtGui.QMessageBox.information(self, 'Connection Information', "Socket is Created!")
        else:
            QtGui.QMessageBox.information(self, 'Connection Information', "Failed to create socket")

        print "Client IP: ", server[0]
        print "Client PORT: ", server[1]
        print "Server IP: ", client[0]
        print "Server PORT: ", client[1]

    def onDisconnect(self):
        self.btnConnect.setEnabled(True)
        self.btnDisconnect.setEnabled(False)
        self.btnSendData.setEnabled(False)

        # Graph buttons start
        self.btnShowGraph1.setEnabled(False)
        self.btnShowGraph2.setEnabled(False)
        self.btnShowGraph3.setEnabled(False)

        # Graph stop buttons
        self.btnCloseGraph1.setEnabled(False)
        self.btnCloseGraph2.setEnabled(False)
        self.btnCloseGraph3.setEnabled(False)

        if self.transport.doDisconnect():
            QtGui.QMessageBox.information(self, 'Connection Information', "Socket is closed!")


    def onClear(self):
        nInitialVal = 0
        strInitialVal = formatFloat(nInitialVal)

        self.labelOnDataSent.setNum(nInitialVal)
        self.labelLevel1Value.setText(strInitialVal)
        self.labelLevel2Value.setText(strInitialVal)
        self.labelLevel3Value.setText(strInitialVal)

    def onClientHostChanged(self, text):
        print "Client Host: " + text

    def onClientPortChanged(self, text):
        print "Client Port: " + text

    def onServerHostChanged(self, text):
        print "Server Host: " + text

    def onServerPortChanged(self, text):
        print "Server Port: " + text

    def onGraphCloseEvent(self, nGraphId):
        self.lstGraphDls[nGraphId - 1] = None

    def doOpenGraph(self, nGraphId):
        if None == self.lstGraphDls[nGraphId - 1]:
            self.lstGraphDls[nGraphId - 1] = GraphDialog(self.transport, nGraphId, self.onGraphCloseEvent, self)
        else:
            self.lstGraphDls[nGraphId - 1].doResume()
    def doPauseGraph(self, nGraphId):
        if None != self.lstGraphDls[nGraphId - 1]:
            self.lstGraphDls[nGraphId - 1].doPause()

    def onGraph1Open(self):
        self.doOpenGraph(1)

    def onGraph1Close(self):
        self.doPauseGraph(1)

    def onGraph2Open(self):
        self.doOpenGraph(2)

    def onGraph2Close(self):
        self.doPauseGraph(2)

    def onGraph3Open(self):
        self.doOpenGraph(3)

    def onGraph3Close(self):
        self.doPauseGraph(3)

    def onSave(self):
        strPath = QtGui.QFileDialog.getSaveFileName(self, 'Open file',
                                            '', "CSV (*.csv)")
        if strPath:
            print "Saving: " + strPath
            with open(strPath, 'w') as csvFile:
                csvWriter = csv.writer(csvFile)
                lstTitles = self.getColumnNamesForSave()
                nColumnCount = len(lstTitles)
                csvWriter.writerow(lstTitles)
                self.saveLock.acquire(True)
                try:
                    for row in self.lstData:
                        if nColumnCount != len(row):
                            QtGui.QMessageBox.information(self, 'Error', "Data and column labels mismatch!")
                            QtCore.QCoreApplication.instance().quit()
                        csvWriter.writerow(row)
                finally:
                    self.saveLock.release()

    def getColumnNamesForSave(self):
        return []

    def getIpValidator(self):
        if not hasattr(self, 'objIpValidator'):
            strIpRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
            ipRegExp = QtCore.QRegExp(
                "^" + strIpRange + "\\." + strIpRange + "\\." + strIpRange + "\\." + strIpRange + "$")
            self.objIpValidator = QtGui.QRegExpValidator(ipRegExp, self)

        return self.objIpValidator

    def connectHandlers(self):
        self.lineEditClientHost.textChanged.connect(self.onClientHostChanged)
        self.btnClearData.clicked.connect(self.onClear)
        self.btnConnect.clicked.connect(self.onConnect)
        self.btnDisconnect.clicked.connect(self.onDisconnect)
        self.btnSendData.clicked.connect(self.onSendBtn)
        self.btnStopData.clicked.connect(self.emergencyStop)
        self.btnShowGraph1.clicked.connect(self.onGraph1Open)
        self.btnCloseGraph1.clicked.connect(self.onGraph1Close)
        self.btnExitFromApp.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.lineEditClientPort.textChanged.connect(self.onClientPortChanged)
        self.lineEditServerHost.textChanged.connect(self.onServerHostChanged)
        self.lineEditServerPort.textChanged.connect(self.onServerPortChanged)
        self.btnShowGraph2.clicked.connect(self.onGraph2Open)
        self.btnShowGraph3.clicked.connect(self.onGraph3Open)
        self.btnCloseGraph2.clicked.connect(self.onGraph2Close)
        self.btnCloseGraph3.clicked.connect(self.onGraph3Close)
        #self.actionOpen.triggered.connect(self.onOpen)
        self.actionSave.triggered.connect(self.onSave)

    def enableControls(self):
        self.btnDisconnect.setEnabled(False)
        self.btnSendData.setEnabled(False)
        # Graph start buttons
        self.btnShowGraph1.setEnabled(False)
        self.btnShowGraph2.setEnabled(False)
        self.btnShowGraph3.setEnabled(False)
        # Graph stop buttons
        self.btnCloseGraph1.setEnabled(False)
        self.btnCloseGraph2.setEnabled(False)
        self.btnCloseGraph3.setEnabled(False)

    def setTexts(self):
        self.groupBoxNetworkInit.setTitle("Network Initialization")
        self.labelClientHost.setText("Client Host:")
        self.labelClientPort.setText("Client Port:")
        self.labelServerHost.setText("Server Host:")
        self.labelServerPort.setText("Server Port:")
        self.labelOpenCloseCnt.setText("Open or Close Connection:")
        self.btnConnect.setText("Create Socket")
        self.btnDisconnect.setText("Close Socket")
        self.btnClearData.setText("Clear Values")
        self.groupBoxGraphs.setTitle("Graphs")
        self.btnShowGraph1.setText("ShowGraphLevel1")
        self.btnCloseGraph1.setText("StopGraph1")
        self.btnShowGraph2.setText("ShowGraphLevel2")
        self.btnCloseGraph2.setText("StopGraph2")
        self.btnShowGraph3.setText("ShowGraphLevel3")
        self.btnCloseGraph3.setText("StopGraph3")
        self.groupBoxDataSent.setTitle("DataSent(bytes)")
        self.labelOnDataSent.setText("0")
        self.groupBoxOutputData.setTitle("Output Data [cm]")
        self.labelStaticLevel2.setText("Level2:")
        self.labelLevel3Value.setText("0.0000")
        self.labelStaticLevel3.setText("Level3:")
        self.labelLevel2Value.setText("0.0000")
        self.labelLevel1Value.setText("0.0000")
        self.labelStaticLevel1.setText("Level1:")
        self.btnExitFromApp.setText("Exit from whole application")
        self.groupBoxParametersInit.setTitle("Parameters Initialization")
        self.labelSendParametersStatic.setText("Send Parameters:")

        self.btnStopData.setText("Stop")

    def createUI(self):
        self.resize(523, 601)
        self.move(0, 0)

        #self.actionOpen = QtGui.QAction(self)
        #self.actionOpen.setText("&Open...")
        self.actionSave = QtGui.QAction(self)
        self.actionSave.setText("&Save...")
        self.menuBar = QtGui.QMenuBar(self)
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setTitle("&File")
        #self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.gridLayoutBasicWindow = QtGui.QGridLayout(self)
        self.gridLayoutBasicWindow.setContentsMargins(10, 40, 10, 10)
        self.groupBoxNetworkInit = QtGui.QGroupBox(self)
        self.verticalLayoutGroupBox = QtGui.QVBoxLayout(self.groupBoxNetworkInit)
        self.labelClientHost = QtGui.QLabel(self.groupBoxNetworkInit)
        self.verticalLayoutGroupBox.addWidget(self.labelClientHost)
        self.lineEditClientHost = QtGui.QLineEdit(self.groupBoxNetworkInit)
        self.lineEditClientHost.setText(DEFAULT_CLIENT_IP)
        self.lineEditClientHost.setMaxLength(IP_LEN)
        self.lineEditClientHost.setValidator(QtGui.QIntValidator())
        self.lineEditClientHost.setValidator(self.getIpValidator())
        self.verticalLayoutGroupBox.addWidget(self.lineEditClientHost)
        self.labelClientPort = QtGui.QLabel(self.groupBoxNetworkInit)
        self.verticalLayoutGroupBox.addWidget(self.labelClientPort)
        self.lineEditClientPort = QtGui.QLineEdit(self.groupBoxNetworkInit)
        self.lineEditClientPort.setText(DEFAULT_CLIENT_PORT)
        self.lineEditClientPort.setMaxLength(PORT_LEN)
        self.lineEditClientPort.setValidator(QtGui.QIntValidator())
        self.verticalLayoutGroupBox.addWidget(self.lineEditClientPort)
        self.line = QtGui.QFrame(self.groupBoxNetworkInit)
        self.line.setFrameShadow(QtGui.QFrame.Raised)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.verticalLayoutGroupBox.addWidget(self.line)
        self.labelServerHost = QtGui.QLabel(self.groupBoxNetworkInit)
        self.verticalLayoutGroupBox.addWidget(self.labelServerHost)
        self.lineEditServerHost = QtGui.QLineEdit(self.groupBoxNetworkInit)
        self.lineEditServerHost.setText(DEFAULT_SERVER_IP)
        self.lineEditServerHost.setMaxLength(IP_LEN)
        self.lineEditServerHost.setValidator(self.getIpValidator())
        self.verticalLayoutGroupBox.addWidget(self.lineEditServerHost)
        self.labelServerPort = QtGui.QLabel(self.groupBoxNetworkInit)
        self.verticalLayoutGroupBox.addWidget(self.labelServerPort)
        self.lineEditServerPort = QtGui.QLineEdit(self.groupBoxNetworkInit)
        self.lineEditServerPort.setText(DEFAULT_SERVER_PORT)
        self.lineEditServerPort.setMaxLength(PORT_LEN)
        self.lineEditServerPort.setValidator(QtGui.QIntValidator())
        self.verticalLayoutGroupBox.addWidget(self.lineEditServerPort)
        self.labelOpenCloseCnt = QtGui.QLabel(self.groupBoxNetworkInit)
        self.labelOpenCloseCnt.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.verticalLayoutGroupBox.addWidget(self.labelOpenCloseCnt)
        self.btnConnect = QtGui.QPushButton(self.groupBoxNetworkInit)
        self.btnConnect.setAutoFillBackground(False)
        self.verticalLayoutGroupBox.addWidget(self.btnConnect)
        self.btnDisconnect = QtGui.QPushButton(self.groupBoxNetworkInit)
        self.verticalLayoutGroupBox.addWidget(self.btnDisconnect)
        self.line_2 = QtGui.QFrame(self.groupBoxNetworkInit)
        self.line_2.setFrameShadow(QtGui.QFrame.Raised)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.verticalLayoutGroupBox.addWidget(self.line_2)
        self.btnClearData = QtGui.QPushButton(self.groupBoxNetworkInit)
        self.verticalLayoutGroupBox.addWidget(self.btnClearData)
        self.gridLayoutBasicWindow.addWidget(self.groupBoxNetworkInit, 0, 0, 1, 1)
        self.groupBoxGraphs = QtGui.QGroupBox(self)
        self.gridLayoutGraphs = QtGui.QGridLayout(self.groupBoxGraphs)
        self.btnShowGraph1 = QtGui.QPushButton(self.groupBoxGraphs)
        self.gridLayoutGraphs.addWidget(self.btnShowGraph1, 0, 0, 1, 1)
        self.btnCloseGraph1 = QtGui.QPushButton(self.groupBoxGraphs)
        self.gridLayoutGraphs.addWidget(self.btnCloseGraph1, 0, 1, 1, 1)
        self.btnShowGraph2 = QtGui.QPushButton(self.groupBoxGraphs)
        self.gridLayoutGraphs.addWidget(self.btnShowGraph2, 1, 0, 1, 1)
        self.btnCloseGraph2 = QtGui.QPushButton(self.groupBoxGraphs)
        self.gridLayoutGraphs.addWidget(self.btnCloseGraph2, 1, 1, 1, 1)
        self.btnShowGraph3 = QtGui.QPushButton(self.groupBoxGraphs)
        self.gridLayoutGraphs.addWidget(self.btnShowGraph3, 2, 0, 1, 1)
        self.btnCloseGraph3 = QtGui.QPushButton(self.groupBoxGraphs)
        self.gridLayoutGraphs.addWidget(self.btnCloseGraph3, 2, 1, 1, 1)
        self.gridLayoutBasicWindow.addWidget(self.groupBoxGraphs, 1, 1, 2, 1)
        self.groupBoxDataSent = QtGui.QGroupBox(self)
        self.labelOnDataSent = QtGui.QLabel(self.groupBoxDataSent)
        self.labelOnDataSent.setGeometry(QtCore.QRect(20, 30, 60, 16))
        self.gridLayoutBasicWindow.addWidget(self.groupBoxDataSent, 2, 0, 2, 1)
        self.groupBoxOutputData = QtGui.QGroupBox(self)
        self.gridLayoutOutputData = QtGui.QGridLayout(self.groupBoxOutputData)
        self.labelStaticLevel2 = QtGui.QLabel(self.groupBoxOutputData)
        self.gridLayoutOutputData.addWidget(self.labelStaticLevel2, 1, 0, 1, 1)
        self.labelStaticLevel3 = QtGui.QLabel(self.groupBoxOutputData)
        self.gridLayoutOutputData.addWidget(self.labelStaticLevel3, 2, 0, 1, 1)
        self.labelLevel1Value = QtGui.QLabel(self.groupBoxOutputData)
        self.lstLabelsForData.append(self.labelLevel1Value)
        self.gridLayoutOutputData.addWidget(self.labelLevel1Value, 0, 1, 1, 1)
        self.labelLevel2Value = QtGui.QLabel(self.groupBoxOutputData)
        self.lstLabelsForData.append(self.labelLevel2Value)
        self.gridLayoutOutputData.addWidget(self.labelLevel2Value, 1, 1, 1, 1)
        self.labelLevel3Value = QtGui.QLabel(self.groupBoxOutputData)
        self.lstLabelsForData.append(self.labelLevel3Value)
        self.gridLayoutOutputData.addWidget(self.labelLevel3Value, 2, 1, 1, 1)
        self.labelStaticLevel1 = QtGui.QLabel(self.groupBoxOutputData)
        self.gridLayoutOutputData.addWidget(self.labelStaticLevel1, 0, 0, 1, 1)
        self.gridLayoutBasicWindow.addWidget(self.groupBoxOutputData, 1, 0, 1, 1)
        self.btnExitFromApp = QtGui.QPushButton(self)
        self.gridLayoutBasicWindow.addWidget(self.btnExitFromApp, 3, 1, 1, 1)
        self.groupBoxParametersInit = QtGui.QGroupBox(self)
        self.gridLayoutParametersInit = QtGui.QGridLayout(self.groupBoxParametersInit)
        self.labelInputValve3 = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelInputValve3, 7, 1, 1, 1)
        self.labelValve1Static = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelValve1Static, 3, 0, 1, 1)
        self.labelInputValve2 = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelInputValve2, 5, 1, 1, 1)
        self.labelInputMotor = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelInputMotor, 1, 1, 1, 1)
        self.labelSendParametersStatic = QtGui.QLabel(self.groupBoxParametersInit)
        self.labelSendParametersStatic.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayoutParametersInit.addWidget(self.labelSendParametersStatic, 9, 0, 1, 2)
        self.labelInputValve1 = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelInputValve1, 3, 1, 1, 1)
        self.labelWarnValues = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelWarnValues, 0, 0, 1, 2)
        self.labelMotorStatic = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelMotorStatic, 1, 0, 1, 1)
        self.labelValve3Static = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelValve3Static, 7, 0, 1, 1)
        self.labelValve2Static = QtGui.QLabel(self.groupBoxParametersInit)
        self.gridLayoutParametersInit.addWidget(self.labelValve2Static, 5, 0, 1, 1)

        self.btnSendData = QtGui.QPushButton(self.groupBoxParametersInit)
        self.btnSendData.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayoutParametersInit.addWidget(self.btnSendData, 10, 0, 1, 1)

        self.btnStopData = QtGui.QPushButton(self.groupBoxParametersInit)
        self.btnStopData.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btnStopData.setStyleSheet('QPushButton {background-color: #FF0000; color: white;}')
        self.gridLayoutParametersInit.addWidget(self.btnStopData, 11, 0, 1, 1)

        self.gridLayoutBasicWindow.addWidget(self.groupBoxParametersInit, 0, 1, 1, 1)

    def resizeEvent(self, event):
        QtGui.QWidget.resizeEvent(self, event)
        # Resize menu to fill entire dialog
        self.menuBar.setFixedWidth(self.width())
