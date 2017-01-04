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


#*****************************************************
# BufferExplorer
#*****************************************************
class BufferExplorer(Explorer):
    def __init__(self):
        self._prefix_length = 0
        self._max_bufname_len = 0

    def getContent(self, *args, **kwargs):
        show_unlisted = False if len(args) == 0 else args[0]
        if show_unlisted:
            buffers = {b.number: b for b in vim.buffers
                       if os.path.basename(b.name) != "LeaderF"}
        else:
            buffers = {b.number: b for b in vim.buffers
                       if lfEval("buflisted(%d)" % b.number) == '1'}

        # e.g., 12 u %a+- aaa.txt
        bufnr_len = len(str(len(vim.buffers)))
        self._prefix_length = bufnr_len + 8

        self._max_bufname_len = max(int(lfEval("strdisplaywidth('%s')"
                                        % escQuote(getBasename(buffers[nr].name))))
                                    for nr in mru.getMruBufnrs() if nr in buffers)

        bufnames = []
        for nr in mru.getMruBufnrs():
            if nr in buffers:
                buf_name = buffers[nr].name
                if not buf_name:
                    buf_name = "[No Name]"
                if lfEval("g:Lf_ShowRelativePath") == '1':
                    try:
                        buf_name = lfEncode(os.path.relpath(lfDecode(buf_name), os.getcwd()))
                    except ValueError:
                        pass
                basename = getBasename(buf_name)
                dirname = getDirname(buf_name)
                space_num = self._max_bufname_len \
                            - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))
                # e.g., 12 u %a+- aaa.txt
                buf_name = '{:{width}d} {:1s} {:1s}{:1s}{:1s}{:1s} {}{} "{}"'.format(nr,
                            '' if buffers[nr].options["buflisted"] else 'u',
                            '%' if int(lfEval("bufnr('%')")) == nr
                                else '#' if int(lfEval("bufnr('#')")) == nr else '',
                            'a' if lfEval("bufwinnr(%d)" % nr) != '-1' else 'h',
                            '+' if buffers[nr].options["modified"] else '',
                            '-' if not buffers[nr].options["modifiable"] else '',
                            basename, ' ' * space_num,
                            dirname if dirname else '.' + os.sep,
                            width=bufnr_len)
                bufnames.append(buf_name)
                del buffers[nr]
            elif lfEval("bufnr(%d)" % nr) == '-1':
                mru.delMruBufnr(nr)

        return bufnames

    def getStlFunction(self):
        return 'Buffer'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return True

    def getPrefixLength(self):
        return self._prefix_length

    def getMaxBufnameLen(self):
        return self._max_bufname_len


#*****************************************************
# BufExplManager
#*****************************************************
class BufExplManager(Manager):
    def __init__(self):
        super(BufExplManager, self).__init__()
        self._match_ids = []

    def _getExplClass(self):
        return BufferExplorer

    def _defineMaps(self):
        lfCmd("call g:LfBufExplMaps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
        lfCmd("hide buffer %d" % buf_number)

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
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            return basename if basename else "[No Name]"
        else:
            start_pos = line.find(' "')
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
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            space_num = self._getExplorer().getMaxBufnameLen() \
                        - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))
            return prefix_len + lfBytesLen(basename) + space_num + 2

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
        help.append('" ---------------------------------------------------------')
        return help

    def _preStart(self):
        super(BufExplManager, self)._preStart()
        id = int(lfEval("matchadd('Lf_hl_bufNumber', '^\s*\zs\d\+')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufIndicators', '^\s*\d\+\s*\zsu\=\s*[#%]\=...')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufModified', '^\s*\d\+\s*u\=\s*[#%]\=.+\s*\zs.*$')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufNomodifiable', '^\s*\d\+\s*u\=\s*[#%]\=..-\s*\zs.*$')"))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_bufDirname', ' \zs".*"$')'''))
        self._match_ids.append(id)

    def _cleanup(self):
        super(BufExplManager, self)._cleanup()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def deleteBuffer(self, wipe=0):
        if vim.current.window.cursor[0] <= self._help_length:
            return
        lfCmd("setlocal modifiable")
        line = vim.current.line
        buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
        lfCmd("confirm %s %d" % ('bw' if wipe else 'bd', buf_number))
        del vim.current.line
        lfCmd("setlocal nomodifiable")



#*****************************************************
# bufExplManager is a singleton
#*****************************************************
bufExplManager = BufExplManager()

__all__ = ['bufExplManager']
