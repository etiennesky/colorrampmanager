#! /usr/bin/python

import sys, os, errno, urllib, warnings
import csv, shutil, string
from xml.etree.ElementTree import ElementTree

if len(sys.argv) != 5:
    print('usage: cpt_city_mkdist idir odir csv_file sel_file')
    sys.exit(1)

idir = sys.argv[1]
odir = sys.argv[2]
csv_file = sys.argv[3]
sel_file = sys.argv[4]

if not os.path.exists(idir):
    print('idir ' + idir + ' does not exist')
    sys.exit(1)
if not os.path.exists(odir):
    os.makedirs(odir)
if not os.path.exists(odir):
    print('odir ' + odir + ' does not exist')
    sys.exit(1)
if not os.path.exists(csv_file):
    print('csv_file ' + csv_file + ' does not exist')
    sys.exit(1)
if not os.path.exists(sel_file):
    print('sel_file ' + sel_file + ' does not exist')
    sys.exit(1)

#for now use sel_file (each line with a dir/ or a file (without .svg) ) but use xml data  when available
sel_files = []
sel_dirs = []
dist_dirs = []

try:
    f = open(sel_file, 'r')
except IOError:
    print "File " + filename + " cannot be read."
    sys.exit(1)

for sel_line in f:
    entry = string.strip(sel_line)
    if entry != '':
        #print(entry)
        if entry[-1] == '/':
            sel_dirs.append(entry)
        else:
            sel_files.append(entry)
f.close()


#for now use csv file (generated from cpt_city_license.py), but use xml data in COPYING.xml when available
# csv file structure is
# fulldirname ; distrib_flag ; license_flag ; license_details
csv_reader = csv.DictReader(open(csv_file), delimiter=';', quotechar='\"')

for row in csv_reader:
    dirname = string.strip(row['fulldirname'])
    distrib_flag = string.strip(row['distrib_flag'])

    if distrib_flag == 'yes':
        dist_dirs.append(dirname)
    #if you want non-commercial (cc3) gradients, uncomment this
    if distrib_flag == 'noncomm' :
        dist_dirs.append(dirname)

print('\nsel_dirs:\n' + str(sel_dirs))
print('\nsel_files:\n' + str(sel_files))
print('\ndist_dirs:\n' + str(dist_dirs))


# copy over directories which are in selection
for sel_dir in sel_dirs:
    sel_dir = sel_dir[:-1]
    for dist_dir in dist_dirs:
        #print(sel_dir+' - '+dist_dir)
        if sel_dir[:len(dist_dir)] == dist_dir:
            print('match / '+sel_dir[:len(dist_dir)])
            shutil.copytree(idir+'/'+sel_dir,odir+'/'+sel_dir)
            break

# function to copy filename from idir/tmpdir to odir/tmpdir, recursively upward
def copyrec(filename,tmpdir):
    print('copyrec '+filename+' '+tmpdir)
    if os.path.exists( idir+'/'+tmpdir+'/'+filename ) \
            and not os.path.exists( odir+'/'+tmpdir+'/'+filename ):
        if not os.path.exists( odir+'/'+tmpdir ):
            os.makedirs(odir+'/'+tmpdir)
        shutil.copy( idir+'/'+tmpdir+'/'+filename, odir+'/'+tmpdir+'/'+filename )
    if tmpdir == '':
        return
    part = tmpdir.rpartition('/')
    print(str(part[0]))
    copyrec(filename,part[0])

# copy over files (and associated .xml files) which are in selection
for sel_file in sel_files:
    sel_file = sel_file+'.svg'
    if not os.path.exists(idir+'/'+sel_file):
        continue
    for dist_dir in dist_dirs:
        #print(sel_file+' - '+dist_dir)
        if sel_file[:len(dist_dir)] == dist_dir:
            print('match / '+sel_file[:len(dist_dir)])
            # first mkdir if not existent
            sel_odir = os.path.split(odir+'/'+sel_file)[0]
            if not os.path.exists(sel_odir):
                os.makedirs(sel_odir)
            # then copy over svg file
            shutil.copy(idir+'/'+sel_file, odir+'/'+sel_file)
            # finally copy over all xml files in previous dirs
            copyrec('DESC.xml', sel_file)
            copyrec('COPYING.xml', sel_file)
            break


