#!/usr/bin/env python

import sys
#from PyQt4 import QtGui, QtCore

from PyQt4 import QtGui
import mainwindow_gui

import parameter_control

class Mainwindow(QtGui.QMainWindow):
    def __init__(self):
        self.app =  QtGui.QApplication([])
        QtGui.QMainWindow.__init__(self)

        self.ui = mainwindow_gui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        param = parameter_control.ParameterControl(
            "force", 0, 1, 0.5)
        self.ui.parameters.layout().addWidget(param)

        mouse = MouseArea()
        self.ui.verticalLayout.addWidget(mouse)

class MouseArea(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

    def mousePressEvent(self, event):
        print event.x(), event.y()
        QtGui.QWidget.mousePressEvent(self, event)


def main():
    mainwindow = Mainwindow()
    sys.exit(mainwindow.app.exec_())

if __name__ == "__main__":
    main()

