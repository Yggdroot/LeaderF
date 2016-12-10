#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from functools import wraps
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *
from leaderf.mru import *


def showRelativePath(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if vim.eval("g:Lf_ShowRelativePath") == '1':
            result = []
            for line in func(*args, **kwargs):
                try:
                    result.append(lfEncode(os.path.relpath(lfDecode(line), os.getcwd())))
                except ValueError:
                    result.append(line)
            return result
        else:
            return func(*args, **kwargs)
    return deco


#*****************************************************
# BufferExplorer
#*****************************************************
class BufferExplorer(Explorer):
    @showRelativePath
    def getContent(self, *args, **kwargs):
        show_unlisted = False if len(args) == 0 else args[0]
        if show_unlisted:
            buffers = {b.number: b for b in vim.buffers
                       if os.path.basename(b.name) != "LeaderF"}
        else:
            buffers = {b.number: b for b in vim.buffers 
                       if vim.eval("buflisted(%d)" % b.number) == '1'}

        bufnames = []
        for nr in mru.getMruBufnrs():
            if nr in buffers:
                buf_name = buffers[nr].name
                if not buf_name:
                    buf_name = "[No Name %d]" % nr
                bufnames.append(buf_name)
                del buffers[nr]
            elif vim.eval("bufnr(%d)" % nr) == '-1':
                mru.delMruBufnr(nr)

        return bufnames

    def acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
        if file.startswith("[No Name "):
            buf_number = int(re.sub(r"^.*?(\d+).$", r"\1", file))
            vim.command("hide buffer %d" % buf_number)
        else:
            vim.command("hide edit %s" % escSpecial(file))

    def getStlFunction(self):
        return 'Buffer'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
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
        help.append('" s : select multiple files')
        help.append('" a : select all files')
        help.append('" c : clear all selections')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def deleteBuffer(self, wipe=0):
        if vim.current.window.cursor[0] <= self._help_length:
            return
        vim.command("setlocal modifiable")
        line = vim.current.line
        if line.startswith("[No Name "):
            buf_number = int(re.sub(r"^.*?(\d+).$", r"\1", line))
            vim.command("confirm %s %d" % ('bw' if wipe else 'bd', buf_number))
        else:
            vim.command("confirm %s %s" % ('bw' if wipe else 'bd', escSpecial(line)))
        del vim.current.line
        vim.command("setlocal nomodifiable")



#*****************************************************
# bufExplManager is a singleton
#*****************************************************
bufExplManager = BufExplManager()

__all__ = ['bufExplManager']
