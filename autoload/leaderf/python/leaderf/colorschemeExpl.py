#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
import glob
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


#*****************************************************
# ColorschemeExplorer
#*****************************************************
class ColorschemeExplorer(Explorer):
    def __init__(self):
        self._content = []

    def getContent(self, *args, **kwargs):
        if self._content:
            return self._content
        else:
            return self.getFreshContent()

    def getFreshContent(self, *args, **kwargs):
        user_home = os.path.expanduser("~")
        content, content_prefer = [], []
        for dir in lfEval("&rtp").split(','):
            try:
                colors = os.listdir(os.path.join(dir, "colors"))
                colors_name = [c[:-4] for c in colors if c.endswith(".vim")]
                if user_home in dir:
                    content_prefer.extend(colors_name)
                else:
                    content.extend(colors_name)
            except:
                pass

        # packpath
        if lfEval("exists('+packpath')") == "1":
            for dir in lfEval("&packpath").split(","):
                for pack_path in [
                    "{}/pack/*/start/*/colors/*.vim",
                    "{}/pack/*/opt/*/colors/*.vim",
                ]:
                    colors_name = [
                        os.path.basename(f)[:-4]
                        for f in glob.glob(pack_path.format(dir))
                    ]
                    if user_home in dir:
                        content_prefer.extend(colors_name)
                    else:
                        content.extend(colors_name)

        content_prefer, content = list(set(content_prefer)), list(set(content))
        self._content = sorted(content_prefer) + sorted(content)

        return self._content

    def getStlCategory(self):
        return "Colorscheme"

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))


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
        lfCmd("silent! colorscheme " + line)
        if self._getInstance().getWinPos() == 'popup':
            pass
        elif lfEval("&filetype") == "leaderf":
            lfCmd("doautocmd FileType leaderf")

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
        help.append('" q : quit')
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
