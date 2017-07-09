#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *


#*****************************************************
# HistoryExplorer
#*****************************************************
class HistoryExplorer(Explorer):
    def __init__(self):
        self._history_type = "History"

    def getContent(self, *args, **kwargs):
        result_list = []
        if len(args) > 0:
            tmp = lfEval("@x")
            lfCmd("redir @x")
            if args[0] == "cmd":
                self._history_type = "Cmd_History"
                lfCmd("silent history :")
            elif args[0] == "search":
                self._history_type = "Search_History"
                lfCmd("silent history /")
            else:
                self._history_type = "History"
                lfCmd("let @x = ''")
            result = lfEval("@x")
            lfCmd("let @x = '%s'" % escQuote(tmp))
            lfCmd("redir END")
            result_list = result.splitlines()
            start = len(result_list[-1]) - len(result_list[-1][1:].lstrip())
            result_list = [line[start:] for line in result_list]

        return result_list[2:][::-1]

    def getStlCategory(self):
        return self._history_type

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def isFilePath(self):
        return False

    def getHistoryType(self):
        return self._history_type


#*****************************************************
# HistoryExplManager
#*****************************************************
class HistoryExplManager(Manager):
    def __init__(self):
        super(HistoryExplManager, self).__init__()
        self._match_ids = []

    def _getExplClass(self):
        return HistoryExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#History#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        cmd = line.lstrip().split(None, 1)[1]
        if self._getExplorer().getHistoryType() == "Cmd_History":
            lfCmd(cmd)
        elif self._getExplorer().getHistoryType() == "Search_History":
            try:
                lfCmd("/%s" % cmd)
            except vim.error as e:
                lfPrintError(e)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the whole line
                  1, return the whole line
                  2, return the whole line
        """
        return line

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start position of the whole line
                  1, return the start position of the whole line
                  2, return the start position of the whole line
        """
        return 0

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(HistoryExplManager, self)._afterEnter()
        id = int(lfEval('''matchadd('Lf_hl_historyIndex', '^\s*\d\+')'''))
        self._match_ids.append(id)

    def _beforeExit(self):
        super(HistoryExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []


#*****************************************************
# historyExplManager is a singleton
#*****************************************************
historyExplManager = HistoryExplManager()

__all__ = ['historyExplManager']
