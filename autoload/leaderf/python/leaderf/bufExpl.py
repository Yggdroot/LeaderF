#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from functools import wraps
from .utils import *
from .explorer import *
from .manager import *
from .mru import *
from .devicons import (
    webDevIconsGetFileTypeSymbol,
    webDevIconsStrLen,
    webDevIconsBytesLen,
    matchaddDevIconsDefault,
    matchaddDevIconsExact,
    matchaddDevIconsExtension,
)


#*****************************************************
# BufferExplorer
#*****************************************************
class BufferExplorer(Explorer):
    def __init__(self):
        self._prefix_length = 0
        self._max_bufname_len = 0

    def getContent(self, *args, **kwargs):
        mru_bufnrs = []
        for num in reversed(lfEval("g:Lf_MruBufnrs")):
            if num not in mru_bufnrs:
                mru_bufnrs.append(int(num))
        for num in reversed(mru_bufnrs):
            mru.setBufferTimestamp(num)
        lfCmd("let g:Lf_MruBufnrs = []")

        if "--all" not in kwargs.get("arguments", {}):
            if "--tabpage" not in kwargs.get("arguments", {}):
                buffers = {b.number: b for b in vim.buffers
                           if lfEval("buflisted(%d)" % b.number) == '1'}
            else:
                buffers = {w.buffer.number: w.buffer for w in vim.current.tabpage.windows
                           if lfEval("buflisted(%d)" % w.buffer.number) == '1'}
        else:
            if "--tabpage" not in kwargs.get("arguments", {}):
                buffers = {b.number: b for b in vim.buffers
                           if os.path.basename(b.name) != "LeaderF"}
            else:
                buffers = {w.buffer.number: w.buffer for w in vim.current.tabpage.windows
                           if os.path.basename(w.buffer.name) != "LeaderF"}


        # e.g., 12 u %a+-  aaa.txt
        bufnr_len = len(lfEval("bufnr('$')"))
        self._prefix_length = bufnr_len + 8
        self.show_icon = False
        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
            self.show_icon = True
            self._prefix_length += webDevIconsStrLen()

        self._max_bufname_len = max([int(lfEval("strdisplaywidth('%s')"
                                        % escQuote(getBasename(buffers[nr].name))))
                                    for nr in mru.getMruBufnrs() if nr in buffers] + [len('[No Name]')] or [0])

        bufnames = []
        for nr in mru.getMruBufnrs():
            if nr in buffers:
                buf_name = buffers[nr].name
                if not buf_name:
                    buf_name = "[No Name]"
                if lfEval("g:Lf_ShowRelativePath") == '1':
                    buf_name = lfRelpath(buf_name)
                basename = getBasename(buf_name)
                dirname = getDirname(buf_name)
                space_num = self._max_bufname_len \
                            - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))
                if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
                    icon = webDevIconsGetFileTypeSymbol(basename)
                else:
                    icon = ''
                # e.g., 12 u %a+-  aaa.txt
                buf_name = '{:{width}d} {:1s} {:1s}{:1s}{:1s}{:1s} {}{}{} "{}"'.format(nr,
                            '' if buffers[nr].options["buflisted"] else 'u',
                            '%' if int(lfEval("bufnr('%')")) == nr
                                else '#' if int(lfEval("bufnr('#')")) == nr else '',
                            'a' if lfEval("bufwinnr(%d)" % nr) != '-1' else 'h',
                            '+' if buffers[nr].options["modified"] else '',
                            '-' if not buffers[nr].options["modifiable"] else '',
                            icon, basename, ' ' * space_num,
                            dirname if dirname else '.' + os.sep,
                            width=bufnr_len)
                bufnames.append(buf_name)
                del buffers[nr]
            elif lfEval("bufnr(%d)" % nr) == '-1':
                mru.delMruBufnr(nr)

        return bufnames

    def getStlCategory(self):
        return 'Buffer'

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))

    def supportsNameOnly(self):
        return True

    def getPrefixLength(self):
        return self._prefix_length

    def getMaxBufnameLen(self):
        return self._max_bufname_len


#*****************************************************
# BufExplManager
#*****************************************************
class BufExplManager(Manager):
    def __init__(self):
        super(BufExplManager, self).__init__()

    def _getExplClass(self):
        return BufferExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Buffer#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
        if kwargs.get("mode", '') == 't':
            for tp, w in ((tp, window) for tp in vim.tabpages for window in tp.windows):
                if w.buffer.number == buf_number:
                    vim.current.tabpage = tp
                    vim.current.window = w
                    break
            else:
                buf_name = vim.buffers[buf_number].name
                lfCmd("tabe %s" % escSpecial(buf_name))
        else:
            if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1':
                for w in vim.windows:
                    if w.buffer.number == buf_number:
                        vim.current.window = w
                        break
                else:
                    lfCmd("hide buffer %d" % buf_number)
            else:
                lfCmd("hide buffer %d" % buf_number)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return ''
        prefix_len = self._getExplorer().getPrefixLength()
        if mode == 0:
            return line[prefix_len:]
        elif mode == 1:
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            return basename if basename else "[No Name]"
        else:
            start_pos = line.find(' "')
            return line[start_pos+2 : -1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if not line:
            return 0

        if self._getExplorer().show_icon:
            prefix_len = self._getExplorer().getPrefixLength() - webDevIconsStrLen() + webDevIconsBytesLen()
        else:
            prefix_len = self._getExplorer().getPrefixLength()

        if mode == 0:
            return prefix_len
        elif mode == 1:
            return prefix_len
        else:
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            space_num = self._getExplorer().getMaxBufnameLen() \
                        - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))
            return prefix_len + lfBytesLen(basename) + space_num + 2

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" d : wipe out buffer under cursor')
        help.append('" D : delete buffer under cursor')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(BufExplManager, self)._afterEnter()

        winid = None
        if self._getInstance().getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_bufNumber'', ''^\s*\zs\d\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_bufIndicators'', ''^\s*\d\+\s*\zsu\=\s*[#%%]\=...'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_bufModified'', ''^\s*\d\+\s*u\=\s*[#%%]\=.+\s*\zs.*$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_bufNomodifiable'', ''^\s*\d\+\s*u\=\s*[#%%]\=..-\s*\zs.*$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_bufDirname'', '' \zs".*"$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            winid = self._getInstance().getPopupWinId()
        else:
            id = int(lfEval("matchadd('Lf_hl_bufNumber', '^\s*\zs\d\+')"))
            self._match_ids.append(id)
            id = int(lfEval("matchadd('Lf_hl_bufIndicators', '^\s*\d\+\s*\zsu\=\s*[#%]\=...')"))
            self._match_ids.append(id)
            id = int(lfEval("matchadd('Lf_hl_bufModified', '^\s*\d\+\s*u\=\s*[#%]\=.+\s*\zs.*$')"))
            self._match_ids.append(id)
            id = int(lfEval("matchadd('Lf_hl_bufNomodifiable', '^\s*\d\+\s*u\=\s*[#%]\=..-\s*\zs.*$')"))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_bufDirname', ' \zs".*"$')'''))
            self._match_ids.append(id)

        # devicons
        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
            self._match_ids.extend(matchaddDevIconsExtension(r'__icon__\ze\s\+.\{-}\.__name__\($\|\s\)', winid))
            self._match_ids.extend(matchaddDevIconsExact(r'__icon__\ze\s\+__name__\($\|\s\)', winid))
            self._match_ids.extend(matchaddDevIconsDefault(r'__icon__\ze\s\+\S\+\($\|\s\)', winid))

    def _beforeExit(self):
        super(BufExplManager, self)._beforeExit()

    def deleteBuffer(self, wipe=0):
        instance = self._getInstance()
        if self._inHelpLines():
            return

        line = instance._buffer_object[instance.window.cursor[0] - 1]
        if line == '':
            return

        if instance.getWinPos() == 'popup':
            lfCmd("call win_execute(%d, 'setlocal modifiable')" % instance.getPopupWinId())
        else:
            lfCmd("setlocal modifiable")
        if len(self._content) > 0:
            self._content.remove(line)
            self._getInstance().setStlTotal(len(self._content)//self._getUnit())
            self._getInstance().setStlResultsCount(len(self._content)//self._getUnit())
        buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
        lfCmd("confirm %s %d" % ('bw' if wipe else 'bd', buf_number))
        del instance._buffer_object[instance.window.cursor[0] - 1]
        if instance.getWinPos() == 'popup':
            instance.refreshPopupStatusline()
            lfCmd("call win_execute(%d, 'setlocal nomodifiable')" % instance.getPopupWinId())
        else:
            lfCmd("setlocal nomodifiable")

    def _previewInPopup(self, *args, **kwargs):
        line = args[0]
        buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
        self._createPopupPreview(vim.buffers[buf_number].name, buf_number, 0)


#*****************************************************
# bufExplManager is a singleton
#*****************************************************
bufExplManager = BufExplManager()

__all__ = ['bufExplManager']
