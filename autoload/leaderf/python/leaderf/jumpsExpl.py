#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *


#*****************************************************
# JumpsExplorer
#*****************************************************
class JumpsExplorer(Explorer):
    def __init__(self):
        pass

    def getContent(self, *args, **kwargs):
        return self.getFreshContent(*args, **kwargs)

    def getFreshContent(self, *args, **kwargs):
        content = lfEval("split(execute('jumps'), '\n')")

        flag = ' '
        self._content = []
        self._content.append(content[0])
        for line in reversed(content[1:]):
            if line.endswith('LeaderF'):
                continue
            if line.startswith('>'):
                flag = '\t'
            self._content.append(line + flag)
        return self._content

    def getStlCategory(self):
        return 'Jumps'

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))


#*****************************************************
# JumpsExplManager
#*****************************************************
class JumpsExplManager(Manager):
    def __init__(self):
        super(JumpsExplManager, self).__init__()

    def _getExplClass(self):
        return JumpsExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Jumps#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        if line.startswith('>'):
            return

        # title
        if re.match('[^0-9]', line.lstrip()):
            return

        if "--recall" in self._arguments or "--stayOpen" in self._arguments \
                or "preview" in kwargs:
            res = line.split(None, 3)
            if len(res) < 4:
                return
            jump, line, col, file_text = res
            file_text = file_text[:-1]
            orig_buf_num = self._getInstance().getOriginalPos()[2].number
            orig_buf = vim.buffers[orig_buf_num]
            # it's text
            if int(line) <= len(orig_buf) and orig_buf[int(line) - 1].lstrip().startswith(file_text):
                self._getInstance().gotoOriginalWindow()
                lfCmd("%s" % line)
            else:
                lfCmd("hide edit %s | %s" % (escSpecial(os.path.expanduser(file_text)), line))
        else:
            number = line.split(None, 1)[0]
            if line.endswith('\t'):
                lfCmd(':exec "norm! %s\<C-O>"' % number)
            else:
                lfCmd(':exec "norm! %s\<C-I>"' % number)

        if "preview" not in kwargs:
            lfCmd("setlocal cursorline! | redraw | sleep 150m | setlocal cursorline!")

        if vim.current.window not in self._cursorline_dict:
            self._cursorline_dict[vim.current.window] = vim.current.window.options["cursorline"]

        lfCmd("setlocal cursorline")


    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        return line[:-1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        return 0

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F5> : refresh the cache')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(JumpsExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_jumpsTitle'', ''^ \D\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_jumpsNumber'', ''^>\?\s*\zs\d\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_jumpsLineCol'', ''^>\?\s*\d\+\s*\zs\d\+\s*\d\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_jumpsIndicator'', ''^>'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval('''matchadd('Lf_hl_jumpsTitle', '^ \D\+')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_jumpsNumber', '^>\?\s*\zs\d\+')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_jumpsLineCol', '^>\?\s*\d\+\s*\zs\d\+\s*\d\+')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_jumpsIndicator', '^>')'''))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(JumpsExplManager, self)._beforeExit()
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()

    def _readFinished(self):
        if "--recall" in self._arguments:
            return
        instance = self._getInstance()
        indicator = 0
        for line in instance.buffer:
            indicator += 1
            if line.startswith('>'):
                instance.window.cursor = (indicator, 0)
                self._getInstance().mimicCursor()
                break

    def _bangReadFinished(self):
        super(JumpsExplManager, self)._bangReadFinished()
        self._readFinished()

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]

        # title
        if re.match('[^0-9]', line.lstrip()):
            return

        res = line.split(None, 3)
        if len(res) < 4:
            return
        jump, line, col, file_text = res
        file_text = file_text[:-1]
        orig_buf_num = self._getInstance().getOriginalPos()[2].number
        orig_buf = vim.buffers[orig_buf_num]
        # it's text
        if int(line) <= len(orig_buf) and orig_buf[int(line) - 1].lstrip().startswith(file_text):
            self._createPopupPreview("", orig_buf_num, line)
        else:
            self._createPopupPreview("", os.path.expanduser(file_text), line)


#*****************************************************
# jumpsExplManager is a singleton
#*****************************************************
jumpsExplManager = JumpsExplManager()

__all__ = ['jumpsExplManager']
