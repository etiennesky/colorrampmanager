#! /usr/bin/python

"""
cpt-city-update
 
a python script to update your copy of the cpt-city package

Copyright (C) 2012 J.J. Green
Copyright (C) 2012 Etienne Tourigny - modifications for QGis

Changelog:

* 2012/08/04 Initial version by J.J. Green
* 2012/08/05 Etienne Tourigny - modifications for QGis :
             * implement as a function and add datadir, install arguments
             * modification for running inside a qgis plugin (recommended) and as standalone
             * add version info to datadir/cpt-city/cpt-city-version) - would be nice to have inside the zip files
             * save .zip file and install_dir in $HOME/.qgis/cache/cpt-city-update/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import sys, os, errno, urllib, warnings, zipfile;
import xml.etree.ElementTree as et
from optparse import OptionParser

#import qgis.core
#from qgis.core import *
#import qgis.utils

################################################################
def cpt_city_update( datadir = None, install = True ):

    # you may want to configure these

    gradtypes = ['svg']
    verbose = True
    # when running standalone, it seems that qgisSettingsDirPath() returns empty...
    #qgisSettingsDir = QgsApplication.qgisSettingsDirPath()
    try:
        qgisSettingsDir = QgsApplication.qgisSettingsDirPath()
    except NameError:
        qgisSettingsDir = None
    if qgisSettingsDir is None or qgisSettingsDir == '':
        qgisSettingsDir = "%s/.qgis" % (os.environ['HOME'])
    cachedir = "%s/cache/cpt-city-update" % (qgisSettingsDir)
    if datadir is None:
        datadir = "%s/" % (qgisSettingsDir)
    verfile   = "%s/cpt-city/cpt-city.version" % (datadir)

    # this will need to be changed if/when the cpt-city site moves
    starturl = "http://soliton.vm.bytemark.co.uk/pub/cpt-city/pkg"

    # if this file is integrated into another package
    # called "foo" then please change the UA string to 
    # "cpt-city-update/foo"

    useragent = "cpt-city-update/qgis"

    # these you probably leave alone

    pkgfile   = "package.xml"

    # handle verbose

    def info(args) :
        if verbose :
            print args

    # say hello

    info("This is cpt-city-update")
    info('cachedir: '+cachedir+' datadir: '+datadir+' verfile: '+verfile)

    # ensure configuration/data dirs exist

    def ensure_directory(path) :
        try:
            os.makedirs(path)
        except OSError, e:
            if os.path.isdir(path):
                pass
            else:
                raise

    ensure_directory(cachedir)
    ensure_directory(datadir)

    # create customised urllib opener class with the
    # specfified user agent string

    class Opener(urllib.FancyURLopener, object):
        version = useragent

    opener = Opener()

    # try to open the package file

    con = opener.open("%s/%s" % (starturl,pkgfile))
    assert con is not None, "Failed to connect to server"

    # get DOM from package file

    dom = et.parse(con).getroot()
    assert dom is not None, "Failed to parse package file"

    # check whether the url in the package file is the
    # same as the starturl, if now warn that an update
    # is needed
    
    if starturl != dom.attrib['url'] :
        print "-------------------------------------------------------"
        print "The cpt-city package file lists a new url as the" 
        print "package location -- this usually means the the cpt-city"
        print "site is moving, and you will need to update this script"
        print "-------------------------------------------------------"

    # get version from dom, compare it with current version
    # we take care to treat the version numbers as major.minor
    # and not floats (version 1.02 is higher than version 1.1)
            
    vernew = dom.attrib['version']

    def verparts(verstring) :
        parts = tuple(map(int,verstring.rsplit('.')))
        assert len(parts) == 2, "Bad version string"
        return parts

    # compare vernew and verold, if install=False then just notify new version

    def vernewer(a,b) :
        return (a[0] > b[0]) or ((a[0] == b[0]) and (a[1] > b[1]))
        
    if os.path.exists(verfile) :
        fd = open(verfile,'r')
        verold = fd.readline().strip()
        if vernewer(vernew,verold) :
            info("newer version available (%s > %s)" % (vernew,verold))
            if not install:
                info("not installing as per user request")
                return(True)                                   
        else:
            info("up to date (version %s) in %s" % (verold,datadir))
            return(False,verold)                     
    else :
        info("initial version (%s)" % (vernew))           
            
    if not install:
        info("not installing as per user request")
        return(True,vernew)                        

    # get the files (if we dont have them already)

    for gradtype in gradtypes :

        gradfile = dom.find(gradtype).text
        gradurl  = "%s/%s" % (starturl,gradfile)
        #gradpath = "%s/%s" % (datadir,gradfile) 
        gradpath = "%s/%s" % (cachedir,gradfile) 
        
        if os.path.exists(gradpath) :
            info("found %s" % (gradfile))
        else:
            info("fetching %s" % (gradfile))
            opener = Opener()
            opener.retrieve(gradurl,gradpath)

        # verify that the zipfile does not write any files
        # outside the directory into which is was unzipped
        #
        # This is a generic security issue with zipfiles,
        # they may contain files like /etc/passwd and if
        # unzipped with sufficient privileges destroy the 
        # OS, replace /bin/sh by a rooted version, ...
            
        zf = zipfile.ZipFile(gradpath,"r")

        prefix = os.getcwd()
        lprefix = len(prefix)

        for path in zf.namelist() :
            abspath = os.path.abspath(path)
            assert abspath[:lprefix] == prefix, "suspect file %s" % (path)

        # unpack the files
        info("unzipping %s to directory %s" % (gradfile,datadir))
        zf.extractall(datadir)

    # done

    # save the new version number

    fd = open(verfile,'w')
    fd.write("%s\n" % (vernew))
    fd.close()

    # say goodbye

    info("done.")
    return(True,vernew)                     

# end function cpt_city_update()
################################################################


################################################################
def Usage():
    print('Usage: cpt-city-update.py <install_dir> <check_only>')
    print('')
    sys.exit( 1 )

def main():

    datadir = None
    install = True
    if len(sys.argv) == 2 and sys.argv[1] == '-h':
        Usage()
    if len(sys.argv) >= 2:
        datadir = sys.argv[1]
    elif len(sys.argv) == 3 and sys.argv[2] != '0':
        install = False
    elif len(sys.argv) > 3:
        Usage()

    # when running standalone, it seems that qgisSettingsDirPath() returns empty, so don't register any qgis stuff...
    #QgsApplication.setPrefixPath("/home/softdev/", True)
    ## load providers
    #QgsApplication.initQgis()

    cpt_city_update(datadir,install)

    #QgsApplication.exitQgis()

if __name__ == "__main__":
    main()


