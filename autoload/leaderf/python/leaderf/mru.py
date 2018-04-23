#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import sys
import os.path
import fnmatch
from .utils import *


#*****************************************************
# Mru
#*****************************************************
class Mru(object):
    def __init__(self):
        self._cache_dir = os.path.join(lfEval("g:Lf_CacheDirectory"),
                                       '.LfCache',
                                       'python' + lfEval("g:Lf_PythonVersion"),
                                       'mru')
        self._cache_file = os.path.join(self._cache_dir, 'mruCache')
        self._initCache()
        self._mru_bufnrs = {}
        self._timestamp = 0

    def _initCache(self):
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
        if not os.path.exists(self._cache_file):
            with lfOpen(self._cache_file, 'w', errors='ignore'):
                pass

    def getCacheFileName(self):
        return self._cache_file

    def normalize(self, name):
        if '~' in name:
            name = os.path.expanduser(name)
        name = os.path.abspath(name)
        if sys.platform[:3] == 'win':
            if name[:4] == '\\\\?\\' and os.path.isabs(name):
                if os.path.isabs(name[4:]) and name[5:6] == ':':
                    name = name[4:]
            if name[1:3] == ':\\':
                name = name[:1].upper() + name[1:]
        elif sys.platform == 'cygwin':
            if name.startswith('/cygdrive/'):
                name = name[:11].lower() + name[11:]
        return name

    def saveToCache(self, buf_name):
        buf_name = self.normalize(buf_name)
        if True in (fnmatch.fnmatch(buf_name, i)
                    for i in lfEval("g:Lf_MruFileExclude")):
            return
        nocase = False
        compare = buf_name
        if sys.platform[:3] == 'win' or sys.platform in ('cygwin', 'msys'):
            nocase = True
            compare = buf_name.lower()
        with lfOpen(self._cache_file, 'r+', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                text = line.rstrip()
                if (compare == text) or (nocase and compare == text.lower()):
                    if i == 0:
                        return
                    del lines[i]
                    break

            lines.insert(0, buf_name + '\n')
            if len(lines) > int(lfEval("g:Lf_MruMaxFiles")):
                del lines[-1]
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

    def setBufferTimestamp(self, buf_number):
        self._mru_bufnrs[buf_number] = self._timestamp
        self._timestamp += 1

    def getMruBufnrs(self):
        bufnrs = sorted(self._mru_bufnrs.items(), key=lambda d:d[1], reverse=True)
        mru_bufnrs = [i[0] for i in bufnrs]
        return mru_bufnrs[1:] + mru_bufnrs[0:1]

    def delMruBufnr(self, buf_number):
        del self._mru_bufnrs[buf_number]

#*****************************************************
# mru is a singleton
#*****************************************************
mru = Mru()

__all__ = ['mru']

#  vim: set ts=4 sw=4 tw=0 et :

