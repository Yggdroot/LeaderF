#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


# *****************************************************
# FiletypeExplorer
# *****************************************************
class FiletypeExplorer(Explorer):
    def __init__(self):
        self._content = []

    def getContent(self, *args, **kwargs):
        if self._content:
            return self._content
        else:
            return self.getFreshContent()

    def getFreshContent(self, *args, **kwargs):
        result = [
            os.path.basename(f).replace(".vim", "")
            for f in lfEval("globpath(&rtp, 'syntax/*.vim')").split("\n")
        ]

        # to unique
        self._content = sorted(set(x for x in result))

        return self._content

    def getStlCategory(self):
        return "Filetype"

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))


# *****************************************************
# FiletypeExplManager
# *****************************************************
class FiletypeExplManager(Manager):
    def __init__(self):
        super(FiletypeExplManager, self).__init__()

    def _getExplClass(self):
        return FiletypeExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Filetype#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        lfCmd("set filetype=" + args[0])

    def _getDigest(self, line, mode):
        return line

    def _getDegestStartPos(self, line, mode):
        return 0

    def _createHelp(self):
        help = []
        help.append('" <CR>/o : set filetype under cursor')
        help.append('" q : quit')
        help.append('" i : switch to input mode')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help


# *****************************************************
# filetypeExplManager is a singleton
# *****************************************************
filetypeExplManager = FiletypeExplManager()

__all__ = ["filetypeExplManager"]
