#! /usr/bin/python
#
''' 
to make a file with free-to-use selections:
./cpt_city_mkdist.py cpt-city cpt-city-qgis-sel 2.02.1 selections.txt 
./cpt_city_mkdist.py cpt-city cpt-city-qgis-min 2.02.1 selections-min.txt 

to make a file with free-to-use files from entire dataset:
./cpt_city_mkdist.py cpt-city cpt-city-qgis-full 2.02.1
'''

import sys, os, errno, urllib, warnings, zipfile, shutil, string, time, subprocess
import xml.etree.ElementTree as xml

if len(sys.argv) != 4 and len(sys.argv) != 5:
    print('usage: cpt_city_mkdist idir odir version <sel_file>')
    sys.exit(1)

idir = sys.argv[1]
odir = sys.argv[2]
version = sys.argv[3]
if len(sys.argv) == 5:
    sel_file = sys.argv[4]
else:
    sel_file = None
ofile = ( '%s-%s.zip' % (odir,version) )

if not os.path.exists(idir):
    print('idir ' + idir + ' does not exist')
    sys.exit(1)
if os.path.exists(odir):
    shutil.rmtree(odir)
os.makedirs(odir)
if not os.path.exists(odir):
    print('odir ' + odir + ' does not exist')
    sys.exit(1)
if sel_file is not None and not os.path.exists(sel_file):
    print('sel_file ' + sel_file + ' does not exist')
    sys.exit(1)

verbose = False
verbose2 = False

#for now use sel_file (each line with a dir/ or a file (without .svg) ) but use xml data when available
sel_files = []
sel_dirs = []
dist_dirs = []

if sel_file is not None:
    print('\ndetermining selection')
    try:
        f = open(sel_file, 'r')
    except IOError:
        print "File " + filename + " cannot be read."
        sys.exit(1)

    for sel_line in f:
        entry = string.strip(sel_line)
        if entry != '' and entry[0] != "#":
            #print(entry)
            if entry[-1] == '/':
                sel_dirs.append(entry)
            else:
                sel_files.append(entry)
    f.close()

print('\ndetermining dirs that we can distribute')
os.chdir(idir)
for root, dirs, files in os.walk('.'): 
    license_file = os.path.join(root,'COPYING.xml')
    if not os.path.exists(license_file):
        continue
    tree = xml.ElementTree()
    tree.parse(license_file)
    if tree is None:
        print("Failed to parse "+license_file)
        continue
    node = tree.find('distribute/qgis')
    if node is None or not node.attrib.has_key('distribute'):
        print("Did not find distribute/qgis tag in "+license_file)
        continue
    distrib_flag=node.attrib['distribute']
    if(verbose):
        print(root+' - '+distrib_flag)
    if distrib_flag == 'yes':
        dist_dirs.append(root[2:]) # remove ./
    # if you want non-commercial (cc3) gradients, uncomment this
#    if distrib_flag == 'noncomm' :
#        dist_dirs.append(dirname)

os.chdir('..')

if sel_file is not None:
    print('\nsel_dirs:\n' + str(sel_dirs))
    print('\nsel_files:\n' + str(sel_files))
print('\ndist_dirs:\n' + str(dist_dirs))


# copy any files in root directory
print('\n\ncopying files in root directory')
for filename in os.listdir(idir):
    if not os.path.isdir(os.path.join(idir,filename)): 
        shutil.copy( os.path.join(idir,filename), os.path.join(odir,filename))
f = open(os.path.join(odir,'README-qgis.txt'), 'w') 
f.write('This package contains a selection of the cpt-city gradients for use by the QGIS application.\n\n')
f.write('The gradients files chosen allow for redistribution and free use, \n')
f.write('subject to individual license information found in the COPYING.xml files.\n\n')
f.close()
shutil.copy( os.path.join(idir,"VERSION.xml"),os.path.join(idir,"VERSION-parent.xml"))

# write modifified VERSION.xml

# parse xml and get info
tree = xml.ElementTree('archive')
tree.parse(idir+'/'+'VERSION.xml')
root = tree.getroot()
if tree is None:
    print("Failed to parse "+idir+'/'+'VERSION.xml')
if verbose:
    print(str(xml.dump(tree)))
node = tree.find('version')
if node is not None:
    parent_version = node.text
else:
    parent_version = 'unknown'
node = tree.find('variant')
if node is not None:
    parent_variant = node.text
else:
    parent_variant = 'unknown'

# copy node values to new tree, replacing where necessary
version_props = dict()
version_props['version'] = version
version_props['variant'] = odir #'qgis-sel'
version_props['creator'] = 'Etienne Tourigny'
version_props['created'] = time.ctime()
root2 = xml.Element('archive')
root2.append(xml.Comment('version information for cpt-city packages'))

for node in list(root):
    if node.tag == 'parent':
        node = xml.Element('parent')
        subnode = xml.SubElement(node,'version')
        subnode.text = parent_version
        subnode = xml.SubElement(node,'variant')
        subnode.text = parent_variant
    elif node.tag in version_props.keys():
        node.text = version_props[node.tag]
    root2.append(node)
    
# save file and process through xmllint because result is not tidy
tree2 = xml.ElementTree(root2)
if verbose:
    xml.dump(tree2)
#tree2.write(odir+'/'+'VERSION.xml',encoding='UTF-8',xml_declaration=True)
tree2.write('tmp.xml',encoding='UTF-8',xml_declaration=True)
subprocess.call(['xmllint', '-o', os.path.join(odir,'VERSION.xml'), '--format', 'tmp.xml'])
os.remove('tmp.xml')

# copy over directories which are in selection
if sel_file is not None:
    print('copying directories in selection')
for sel_dir in sel_dirs:
    sel_dir = sel_dir[:-1]
    if verbose2:
        print(sel_dir)
    for dist_dir in dist_dirs:
        #print(sel_dir+' - '+dist_dir)
        if sel_dir == dist_dir or \
                ( sel_dir[:len(dist_dir)] == dist_dir and sel_dir[len(dist_dir)] == '/' ) :
            if verbose2:
                print('match / '+sel_dir[:len(dist_dir)])
            if verbose:
                print(sel_dir)
            shutil.copytree(idir+'/'+sel_dir,odir+'/'+sel_dir)
            break

# function to copy filename from idir/tmpdir to odir/tmpdir, recursively upward
def copyrec(filename,tmpdir):
    #print('copyrec '+filename+' '+tmpdir)
    if os.path.exists( idir+'/'+tmpdir+'/'+filename ) \
            and not os.path.exists( odir+'/'+tmpdir+'/'+filename ):
        if not os.path.exists( odir+'/'+tmpdir ):
            os.makedirs(odir+'/'+tmpdir)
        shutil.copy( idir+'/'+tmpdir+'/'+filename, odir+'/'+tmpdir+'/'+filename )
    if tmpdir == '':
        return
    part = tmpdir.rpartition('/')
    #print(str(part[0]))
    copyrec(filename,part[0])

# copy over files (and associated .xml files) which are in selection
if sel_file is not None:
    print('copying files in selection')
for sel_file in sel_files:
    sel_file = sel_file+'.svg'
    if not os.path.exists(idir+'/'+sel_file):
        continue
    if verbose2:
        print(sel_file)
    for dist_dir in dist_dirs:
        #print(sel_file+' - '+dist_dir)
        if sel_file[:len(dist_dir)] == dist_dir and sel_file[len(dist_dir)] == '/':
            if verbose2:
                print('match / '+sel_file[:len(dist_dir)])
            # first mkdir if not existent
            sel_odir = os.path.split(odir+'/'+sel_file)[0]
            if not os.path.exists(sel_odir):
                os.makedirs(sel_odir)
            # then copy over svg file
            if verbose:
                print(sel_file)
            shutil.copy(idir+'/'+sel_file, odir+'/'+sel_file)
            # finally copy over all xml files in previous dirs
            copyrec('DESC.xml', sel_file)
            copyrec('COPYING.xml', sel_file)
            break

if sel_file is None:
    print('copying directories')
    for dist_dir in dist_dirs:
        shutil.copytree(idir+'/'+dist_dir,odir+'/'+dist_dir)

# copy "selections" directory - these must be copied from cpt-city directory in qgis directory (downloaded by update script)
shutil.copytree(idir+'/selections',odir+'/selections')

# fix permissions: dirs are 755, files are 644
for root, dirs, files in os.walk(odir):
    os.chmod(root,0755)
    for f in files:
        os.chmod(os.path.join(root,f),0644)

# create zip file
print('creating zipfile')
zf = zipfile.ZipFile(ofile, 'w', zipfile.ZIP_DEFLATED)
for root, dirs, files in os.walk(odir):
    for f in files:
        zf.write(os.path.join(root,f))
zf.close()

# remove output directory ?

print('\nfiles copied to folder %s and zipfile %s' % (odir,ofile))
