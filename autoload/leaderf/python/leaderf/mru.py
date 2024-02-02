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
                                       'LeaderF',
                                       'python' + lfEval("g:Lf_PythonVersion"),
                                       'mru')
        self._cache_file = os.path.join(self._cache_dir, 'frecency')
        self._old_cache_file = os.path.join(self._cache_dir, 'mruCache')
        self._initCache()
        self._mru_bufnrs = { b.number: 0 for b in vim.buffers }
        self._timestamp = 0

    def _initCache(self):
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
        if not os.path.exists(self._cache_file):
            with lfOpen(self._cache_file, 'w', errors='ignore'):
                pass

    def getCacheFileName(self):
        return self._cache_file

    def getOldCacheFileName(self):
        return self._old_cache_file

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

    def filename(self, line):
        return line.rstrip().split(None, 2)[2]

    def saveToCache(self, data_list):
        frecency_list = []
        for item in data_list:
            name = self.normalize(self.filename(item))
            if True in (fnmatch.fnmatch(name, i)
                        for i in lfEval("g:Lf_MruFileExclude")):
                continue
            frecency_list.append(item)

        if not frecency_list:
            return

        with lfOpen(self._cache_file, 'r+', errors='ignore', encoding='utf-8') as f:
            lines = f.readlines()
            for item in frecency_list:
                nocase = False
                compare = self.filename(item)
                if sys.platform[:3] == 'win' or sys.platform in ('cygwin', 'msys'):
                    nocase = True
                    compare = compare.lower()

                for i, line in enumerate(lines):
                    text = self.filename(line)
                    if (compare == text) or (nocase and compare == text.lower()):
                        time1, rank1, filename = item.split(None, 2)
                        time2, rank2, _ = lines[i].split(None, 2)
                        lines[i] = "{} {} {}\n".format(time1, int(rank1) + int(rank2), filename)
                        break
                else:
                    lines.append(item + '\n')

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

