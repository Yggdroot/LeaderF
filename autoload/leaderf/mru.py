#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
import fnmatch
from leaderf.util import *


#*****************************************************
# Mru
#*****************************************************
class Mru(object):
    def __init__(self):
        self._cacheDir = os.path.join(vim.eval("g:Lf_CacheDiretory"), '.LfCache', 'mru')
        self._cacheFile = os.path.join(self._cacheDir, 'mruCache')
        self._initCache()

    def _initCache(self):
        if not os.path.exists(self._cacheDir):
            os.makedirs(self._cacheDir)
        if not os.path.exists(self._cacheFile):
            with lfOpen(self._cacheFile, 'w', errors = 'ignore'):
                pass

    def getCacheFileName(self):
        return self._cacheFile

    def saveToCache(self, bufName):
        if True in (fnmatch.fnmatch(bufName,i) for i in vim.eval("g:Lf_MruFileExclude")):
            return
        with lfOpen(self._cacheFile, 'r+', errors = 'ignore') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if bufName == lines[i].rstrip():
                    del lines[i]
                    break
            lines.insert(0, bufName + '\n')
            if len(lines) > int(vim.eval("g:Lf_MruMaxFiles")):
                del lines[-1]
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

#*****************************************************
# mru is a sigleton
#*****************************************************
mru = Mru()

__all__ = ['mru']
