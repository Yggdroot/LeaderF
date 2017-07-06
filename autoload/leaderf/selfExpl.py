#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


#*****************************************************
# SelfExplorer
#*****************************************************
class SelfExplorer(Explorer):
    def __init__(self):
        self._self_type = "Self"
        self._content = [
            '0  LeaderfFile             "search files"',
            '1  LeaderfBuffer           "search listed buffers"',
            '2  LeaderfBufferAll        "search all buffers"',
            '3  LeaderfMru              "search most recently used files"',
            '4  LeaderfMruCwd           "search MRU in current working directory"',
            '5  LeaderfTag              "navigate tags using the tags file"',
            '6  LeaderfBufTag           "navigate tags in current buffer"',
            '7  LeaderfBufTagAll        "navigate tags in all listed buffers"',
            '8  LeaderfFunction         "navigate functions or methods in current buffer"',
            '9  LeaderfFunctionAll      "navigate functions or methods in all listed buffers"',
            '10 LeaderfLine             "search a line in current buffer"',
            '11 LeaderfLineAll          "search a line in all listed buffers"',
            '12 LeaderfHistoryCmd       "execute the command in the history"',
            '13 LeaderfHistorySearch    "execute the search command in the history"'
            ] 

    def getContent(self, *args, **kwargs):
        return self._content

    def getStlCategory(self):
        return "Self"

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def isFilePath(self):
        return False


#*****************************************************
# SelfExplManager
#*****************************************************
class SelfExplManager(Manager):
    def __init__(self):
        super(SelfExplManager, self).__init__()
        self._match_ids = []

    def _getExplClass(self):
        return SelfExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#selfExplMaps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        cmd = line.split(maxsplit=2)[1]
        lfCmd(cmd)

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
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(SelfExplManager, self)._afterEnter()
        id = int(lfEval('''matchadd('Lf_hl_selfIndex', '^\d\+')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_selfDescription', ' \zs".*"$')'''))
        self._match_ids.append(id)

    def _beforeExit(self):
        super(SelfExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def _supportsRefine(self):
        return True


#*****************************************************
# selfExplManager is a singleton
#*****************************************************
selfExplManager = SelfExplManager()

__all__ = ['selfExplManager']
