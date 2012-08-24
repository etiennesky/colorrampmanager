#! /usr/bin/python
# run this script from a cpt-city directory

# look for files with license that allows for redistribution
# GPL, Apache, public domain 
# look in <informal tag>
#  <license>
#    <informal>Apache-style</informal>
#  </license>
# or
#   <license>
#    <informal>GPLv2</informal>
#    <year>2006</year>
#    <text href="http://www.gnu.org/licenses/gpl-2.0.html"/>
#  </license>

import sys, os, errno, urllib, warnings
from xml.etree.ElementTree import ElementTree

# definitions
# gpl,gplv2,apache,ccnc,cc3,otherok,freeuse,other,none
license_dict=dict()
license_dict['gpl']=[]     #GPL
license_dict['gplv2']=[]   #GPLv2
license_dict['apache']=[]  #Apache-like | Apache-style
license_dict['ccnc']=[]    #Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported
                           #Creative Commons Attribution-NonCommercial 2.5 Generic
license_dict['cc3']=[]     #Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
                           #Creative commons attribution share-alike 3.0 unported
license_dict['otherok']=[] #Public domain | BSD-like | MIT ( should parse for "Public domain" or "Public Domain" ? )
license_dict['freeuse']=[] #Free to use
license_dict['other']=[]  #need to verify
license_dict['none']=[]    #none

distribute_dict=dict()
distribute_dict['yes']=[]
distribute_dict['no']=[]
distribute_dict['unsure']=[]
distribute_dict['noncomm']=[]

licenses_dist_yes=[ 'gpl', 'gplv2', 'apache', 'cc3', 'otherok' ]
licenses_dist_no=[ 'freeuse', 'none' ]
licenses_dist_unsure=[ 'other' ]
licenses_dist_noncomm=[ 'ccnc' ]
licenses_dist_force_yes=[ 'jm', 'fg', 'rf', 'wkp/ice', 'dg', 'es', 'gery', 'ncl', 'os', 'ukmo', 'wkp/encyclopedia', 'go2/button', 'go2/ipod', 'go2/webtwo', 'ds', 'esdb' ]
licenses_dist_force_no=[ 'njgs', 'esri' ]

"""
Distribution:

Exceptions (allowed):
jm       Attribution required
rf       Credit requested
wkp/ice  Attribution and share-alike required
dg       Contributed to the public domain, citation requested.
fg       Credit requested [link broken]
es       Credit requested for use, required for distribution
gery     Contributed to the Public Domain by the author.
ncl      Custom open-source
os       UK Open Government Licence
ukmo     UK Open Government Licence
wkp/encyclopedia Public domain due to age
go2/*    Attribution requested
ds       Link requested
esdb     Free to use for any purpose

Exceptions (not allowed):
esri     export restrictions

not sure
ds, esdb, 'esri', 
xkcd     ccnc

need to add to doc/UI:
- ColorBrewer acknowledgment
"""


count = 0
count_miss = 0
count_err = 0
dirs_miss=[]

print('')
print('fulldirname;distrib_flag;license_flag;license_details')

#cpt_city_basedir = "%s/.qgis/cpt-city" % (os.environ['HOME'])
#os.chdir(cpt_city_basedir)
for dirname, dirnames, filenames in os.walk('.'):

    dirnames.sort()
    filenames.sort()

    for subdirname in dirnames:

        fulldirname = os.path.join(dirname, subdirname)[2:] 
        license_file = os.path.join(fulldirname, 'COPYING.xml')
        
        if not os.path.exists(license_file):
            #print('ERROR: file %s does not exist' % (license_file))
            for filename in filenames:
                #print os.path.join(fulldirname, filename)
                ext = os.path.splitext(filename)[1]
                if ext == '.svg':
                    count_err = count_err + 1
                    print('ERROR: svg file %s in directory without COPYING.xml file' % (os.path.join(fulldirname, filename)))
            count_miss = count_miss + 1
            dirs_miss.append( fulldirname )
            continue

        count = count + 1

        tree = ElementTree()
        tree.parse(license_file)
        if tree is None:
            print("Failed to parse "+license_file)
        
        node = tree.find('license/informal')
        if node is not None:
            license_name = node.text
            if license_name is not None:
                license_name = license_name.strip().replace("\r"," ").replace("\n"," ")
        else:
            license_name = ''

        # decide which license class this one belongs to
        # based on license_name
        license_tmp = ''
        if license_name == '' or license_name == 'Not specified':
            license_tmp = 'none'
        elif license_name == 'GPL':
            license_tmp = 'gpl'
        elif license_name == 'GPLv2':
            license_tmp = 'gplv2'
        elif license_name == 'Apache-like' or license_name == 'Apache-style':
            license_tmp = 'apache'
        elif license_name == "Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported" \
               or license_name == "Creative Commons Attribution-NonCommercial 2.5 Generic":
            license_tmp = 'ccnc'
        elif license_name == "Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)" \
                or license_name == "Creative commons attribution share-alike 3.0 unported":
            license_tmp = 'cc3'
        elif license_name == "Public domain" or license_name == "BSD-like" or license_name == "MIT":
            license_tmp = 'otherok'
        # unsure
        elif license_name == "Free to use":
            license_tmp = 'freeuse'
        elif license_name == "Credit requested" or  license_name == "Free to use" \
                or license_name == "Attribution required" \
                or license_name == "Attribution and share-alike required" \
                or license_name == "Link requested":
            license_tmp = 'other'
        else:
            license_tmp = 'other'
        
        # fallback to license url
        if license_tmp == 'other':
            node = tree.find('license/text')
            license_text = ''
            license_href = ''
            if node is not None:
                license_text = node.text
                if license_text is not None:
                    license_text = license_text.strip()
                #print(str(node.attrib))
                if node.attrib.has_key('href'):
                    license_href=node.attrib['href']
                    #print(fulldirname+' - '+license_href)
            if license_href == 'http://creativecommons.org/licenses/by/3.0/' \
                    or license_href == 'http://creativecommons.org/licenses/by-sa/3.0/':
                license_tmp = 'cc3'
            elif license_href == 'http://creativecommons.org/licenses/by-sa-nc/3.0/' :
                license_tmp = 'ccnc'

        # decide if we can distribute it, based on license class 
        distribute_tmp = 'unsure'
        if license_tmp in licenses_dist_yes:
            distribute_tmp = 'yes'
        elif license_tmp in licenses_dist_no:
            distribute_tmp = 'no'
        elif license_tmp in licenses_dist_unsure:
            distribute_tmp = 'unsure'
        elif license_tmp in licenses_dist_noncomm:
            distribute_tmp = 'noncomm'
        # exceptions
        if fulldirname in licenses_dist_force_yes:
            distribute_tmp = 'yes'
        if fulldirname in licenses_dist_force_no:
            distribute_tmp = 'no'

        license_dict[ license_tmp ].append(fulldirname)
        distribute_dict[ distribute_tmp ].append(fulldirname)
        print(fulldirname+';'+distribute_tmp+';'+license_tmp+';\"'+license_name+'\"')

print('')
    
print(str(count)+' dirs with licenses found')
print('')
print(str(count_miss)+' dirs without licenses found')
print(str(dirs_miss))
print('')
print(str(count_err)+' dirs without licenses and svg files found')

print('\nlicense categories:')
#print(str(license_dict))
for key in license_dict.iterkeys():
    print('')
    print(key+' : '+str(len(license_dict[key])))
    print(str(license_dict[key]))

print('\ndistribute categories:')
#print(str(license_dict))
for key in distribute_dict.iterkeys():
    print('')
    print(key+' : '+str(len(distribute_dict[key])))
    print(str(distribute_dict[key]))


#for val in license_dict['cc3']:
#    filename=cpt_city_basedir+'/'+val+'/COPYING.xml'
#    print('=====')
#    print(filename)
#    try:
#        f = open(filename, 'r')
#        print f.read(),
#        f.close()
#    except IOError:
#        print "File " + filename + " does not exist."


