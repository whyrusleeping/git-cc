"""Copy files from Clearcase to Git manually"""

from common import *
from cache import *
import os, shutil, stat
from os.path import join, abspath, isdir
from fnmatch import fnmatch

ARGS = {
    'cache': 'Use the cache for faster syncing'
}

def main(cache=False):
    validateCC()
    if cache:
        return syncCache()
    glob = '*'
    base = abspath(CC_DIR)
    for i in cfg.getInclude():
        for (dirpath, dirnames, filenames) in os.walk(join(CC_DIR, i)):
            reldir = dirpath[len(base):]
            if fnmatch(reldir, './lost+found'):
                continue
            for file in filenames:
                if fnmatch(file, glob):
                    #python's join function creates an 'absolute path'
                    #this is fine until you use the result of join in another
                    #call to join, when given an absolute path it disregards
                    #ALL other things its trying to join. Python sucks.
                    relFileName = join(reldir, file)
                    if relFileName[0] == '\\' or relFileName[0] == '/':
                        relFileName = relFileName[1:]
                    copy(relFileName)

def copy(file):
    print(GIT_DIR)
    print(CC_DIR)
    newFile = join(GIT_DIR, file)
    debug('Source: %s' % file)
    debug('Copying to %s' % newFile)
    mkdirs(newFile)
    shutil.copy(join(CC_DIR, file), newFile)
    os.chmod(newFile, stat.S_IREAD | stat.S_IWRITE)

def syncCache():
    cache1 = Cache(GIT_DIR)
    cache1.start()
    
    cache2 = Cache(GIT_DIR)
    cache2.initial()
    
    for path in cache2.list():
        if not cache1.contains(path):
            cache1.update(path)
            if not isdir(join(CC_DIR, path.file)):
                copy(path.file)
    cache1.write()
