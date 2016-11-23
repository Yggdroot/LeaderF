#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *
from leaderf.mru import *


#*****************************************************
# BufferExplorer
#*****************************************************
class BufferExplorer(Explorer):
    @showRelativePath
    def getContent(self, *args, **kwargs):
        show_unlisted = False if len(args) == 0 else args[0]
        buffers = {b.name:b for b in vim.buffers}
        if show_unlisted:
            return [b for b in mru.getMruBuffers() if b in buffers \
                    and os.path.basename(b) != "LeaderF"]
        if int(vim.eval("v:version")) > 703:
            return [b for b in mru.getMruBuffers() if b in buffers \
                    and buffers[b].options["buflisted"]]
        else:
            return [b for b in mru.getMruBuffers() if b in buffers \
                    and vim.eval("buflisted('%s')" % escQuote(b)) == '1']

    def acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
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
        line = lfEncode(os.path.abspath(lfDecode(line)))
        if wipe == 0:
            vim.command("confirm bd %s" % re.sub(' ', '\\ ', line))
        else:
            vim.command("confirm bw %s" % re.sub(' ', '\\ ', line))
        del vim.current.line
        vim.command("setlocal nomodifiable")



#*****************************************************
# bufExplManager is a singleton
#*****************************************************
bufExplManager = BufExplManager()

__all__ = ['bufExplManager']
