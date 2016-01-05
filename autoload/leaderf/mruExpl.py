#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
from functools import wraps
from leaderf.util import *
from leaderf.explorer import *
from leaderf.manager import *
from leaderf.mru import *


def showRelativePath(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if vim.eval("g:Lf_ShowRelativePath") == '1':
            try:
                return [os.path.relpath(line) for line in func(*args, **kwargs)]
            except ValueError:
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return deco


#*****************************************************
# MruExplorer
#*****************************************************
class MruExplorer(Explorer):
    @showRelativePath
    def getContent(self, *args, **kwargs):
        with lfOpen(mru.getCacheFileName(), 'r+', errors = 'ignore') as f:
            lines = f.readlines()
            lines[:] = [name for name in lines if os.path.exists(name.rstrip())]
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)
            return lines

    def acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
        vim.command("hide edit %s" % escSpecial(file))

    def getStlFunction(self):
        return 'Mru'

    def getStlCurDir(self):
        return escQuote(uniCoding(os.getcwd()))

    def supportsMulti(self):
        return True

    def supportsFullPath(self):
        return True

    def supportsSort(self):
        return True

    def delFromCache(self, name):
        with lfOpen(mru.getCacheFileName(), 'r+', errors = 'ignore') as f:
            lines = f.readlines()
            lines.remove(name + '\n')
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

#*****************************************************
# MruExplManager
#*****************************************************
class MruExplManager(Manager):
    def _getExplClass(self):
        return MruExplorer

    def _defineMaps(self):
        vim.command("call g:LfMruExplMaps()")

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" d : remove from mru list')
        help.append('" i : switch to input mode')
        help.append('" s : select multiple files')
        help.append('" a : select all files')
        help.append('" l : clear all selections')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------')
        return help


    def deleteMru(self):
        if vim.current.window.cursor[0] <= self._helpLength:
            return
        vim.command("setlocal modifiable")
        line = vim.current.line
        self._explorer.delFromCache(line)
        if len(self._content) > 0:
            self._content.remove(line + '\n')
        del vim.current.line
        vim.command("setlocal nomodifiable")



#*****************************************************
# bufExplManager is a singleton
#*****************************************************
mruExplManager = MruExplManager()

__all__ = ['mruExplManager']
