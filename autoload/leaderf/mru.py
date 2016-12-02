#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
import fnmatch
import time
from leaderf.utils import *


#*****************************************************
# Mru
#*****************************************************
class Mru(object):
    def __init__(self):
        self._cache_dir = os.path.join(vim.eval("g:Lf_CacheDiretory"),
                                       '.LfCache',
                                       'python' + vim.eval("g:Lf_PythonVersion"),
                                       'mru')
        self._cache_file = os.path.join(self._cache_dir, 'mruCache')
        self._initCache()
        self._mru_buffers = {}

    def _initCache(self):
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
        if not os.path.exists(self._cache_file):
            with lfOpen(self._cache_file, 'w', errors='ignore'):
                pass

    def getCacheFileName(self):
        return self._cache_file

    def saveToCache(self, buf_name):
        if True in (fnmatch.fnmatch(buf_name, i)
                    for i in vim.eval("g:Lf_MruFileExclude")):
            return
        with lfOpen(self._cache_file, 'r+', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if buf_name == line.rstrip():
                    if i == 0:
                        return
                    del lines[i]
                    break
            lines.insert(0, buf_name + '\n')
            if len(lines) > int(vim.eval("g:Lf_MruMaxFiles")):
                del lines[-1]
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

    def setBufferTimestamp(self, buf_name):
        self._mru_buffers[buf_name] = time.time()

    def getMruBuffers(self):
        buffers = sorted(self._mru_buffers.items(), key=lambda d:d[1], reverse=True)
        mru_buf = [i[0] for i in buffers]
        return mru_buf[1:] + mru_buf[0:1]


#*****************************************************
# mru is a singleton
#*****************************************************
mru = Mru()

__all__ = ['mru']
