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

#from PyQt4 import QtGui, QtCore
from PyQt4 import QtGui
import parameter_control_gui

class ParameterControl(QtGui.QWidget):
    def __init__(self, name, min_value, max_value, default_value):
        QtGui.QMainWindow.__init__(self)

        self.ui = parameter_control_gui.Ui_ParameterControl()
        self.ui.setupUi(self)

        self.ui.label.setText(name)

        ### connections
        # min/max
        self.ui.min_value_box.valueChanged.connect(
            self.set_min_value)
        self.ui.max_value_box.valueChanged.connect(
            self.set_max_value)
        # current value
        self.ui.current_value_box.valueChanged.connect(
            self.set_value_box)
        self.ui.current_value_slider.valueChanged.connect(
            self.set_value_slider)

        ### set initial parameters
        self.set_min_value(min_value)
        self.set_max_value(max_value)
        self.set_current_value(default_value)

    def set_current_value(self, value):
        self.value = value
        self.ui.current_value_box.setValue(value)


    def set_min_value(self, value):
        self.min_value = value
        self.ui.min_value_box.setValue(value)

    def set_max_value(self, value):
        self.max_value = value
        self.ui.max_value_box.setValue(value)

    def set_value_slider(self, value):
        new_value = float(value-self.min_value) / (
            99/(self.max_value - self.min_value))
        print value, new_value
        self.ui.current_value_box.setValue(new_value)

    def set_value_box(self, value):
        new_value = (value-self.min_value) * (
            99/(self.max_value - self.min_value))
        print value, new_value
        self.ui.current_value_slider.setValue(new_value)


