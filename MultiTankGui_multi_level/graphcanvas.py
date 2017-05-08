import traceback, sys
import matplotlib
import numpy as np
import random

matplotlib.use("Qt4Agg")
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from time import time
from threading import Lock
from matplotlib.ticker import FuncFormatter
from config import *

class GraphCanvas(FigureCanvas, TimedAnimation):
    TAIL_LEN_SEC = 2
    TIME_MARGIN = 5

    def __init__(self, graphXLimit, graphYLimit, graphYLevelMin):
        print("Using: matplotlib v." + matplotlib.__version__)

        timeSpanFormatter = FuncFormatter(self.formatTime)

        self.graphXLimit = graphXLimit
        self.graphYLimit = graphYLimit
        self.graphYLevelMin = graphYLevelMin
        self.valuesXYP = ([0.0], [0.0], -1)  # !!! must not be accessed directly only via sedData() and getData()
        self.dataLock = Lock()

        # The window
        self.fig = Figure(dpi=100)
        self.ax1 = self.fig.add_subplot(111)

        # self.ax1 settings
        self.ax1.set_xlabel('Time')
        self.ax1.set_ylabel('Level')
        self.ax1.grid(True)
        self.ax1.xaxis.set_major_formatter(timeSpanFormatter)
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax1.set_xlim(0, self.graphXLimit - 1)  # X axis range
        self.ax1.set_ylim(self.graphYLevelMin, self.graphYLimit - 1)  # Y axis range

        self.line_setPoint = None

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=TIMED_INTERVAL, blit=False)
        # Graph interval for delay in millisecond / Change it if you have weak cpu
        # Set blit = True if need more cpu %

    def closeEvent(self, event):
        # Stop the animation loop on exit
        FigureCanvas.closeEvent(self, event)
        self._stop()
        event.accept()

    def setData(self, valuesX, valuesY, setPoint):
        # To avoid manipulations with partially updated data, do update under lock
        self.dataLock.acquire(True)
        try:
            self.valuesXYP = (valuesX, valuesY, setPoint)
        finally:
            self.dataLock.release()

    def getData(self):
        self.dataLock.acquire(True)
        try:
            return self.valuesXYP
        finally:
            self.dataLock.release()

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for line2D in lines:
            line2D.set_data([], [])
        if None != self.line_setPoint:
            self.line_setPoint.set_data([], [])

    def _step(self, *args):
        try:  # Extends the _step() method for the TimedAnimation class.
            TimedAnimation._step(self, *args)
        except Exception as e:
            print("Failed to execute animation. Animation stopped!")
            traceback.print_exc(file=sys.stdout)
            TimedAnimation._stop(self)
            pass

    def new_frame_seq(self):
        return iter(range(self.valuesXYP[0].__len__()))

    def _draw_frame(self, framedata):  # Draw graph line itself
        # Print random.uniform(0, 10) # Check if drawing closed
        valuesX, valuesY, setPoint = self.getData()
        tailXY = (valuesX, valuesY)
        self.line1.set_data(valuesX, valuesY)

        lastTimeValue = valuesX[len(valuesX) - 1]
        tailEndTime = lastTimeValue - self.TAIL_LEN_SEC
        for i in reversed(range(len(valuesX))):
            if valuesX[i] < tailEndTime:
                tailStartIdx = min(i + 1, len(valuesX))
                tailEndIndex = len(valuesX)
                if (tailStartIdx == tailEndIndex and len(valuesX) > 1):
                    tailStartIdx = len(valuesX) - 2
                tailXY = (valuesX[tailStartIdx: tailEndIndex], valuesY[tailStartIdx: tailEndIndex])
                break

        self.line1_tail.set_data(tailXY)
        self.line1_head.set_data([valuesX[len(valuesX) - 1]], [valuesY[len(valuesY) - 1]])

        lastTimeValueRounded = round(lastTimeValue, 0)
        # Maximum and minimum values for x
        xMin = max(0, lastTimeValueRounded - self.graphXLimit + self.TIME_MARGIN)
        xMax = max(self.graphXLimit, lastTimeValueRounded + self.TIME_MARGIN)
        self.ax1.set_xlim(xMin, xMax)  # X axis range

        # Create set point line
        if self.line_setPoint is None and -1 != setPoint:
            self.line_setPoint = Line2D([], [], color='black')
            self.ax1.add_line(self.line_setPoint)

        lstArtists = [self.line1, self.line1_tail, self.line1_head, self.ax1]
        if None != self.line_setPoint:
            self.line_setPoint.set_data([xMin, xMax], [setPoint, setPoint])
            lstArtists.append(self.line_setPoint)

        self._drawn_artists = lstArtists

    def formatTime(self, value, position):
        nHours, nRemainder = divmod(int(value), 3600)
        nMinutes, nSeconds = divmod(nRemainder, 60)
        if (nHours > 0):
            return '%02d:02%d:02%d' % (nHours, nMinutes, nSeconds)
        else:
            return '%02d:%02d' % (nMinutes, nSeconds)
