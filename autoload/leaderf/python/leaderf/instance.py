#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import time
import itertools
from .utils import *


#*****************************************************
# LfInstance
#*****************************************************
class LfInstance(object):
    """
    This class is used to indicate the LeaderF instance, which including
    the tabpage, the window, the buffer, the statusline, etc.
    """
    def __init__(self, category,
                 before_enter_cb,
                 after_enter_cb,
                 before_exit_cb,
                 after_exit_cb):
        self._category = category
        self._before_enter = before_enter_cb
        self._after_enter = after_enter_cb
        self._before_exit = before_exit_cb
        self._after_exit = after_exit_cb
        self._tabpage_object = None
        self._window_object = None
        self._buffer_object = None
        self._buffer_name = lfEval("expand('$VIMRUNTIME/')") + category + '/LeaderF'
        self._cur_buffer_name = ""
        self._win_height = float(lfEval("g:Lf_WindowHeight"))
        self._show_tabline = int(lfEval("&showtabline"))
        self._is_autocmd_set = False
        self._reverse_order = lfEval("get(g:, 'Lf_ReverseOrder', 0)") == '1'
        self._last_reverse_order = self._reverse_order
        self._orig_pos = () # (tabpage, window, buffer)
        self._running_status = 0
        self._cursor_row = None
        self._help_length = None
        self._current_working_directory = None
        self._highlightStl()

    def _initStlVar(self):
        if int(lfEval("!exists('g:Lf_{}_StlCategory')".format(self._category))):
            lfCmd("let g:Lf_{}_StlCategory = '-'".format(self._category))
            lfCmd("let g:Lf_{}_StlMode = '-'".format(self._category))
            lfCmd("let g:Lf_{}_StlCwd= '-'".format(self._category))
            lfCmd("let g:Lf_{}_StlRunning = ':'".format(self._category))
            lfCmd("let g:Lf_{}_StlTotal = '0'".format(self._category))
            lfCmd("let g:Lf_{}_StlLineNumber = '1'".format(self._category))
            lfCmd("let g:Lf_{}_StlResultsCount = '0'".format(self._category))

        stl = "%#Lf_hl_{0}_stlName# LeaderF "
        stl += "%#Lf_hl_{0}_stlSeparator0#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlCategory# %{{g:Lf_{0}_StlCategory}} "
        stl += "%#Lf_hl_{0}_stlSeparator1#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlMode# %(%{{g:Lf_{0}_StlMode}}%) "
        stl += "%#Lf_hl_{0}_stlSeparator2#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlCwd# %<%{{g:Lf_{0}_StlCwd}} "
        stl += "%#Lf_hl_{0}_stlSeparator3#%{{g:Lf_StlSeparator.left}}"
        stl += "%=%#Lf_hl_{0}_stlBlank#"
        stl += "%#Lf_hl_{0}_stlSeparator4#%{{g:Lf_StlSeparator.right}}"
        if self._reverse_order:
            stl += "%#Lf_hl_{0}_stlLineInfo# %{{g:Lf_{0}_StlLineNumber}}/%{{g:Lf_{0}_StlResultsCount}} "
        else:
            stl += "%#Lf_hl_{0}_stlLineInfo# %l/%{{g:Lf_{0}_StlResultsCount}} "
        stl += "%#Lf_hl_{0}_stlSeparator5#%{{g:Lf_StlSeparator.right}}"
        stl += "%#Lf_hl_{0}_stlTotal# Total%{{g:Lf_{0}_StlRunning}} %{{g:Lf_{0}_StlTotal}} "
        self._stl = stl.format(self._category)

    def _highlightStl(self):
        lfCmd("call leaderf#colorscheme#highlight('{}')".format(self._category))

    def _setAttributes(self):
        lfCmd("setlocal nobuflisted")
        lfCmd("setlocal buftype=nofile")
        lfCmd("setlocal bufhidden=hide")
        lfCmd("setlocal undolevels=-1")
        lfCmd("setlocal noswapfile")
        lfCmd("setlocal nolist")
        lfCmd("setlocal norelativenumber")
        lfCmd("setlocal nospell")
        lfCmd("setlocal wrap")
        lfCmd("setlocal nofoldenable")
        lfCmd("setlocal foldmethod=manual")
        lfCmd("setlocal shiftwidth=4")
        lfCmd("setlocal cursorline")
        if self._reverse_order:
            lfCmd("setlocal nonumber")
            lfCmd("setlocal foldcolumn=1")
            lfCmd("setlocal winfixheight")
        else:
            lfCmd("setlocal number")
            lfCmd("setlocal foldcolumn=0")
            lfCmd("setlocal nowinfixheight")
        lfCmd("setlocal filetype=leaderf")

    def _setStatusline(self):
        self._initStlVar()
        self.window.options["statusline"] = self._stl
        lfCmd("redrawstatus")
        if not self._is_autocmd_set:
            self._is_autocmd_set = True
            lfCmd("augroup Lf_{}_Colorscheme".format(self._category))
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#setStatusline({}, '{}')"
                  .format(self.buffer.number, self._stl))
            lfCmd("autocmd WinEnter,FileType * call leaderf#colorscheme#setStatusline({}, '{}')"
                  .format(self.buffer.number, self._stl))
            lfCmd("augroup END")

    def _createBufWindow(self, win_pos):
        self._win_pos = win_pos

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'all'
        try:
            orig_win = vim.current.window
            for w in vim.windows:
                vim.current.window = w
                if lfEval("exists('w:lf_win_view')") == '0':
                    lfCmd("let w:lf_win_view = {}")
                lfCmd("let w:lf_win_view['%s'] = winsaveview()" % self._category)
        finally:
            vim.current.window = orig_win
            vim.options['eventignore'] = saved_eventignore

        if win_pos != 'fullScreen':
            self._restore_sizes = lfEval("winrestcmd()")
            self._orig_win_count = len(vim.windows)

        """
        https://github.com/vim/vim/issues/1737
        https://github.com/vim/vim/issues/1738
        """
        # clear the buffer first to avoid a flash
        if self._buffer_object is not None and self._buffer_object.valid \
                and lfEval("g:Lf_RememberLastSearch") == '0' \
                and "--append" not in self._arguments \
                and "--recall" not in self._arguments:
            self.buffer.options['modifiable'] = True
            del self._buffer_object[:]

        if win_pos == 'bottom':
            lfCmd("silent! noa keepa keepj bo sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'belowright':
            lfCmd("silent! noa keepa keepj bel sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'aboveleft':
            lfCmd("silent! noa keepa keepj abo sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'top':
            lfCmd("silent! noa keepa keepj to sp %s" % self._buffer_name)
            if self._win_height >= 1:
                lfCmd("resize %d" % self._win_height)
            elif self._win_height > 0:
                lfCmd("resize %d" % (int(lfEval("&lines")) * self._win_height))
        elif win_pos == 'fullScreen':
            lfCmd("silent! noa keepa keepj $tabedit %s" % self._buffer_name)
        elif win_pos == 'left':
            lfCmd("silent! noa keepa keepj to vsp %s" % self._buffer_name)
        elif win_pos == 'right':
            lfCmd("silent! noa keepa keepj bo vsp %s" % self._buffer_name)
        else:
            lfCmd("echoe 'Wrong value of g:Lf_WindowPosition'")

        self._tabpage_object = vim.current.tabpage
        self._window_object = vim.current.window
        self._initial_win_height = self._window_object.height
        if self._reverse_order:
            self._window_object.height = 1

        if self._buffer_object is None or not self._buffer_object.valid:
            self._buffer_object = vim.current.buffer
            lfCmd("augroup Lf_{}_Colorscheme".format(self._category))
            lfCmd("autocmd!")
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlight('{}')"
                  .format(self._category))
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlightMode('{0}', g:Lf_{0}_StlMode)"
                  .format(self._category))
            lfCmd("autocmd ColorScheme <buffer> doautocmd syntax")
            lfCmd("autocmd CursorMoved <buffer> let g:Lf_{}_StlLineNumber = 1 + line('$') - line('.')"
                  .format(self._category))
            lfCmd("autocmd VimResized * let g:Lf_VimResized = 1")
            lfCmd("augroup END")

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'all'
        try:
            orig_win = vim.current.window
            for w in vim.windows:
                vim.current.window = w
                if lfEval("exists('w:lf_win_view')") != '0' and lfEval("has_key(w:lf_win_view, '%s')" % self._category) != '0':
                    lfCmd("call winrestview(w:lf_win_view['%s'])" % self._category)
        finally:
            vim.current.window = orig_win
            vim.options['eventignore'] = saved_eventignore

    def _enterOpeningBuffer(self):
        if (self._tabpage_object and self._tabpage_object.valid
            and self._window_object and self._window_object.valid
            and self._window_object.buffer == self._buffer_object):
            vim.current.tabpage = self._tabpage_object
            vim.current.window = self._window_object
            self._after_enter()
            return True
        return False

    def setArguments(self, arguments):
        self._last_reverse_order = self._reverse_order
        self._arguments = arguments
        if "--reverse" in self._arguments or lfEval("get(g:, 'Lf_ReverseOrder', 0)") == '1':
            self._reverse_order = True
        else:
            self._reverse_order = False

    def ignoreReverse(self):
        self._reverse_order = False

    def setStlCategory(self, category):
        lfCmd("let g:Lf_{}_StlCategory = '{}'".format(self._category, category) )

    def setStlMode(self, mode):
        lfCmd("let g:Lf_{}_StlMode = '{}'".format(self._category, mode))
        lfCmd("call leaderf#colorscheme#highlightMode('{0}', g:Lf_{0}_StlMode)"
              .format(self._category))

    def setStlCwd(self, cwd):
        lfCmd("let g:Lf_{}_StlCwd = '{}'".format(self._category, cwd))

    def setStlTotal(self, total):
        lfCmd("let g:Lf_{}_StlTotal = '{}'".format(self._category, total))

    def setStlResultsCount(self, count):
        lfCmd("let g:Lf_{}_StlResultsCount = '{}'".format(self._category, count))
        if lfEval("has('nvim')") == '1':
            lfCmd("redrawstatus")

    def setStlRunning(self, running):
        if running:
            status = (':', ' ')
            lfCmd("let g:Lf_{}_StlRunning = '{}'".format(self._category, status[self._running_status]))
            self._running_status = (self._running_status + 1) & 1
        else:
            self._running_status = 0
            lfCmd("let g:Lf_{}_StlRunning = ':'".format(self._category))

    def enterBuffer(self, win_pos):
        if self._enterOpeningBuffer():
            return

        lfCmd("let g:Lf_{}_StlLineNumber = '1'".format(self._category))
        self._orig_pos = (vim.current.tabpage, vim.current.window, vim.current.buffer)
        self._orig_cursor = vim.current.window.cursor

        self._before_enter()

        if win_pos == 'fullScreen':
            self._orig_tabpage = vim.current.tabpage
            if len(vim.tabpages) < 2:
                lfCmd("set showtabline=0")
            self._createBufWindow(win_pos)
        else:
            self._orig_win_nr = vim.current.window.number
            self._orig_win_id = lfWinId(self._orig_win_nr)
            self._createBufWindow(win_pos)
        self._setAttributes()
        self._setStatusline()

        self._after_enter()

    def exitBuffer(self):
        self._before_exit()

        if self._win_pos == 'fullScreen':
            try:
                lfCmd("tabclose!")
                vim.current.tabpage = self._orig_tabpage
            except:
                lfCmd("new | only")

            lfCmd("set showtabline=%d" % self._show_tabline)
        else:
            saved_eventignore = vim.options['eventignore']
            vim.options['eventignore'] = 'all'
            try:
                orig_win = vim.current.window
                for w in vim.windows:
                    vim.current.window = w
                    if lfEval("exists('w:lf_win_view')") == '0':
                        lfCmd("let w:lf_win_view = {}")
                    lfCmd("let w:lf_win_view['%s'] = winsaveview()" % self._category)
            finally:
                vim.current.window = orig_win
                vim.options['eventignore'] = saved_eventignore

            if len(vim.windows) > 1:
                lfCmd("silent! hide")
                if self._orig_win_id is not None:
                    lfCmd("call win_gotoid(%d)" % self._orig_win_id)
                else:
                    # 'silent!' is used to skip error E16.
                    lfCmd("silent! exec '%d wincmd w'" % self._orig_win_nr)
                if lfEval("get(g:, 'Lf_VimResized', 0)") == '0' \
                        and self._orig_win_count == len(vim.windows):
                    lfCmd(self._restore_sizes) # why this line does not take effect?
                                               # it's weird. repeat 4 times
                    lfCmd(self._restore_sizes) # fix issue #102
                    lfCmd(self._restore_sizes) # fix issue #102
                    lfCmd(self._restore_sizes) # fix issue #102
                    lfCmd(self._restore_sizes) # fix issue #102
            else:
                lfCmd("bd")

            saved_eventignore = vim.options['eventignore']
            vim.options['eventignore'] = 'all'
            try:
                orig_win = vim.current.window
                for w in vim.windows:
                    vim.current.window = w
                    if lfEval("exists('w:lf_win_view')") != '0' and lfEval("has_key(w:lf_win_view, '%s')" % self._category) != '0':
                        lfCmd("call winrestview(w:lf_win_view['%s'])" % self._category)
            finally:
                vim.current.window = orig_win
                vim.options['eventignore'] = saved_eventignore

        lfCmd("echo")

        self._after_exit()

    def _actualLength(self, buffer):
        num = 0
        columns = int(lfEval("&columns"))
        for i in buffer:
            num += (int(lfEval("strdisplaywidth('%s')" % escQuote(i))) + columns - 1)// columns
        return num

    def setBuffer(self, content):
        if lfEval("g:Lf_IgnoreBufferName") == '1':
            buffer_name = os.path.normpath(lfDecode(self._cur_buffer_name))
            if lfEval("g:Lf_ShowRelativePath") == '1':
                buffer_name = os.path.relpath(buffer_name)

            if buffer_name in content:
                content.remove(buffer_name)

        self.buffer.options['modifiable'] = True
        if lfEval("has('nvim')") == '1':
            if isinstance(content, list) and len(content) > 0 and len(content[0]) != len(content[0].rstrip("\r\n")):
                # NvimError: string cannot contain newlines
                content = [ line.rstrip("\r\n") for line in content ]
        try:
            if self._reverse_order:
                orig_row = self._window_object.cursor[0]
                orig_buf_len = len(self._buffer_object)

                self._buffer_object[:] = content[::-1]
                buffer_len = len(self._buffer_object)
                if buffer_len < self._initial_win_height:
                    if "--nowrap" not in self._arguments:
                        self._window_object.height = min(self._initial_win_height, self._actualLength(self._buffer_object))
                    else:
                        self._window_object.height = buffer_len
                elif self._window_object.height < self._initial_win_height:
                    self._window_object.height = self._initial_win_height

                try:
                    self._window_object.cursor = (orig_row + buffer_len - orig_buf_len, 0)
                    # if self._window_object.cursor == (buffer_len, 0):
                    #     lfCmd("normal! zb")
                except vim.error:
                    self._window_object.cursor = (buffer_len, 0)
                    # lfCmd("normal! zb")

                self.setLineNumber()
            else:
                self._buffer_object[:] = content
        finally:
            self.buffer.options['modifiable'] = False

    def appendBuffer(self, content):
        self.buffer.options['modifiable'] = True
        if self.empty():
            self._buffer_object[:] = content
        else:
            self._buffer_object.append(content)

        if self._reverse_order:
            buffer_len = len(self._buffer_object)
            if buffer_len < self._initial_win_height:
                if "--nowrap" not in self._arguments:
                    self._window_object.height = min(self._initial_win_height, self._actualLength(self._buffer_object))
                else:
                    self._window_object.height = buffer_len
            elif self._window_object.height < self._initial_win_height:
                self._window_object.height = self._initial_win_height
            lfCmd("normal! Gzb")

        self.buffer.options['modifiable'] = False

    def clearBuffer(self):
        self.buffer.options['modifiable'] = True
        if self._buffer_object and self._buffer_object.valid:
            del self._buffer_object[:]
        self.buffer.options['modifiable'] = False

    def appendLine(self, line):
        self._buffer_object.append(line)

    def initBuffer(self, content, unit, set_content):
        if isinstance(content, list):
            self.setBuffer(content)
            self.setStlTotal(len(content)//unit)
            self.setStlResultsCount(len(content)//unit)
            return content

        self.buffer.options['modifiable'] = True
        self._buffer_object[:] = []

        try:
            start = time.time()
            status_start = start
            cur_content = []
            for line in content:
                cur_content.append(line)
                if time.time() - start > 0.1:
                    start = time.time()
                    if len(self._buffer_object) <= self._window_object.height:
                        self.setBuffer(cur_content)
                        if self._reverse_order:
                            lfCmd("normal! G")

                    if time.time() - status_start > 0.45:
                        status_start = time.time()
                        self.setStlRunning(True)
                    self.setStlTotal(len(cur_content)//unit)
                    self.setStlResultsCount(len(cur_content)//unit)
                    lfCmd("redrawstatus")
            self.setBuffer(cur_content)
            self.setStlTotal(len(self._buffer_object)//unit)
            self.setStlRunning(False)
            self.setStlResultsCount(len(self._buffer_object)//unit)
            lfCmd("redrawstatus")
            set_content(cur_content)
        except vim.error: # neovim <C-C>
            pass
        except KeyboardInterrupt: # <C-C>
            pass

        return cur_content

    @property
    def tabpage(self):
        return self._tabpage_object

    @property
    def window(self):
        return self._window_object

    @property
    def buffer(self):
        return self._buffer_object

    @property
    def currentLine(self):
        return vim.current.line if self._buffer_object == vim.current.buffer else None

    def empty(self):
        return len(self._buffer_object) == 1 and self._buffer_object[0] == ''

    def getCurrentPos(self):
        return self._window_object.cursor

    def getOriginalPos(self):
        return self._orig_pos

    def getOriginalCursor(self):
        return self._orig_cursor

    def getInitialWinHeight(self):
        if self._reverse_order:
            return self._initial_win_height
        else:
            return 200

    def isReverseOrder(self):
        return self._reverse_order

    def isLastReverseOrder(self):
        return self._last_reverse_order

    def setLineNumber(self):
        if self._reverse_order:
            line_nr = 1 + len(self._buffer_object) - self._window_object.cursor[0]
            lfCmd("let g:Lf_{}_StlLineNumber = '{}'".format(self._category, line_nr))

    def setCwd(self, cwd):
        self._current_working_directory = cwd

    def getCwd(self):
        return self._current_working_directory

    @property
    def cursorRow(self):
        return self._cursor_row

    @cursorRow.setter
    def cursorRow(self, row):
        self._cursor_row = row

    @property
    def helpLength(self):
        return self._help_length

    @helpLength.setter
    def helpLength(self, length):
        self._help_length = length

    def gotoOriginalWindow(self):
        if self._orig_win_id is not None:
            lfCmd("call win_gotoid(%d)" % self._orig_win_id)
        else:
            # 'silent!' is used to skip error E16.
            lfCmd("silent! exec '%d wincmd w'" % self._orig_win_nr)

#  vim: set ts=4 sw=4 tw=0 et :
