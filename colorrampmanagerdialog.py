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
from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog, QFileDialog, QMessageBox
from qgis.core import *
import os

from ui_colorrampmanager import Ui_ColorRampManager

# create the dialog
class ColorRampManagerDialog(QDialog, Ui_ColorRampManager):

    def __init__(self):

        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_ColorRampManager()
        self.setupUi(self)
        #self.updateUi()

        self.installDir = QString() #here a QString
        self.checkUpdateAuto = QtCore.pyqtSignal() 
        self.connect(self, SIGNAL("checkUpdate"),
                     self.pbtnUpdateCheck, SIGNAL('clicked()'))

    def updateUI(self):
        #enable/disable update buttons
        self.pbtnUpdateCheck.setEnabled( True )

        #TODO other OSes

        # set dir. labels
        s = QSettings()
        self.installDir = s.value('CptCity/installDir', QgsApplication.qgisSettingsDirPath()).toString()
        dirSystem = '/usr'
        self.lblDirSystem.setText(dirSystem + '/share/')
        if dirSystem == QgsApplication.prefixPath():
            self.rbtnDirQgis.setVisible( False )
            self.lblDirQgis.setVisible( False )
            self.rbtnDirQgis.setEnabled( False )
            self.lblDirQgis.setEnabled( False )
        else:
            if not os.access(self.lblDirSystem.text(), os.W_OK):
                self.rbtnDirSystem.setEnabled( False )
                self.lblDirSystem.setEnabled( False )
        self.lblDirQgis.setText(QgsApplication.prefixPath() + '/share/')
        if not os.access(self.lblDirQgis.text(), os.W_OK):
            self.rbtnDirQgis.setEnabled( False )
            self.lblDirQgis.setEnabled( False )
        self.lblDirUser.setText(QgsApplication.qgisSettingsDirPath())
        self.leDirCustom.setText('')

        # set which dir is selected, default is in user dir
        if self.rbtnDirSystem.isEnabled() and self.installDir == self.lblDirSystem.text():
            self.rbtnDirSystem.setChecked( True )
        elif self.installDir == self.lblDirQgis.text():
            self.rbtnDirQgis.setChecked( True )
        elif self.installDir == self.lblDirUser.text():
            self.rbtnDirUser.setChecked( True )
        elif self.installDir != '':
            self.rbtnDirCustom.setChecked( True )
            self.leDirCustom.setText( self.installDir )
        else:
            self.rbtnDirUser.setChecked( True )
            self.installDir = self.lblDirUser.text()
            
    def apply(self):
        if self.rbtnDirCustom.isChecked():
            installDir = self.leDirCustom.text()
        s = QSettings()
        if str(self.installDir) != '':
            s.setValue('CptCity/installDir', self.installDir)
        if self.cboxCheckUpdateAuto.isChecked():
            checkAuto=7
        else:
            checkAuto=0
        s.setValue('CptCity/updateCheckAuto', checkAuto)
        

    def on_buttonGroupDir_buttonClicked(self, button):
        name = self.buttonGroupDir.checkedButton().objectName()
        if name == 'rbtnDirSystem':
            self.installDir = self.lblDirSystem.text()
        elif name == 'rbtnDirQgis':
            self.installDir = self.lblDirQgis.text()
        elif name == 'rbtnDirUser':
            self.installDir = self.lblDirUser.text()
        elif name == 'rbtnDirCustom':
            self.installDir = self.leDirCustom.text()
       
    def on_btnDirCustom_pressed(self):
        selectedDir = QFileDialog.getExistingDirectory(self, self.tr('Open Directory'),
                                                       os.environ['HOME'],
                                                       QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks);
        if selectedDir is not None and selectedDir != '':
            self.leDirCustom.setText(selectedDir)
            self.installDir = selectedDir

    def show(self):
        QDialog.show(self)
        # if we have an available update, go fetch it
        s = QSettings()
        if str(s.value('CptCity/updateAvailable', '').toString()) != '':
            self.emit(SIGNAL('checkUpdate'))

