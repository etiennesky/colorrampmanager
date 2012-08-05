# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ColorRampManagerDialog
                                 A QGIS plugin
 plugin to manage and download color ramp definitions
                             -------------------
        begin                : 2012-08-04
        copyright            : (C) 2012 by Etienne Tourigny
        email                : etourigny dot dev at gmail dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_colorrampmanager import Ui_ColorRampManager
# create the dialog for zoom to point
class ColorRampManagerDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_ColorRampManager()
        self.ui.setupUi(self)
