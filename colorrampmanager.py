# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ColorRampManager
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import time
from datetime import date
from qgis.core import *

# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from colorrampmanagerdialog import ColorRampManagerDialog

# Import update script
from cpt_city_update import cpt_city_update

#misc functions
def info(args) :
    if verbose :
        print args

def ensure_directory(path) :
    try:
        os.makedirs(path)
    except OSError, e:
        if os.path.isdir(path):
            pass
        else:
            raise

class ColorRampManager(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        # Save reference to the QGIS interface
        self.iface = iface
        # Create the dialog and keep reference
        self.dlg = ColorRampManagerDialog()
        
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/colorrampmanager"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale").toString()[0:2]
       
        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/colorrampmanager_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # check for updates in background - every 7 days, optional
        ret = self.checkUpdateAuto()

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/colorrampmanager/icon.png"), \
            u"Color Ramp Manager", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        QObject.connect(self.dlg.pbtnUpdateCheck, SIGNAL('clicked()'), self.on_pbtnUpdateCheck_clicked)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Color Ramp Manager", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Color Ramp Manager",self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.updateUI()
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            self.dlg.apply()

    def getInstallDir(self):
        #return a python string
        installDir = str(self.dlg.installDir)
        if self.dlg.rbtnDirCustom.isChecked():
            installDir = str(self.dlg.leDirCustom.text())
        if installDir is None or installDir=='':
            s = QSettings()
            installDir = str(s.value('CptCity/baseDir', \
                                         QgsApplication.pkgDataPath() + "/resources" ).toString())
        return installDir
    
    def getPackageType(self):
        #return a python string
        packageType = str(self.dlg.packageType)
        if packageType is None or packageType=='':
            s = QSettings()
            packageType = s.value('CptCity/archiveName', 'cpt-city-qgis-sel').toString()
        return packageType
    
    def checkUpdateAuto(self):
        #default check on start if last check was 7+ days ago
        s = QSettings()
        daysCheck = s.value('CptCity/updateCheckAuto',0).toInt()[0]
        if daysCheck <= 0:
            return
        prevCheckStr = str(s.value('CptCity/updateChecked', '').toString())
        check = False
        if prevCheckStr == '':
            check = True
        else:
            prevCheckDate = date( int(prevCheckStr[0:4]), int(prevCheckStr[5:7]), \
                                      int(prevCheckStr[8:10]) )
            todayDate = date.today()
            diff = abs(todayDate - prevCheckDate).days
            if diff >= daysCheck:
                check = True
        if check:
            message = self.checkUpdate('',False,'')
            return message
        return ''
                
    def on_pbtnUpdateCheck_clicked(self):
        self.checkUpdate('',True,self.dlg.windowTitle())

    # returns '' if no update available, else returns a descriptive string
    def checkUpdate(self,installDir='',gui=False,title=''):
        if installDir is None or installDir=='':
            installDir = self.getInstallDir()

        #message = self.checkPermissions(installDir,gui,title)
        #if message != '':
        #    return message

        # if we have an available update, no need to check
        s = QSettings()
        if str(s.value('CptCity/updateAvailable', '').toString()) != '':
            (ret,version) = (True,str(s.value('CptCity/updateAvailable', '').toString()))
        else:
            # set override cursor
            if gui:
                QApplication.setOverrideCursor( Qt.WaitCursor )      
            # fetch new version
            packageType = self.getPackageType()
            (ret,version) = cpt_city_update( installDir, False, packageType )
            if gui:
                QApplication.restoreOverrideCursor()
            s = QSettings()
            # update settings
            s.setValue('CptCity/updateChecked', QString(date.today().isoformat()))
            if ret:
                s.setValue('CptCity/updateAvailable', str(version))
            
                
        # we have an update, act on it
        if ret:
            #TODO print new version info and/or log, when not running from gui
            if gui:
                result = QMessageBox.information(None, title, \
                                                     self.tr('Version (%1) is available, download and install?').arg( version ), \
                                                     QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.No:
                    return ''
                else:
                    return self.installUpdate(installDir,gui,title)
            else:
                return self.tr('New cpt-city version (%1) is available').arg( version )
        elif version != 0:
            if gui:
                QMessageBox.information(None, title, self.tr('Up to date (version %1)').arg(version), QMessageBox.Close)
                self.dlg.pbtnUpdateCheck.setEnabled( False )
            else:
                return ''
        else:
            message = self.tr('Error checking update')
            if gui:
                QMessageBox.warning(None, self.dlg.windowTitle(), message, QMessageBox.Close)
            return message

        return ''

    # returns a descriptive string
    def installUpdate(self,installDir='',gui=False,title=''):
        if installDir is None or installDir=='':
            installDir = self.getInstallDir()
        message = self.checkPermissions(installDir,gui,title)
        if message != '':
            return message
        if gui:
            QApplication.setOverrideCursor( Qt.WaitCursor )
        s = QSettings()
        packageType = self.getPackageType()
        (ret,version) = cpt_city_update( installDir, True, packageType )
        if gui:
            QApplication.restoreOverrideCursor()
        if ret:       
            s = QSettings()
            s.setValue('CptCity/updateChecked', QString(date.today().isoformat()))
            s.setValue('CptCity/updateAvailable', QString(''))
            message = self.tr('Version %1 installed').arg(version)
            if gui:
                QMessageBox.information(None, self.dlg.windowTitle(), message, QMessageBox.Close)
                self.dlg.pbtnUpdateCheck.setEnabled( False )
            return message
        else:
            message = self.tr('Error downloading or installing update, check console')
            if gui:
                QMessageBox.warning(None, self.dlg.windowTitle(), message, QMessageBox.Close)
            return message
            
    # returns ''if permissions ok, else returns a descriptive string
    def checkPermissions(self,installDir,gui=False,title=''):
        if installDir is None or installDir=='':
            message = self.tr('Please select a directory')
            if gui:
                QMessageBox.warning(None, title, message, QMessageBox.Close)
            return message
        if not os.access(installDir, os.W_OK):
            message = self.tr('Cannot write to directory %1').arg(installDir)
            if gui:
                QMessageBox.warning(None, title, message, QMessageBox.Close)
            return message
        return ''


                     
