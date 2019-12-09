#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *


#*****************************************************
# LineExplorer
#*****************************************************
class LineExplorer(Explorer):
    def __init__(self):
        pass

    def getContent(self, *args, **kwargs):
        line_list = []
        if "--all" in kwargs.get("arguments", {}): # all buffers
            cur_buffer = vim.current.buffer
            for b in vim.buffers:
                if b.options["buflisted"]:
                    if lfEval("bufloaded(%d)" % b.number) == '0':
                        lfCmd("silent hide buffer %d" % b.number)
                    line_list.extend(self._getLineList(b))
            if vim.current.buffer != cur_buffer:
                vim.current.buffer = cur_buffer
        else:
            line_list = self._getLineList(vim.current.buffer)
        return line_list

    def _getLineList(self, buffer):
        bufname = os.path.basename(buffer.name)
        if sys.version_info >= (3, 0):
            return ["%s\t[%s:%d %d]" % (line.encode('utf-8', "replace").decode('utf-8', "replace"), bufname, i, buffer.number)
                    for i, line in enumerate(buffer, 1) if line and not line.isspace()]
        else:
            return ["%s\t[%s:%d %d]" % (line, bufname, i, buffer.number)
                    for i, line in enumerate(buffer, 1) if line and not line.isspace()]

    def getStlCategory(self):
        return 'Line'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))


#*****************************************************
# LineExplManager
#*****************************************************
class LineExplManager(Manager):
    def __init__(self):
        super(LineExplManager, self).__init__()

    def _getExplClass(self):
        return LineExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Line#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        line = line.rsplit("\t", 1)[1][1:-1]    # file:line buf_number
        line_nr, buf_number = line.rsplit(":", 1)[1].split()
        lfCmd("hide buffer +%s %s" % (line_nr, buf_number))
        lfCmd("norm! ^zv")
        lfCmd("norm! zz")

        if vim.current.window not in self._cursorline_dict:
            self._cursorline_dict[vim.current.window] = vim.current.window.options["cursorline"]

        lfCmd("setlocal cursorline")

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the whole line
                  1, return the whole line
                  2, return the whole line
        """
        return line.rsplit("\t", 1)[0]

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
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(LineExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_lineLocation'', ''\t\zs\[.*:\d\+ \d\+]$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval('''matchadd('Lf_hl_lineLocation', '\t\zs\[.*:\d\+ \d\+]$')'''))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(LineExplManager, self)._beforeExit()
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        line = line.rsplit("\t", 1)[1][1:-1]    # file:line buf_number
        line_nr, buf_number = line.rsplit(":", 1)[1].split()
        self._createPopupPreview(vim.buffers[int(buf_number)].name, buf_number, line_nr)


#*****************************************************
# lineExplManager is a singleton
#*****************************************************
lineExplManager = LineExplManager()

__all__ = ['lineExplManager']
