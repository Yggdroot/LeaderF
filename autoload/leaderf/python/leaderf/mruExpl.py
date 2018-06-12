#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
from fnmatch import fnmatch
from .utils import *
from .explorer import *
from .manager import *
from .mru import *


#*****************************************************
# MruExplorer
#*****************************************************
class MruExplorer(Explorer):
    def __init__(self):
        self._prefix_length = 0
        self._max_bufname_len = 0

    def getContent(self, *args, **kwargs):
        with lfOpen(mru.getCacheFileName(), 'r+', errors='ignore') as f:
            lines = f.readlines()
            lines = [name for name in lines if os.path.exists(lfDecode(name.rstrip()))]
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

        if "--cwd" in kwargs.get("arguments", {}):
            lines = [name for name in lines if lfDecode(name).startswith(os.getcwd())]

        lines = [line.rstrip() for line in lines] # remove the '\n'
        wildignore = lfEval("g:Lf_MruWildIgnore")
        lines = [name for name in lines if True not in (fnmatch(name, j) for j in wildignore['file'])
                    and True not in (fnmatch(name, "*/" + j + "/*") for j in wildignore['dir'])]

        if len(lines) == 0:
            return lines

        if kwargs["cb_name"] == lines[0]:
            lines = lines[1:] + lines[0:1]

        self._max_bufname_len = max(int(lfEval("strdisplaywidth('%s')"
                                        % escQuote(getBasename(line))))
                                    for line in lines)
        for i, line in enumerate(lines):
            if lfEval("g:Lf_ShowRelativePath") == '1':
                line = lfRelpath(line)
            basename = getBasename(line)
            dirname = getDirname(line)
            space_num = self._max_bufname_len \
                        - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))
            lines[i] = '{}{} "{}"'.format(getBasename(line), ' ' * space_num,
                                          dirname if dirname else '.' + os.sep)
        return lines

    def getStlCategory(self):
        return 'Mru'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsMulti(self):
        return True

    def supportsNameOnly(self):
        return True

    def delFromCache(self, name):
        with lfOpen(mru.getCacheFileName(), 'r+', errors='ignore') as f:
            lines = f.readlines()
            lines.remove(lfEncode(os.path.abspath(lfDecode(name))) + '\n')
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

    def getPrefixLength(self):
        return self._prefix_length

    def getMaxBufnameLen(self):
        return self._max_bufname_len

#*****************************************************
# MruExplManager
#*****************************************************
class MruExplManager(Manager):
    def __init__(self):
        super(MruExplManager, self).__init__()
        self._match_ids = []

    def _getExplClass(self):
        return MruExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Mru#Maps()")

    def _argaddFiles(self, files):
        # It will raise E480 without 'silent!'
        lfCmd("silent! argdelete *")
        for file in files:
            dirname = self._getDigest(file, 2)
            basename = self._getDigest(file, 1)
            lfCmd("argadd %s" % escSpecial(dirname + basename))

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        dirname = self._getDigest(line, 2)
        basename = self._getDigest(line, 1)
        try:
            lfCmd("hide edit %s" % escSpecial(dirname + basename))
        except vim.error as e: # E37
            lfPrintError(e)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return ''
        prefix_len = self._getExplorer().getPrefixLength()
        if mode == 0:
            return line[prefix_len:]
        elif mode == 1:
            start_pos = line.find(' "') # what if there is " in file name?
            return line[prefix_len:start_pos].rstrip()
        else:
            start_pos = line.find(' "') # what if there is " in file name?
            return line[start_pos+2 : -1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if not line:
            return 0
        prefix_len = self._getExplorer().getPrefixLength()
        if mode == 0:
            return prefix_len
        elif mode == 1:
            return prefix_len
        else:
            start_pos = line.find(' "') # what if there is " in file name?
            return lfBytesLen(line[:start_pos+2])

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" d : remove from mru list')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" s : select multiple files')
        help.append('" a : select all files')
        help.append('" c : clear all selections')
        help.append('" q/<Esc> : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(MruExplManager, self)._afterEnter()
        id = int(lfEval('''matchadd('Lf_hl_bufDirname', ' \zs".*"$')'''))
        self._match_ids.append(id)

    def _beforeExit(self):
        super(MruExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def deleteMru(self):
        if vim.current.window.cursor[0] <= self._help_length:
            return
        lfCmd("setlocal modifiable")
        line = vim.current.line
        dirname = self._getDigest(line, 2)
        basename = self._getDigest(line, 1)
        self._explorer.delFromCache(escSpecial(dirname + basename))
        if len(self._content) > 0:
            self._content.remove(line)
        del vim.current.line
        lfCmd("setlocal nomodifiable")



#*****************************************************
# mruExplManager is a singleton
#*****************************************************
mruExplManager = MruExplManager()

__all__ = ['mruExplManager']
