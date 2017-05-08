from PyQt4 import QtCore, QtGui
from graphcanvas import GraphCanvas
from threading import Lock
from time import time
from matplotlib.backends.backend_qt4agg import ( FigureCanvasQTAgg as FigureCanvas,
                                                 NavigationToolbar2QT as NavigationToolbar)
'''Creating graph'''
class GraphDialog(QtGui.QDialog):
    GRAPH_TIME_SPAN_SEC = 60 # Length of the steps in seconds
    GRAPH_LEVEL_MAX = 35
    GRAPH_LEVEL_MIN = -1

    def __init__(self, transport, nGraphId, closeCbk=None, parent=None):
        super(GraphDialog, self).__init__(parent)

        self.nGraphId = nGraphId
        self.transport = transport
        self.closeCbk = closeCbk
        self.bPause = False
        self.lstValuesXY = []
        self.setPoint = -1
        self.startTime = None
        self.receiveLock = Lock()


        self.setWindowTitle("Level " + str(self.nGraphId))
        #self.setGeometry(545, 0, 400, 300)
        self.graphCanvas = GraphCanvas(self.GRAPH_TIME_SPAN_SEC, self.GRAPH_LEVEL_MAX, self.GRAPH_LEVEL_MIN)
        self.toolbar = NavigationToolbar(self.graphCanvas, self)
        gridLayout = QtGui.QVBoxLayout(self)
        gridLayout.addWidget(self.toolbar)
        gridLayout.addWidget(self.graphCanvas)
        self.show()

        self.transport.registerCallback(self, self.onDataReceived)

    def doPause(self):
        self.bPause = True

    def doResume(self):
        self.bPause = False

    def updateSetPoint(self, val):
        self.setPoint = val

    def onDataReceived(self, lstServerData):
        if self.nGraphId < 0 or lstServerData.__len__() < self.nGraphId:
            QtGui.QMessageBox.information(self, 'Error', "Data for provided graph id doesn't exist!")
            QtCore.QCoreApplication.instance().quit()

        # Assign start time when first chunk of data is received
        if None == self.startTime:
            self.startTime = time()

        timeNow = time()
        timeSpan = timeNow - self.startTime
        fValueToUse = lstServerData[self.nGraphId - 1]
        print "Graph " + str(self.nGraphId) + " received value " + str(round(fValueToUse, 4)) + "\ttime " + str(round(timeSpan, 2)) + " sec"

        # onDataReceived callback can be called again in time of first call processing
        # to avoid corruption of lstValuesXY, data manipulation should be done under lock
        self.receiveLock.acquire(True)
        try:
            self.lstValuesXY.append([timeSpan, fValueToUse])

            # Remove all stale points (with time less than minimal time on graph)
            while (timeSpan - self.lstValuesXY[0][0]) > self.GRAPH_TIME_SPAN_SEC:
                del (self.lstValuesXY[0])

            if not self.bPause:
                # pass a copy of data to avoid synchronization issues
                valuesX = [row[0] for row in self.lstValuesXY] # Time
                valuesY = [row[1] for row in self.lstValuesXY] # Level
                self.graphCanvas.setData(valuesX, valuesY, self.setPoint)
        finally:
            self.receiveLock.release()

    def hideEvent(self, *args, **kwargs):
        super(GraphDialog, self).hideEvent(*args, **kwargs)
        self.transport.unRegisterCallback(self)
        if None != self.closeCbk:
            self.closeCbk(self.nGraphId)

        # Canvas creator is responsible for closing canvas
        self.graphCanvas.close()