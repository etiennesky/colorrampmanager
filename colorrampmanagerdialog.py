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
        self.packageType = QString()
        self.checkUpdateAuto = QtCore.pyqtSignal() 
        self.connect(self, SIGNAL("checkUpdate"),
                     self.pbtnUpdateCheck, SIGNAL('clicked()'))

    def updateUI(self):
        #enable/disable update buttons
        self.pbtnUpdateCheck.setEnabled( True )

        #TODO other OSes

        # set dir. labels
        s = QSettings()
        self.installDir = s.value('CptCity/baseDir', \
                                      QgsApplication.pkgDataPath() + "/resources/" ).toString()
        print('got installdir='+str(self.installDir))
        self.lblDirQgis.setText(QgsApplication.pkgDataPath() + "/resources/")
        if not os.access(self.lblDirQgis.text(), os.W_OK):
            if self.installDir == QgsApplication.pkgDataPath() + "/resources/":
                self.installDir = QgsApplication.qgisSettingsDirPath()
            self.rbtnDirQgis.setEnabled( False )
            self.lblDirQgis.setEnabled( False )
        self.lblDirUser.setText(QgsApplication.qgisSettingsDirPath())
        #self.leDirCustom.setText('')

        print('got installdir='+str(self.installDir))
        # package type
        self.packageType = s.value('CptCity/archiveName', 'cpt-city-qgis-min').toString()
        print(str(self.packageType))
        if str(self.packageType) == 'cpt-city':
            self.rbtnPackageCptCity.setChecked( True )
        elif str(self.packageType) == 'cpt-city-qgis-sel':
            self.rbtnPackageQgis.setChecked( True )
        elif str(self.packageType) == 'cpt-city-qgis-min':
            self.rbtnPackageBuiltin.setChecked( True )
        #else:
            #self.cboxBuiltin.setChecked( False )
            #self.on_cboxBuiltin_toggled(self,checked):

        # set which dir is selected, default is in qgis user dir
 
        print('got installdir='+str(self.installDir))
        if self.installDir == self.lblDirQgis.text():
            self.rbtnDirQgis.setChecked( True )
        elif self.installDir == self.lblDirUser.text():
            self.rbtnDirUser.setChecked( True )
        elif self.installDir != '':
            print('custom')
            self.rbtnDirCustom.setChecked( True )
            self.leDirCustom.setText( self.installDir )
        elif self.installDir == QgsApplication.qgisSettingsDirPath():
            print('user')
            self.rbtnDirUser.setChecked( True )
            #self.installDir = QgsApplication.qgisSettingsDirPath()
        else:
            if str(self.packageType) == 'cpt-city-qgis-min' and self.rbtnDirQgis.isEnabled():
                self.rbtnDirQgis.setChecked( True )
            else:
                self.rbtnDirUser.setChecked( True )
            
        self.on_buttonGroupDir_buttonClicked(self.buttonGroupDir.checkedButton())
        self.on_buttonGroupPackage_buttonClicked(self.buttonGroupPackage.checkedButton())
        self.setLocation()
            

    def apply(self):
        if self.rbtnDirCustom.isChecked():
            installDir = self.leDirCustom.text()
        s = QSettings()
        if self.rbtnPackageBuiltin.isChecked():
            #s.setValue('CptCity/baseDir', QgsApplication.qgisSettingsDirPath() + QDir.separator() + "resources" )
            s.remove('CptCity/baseDir')
            s.remove('CptCity/archiveName')
            s.setValue('CptCity/updateCheckAuto', 0)
        else:
            if str(self.installDir) != '':
                s.setValue('CptCity/baseDir', self.installDir)
            if str(self.packageType) != '':
                s.setValue('CptCity/archiveName', self.packageType)
            if self.cboxCheckUpdateAuto.isChecked():
                checkAuto=7
            else:
                checkAuto=0
            s.setValue('CptCity/updateCheckAuto', checkAuto)
        

    def on_buttonGroupDir_buttonClicked(self, button):
        name = self.buttonGroupDir.checkedButton().objectName()
        if name == 'rbtnDirQgis':
            self.installDir = self.lblDirQgis.text()
        elif name == 'rbtnDirUser':
            self.installDir = self.lblDirUser.text()
        elif name == 'rbtnDirCustom':
            self.installDir = self.leDirCustom.text()
        self.setLocation()

    def on_buttonGroupPackage_buttonClicked(self, button):
        name = self.buttonGroupPackage.checkedButton().objectName()
        if name == 'rbtnPackageBuiltin':
            self.packageType = 'cpt-city-qgis-min'
        elif name == 'rbtnPackageQgis':
            self.packageType = 'cpt-city-qgis-sel'
        elif name == 'rbtnPackageCptCity':
            self.packageType = 'cpt-city'

        builtin = ( name == 'rbtnPackageBuiltin' )
        if builtin:
            self.installDir = self.lblDirQgis.text()
        else:
            self.on_buttonGroupDir_buttonClicked(self.buttonGroupDir.checkedButton())
        self.groupBoxDirectory.setEnabled(not builtin)
        self.pbtnUpdateCheck.setEnabled(not builtin)
        self.cboxCheckUpdateAuto.setEnabled(not builtin)

        self.setLocation()
       
    def on_btnDirCustom_pressed(self):
        selectedDir = QFileDialog.getExistingDirectory(self, self.tr('Open Directory'),
                                                       os.environ['HOME'],
                                                       QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks);
        if selectedDir is not None and selectedDir != '':
            selectedDir = selectedDir+QDir.separator()
            self.leDirCustom.setText(selectedDir)
            self.installDir = selectedDir
        #TODO add hook for edit changed
        self.setLocation()

    def setLocation(self):
        self.leLocation.setText(self.installDir+self.packageType)
        #if self.rbtnPackageBuiltin.isChecked():
        #    self.leLocation.setText(QgsApplication.pkgDataPath()+'/resources/cpt-city-qgis-min')
        #else:
        #    self.leLocation.setText(self.installDir+self.packageType)

    def show(self):
        QDialog.show(self)
        # if we have an available update, go fetch it
        s = QSettings()
        if str(s.value('CptCity/updateAvailable', '').toString()) != '':
            self.emit(SIGNAL('checkUpdate'))

