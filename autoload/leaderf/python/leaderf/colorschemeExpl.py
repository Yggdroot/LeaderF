#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


#*****************************************************
# ColorschemeExplorer
#*****************************************************
class ColorschemeExplorer(Explorer):
    def __init__(self):
        pass

    def getContent(self, *args, **kwargs):
        content = []
        for dir in lfEval("&rtp").split(','):
            try:
                colors = os.listdir(os.path.join(dir, "colors"))
                content.extend([c[:-4] for c in colors if c.endswith(".vim")])
            except:
                pass

        return content

    def getStlCategory(self):
        return "Colorscheme"

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))


#*****************************************************
# ColorschemeExplManager
#*****************************************************
class ColorschemeExplManager(Manager):
    def __init__(self):
        super(ColorschemeExplManager, self).__init__()
        self._orig_line = ''

    def _getExplClass(self):
        return ColorschemeExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Colors#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        lfCmd("colorscheme " + line)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, 1, 2, return the whole line
        """
        if not line:
            return ''

        return line

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, 1, 2, return 0
        """
        return 0

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : execute command under cursor')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q/<Esc> : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(ColorschemeExplManager, self)._afterEnter()

    def _beforeExit(self):
        super(ColorschemeExplManager, self)._beforeExit()

    def _previewResult(self, preview):
        if not self._needPreview(preview):
            return

        self._acceptSelection(self._getInstance().currentLine)


#*****************************************************
# colorschemeExplManager is a singleton
#*****************************************************
colorschemeExplManager = ColorschemeExplManager()

__all__ = ['colorschemeExplManager']
