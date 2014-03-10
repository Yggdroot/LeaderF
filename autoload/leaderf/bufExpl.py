#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from functools import wraps
from leaderf.util import *
from leaderf.explorer import *
from leaderf.manager import *


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
# BufferExplorer
#*****************************************************
class BufferExplorer(Explorer):
    @showRelativePath
    def getContent(self, *args, **kwargs):
        showUnlisted = False if len(args) == 0 else args[0]
        if showUnlisted:
            return [b.name for b in vim.buffers if b.name is not None]
        if int(vim.eval("v:version")) > 703:
            return [b.name for b in vim.buffers if b.options["buflisted"]]
        else:
            return [b.name for b in vim.buffers if vim.eval("buflisted('%s')" % escQuote(b.name)) == '1']

    def acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
        vim.command("hide edit %s" % escSpecial(file))

    def getStlFunction(self):
        return 'Buffer'

    def getStlCurDir(self):
        return escQuote(uniCoding(os.getcwd()))

    def supportsFullPath(self):
        return True

    def supportsSort(self):
        return True

#*****************************************************
# BufExplManager
#*****************************************************
class BufExplManager(Manager):
    def _getExplClass(self):
        return BufferExplorer

    def _defineMaps(self):
        vim.command("call g:LfBufExplMaps()")

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" d : wipe out buffer under cursor')
        help.append('" D : delete buffer under cursor')
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------')
        return help

    def deleteBuffer(self, wipe = 0):
        if vim.current.window.cursor[0] <= self._helpLength:
            return
        vim.command("setlocal modifiable")
        try:
            line = vim.current.line
            if wipe == 0:
                vim.command("confirm bd %s" % re.sub(' ', '\\ ', os.path.abspath(line)))
            else:
                vim.command("confirm bw %s" % re.sub(' ', '\\ ', os.path.abspath(line)))
            if len(self._content) > 0:
                self._content.remove(line)
            del vim.current.line
        except:
            pass
        vim.command("setlocal nomodifiable")



#*****************************************************
# bufExplManager is a singleton
#*****************************************************
bufExplManager = BufExplManager()

__all__ = ['bufExplManager']
