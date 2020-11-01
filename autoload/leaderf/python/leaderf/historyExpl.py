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
        pattern_exclude = []
        history_pattern_exclude = lfEval("g:Lf_HistoryExclude")
        if "history" in kwargs:
            lfCmd("let tmp = @x")
            lfCmd("redir @x")
            if kwargs.get("history") == "cmd":
                self._history_type = "Cmd_History"
                lfCmd("silent history :")
                pattern_exclude = history_pattern_exclude.get('cmd', [])
            elif kwargs.get("history") == "search":
                self._history_type = "Search_History"
                lfCmd("silent history /")
                pattern_exclude = history_pattern_exclude.get('search', [])
            else:
                self._history_type = "History"
                lfCmd("let @x = ''")
            result = lfEval("@x")
            lfCmd("let @x = tmp")
            lfCmd("redir END")
            result_list = result.splitlines()[2:]
            result_list = [line[1:].lstrip().split('  ', 1)[1] for line in result_list]

            compiled = [re.compile(p) for p in pattern_exclude]
            result_list = [line for line in result_list if all(p.search(line) is None for p in compiled)]

        return result_list[::-1]

    def getStlCategory(self):
        return self._history_type

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))

    def getHistoryType(self):
        return self._history_type


#*****************************************************
# HistoryExplManager
#*****************************************************
class HistoryExplManager(Manager):
    def __init__(self):
        super(HistoryExplManager, self).__init__()

    def _getExplClass(self):
        return HistoryExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#History#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        cmd = args[0]
        if self._getExplorer().getHistoryType() == "Cmd_History":
            try:
                lfCmd(cmd)
            except vim.error:
                lfPrintTraceback()
            lfCmd("call histadd(':', '%s')" % escQuote(cmd))
        elif self._getExplorer().getHistoryType() == "Search_History":
            try:
                lfCmd("/%s" % cmd)
            except vim.error:
                lfPrintTraceback()

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
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" e : edit command under cursor')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _cmdExtension(self, cmd):
        if equal(cmd, '<C-o>'):
            self.editHistory()
        return True

    def editHistory(self):
        instance = self._getInstance()

        line = instance.currentLine
        edit_prompt = lfEval("g:Lf_HistoryEditPromptIfEmpty") == "1"
        if edit_prompt and len(line.strip()) == 0:
            line = ''.join(instance._cli._cmdline)

        instance.exitBuffer()
        cmd = ":"

        if self._getExplorer().getHistoryType() == "Search_History":
            cmd = "/"

        lfCmd("call feedkeys('%s', 'n')" % (cmd + escQuote(line)))


#*****************************************************
# historyExplManager is a singleton
#*****************************************************
historyExplManager = HistoryExplManager()

__all__ = ['historyExplManager']
