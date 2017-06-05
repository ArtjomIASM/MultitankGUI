from PyQt4 import QtCore, QtGui
from windowbase import WindowBase

class BasicWindow(WindowBase):
    SLIDER_START_VALUE = 0
    LEVEL_SLIDER_STEPS = 20.0
    STOP_VALUES = [0.0, 0.0, 0.0, 0.0]
    SAVE_TITLES = [
        'Motor (out)',
        'Level 1 (out)',
        'Level 2 (out)',
        'Level 3 (out)',
        'Level 1 (in)',
        'Level 2 (in)',
        'Level 3 (in)'
    ]

    def __init__(self, parent=None):
        super(BasicWindow, self).__init__(parent)

    def emergencyStop(self):
        super(BasicWindow, self).emergencyStop()
        self.onSend()
        print "Stop from BasicWindow!"

    def getValuesForSend(self):
        if self.stopped:
            arrData = self.STOP_VALUES
        else:
            arrData = [
                float(self.labelInputMotor.text()),
                float(self.labelInputValve1.text()),
                float(self.labelInputValve2.text()),
                float(self.labelInputValve3.text())
            ]
        return arrData

    def getColumnNamesForSave(self):
        return self.SAVE_TITLES

    def onMotorChanged(self, value):
        self.updateValue(value, self.labelInputMotor, "Motor")

    def onLevel1Changed(self, value):
        self.updateValue(value, self.labelInputValve1, "Level1")

    def onLevel2Changed(self, value):
        self.updateValue(value, self.labelInputValve2, "Level2")

    def onLevel3Changed(self, value):
        self.updateValue(value, self.labelInputValve3, "Level3")

    def updateValue(self, value, objLabel, strNameForLog):        
        formattedValue = '{0:.3f}'.format(value / self.LEVEL_SLIDER_STEPS)
        objLabel.setText(formattedValue)
        print strNameForLog + ": " + formattedValue
        # Remove comment from "self.onSend()" for instant send
        #self.onSend()

    def connectHandlers(self):
        super(BasicWindow, self).connectHandlers()
        self.horizontalSliderValve1.valueChanged.connect(self.onLevel1Changed)
        self.horizontalSliderValve2.valueChanged.connect(self.onLevel2Changed)
        self.horizontalSliderValve3.valueChanged.connect(self.onLevel3Changed)
        self.horizontalSliderMotor.valueChanged.connect(self.onMotorChanged)

    def enableControls(self):
        super(BasicWindow, self).enableControls()
        self.horizontalSliderValve2.setEnabled(True)
        self.horizontalSliderValve3.setEnabled(True)
        self.horizontalSliderMotor.setEnabled(True)
        self.horizontalSliderValve1.setEnabled(True)

    def enableControlsTrue(self):
        super(BasicWindow, self).enableControls()
        self.horizontalSliderValve2.setEnabled(True)
        self.horizontalSliderValve3.setEnabled(True)
        self.horizontalSliderMotor.setEnabled(True)
        self.horizontalSliderValve1.setEnabled(True)

    def setTexts(self):
        super(BasicWindow, self).setTexts()
        self.setWindowTitle("Basic Test")
        self.labelMotorStatic.setText("Motor:")
        self.labelValve1Static.setText("Valve1:")
        self.labelValve2Static.setText("Valve2:")
        self.labelValve3Static.setText("Valve3:")
        self.labelInputMotor.setText("0.000")
        self.labelInputValve1.setText("0.000")
        self.labelInputValve2.setText("0.000")
        self.labelInputValve3.setText("0.000")
        self.labelWarnValues.setText("NB! VALUES FROM 0,000 - 1,000")
        self.btnSendData.setText("Send/Resume")

    def createUI(self):
        super(BasicWindow, self).createUI()

        self.horizontalSliderValve2 = QtGui.QSlider(self.groupBoxParametersInit)
        self.horizontalSliderValve2.setRange(self.SLIDER_START_VALUE, self.LEVEL_SLIDER_STEPS)
        self.horizontalSliderValve2.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayoutParametersInit.addWidget(self.horizontalSliderValve2, 6, 0, 1, 1)

        self.horizontalSliderValve3 = QtGui.QSlider(self.groupBoxParametersInit)
        self.horizontalSliderValve3.setRange(self.SLIDER_START_VALUE, self.LEVEL_SLIDER_STEPS)
        self.horizontalSliderValve3.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayoutParametersInit.addWidget(self.horizontalSliderValve3, 8, 0, 1, 1)

        self.horizontalSliderMotor = QtGui.QSlider(self.groupBoxParametersInit)
        self.horizontalSliderMotor.setRange(self.SLIDER_START_VALUE, self.LEVEL_SLIDER_STEPS)
        self.horizontalSliderMotor.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayoutParametersInit.addWidget(self.horizontalSliderMotor, 2, 0, 1, 1)

        self.horizontalSliderValve1 = QtGui.QSlider(self.groupBoxParametersInit)
        self.horizontalSliderValve1.setRange(self.SLIDER_START_VALUE, self.LEVEL_SLIDER_STEPS)
        self.horizontalSliderValve1.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayoutParametersInit.addWidget(self.horizontalSliderValve1, 4, 0, 1, 1)
