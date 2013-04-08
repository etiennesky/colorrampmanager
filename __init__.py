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
 This script initializes the plugin, making it known to QGIS.
"""
def name():
    return "Color Ramp Manager"
def description():
    return "plugin to manage and download color ramp definitions"
def version():
    return "Version 0.2.1"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.9"
def classFactory(iface):
    # load ColorRampManager class from file ColorRampManager
    from colorrampmanager import ColorRampManager
    return ColorRampManager(iface)
