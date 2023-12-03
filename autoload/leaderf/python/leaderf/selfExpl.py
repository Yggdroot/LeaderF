#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *


#*****************************************************
# SelfExplorer
#*****************************************************
class SelfExplorer(Explorer):
    def __init__(self):
        self._self_type = "Self"
        self._content = [
            '0  LeaderfFile             "search files"',
            '1  LeaderfFileFullScreen   "search files, LeaderF window take up full screen"',
            '2  LeaderfBuffer           "search listed buffers"',
            '3  LeaderfBufferAll        "search all buffers"',
            '4  LeaderfTabBuffer        "search listed buffers in current tabpage"',
            '5  LeaderfTabBufferAll     "search all buffers in current tabpage"',
            '6  LeaderfMru              "search most recently used files"',
            '7  LeaderfMruCwd           "search MRU in current working directory"',
            '8  LeaderfTag              "navigate tags using the tags file"',
            '9  LeaderfBufTag           "navigate tags in current buffer"',
            '10 LeaderfBufTagAll        "navigate tags in all listed buffers"',
            '11 LeaderfFunction         "navigate functions or methods in current buffer"',
            '12 LeaderfFunctionAll      "navigate functions or methods in all listed buffers"',
            '13 LeaderfLine             "search a line in current buffer"',
            '14 LeaderfLineAll          "search a line in all listed buffers"',
            '15 LeaderfHistoryCmd       "execute the command in the history"',
            '16 LeaderfHistorySearch    "execute the search command in the history"',
            '17 LeaderfHelp             "navigate the help tags"',
            '18 LeaderfColorscheme      "switch between colorschemes"',
            '19 LeaderfFiletype         "navigate the filetype"',
            '20 LeaderfCommand          "execute built-in/user-defined Ex commands"',
            '21 LeaderfWindow           "search windows"',
            '22 LeaderfQuickFix         "navigate quickfix"',
            '23 LeaderfLocList          "navigate location list"',
            ]

    def getContent(self, *args, **kwargs):
        extra_content = lfEval("g:Lf_SelfContent")
        length = len(self._content)
        content = self._content[:]
        for i, (key, value) in enumerate(extra_content.items()):
            content.append('{:<3d}{:<24s}"{}"'.format(length + i, key, value))
        return content

    def getStlCategory(self):
        return "Self"

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))


#*****************************************************
# SelfExplManager
#*****************************************************
class SelfExplManager(Manager):
    def __init__(self):
        super(SelfExplManager, self).__init__()

    def _getExplClass(self):
        return SelfExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Self#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        cmd = line.split(None, 2)[1]
        try:
            lfCmd(cmd)
        except vim.error:
            lfPrintTraceback()

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the description
        """
        if not line:
            return ''
        if mode == 0:
            return line
        elif mode == 1:
            start_pos = line.find(' "') # what if there is " in file name?
            return line[:start_pos].rstrip()
        else:
            start_pos = line.find(' "') # what if there is " in file name?
            return line[start_pos+2 : -1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of description
        """
        if not line:
            return 0
        if mode == 0:
            return 0
        elif mode == 1:
            return 0
        else:
            start_pos = line.find(' "') # what if there is " in file name?
            return lfBytesLen(line[:start_pos+2])

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : execute command under cursor')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(SelfExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_selfIndex'', ''^\d\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_selfDescription'', '' \zs".*"$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval(r'''matchadd('Lf_hl_selfIndex', '^\d\+')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_selfDescription', ' \zs".*"$')'''))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(SelfExplManager, self)._beforeExit()

    def _supportsRefine(self):
        return True


#*****************************************************
# selfExplManager is a singleton
#*****************************************************
selfExplManager = SelfExplManager()

__all__ = ['selfExplManager']
