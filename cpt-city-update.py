#! /usr/bin/python

# cpt-city-update
# 
# a python script to update your copy of the 
# cpt-city package
# 
# J.J. Green 2012
# $Id: cpt-city-update.py,v 1.3 2012/08/03 19:22:28 jjg Exp $

import os, errno, urllib, warnings, zipfile;
import xml.etree.ElementTree as et

# you may want to configure these

gradtypes = ['svg']
configdir = "%s/.cpt-city-update" % (os.environ['HOME'])
datadir   = "%s/share" % (os.environ['HOME'])
verbose   = True

# this will need to be changed if/when the cpt-city
# site moves

starturl = "http://soliton.vm.bytemark.co.uk/pub/cpt-city/pkg"

# if this file is integrated into another package
# called "foo" then please change the UA string to 
# "cpt-city-update/foo"

useragent = "cpt-city-update/testing"

# these you probably leave alone

verfile   = "%s/cpt-city.version" % (configdir)
pkgfile   = "package.xml"

# handle verbose

def info(args) :
    if verbose :
        print args

# say hello

info("This is cpt-city-update")

# ensure configuration/data dirs exist

def ensure_directory(path) :
    try:
        os.makedirs(path)
    except OSError, e:
        if os.path.isdir(path):
            pass
        else:
            raise

ensure_directory(configdir)
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

def vernewer(a,b) :
    return (a[0] > b[0]) or ((a[0] == b[0]) and (a[1] > b[1]))

if os.path.exists(verfile) :
    fd = open(verfile,'r')
    verold = fd.readline().strip()
    if vernewer(vernew,verold) :
        info("newer version available (%s > %s), updating" % (vernew,verold))
    else:
        info("up to date (version %s)" % (verold))
        exit(0)                     
else :
    info("initial version (%s)" % (vernew))

# get the files (if we dont have them already)

for gradtype in gradtypes :

    gradfile = dom.find(gradtype).text
    gradurl  = "%s/%s" % (starturl,gradfile)
    gradpath = "%s/%s" % (datadir,gradfile) 

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

    zf.extractall(datadir)

    # done

# save the new version number

fd = open(verfile,'w')
fd.write("%s\n" % (vernew))
fd.close()

# say goodbye

info("done.")
