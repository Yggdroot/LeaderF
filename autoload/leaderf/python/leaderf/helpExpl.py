#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import re
import os.path
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


#*****************************************************
# HelpExplorer
#*****************************************************
class HelpExplorer(Explorer):
    def __init__(self):
        self._content = []
        self._file_ids = {}

    def getContent(self, *args, **kwargs):
        if self._content:
            return self._content
        else:
            return self.getFreshContent()

    def getFreshContent(self, *args, **kwargs):
        self._content = []
        lfCmd("silent! helptags ALL")
        file_id = 0
        for dir in lfEval("&rtp").split(','):
            tags_file = os.path.join(dir, "doc", "tags")
            try:
                with lfOpen(tags_file, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines:
                        tag, file = line.split()[:2]
                        self._content.append("{:<40} {} {}".format(tag, file, file_id))
            except IOError:
                pass

            self._file_ids[file_id] = os.path.dirname(tags_file)
            file_id += 1

        return self._content

    def getStlCategory(self):
        return "Help"

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))


#*****************************************************
# HelpExplManager
#*****************************************************
class HelpExplManager(Manager):
    def __init__(self):
        super(HelpExplManager, self).__init__()

    def _getExplClass(self):
        return HelpExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Help#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        cmd = line.split(None, 1)[0]
        if kwargs.get("mode", '') == 't':
            lfCmd("tab help " + cmd)
        elif kwargs.get("mode", '') == 'v':
            lfCmd("vertical help " + cmd)
        elif kwargs.get("mode", '') == 'h':
            lfCmd("help " + cmd)
        else:
            lfCmd("help " + cmd)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the whole line
                  1, return the tagname
                  2, return the tagfile
        """
        if not line:
            return ''
        if mode == 0:
            return line
        elif mode == 1:
            return line.split(None, 1)[0]
        else:
            return line.split(None, 1)[1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start position of the whole line
                  1, return the start position of the tagname
                  2, return the start position of the tagfile
        """
        if mode == 0:
            return 0
        elif mode == 1:
            return 0
        else:
            return line.rfind(' ') + 1

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : execute command under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(HelpExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_helpTagfile'', '' \zs.*$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval(r'''matchadd('Lf_hl_helpTagfile', ' \zs.*$')'''))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(HelpExplManager, self)._beforeExit()

    def _supportsRefine(self):
        return True

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0 or args[0] == '':
            return

        line = args[0]
        tagname, tagfile, file_id = line.split(None, 2)
        tagfile = os.path.join(self._getExplorer()._file_ids[int(file_id)], tagfile)
        jump_cmd = r"call search('\m\*%s\*', 'w')" % escQuote(tagname)
        self._createPopupPreview("", tagfile, 0, jump_cmd)


#*****************************************************
# helpExplManager is a singleton
#*****************************************************
helpExplManager = HelpExplManager()

__all__ = ['helpExplManager']
