#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import fnmatch
import time
from functools import wraps
from leaderf.util import *
from leaderf.explorer import *
from leaderf.manager import *


def showRelativePath(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if vim.eval("g:Lf_ShowRelativePath") == '1':
            # os.path.relpath() is too slow!
            dir = os.getcwd() if len(args) == 1 else args[1]
            cwdLen = len(uniCoding(dir))
            if not dir.endswith(os.sep):
                cwdLen += 1
            return [line[cwdLen:] for line in func(*args, **kwargs)]
        else:
            return func(*args, **kwargs)
    return deco


#*****************************************************
# FileExplorer
#*****************************************************
class FileExplorer(Explorer):
    def __init__(self):
        self._curDir = ''
        self._content = []
        self._cacheDir = os.path.join(vim.eval("g:Lf_CacheDiretory"), '.LfCache', 'file')
        self._cacheIndex = os.path.join(self._cacheDir, 'cacheIndex')
        self._initCache()

    def _initCache(self):
        if not os.path.exists(self._cacheDir):
            os.makedirs(self._cacheDir)
        if not os.path.exists(self._cacheIndex):
            with lfOpen(self._cacheIndex, 'w', errors = 'ignore'):
                pass

    def _getFiles(self, dir):
        startTime = time.time()
        wildignore = vim.eval("g:Lf_WildIgnore")
        fileList = []
        for dirPath,dirs,files in os.walk(dir, followlinks = False if vim.eval("g:Lf_FollowLinks") == '0' else True):
            dirs[:] = [i for i in dirs if True not in (fnmatch.fnmatch(i,j) for j in wildignore['dir'])]
            for name in files:
                if True not in (fnmatch.fnmatch(name,j) for j in wildignore['file']):
                    fileList.append(uniCoding(os.path.join(dirPath,name)))
                if time.time() - startTime > float(vim.eval("g:Lf_IndexTimeLimit")):
                    return fileList
        return fileList

    @showRelativePath
    def _getFileList(self, dir):
        dir = dir if dir.endswith(os.sep) else dir + os.sep
        with lfOpen(self._cacheIndex, 'r+', errors = 'ignore') as f:
            lines = f.readlines()
            lineCount = len(lines)
            pathLen = 0
            target = -1
            for i in range(lineCount):
                path = lines[i].split(None, 2)[2].strip()
                if dir.startswith(path) and len(path) > pathLen:
                    pathLen = len(path)
                    target = i

            if target != -1:
                lines[target] = re.sub('^\S*', '%.3f' % time.time(), lines[target])
                f.seek(0)
                f.truncate(0)
                f.writelines(lines)
                with lfOpen(os.path.join(self._cacheDir, lines[target].split(None, 2)[1]), 'r', errors = 'ignore') as cacheFile:
                    if lines[target].split(None, 2)[2].strip() == dir:
                        return cacheFile.readlines()
                    else:
                        fileList = [line for line in cacheFile.readlines() if line.startswith(dir)]
                        if fileList == []:
                            fileList = self._getFiles(dir)
                        return fileList
            else:
                startTime = time.time()
                fileList = self._getFiles(dir)
                deltaSec = time.time() - startTime
                if deltaSec > float(vim.eval("g:Lf_NeedCacheTime")):
                    cacheFileName = ''
                    if lineCount < int(vim.eval("g:Lf_NumberOfCache")):
                        f.seek(0, 2)
                        ts = time.time()
                        line = '%.3f cache_%.3f %s\n' % (ts, ts, dir)
                        f.write(line)
                        cacheFileName = 'cache_%.3f' % ts
                    else:
                        for i in range(lineCount):
                            path = lines[i].split(None, 2)[2].strip()
                            if path.startswith(dir):
                                cacheFileName = lines[i].split(None, 2)[1].strip()
                                lines[i] = '%.3f %s %s\n' % (time.time(), cacheFileName, dir)
                                break
                        if cacheFileName == '':
                            timestamp = lines[0].split(None, 2)[0]
                            oldest = 0
                            for i in range(lineCount):
                                if lines[i].split(None, 2)[0] < timestamp:
                                    timestamp = lines[i].split(None, 2)[0]
                                    oldest = i
                            cacheFileName = lines[oldest].split(None, 2)[1].strip()
                            lines[oldest] = '%.3f %s %s\n' % (time.time(), cacheFileName, dir)
                        f.seek(0)
                        f.truncate(0)
                        f.writelines(lines)
                    with lfOpen(os.path.join(self._cacheDir, cacheFileName), 'w', errors = 'ignore') as cacheFile:
                        for line in fileList:
                            cacheFile.write(line + '\n')
                return fileList

    def _refresh(self):
        dir = os.path.abspath(self._curDir)
        dir = dir if dir.endswith(os.sep) else dir + os.sep
        with lfOpen(self._cacheIndex, 'r+', errors = 'ignore') as f:
            lines = f.readlines()
            lineCount = len(lines)
            pathLen = 0
            target = -1
            for i in range(lineCount):
                path = lines[i].split(None, 2)[2].strip()
                if dir.startswith(path) and len(path) > pathLen:
                    pathLen = len(path)
                    target = i

            if target != -1:
                lines[target] = re.sub('^\S*', '%.3f' % time.time(), lines[target])
                f.seek(0)
                f.truncate(0)
                f.writelines(lines)
                cacheFileName = lines[target].split(None, 2)[1]
                fileList = self._getFiles(dir)
                with lfOpen(os.path.join(self._cacheDir, cacheFileName), 'w', errors = 'ignore') as cacheFile:
                    for line in fileList:
                        cacheFile.write(line + '\n')

    def getContent(self, *args, **kwargs):
        if len(args) > 0:
            if os.path.exists(args[0]):
                os.chdir(args[0])
            else:
                vim.command("echohl ErrorMsg | redraw | echon 'Unknown directory `%s`' | echohl NONE" % args[0])
                return None
        dir = os.getcwd()
        if vim.eval("g:Lf_UseMemoryCache") == 0 or dir != self._curDir:
            self._curDir = dir
            self._content = self._getFileList(dir)
        return self._content

    def acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
        vim.command("hide edit %s" % escSpecial(file))

    def getFreshContent(self, *args, **kwargs):
        self._refresh()
        self._content = self._getFileList(self._curDir)
        return self._content

    def getStlFunction(self):
        return 'File'

    def getStlCurDir(self):
        return escQuote(uniCoding(os.path.abspath(self._curDir)))

    def supportsMulti(self):
        return True

    def supportsFullPath(self):
        return True

    def supportsSort(self):
        return True


#*****************************************************
# FileExplManager
#*****************************************************
class FileExplManager(Manager):
    def _getExplClass(self):
        return FileExplorer

    def _defineMaps(self):
        vim.command("call g:LfFileExplMaps()")

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i : switch to input mode')
        help.append('" s : select multiple files')
        help.append('" a : select all files')
        help.append('" l : clear all selections')
        help.append('" q : quit')
        help.append('" <F5> : refresh the cache')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------')
        return help

#*****************************************************
# fileExplManager is a singleton
#*****************************************************
fileExplManager = FileExplManager()

__all__ = ['fileExplManager']
