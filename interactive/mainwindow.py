#!/usr/bin/env python

##
# Copyright 2010--2013 Graham Percival
# This file is part of Artifastring.
#
# Artifastring is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Artifastring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with Artifastring.  If not, see
# <http://www.gnu.org/licenses/>.
##

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

