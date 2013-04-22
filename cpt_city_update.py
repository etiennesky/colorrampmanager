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

import sys, os, errno, urllib2, warnings, zipfile, shutil
import xml.etree.ElementTree as et
from optparse import OptionParser

################################################################
def cpt_city_update( datadir = None, install = True, package = 'cpt-city' ):

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
    cachedir = "%s/cache/cpt-city" % (qgisSettingsDir)
    if datadir is None:
        datadir = "%s/" % (qgisSettingsDir)
    verfile = "%s/%s/VERSION.xml" % (datadir,package)

    # this will need to be changed if/when the cpt-city site moves
    if package == 'cpt-city':
        starturl = "http://soliton.vm.bytemark.co.uk/pub/cpt-city/pkg"
        pkgfile   = "package.xml"
        selectionfile = "../views/index-static.xml"
    elif package == 'cpt-city-qgis-sel':
        #TODO change this before release!
        starturl = "https://raw.github.com/etiennesky/colorrampmanager/master/pub/cpt-city/pkg"
        pkgfile   = "package-qgis-sel.xml"
        selectionfile = "../views/index-static.xml"
    else:
        print('illegal value '+cpt-city+' for package argument')
        return

    # if this file is integrated into another package
    # called "foo" then please change the UA string to 
    # "cpt-city-update/foo"
    useragent = "cpt-city-update/qgis"

    # handle verbose
    def info(args) :
        if verbose :
            print args

    # say hello
    info("This is cpt-city-update")
    info('cachedir: '+cachedir+' datadir: '+datadir+' verfile: '+verfile)
    info('starturl: '+starturl+' pkgfile: '+pkgfile)

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
    # specified user agent string
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', useragent)]

    # opens a url and returns connection, or None if an error occured
    def openurl(url):
        info('fetching %s' % url)
        try:
            con = opener.open(url)
        except urllib2.URLError, e:
            print('error retrieving %s : %d' % (xmlurl,e.code))
            return None
        return con

    # copies url to local path, returns False on error
    def retrieveurl(url,path):
        info('fetching %s to %s' % (url,path))
        # get url
        try:
            con = opener.open(url)
        except urllib2.URLError, e:
            print('error retrieving %s : %d' % (url,e.code))
            #print e.read()
            return False
    
        #copy to file
        try:
            output = open(path,'wb')
        except IOError as e:
            print('error creating file %s : %s' % (path,e.strerror))
            return False
        output.write(con.read())
        output.close()
    
        return True

    # try to open the package file
    xmlurl = "%s/%s" % (starturl,pkgfile)
    con = openurl(xmlurl)
    if con is None:
        return (False,0)

    # get DOM from package file
    dom = et.parse(con).getroot()
    if dom is None:
        print("Failed to parse package file")
        return (False,0)        

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
    # we take care to treat the version numbers as major.minor<.release>
    # and not floats (version 1.02 is higher than version 1.1)
            
    vernew = dom.attrib['version']
    info('vernew: '+str(vernew))

    def verparts(verstring) :
        parts = tuple(map(int,verstring.rsplit('.')))
        assert len(parts) == 2, "Bad version string"
        return parts

    # compare vernew and verold, if install=False then just notify new version
    def vernewer(a,b) :
        #return (a[0] > b[0]) or ((a[0] == b[0]) and (a[1] > b[1]))
        if a[0] > b[0]:
            return True
        if len(a) == 2:
            return ((a[0] >= b[0]) and (a[1] > b[1]))
        if len(a) == 3:
            return ((a[0] >= b[0]) and ( (a[1] > b[1]) or ( (a[1] >= b[1]) and (a[2] > b[2])) ) )
        return False
        
    if os.path.exists(verfile) :
        tree = et.ElementTree('archive')
        tree.parse(verfile)
        if tree is None:
            print("Failed to parse %s" % (verfile))
            return (False,0)
        node = tree.find('version')
        if node is None:
            print("Did not find version in %s" % (verfile))
            return (False,0)
        verold = node.text
        info("verold: %s" % (verold))
        # if vernew has 3 parts, make sure verold also
        parts_new = tuple(map(int,vernew.rsplit('.')))
        parts_old = tuple(map(int,verold.rsplit('.')))
        if len(parts_new) == 3 and len(parts_old) == 2:
            #verold_tmp = ( '%s.0' % verold )
            parts_old = parts_old + (0,)
        #else:
        #    verold_tmp = verold
        #if vernewer(vernew,verold_tmp) :
        if vernewer(parts_new,parts_old) :
            info("newer version available (%s > %s)" % (vernew,verold))
            if not install:
                info("not installing as per user request")
                return (True,vernew)                                   
        else:
            info("up to date (version %s) in %s" % (verold,datadir))
            return (False,verold)                     
    else :
        info("initial version (%s)" % (vernew))           
            
    if not install:
        info("not installing as per user request")
        return (True,vernew)                        

    # get the files (if we don't have them already)

    for gradtype in gradtypes :

        gradfile = dom.find(gradtype).text
        gradurl  = "%s/%s" % (starturl,gradfile)
        #gradpath = "%s/%s" % (datadir,gradfile) 
        gradpath = "%s/%s" % (cachedir,gradfile) 
        
        if os.path.exists(gradpath) :
            info("found %s" % (gradfile))
        else:
            if not retrieveurl(gradurl,gradpath):
                return (False,vernew)

        # verify that the zipfile does not write any files
        # outside the directory into which is was unzipped
        #
        # This is a generic security issue with zipfiles,
        # they may contain files like /etc/passwd and if
        # unzipped with sufficient privileges destroy the 
        # OS, replace /bin/sh by a rooted version, ...
            
        try:
            zf = zipfile.ZipFile(gradpath,"r")
        except zipfile.BadZipfile:
            print('invalid zipfile %s' %(gradpath))
            os.remove(gradpath)
            return (False,0)
            
        prefix = os.getcwd()
        lprefix = len(prefix)

        for path in zf.namelist() :
            abspath = os.path.abspath(path)
            assert abspath[:lprefix] == prefix, "suspect file %s" % (path)

        # cleanup path
        if os.path.exists(datadir+'/'+package):
            print('removing '+datadir+'/'+package)
            shutil.rmtree(datadir+'/'+package)
        
        # unpack the files
        info("unzipping %s to directory %s" % (gradfile,datadir))
        umask_old = os.umask( 0022 ) #set umask so files can be read by others
        zf.extractall(datadir)
        os.umask( umask_old )

        # fix permissions: dirs are 755, files are 644
        for root, dirs, files in os.walk(datadir):
            os.chmod(root,0755)
            for f in files:
                os.chmod(os.path.join(root,f),0644)


    # get selection files

    seldir =  "%s/%s/selections" % (datadir,package)
    if not os.path.exists(seldir):
        os.makedirs(seldir)

    xmlurl = "%s/%s" % (starturl,selectionfile)

    # try to open the package file
    con = openurl(xmlurl)
    if con is None:
        return (False,0)

    # get DOM from package file
    dom = et.parse(con).getroot()
    if dom is None:
        print("Failed to parse package file")
        return (False,0)    

    # get selection files
    for sel in dom.findall("selection"):
        selfileurl = "%s/../views/%s.xml" % (starturl,sel.text)
        selfile = "%s/%s.xml" % (seldir,sel.text)
        if not retrieveurl(selfileurl,selfile):
            return (False,vernew)

    # get popular selections
    popfiles = [ "totp-svg", "totp-cpt" ]
    for sel in popfiles:
        selfileurl = "%s/../views/%s.xml" % (starturl,sel)
        selfile = "%s/%s.xml" % (seldir,sel)
        if not retrieveurl(selfileurl,selfile):
            return (False,vernew)
    

    # done - say goodbye

    info("done.")

    return (True,vernew)                     

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


