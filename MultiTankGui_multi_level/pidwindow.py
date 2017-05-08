from PyQt4 import QtCore, QtGui
from windowbase import WindowBase
from PID import PID
from config import *

class PIDWindow(WindowBase):
    MAX_DIGITS_IN_PID_VALUES = 5
    SAVE_TITLES = [
        'Motor (out)',
        'Derivative (internal)',
        'Integral (internal)',
        'Proportional (internal)',
        'Set point (internal)',
        'Last error (internal)',
        'Level 1 (in)',
        'Level 2 (in)',
        'Level 3 (in)'
    ]

    def __init__(self, parent=None):
        super(PIDWindow, self).__init__(parent)
        self.resetOutValuesOnSend = True
        self.lstOutValues = [0.0, 0.0, 0.0, 0.0]
        self.lstCustomData = ['0.0000', '0.0000', '0.0000', '0.0000', '0.0000']
        #  self.pid = PID(0.0, 0.0, 0.0)
        self.lstPIDs = [PID(0.0, 0.0, 0.0), PID(0.0, 0.0, 0.0), PID(0.0, 0.0, 0.0)]

    def getValuesForSend(self):
        return self.lstOutValues

    def getOutValuesForSave(self):
        return self.lstOutValues

    def customProcessingOnReceive(self, lstServerData): # lstServerData data from server
        if not self.stopped:
            nLevel, success = self.comboBoxPID.itemData(self.comboBoxPID.currentIndex()).toInt()
            if -1 == nLevel or not success:
                for idx in range(len(self.lstOutValues)): # Old value was lstServerData
                    self.usePID(idx, lstServerData)
            else:
                self.usePID(nLevel - 1, lstServerData)
            self.onSend()

    def getColumnNamesForSave(self):
        return self.SAVE_TITLES

    def getCustomDataForSave(self):
        return self.lstCustomData

    def usePID(self, idx, lstServerData):
        print "Apply PID to level " + str(idx + 1) + " Value:" + str(lstServerData[idx])

        pidToUse = self.lstPIDs[idx]

        fKd = self.getFloatValue(self.lineEditDerivative)
        fKi = self.getFloatValue(self.lineEditIntegral)
        fKp = self.getFloatValue(self.lineEditProportional)
        pidToUse.setKd(fKd)
        pidToUse.setKi(fKi)
        pidToUse.setKp(fKp)

        setPoint = self.getFloatValue(self.lineEditSetPoint)
        # Update set point for graph
        self.updateSetPoint(setPoint)
        # Update set point in PID
        pidToUse.SetPoint = setPoint

        # get new value from PID and update output data
        pidToUse.update(lstServerData[idx])
        self.lstOutValues[0] = round(pidToUse.output, 1) / 100
        # self.lstOutValues[1] = round(pidToUse.output, 2) / 100
        # self.lstOutValues[2] = round(pidToUse.output, 2) / 100
        # self.lstOutValues[3] = round(pidToUse.output, 2) / 100


        self.lstCustomData = [
            formatFloat(fKd),
            formatFloat(fKi),
            formatFloat(fKp),
            formatFloat(setPoint),
            formatFloat(pidToUse.last_error / 100)
        ]

    # Converting str to float. Default value is 0
    def getFloatValue(self, ctrl, defaultVal = 0.0):
        strVal = ctrl.text()
        dVal = defaultVal
        if 0 != len(strVal):
            dValueToUser, success = strVal.toDouble()
            if success:
                dVal = dValueToUser
        return dVal

    def onSetPointChanged(self, text):
        print "Set Point: " + text

    def onProportionalChanged(self, text):
        print "Proportional: " + text

    def onIntegralChanged(self, text):
        print "Integral: " + text

    def onDerivativeChanged(self, text):
        print "Derivative: " + text

    def emergencyStop(self):
        super(PIDWindow, self).emergencyStop()
        print "Stop from PidWindow!"
        self.lstOutValues = [0.0, 0.0, 0.0, 0.0]  # Old value: [0.0, 0.0, 0.0, 0.0]
        self.lstPIDs = [PID(0.0, 0.0, 0.0)]
        self.onSend()

    def connectHandlers(self):
        super(PIDWindow, self).connectHandlers()
        self.lineEditSetPoint.textChanged.connect(self.onSetPointChanged)
        self.lineEditProportional.textChanged.connect(self.onProportionalChanged)
        self.lineEditIntegral.textChanged.connect(self.onIntegralChanged)
        self.lineEditDerivative.textChanged.connect(self.onDerivativeChanged)

    def enableControls(self):
        super(PIDWindow, self).enableControls()
        self.lineEditSetPoint.setEnabled(True)
        self.lineEditProportional.setEnabled(True)
        self.lineEditIntegral.setEnabled(True)
        self.lineEditDerivative.setEnabled(True)
        #self.comboBoxPID.setEnabled(True)

    def setTexts(self):
        super(PIDWindow, self).setTexts()

        self.setWindowTitle("PID Controller")
        self.labelMotorStatic.setText("Set Point:")
        self.labelValve1Static.setText("Proportional:")
        self.labelValve2Static.setText("Integral:")
        self.labelValve3Static.setText("Derivative:")
        self.labelWarnValues.setText("PID Controller Parameters:")
        # self.lineEditSetPoint.setText("0.0000")
        self.lineEditProportional.setText("0.000")
        self.lineEditIntegral.setText("0.000")
        self.lineEditDerivative.setText("0.000")
        self.btnSendData.setText("Resume")

    def createUI(self):
        super(PIDWindow, self).createUI()

        self.comboBoxPID = QtGui.QComboBox(self.groupBoxParametersInit)
        self.comboBoxPID.setObjectName("comboBoxPID")
        #self.comboBoxPID.addItem("All Levels", -1)
        self.comboBoxPID.addItem("Level1", 1)
        self.comboBoxPID.addItem("Level2", 2)
        self.comboBoxPID.addItem("Level3", 3)
        self.comboBoxPID.setEditable(False)
        self.gridLayoutParametersInit.addWidget(self.comboBoxPID, 0, 0, 1, 1)

        self.lineEditIntegral = QtGui.QLineEdit(self.groupBoxParametersInit)
        self.lineEditIntegral.setValidator(QtGui.QDoubleValidator())
        self.lineEditIntegral.setMaxLength(self.MAX_DIGITS_IN_PID_VALUES)
        self.gridLayoutParametersInit.addWidget(self.lineEditIntegral, 6, 0, 1, 1)

        self.lineEditDerivative = QtGui.QLineEdit(self.groupBoxParametersInit)
        self.lineEditDerivative.setValidator(QtGui.QDoubleValidator())
        self.lineEditDerivative.setMaxLength(self.MAX_DIGITS_IN_PID_VALUES)
        self.gridLayoutParametersInit.addWidget(self.lineEditDerivative, 8, 0, 1, 1)

        self.lineEditSetPoint = QtGui.QLineEdit(self.groupBoxParametersInit)
        self.lineEditSetPoint.setValidator(QtGui.QDoubleValidator())
        self.lineEditSetPoint.setMaxLength(self.MAX_DIGITS_IN_PID_VALUES)
        self.gridLayoutParametersInit.addWidget(self.lineEditSetPoint, 2, 0, 1, 1)

        self.lineEditProportional = QtGui.QLineEdit(self.groupBoxParametersInit)
        self.lineEditProportional.setValidator(QtGui.QDoubleValidator())
        self.lineEditProportional.setMaxLength(self.MAX_DIGITS_IN_PID_VALUES)
        self.gridLayoutParametersInit.addWidget(self.lineEditProportional, 4, 0, 1, 1)
