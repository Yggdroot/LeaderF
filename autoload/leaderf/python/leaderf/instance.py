#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import time
import itertools
from .utils import *
from .devicons import (
    webDevIconsGetFileTypeSymbol,
    highlightDevIcons
)


def iconLine(line):
    if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1":
        return webDevIconsGetFileTypeSymbol(line) + line
    else:
        return line


class FloatWindow(object):
    def __init__(self, winid, window, buffer, tabpage, init_line):
        self._winid = winid
        self._window = window
        self._buffer = buffer
        self._tabpage = tabpage
        self._init_line = init_line

    @property
    def id(self):
        return self._winid

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, buffer):
        self._buffer = buffer

    @property
    def tabpage(self):
        return self._tabpage

    @property
    def window(self):
        return self._window

    @property
    def cursor(self):
        return self._window.cursor

    @cursor.setter
    def cursor(self, cursor):
        self._window.cursor = cursor

    @property
    def options(self):
        return self._window.options

    @options.setter
    def options(self, options):
        self._window.options = options

    @property
    def height(self):
        return self._window.height

    @height.setter
    def height(self, height):
        self._window.height = height

    @property
    def width(self):
        return self._window.width

    @property
    def number(self):
        return self._window.number

    @property
    def valid(self):
        return self._window.valid

    @property
    def initialLine(self):
        return self._init_line

    def close(self):
        lfCmd("silent! call nvim_win_close(%d, 0)" % self._winid)

class PopupWindow(object):
    def __init__(self, winid, buffer, tabpage, init_line):
        self._winid = winid
        self._buffer = buffer
        self._tabpage = tabpage
        self._init_line = init_line

    @property
    def id(self):
        return self._winid

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, buffer):
        self._buffer = buffer

    @property
    def tabpage(self):
        return self._tabpage

    @property
    def cursor(self):
        # the col of window.cursor starts from 0, while the col of getpos() starts from 1
        lfCmd("""call win_execute(%d, 'let cursor_pos = getpos(".")') | let cursor_pos[2] -= 1""" % self._winid)
        return [int(i) for i in lfEval("cursor_pos[1:2]")]

    @cursor.setter
    def cursor(self, cursor):
        cursor = [cursor[0], cursor[1]+1]
        lfCmd("""call win_execute(%d, 'call cursor(%s)')""" % (self._winid, str(cursor)))

    @property
    def height(self):
        popup_pos = lfEval("popup_getpos(%d)" % self._winid)
        return int(popup_pos["height"])

    @property
    def width(self):
        popup_pos = lfEval("popup_getpos(%d)" % self._winid)
        return int(popup_pos["width"])

    @property
    def number(self):
        # popup window seems does no have a window number
        # this always return 0
        return int(lfEval("win_id2win(%d)" % self._winid))

    @property
    def valid(self):
        return int(lfEval("winbufnr(%d)" % self._winid)) != -1

    @property
    def initialLine(self):
        return self._init_line

    def close(self):
        lfCmd("call popup_close(%d)" % self._winid)

    def show(self):
        lfCmd("call popup_show(%d)" % self._winid)

    def hide(self):
        lfCmd("call popup_hide(%d)" % self._winid)


class LfPopupInstance(object):
    def __init__(self):
        self._popup_wins = {
                "content_win": None,
                "input_win": None,
                "statusline_win": None,
                }

    def close(self):
        for win in self._popup_wins.values():
            if win:
                win.close()

    def show(self):
        for win in self._popup_wins.values():
            if win:
                win.show()

    def hide(self):
        for win in self._popup_wins.values():
            if win:
                win.hide()

    @property
    def content_win(self):
        return self._popup_wins["content_win"]

    @content_win.setter
    def content_win(self, content_win):
        self._popup_wins["content_win"] = content_win

    @property
    def input_win(self):
        return self._popup_wins["input_win"]

    @input_win.setter
    def input_win(self, input_win):
        self._popup_wins["input_win"] = input_win

    @property
    def statusline_win(self):
        return self._popup_wins["statusline_win"]

    @statusline_win.setter
    def statusline_win(self, statusline_win):
        self._popup_wins["statusline_win"] = statusline_win

    def getWinIdList(self):
        return [win.id for win in self._popup_wins.values() if win is not None]

#*****************************************************
# LfInstance
#*****************************************************
class LfInstance(object):
    """
    This class is used to indicate the LeaderF instance, which including
    the tabpage, the window, the buffer, the statusline, etc.
    """
    def __init__(self, manager, category, cli,
                 before_enter_cb,
                 after_enter_cb,
                 before_exit_cb,
                 after_exit_cb):
        self._manager = manager
        self._category = category
        self._cli = cli
        self._cli.setInstance(self)
        self._before_enter = before_enter_cb
        self._after_enter = after_enter_cb
        self._before_exit = before_exit_cb
        self._after_exit = after_exit_cb
        self._tabpage_object = None
        self._window_object = None
        self._buffer_object = None
        self._buffer_name = lfEval("expand('$VIMRUNTIME/')") + category + '/LeaderF'
        self._input_buffer_number = -1
        self._stl_buffer_number = -1
        self._win_height = float(lfEval("g:Lf_WindowHeight"))
        self._show_tabline = int(lfEval("&showtabline"))
        self._is_autocmd_set = False
        self._is_colorscheme_autocmd_set = False
        self._is_popup_colorscheme_autocmd_set = False
        self._is_icon_colorscheme_autocmd_set = False
        self._reverse_order = lfEval("get(g:, 'Lf_ReverseOrder', 0)") == '1'
        self._last_reverse_order = self._reverse_order
        self._orig_pos = () # (tabpage, window, buffer)
        self._running_status = 0
        self._cursor_row = None
        self._help_length = 0
        self._current_working_directory = None
        self._cur_buffer_name_ignored = False
        self._ignore_cur_buffer_name = lfEval("get(g:, 'Lf_IgnoreCurrentBufferName', 0)") == '1' \
                                            and self._category in ["File"]
        self._popup_winid = 0
        self._popup_maxheight = 0
        self._popup_instance = LfPopupInstance()
        self._win_pos = None
        self._stl_buf_namespace = None
        self._auto_resize = lfEval("get(g:, 'Lf_AutoResize', 0)") == '1'

    def _initStlVar(self):
        if int(lfEval("!exists('g:Lf_{}_StlCategory')".format(self._category))):
            lfCmd("let g:Lf_{}_StlCategory = '-'".format(self._category))
            lfCmd("let g:Lf_{}_StlMode = '-'".format(self._category))
            lfCmd("let g:Lf_{}_StlCwd= '-'".format(self._category))
            lfCmd("let g:Lf_{}_StlRunning = ''".format(self._category))
            lfCmd("let g:Lf_{}_IsRunning = 0".format(self._category))
            lfCmd("let g:Lf_{}_StlTotal = '0'".format(self._category))
            lfCmd("let g:Lf_{}_StlLineNumber = '1'".format(self._category))
            lfCmd("let g:Lf_{}_StlResultsCount = '0'".format(self._category))

        stl = "%#Lf_hl_stlName# LeaderF "
        stl += "%#Lf_hl_{0}_stlSeparator0#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_stlCategory# %{{g:Lf_{0}_StlCategory}} "
        stl += "%#Lf_hl_{0}_stlSeparator1#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlMode# %(%{{g:Lf_{0}_StlMode}}%) "
        stl += "%#Lf_hl_{0}_stlSeparator2#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_stlCwd# %<%{{g:Lf_{0}_StlCwd}} "
        stl += "%#Lf_hl_{0}_stlSeparator3#%{{g:Lf_StlSeparator.left}}"
        stl += "%#Lf_hl_{0}_stlBlank#%="
        stl += "%#Lf_hl_stlSpin#%{{g:Lf_{0}_StlRunning}}"
        stl += "%#Lf_hl_{0}_stlSeparator4#%{{g:Lf_StlSeparator.right}}"
        if self._reverse_order:
            stl += "%#Lf_hl_stlLineInfo# %{{g:Lf_{0}_StlLineNumber}}/%{{g:Lf_{0}_StlResultsCount}} "
        else:
            stl += "%#Lf_hl_stlLineInfo# %l/%{{g:Lf_{0}_StlResultsCount}} "
        stl += "%#Lf_hl_{0}_stlSeparator5#%{{g:Lf_StlSeparator.right}}"
        stl += "%#Lf_hl_stlTotal# Total: %{{g:Lf_{0}_StlTotal}} "
        self._stl = stl.format(self._category)

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
        if lfEval("exists('+cursorlineopt')") == '1':
            lfCmd("setlocal cursorlineopt=both")
        if lfEval("has('nvim')") == '1':
            lfCmd("silent! setlocal signcolumn=no")   # make vim flicker
        lfCmd("setlocal colorcolumn=")
        if self._reverse_order:
            lfCmd("setlocal nonumber")
            lfCmd("setlocal foldcolumn=1")
            lfCmd("setlocal winfixheight")
        else:
            lfCmd("setlocal number")
            lfCmd("setlocal foldcolumn=0")
            lfCmd("setlocal nowinfixheight")
        if self._win_pos != "floatwin":
            lfCmd("silent! setlocal filetype=leaderf")

    def _setStatusline(self):
        if self._win_pos in ('popup', 'floatwin'):
            self._initStlVar()
            return

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

    def _createPopupWindow(self, clear):
        # `type(self._window_object) != type(vim.current.window)` is necessary, error occurs if
        # `Leaderf file --popup` after `Leaderf file` without it.
        if self._window_object is not None and type(self._window_object) != type(vim.current.window)\
                and isinstance(self._window_object, PopupWindow): # type is PopupWindow
            if self._window_object.tabpage == vim.current.tabpage and lfEval("get(g:, 'Lf_Popup_VimResized', 0)") == '0' \
                    and "--popup-width" not in self._arguments and "--popup-height" not in self._arguments:
                if self._popup_winid > 0 and self._window_object.valid: # invalid if cleared by popup_clear()
                    # clear the buffer first to avoid a flash
                    if clear and lfEval("g:Lf_RememberLastSearch") == '0' \
                            and "--append" not in self._arguments \
                            and "--recall" not in self._arguments:
                        self.buffer.options['modifiable'] = True
                        del self._buffer_object[:]
                        self.refreshPopupStatusline()

                    self._popup_instance.show()
                    return
            else:
                lfCmd("let g:Lf_Popup_VimResized = 0")
                self._popup_instance.close()

        buf_number = int(lfEval("bufadd('{}')".format(escQuote(self._buffer_name))))

        width = lfEval("get(g:, 'Lf_PopupWidth', 0)")
        width = self._arguments.get("--popup-width", [width])[0]
        width = width.strip('"').strip("'")
        width = float(lfEval(width))
        if width <= 0:
            maxwidth = int(int(lfEval("&columns")) * 2 // 3)
        elif width < 1:
            maxwidth = int(int(lfEval("&columns")) * width)
            maxwidth = max(20, maxwidth)
        else:
            width = int(width)
            maxwidth = min(width, int(lfEval("&columns")))
            maxwidth = max(20, maxwidth)

        height = lfEval("get(g:, 'Lf_PopupHeight', 0)")
        height = self._arguments.get("--popup-height", [height])[0]
        height = height.strip('"').strip("'")
        height = float(lfEval(height))
        if height <= 0:
            maxheight = int(int(lfEval("&lines")) * 0.4)
        elif height < 1:
            maxheight = int(int(lfEval("&lines")) * height)
            if maxheight < 1:
                maxheight = 1
        else:
            height = int(height)
            maxheight = min(height, int(lfEval("&lines")))

        line, col = [int(i) for i in lfEval("get(g:, 'Lf_PopupPosition', [0, 0])")]
        if line == 0:
            line = (int(lfEval("&lines")) - maxheight) // 2
        else:
            line = min(line, int(lfEval("&lines")) - maxheight)

        if col == 0:
            col = (int(lfEval("&columns")) - maxwidth) // 2
        else:
            col = min(col, int(lfEval("&columns")) - maxwidth)

        if line <= 0:
            line = 1

        if col <= 0:
            col = 1

        self._popup_maxheight = max(maxheight - 2, 1) # there is an input window above

        if lfEval("has('nvim')") == '1':
            self._win_pos = "floatwin"
            floatwin_height = 1

            config = {
                    "relative": "editor",
                    "anchor"  : "NW",
                    "height"  : floatwin_height,
                    "width"   : maxwidth,
                    "row"     : line + 1,
                    "col"     : col
                    }
            lfCmd("silent noswapfile let winid = nvim_open_win(%d, 1, %s)" % (buf_number, str(config)))
            self._popup_winid = int(lfEval("winid"))
            self._setAttributes()
            if lfEval("get(g:, 'Lf_PopupShowFoldcolumn', 1)") == '0':
                try:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', 0)" % self._popup_winid)
                except vim.error:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', '0')" % self._popup_winid)
            else:
                try:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', 1)" % self._popup_winid)
                except vim.error:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', '1')" % self._popup_winid)
            lfCmd("call nvim_win_set_option(%d, 'winhighlight', 'Normal:Lf_hl_popup_window')" % self._popup_winid)
            lfCmd("silent! call nvim_buf_set_option(%d, 'filetype', 'leaderf')" % buf_number)

            self._tabpage_object = vim.current.tabpage
            self._buffer_object = vim.buffers[buf_number]
            self._window_object = FloatWindow(self._popup_winid, vim.current.window, self._buffer_object, self._tabpage_object, line + 1)
            self._popup_instance.content_win = self._window_object

            input_win_config = {
                    "relative": "editor",
                    "anchor"  : "NW",
                    "height"  : 1,
                    "width"   : maxwidth,
                    "row"     : line,
                    "col"     : col
                    }

            if self._input_buffer_number == -1:
                self._input_buffer_number = int(lfEval("bufadd('')"))

            buf_number = self._input_buffer_number
            lfCmd("silent let winid = nvim_open_win(%d, 0, %s)" % (buf_number, str(input_win_config)))
            winid = int(lfEval("winid"))
            lfCmd("call nvim_buf_set_option(%d, 'buflisted', v:false)" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'buftype', 'nofile')" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'bufhidden', 'hide')" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'undolevels', -1)" % buf_number)
            lfCmd("call nvim_buf_set_option(%d, 'swapfile', v:false)" % buf_number)

            lfCmd("call nvim_win_set_option(%d, 'list', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'relativenumber', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'spell', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'foldenable', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'foldmethod', 'manual')" % winid)
            try:
                lfCmd("call nvim_win_set_option(%d, 'foldcolumn', 0)" % winid)
            except vim.error:
                lfCmd("call nvim_win_set_option(%d, 'foldcolumn', '0')" % winid)
            # lfCmd("call nvim_win_set_option(%d, 'signcolumn', 'no')" % winid)
            lfCmd("call nvim_win_set_option(%d, 'cursorline', v:false)" % winid)
            if lfEval("exists('+cursorlineopt')") == '1':
                lfCmd("call nvim_win_set_option(%d, 'cursorlineopt', 'both')" % winid)
            lfCmd("call nvim_win_set_option(%d, 'colorcolumn', '')" % winid)
            lfCmd("call nvim_win_set_option(%d, 'winhighlight', 'Normal:Lf_hl_popup_inputText')" % winid)
            lfCmd("silent! call nvim_buf_set_option(%d, 'filetype', 'leaderf')" % buf_number)
            def getWindow(number):
                for w in vim.windows:
                    if number == w.number:
                        return w
                return vim.current.window

            self._popup_instance.input_win = FloatWindow(winid, getWindow(int(lfEval("win_id2win(%d)" % winid))), vim.buffers[buf_number], vim.current.tabpage, line)

            show_stl = 0
            if lfEval("get(g:, 'Lf_PopupShowStatusline', 1)") == '1':
                show_stl = 1
                stl_win_config = {
                        "relative": "editor",
                        "anchor"  : "NW",
                        "height"  : 1,
                        "width"   : maxwidth,
                        "row"     : line + 1 + floatwin_height,
                        "col"     : col
                        }

                if self._stl_buffer_number == -1:
                    self._stl_buffer_number = int(lfEval("bufadd('')"))

                buf_number = self._stl_buffer_number
                lfCmd("silent let winid = nvim_open_win(%d, 0, %s)" % (buf_number, str(stl_win_config)))
                winid = int(lfEval("winid"))
                lfCmd("call nvim_buf_set_option(%d, 'buflisted', v:false)" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'buftype', 'nofile')" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'bufhidden', 'hide')" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'undolevels', -1)" % buf_number)
                lfCmd("call nvim_buf_set_option(%d, 'swapfile', v:false)" % buf_number)

                lfCmd("call nvim_win_set_option(%d, 'list', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'relativenumber', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'spell', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'foldenable', v:false)" % winid)
                lfCmd("call nvim_win_set_option(%d, 'foldmethod', 'manual')" % winid)
                try:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', 0)" % winid)
                except vim.error:
                    lfCmd("call nvim_win_set_option(%d, 'foldcolumn', '0')" % winid)
                # lfCmd("call nvim_win_set_option(%d, 'signcolumn', 'no')" % winid)
                lfCmd("call nvim_win_set_option(%d, 'cursorline', v:false)" % winid)
                if lfEval("exists('+cursorlineopt')") == '1':
                    lfCmd("call nvim_win_set_option(%d, 'cursorlineopt', 'both')" % winid)
                lfCmd("call nvim_win_set_option(%d, 'colorcolumn', '')" % winid)
                lfCmd("call nvim_win_set_option(%d, 'winhighlight', 'Normal:Lf_hl_popup_blank')" % winid)
                lfCmd("silent! call nvim_buf_set_option(%d, 'filetype', 'leaderf')" % buf_number)
                self._popup_instance.statusline_win = FloatWindow(winid, getWindow(int(lfEval("win_id2win(%d)" % winid))), vim.buffers[buf_number], vim.current.tabpage, line + 1 + floatwin_height)

            if "--recall" in self._arguments:
                self.refreshPopupStatusline()

            lfCmd("augroup Lf_Floatwin_Close")
            lfCmd("autocmd! WinEnter * call leaderf#closeAllFloatwin(%d, %d, %d, %d)" % (self._popup_instance.input_win.id,
                                                                                         self._popup_instance.content_win.id,
                                                                                         self._popup_instance.statusline_win.id if show_stl else -1,
                                                                                         show_stl))
            lfCmd("augroup END")
        else:
            self._win_pos = "popup"

            options = {
                    "maxwidth":        maxwidth,
                    "minwidth":        maxwidth,
                    "maxheight":       self._popup_maxheight,
                    "zindex":          20480,
                    "pos":             "topleft",
                    "line":            line + 1,      # there is an input window above
                    "col":             col,
                    "padding":         [0, 0, 0, 0],
                    "scrollbar":       0,
                    "mapping":         0,
                    "filter":          "leaderf#PopupFilter",
                    }

            lfCmd("silent noswapfile let winid = popup_create(%d, %s)" % (buf_number, str(options)))
            self._popup_winid = int(lfEval("winid"))
            lfCmd("call win_execute(%d, 'setlocal nobuflisted')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal buftype=nofile')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal bufhidden=hide')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal undolevels=-1')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal noswapfile')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal nolist')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal number norelativenumber')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal nospell')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal nofoldenable')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal foldmethod=manual')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal shiftwidth=4')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal cursorline')" % self._popup_winid)
            if lfEval("exists('+cursorlineopt')") == '1':
                lfCmd("call win_execute(%d, 'setlocal cursorlineopt=both')" % self._popup_winid)
            if lfEval("get(g:, 'Lf_PopupShowFoldcolumn', 1)") == '0':
                lfCmd("call win_execute(%d, 'setlocal foldcolumn=0')" % self._popup_winid)
            else:
                lfCmd("call win_execute(%d, 'setlocal foldcolumn=1')" % self._popup_winid)
            # lfCmd("call win_execute(%d, 'silent! setlocal signcolumn=no')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal colorcolumn=')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'setlocal wincolor=Lf_hl_popup_window')" % self._popup_winid)
            lfCmd("call win_execute(%d, 'silent! setlocal filetype=leaderf')" % self._popup_winid)

            self._tabpage_object = vim.current.tabpage
            self._buffer_object = vim.buffers[buf_number]
            self._window_object = PopupWindow(self._popup_winid, self._buffer_object, self._tabpage_object, line+1)
            self._popup_instance.content_win = self._window_object

            input_win_options = {
                    "maxwidth":        maxwidth,
                    "minwidth":        maxwidth,
                    "maxheight":       1,
                    "zindex":          20480,
                    "pos":             "topleft",
                    "line":            line,
                    "col":             col,
                    "scrollbar":       0,
                    "mapping":         0,
                    }

            if self._input_buffer_number == -1:
                self._input_buffer_number = int(lfEval("bufadd('')"))

            buf_number = self._input_buffer_number
            lfCmd("silent let winid = popup_create(%d, %s)" % (buf_number, str(input_win_options)))
            winid = int(lfEval("winid"))
            lfCmd("call win_execute(%d, 'setlocal nobuflisted')" % winid)
            lfCmd("call win_execute(%d, 'setlocal buftype=nofile')" % winid)
            lfCmd("call win_execute(%d, 'setlocal bufhidden=hide')" % winid)
            lfCmd("call win_execute(%d, 'setlocal undolevels=-1')" % winid)
            lfCmd("call win_execute(%d, 'setlocal noswapfile')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nolist')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nonumber norelativenumber')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nospell')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nofoldenable')" % winid)
            lfCmd("call win_execute(%d, 'setlocal foldmethod=manual')" % winid)
            lfCmd("call win_execute(%d, 'setlocal shiftwidth=4')" % winid)
            lfCmd("call win_execute(%d, 'setlocal nocursorline')" % winid)
            lfCmd("call win_execute(%d, 'setlocal foldcolumn=0')" % winid)
            # lfCmd("call win_execute(%d, 'silent! setlocal signcolumn=no')" % winid)
            lfCmd("call win_execute(%d, 'setlocal colorcolumn=')" % winid)
            lfCmd("call win_execute(%d, 'setlocal wincolor=Lf_hl_popup_inputText')" % winid)
            lfCmd("call win_execute(%d, 'silent! setlocal filetype=leaderf')" % winid)

            self._popup_instance.input_win = PopupWindow(winid, vim.buffers[buf_number], vim.current.tabpage, line)

            if lfEval("get(g:, 'Lf_PopupShowStatusline', 1)") == '1':
                statusline_win_options = {
                        "maxwidth":        maxwidth,
                        "minwidth":        maxwidth,
                        "maxheight":       1,
                        "zindex":          20480,
                        "pos":             "topleft",
                        "line":            line + 1 + self._window_object.height,
                        "col":             col,
                        "scrollbar":       0,
                        "mapping":         0,
                        }

                if self._stl_buffer_number == -1:
                    self._stl_buffer_number = int(lfEval("bufadd('')"))

                buf_number = self._stl_buffer_number
                lfCmd("silent let winid = popup_create(%d, %s)" % (buf_number, str(statusline_win_options)))
                winid = int(lfEval("winid"))
                lfCmd("call win_execute(%d, 'setlocal nobuflisted')" % winid)
                lfCmd("call win_execute(%d, 'setlocal buftype=nofile')" % winid)
                lfCmd("call win_execute(%d, 'setlocal bufhidden=hide')" % winid)
                lfCmd("call win_execute(%d, 'setlocal undolevels=-1')" % winid)
                lfCmd("call win_execute(%d, 'setlocal noswapfile')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nolist')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nonumber norelativenumber')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nospell')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nofoldenable')" % winid)
                lfCmd("call win_execute(%d, 'setlocal foldmethod=manual')" % winid)
                lfCmd("call win_execute(%d, 'setlocal shiftwidth=4')" % winid)
                lfCmd("call win_execute(%d, 'setlocal nocursorline')" % winid)
                lfCmd("call win_execute(%d, 'setlocal foldcolumn=0')" % winid)
                # lfCmd("call win_execute(%d, 'silent! setlocal signcolumn=no')" % winid)
                lfCmd("call win_execute(%d, 'setlocal colorcolumn=')" % winid)
                lfCmd("call win_execute(%d, 'setlocal wincolor=Lf_hl_popup_blank')" % winid)
                lfCmd("call win_execute(%d, 'silent! setlocal filetype=leaderf')" % winid)

                self._popup_instance.statusline_win = PopupWindow(winid, vim.buffers[buf_number], vim.current.tabpage, line + 1 + self._window_object.height)

            lfCmd("call leaderf#ResetPopupOptions(%d, 'callback', function('leaderf#PopupClosed', [%s, %d]))"
                    % (self._popup_winid, str(self._popup_instance.getWinIdList()), id(self._manager)))

        if not self._is_popup_colorscheme_autocmd_set:
            self._is_popup_colorscheme_autocmd_set = True
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')".format(self._category, lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))
            lfCmd("augroup Lf_Popup_{}_Colorscheme".format(self._category))
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#popup#load('{}', '{}')".format(self._category,
                    lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))
            lfCmd("autocmd VimResized * let g:Lf_Popup_VimResized = 1")
            lfCmd("augroup END")

    def _createBufWindow(self, win_pos):
        self._win_pos = win_pos
        lfCmd("let g:Lf_VimResized = 0")

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

        lfCmd("doautocmd WinEnter")

        self._tabpage_object = vim.current.tabpage
        self._window_object = vim.current.window
        self._initial_win_height = self._window_object.height
        if (self._reverse_order or lfEval("get(g:, 'Lf_AutoResize', 0)") == '1') and "--recall" not in self._arguments:
            self._window_object.height = 1

        if self._buffer_object is None or not self._buffer_object.valid:
            self._buffer_object = vim.current.buffer

        self._setAttributes()

        if not self._is_colorscheme_autocmd_set:
            self._is_colorscheme_autocmd_set = True
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')".format(self._category, lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))
            lfCmd("call leaderf#colorscheme#highlight('{}', {})".format(self._category, self._buffer_object.number))
            lfCmd("augroup Lf_{}_Colorscheme".format(self._category))
            lfCmd("autocmd!")
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlight('{}', {})".format(self._category, self._buffer_object.number))
            lfCmd("autocmd ColorScheme * call leaderf#colorscheme#highlightMode('{0}', g:Lf_{0}_StlMode)".format(self._category))
            lfCmd("autocmd ColorScheme <buffer> doautocmd syntax")
            lfCmd("autocmd CursorMoved <buffer> let g:Lf_{}_StlLineNumber = 1 + line('$') - line('.')".format(self._category))
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
            and self._window_object and self._window_object.valid and self._window_object.number != 0 # the number may be 0 although PopupWindow is valid because of popup_hide()
            and self._window_object.buffer == self._buffer_object):
            vim.current.tabpage = self._tabpage_object
            if self._win_pos == 'floatwin':
                vim.current.window = self._window_object.window
            else:
                vim.current.window = self._window_object
            self._after_enter()
            return True
        return False

    def setArguments(self, arguments):
        self._last_reverse_order = self._reverse_order
        self._arguments = arguments
        if self._arguments.get("--reverse", 1) is None:
            self._reverse_order = False
        else:
            if "--reverse" in self._arguments or lfEval("get(g:, 'Lf_ReverseOrder', 0)") == '1':
                self._reverse_order = True
            else:
                self._reverse_order = False

            if ("--popup" in self._arguments or lfEval("g:Lf_WindowPosition") == 'popup') \
                    and "--bottom" not in self._arguments: # popup does not support reverse order
                self._reverse_order = False

    def useLastReverseOrder(self):
        self._reverse_order = self._last_reverse_order

    def hideMimicCursor(self):
        lfCmd("""silent! call matchdelete(g:Lf_mimicedCursorId, %d)""" % self._popup_winid)

    def mimicCursor(self):
        if self._win_pos == 'popup' and self._manager._current_mode == 'NORMAL':
            if self._popup_winid > 0 and self._window_object.valid:
                self.hideMimicCursor()
                lfCmd("""call win_execute(%d, "let cursor_pos = getcurpos()[1:2]")""" % (self._popup_winid))
                lfCmd("""silent! call win_execute(%d, 'let g:Lf_mimicedCursorId = matchaddpos("Cursor", [cursor_pos])')""" % (self._popup_winid))

    def setPopupStl(self, current_mode):
        statusline_win = self._popup_instance.statusline_win
        if not statusline_win:
            return

        sep = lfEval("g:Lf_StlSeparator.left")
        sep_len = lfBytesLen(sep)
        match_mode = lfEval("g:Lf_{}_StlMode".format(self._category))
        cwd = lfEval("g:Lf_{}_StlCwd".format(self._category))

        text = " {} {} {} {} {} {} {} {}".format(current_mode, sep,
                                                 self._category, sep,
                                                 match_mode, sep,
                                                 cwd, sep
                                                 )
        if self._win_pos == 'popup':
            # prop_add() column starts from 1
            sep0_start = lfBytesLen(current_mode) + 3
        else:
            # nvim_buf_add_highlight() column starts from 0
            sep0_start = lfBytesLen(current_mode) + 2
        category_start = sep0_start + sep_len
        category_len = lfBytesLen(self._category) + 2
        sep1_start = category_start + category_len
        match_mode_start = sep1_start + sep_len
        match_mode_len = lfBytesLen(match_mode) + 2
        sep2_start = match_mode_start + match_mode_len
        cwd_start = sep2_start + sep_len
        cwd_len = lfBytesLen(cwd) + 2
        sep3_start = cwd_start + cwd_len

        if self._win_pos == 'popup':
            lfCmd("""call popup_settext(%d, '%s')""" % (statusline_win.id, escQuote(text)))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_mode'})")""" % (statusline_win.id, self._category))
            lfCmd("""call win_execute(%d, "call prop_add(1, 1, {'length': %d, 'type': 'Lf_hl_popup_%s_mode'})")"""
                    % (statusline_win.id, lfBytesLen(current_mode) + 2, self._category))

            if sep != "":
                lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_sep0'})")""" % (statusline_win.id, self._category))
                lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_%s_sep0'})")"""
                        % (statusline_win.id, sep0_start, sep_len, self._category))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_category'})")""" % (statusline_win.id))
            lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_category'})")"""
                    % (statusline_win.id, category_start, category_len))

            if sep != "":
                lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_sep1'})")""" % (statusline_win.id, self._category))
                lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_%s_sep1'})")"""
                        % (statusline_win.id, sep1_start, sep_len, self._category))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_matchMode'})")""" % (statusline_win.id, self._category))
            lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_%s_matchMode'})")"""
                    % (statusline_win.id, match_mode_start, match_mode_len, self._category))

            if sep != "":
                lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_sep2'})")""" % (statusline_win.id, self._category))
                lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_%s_sep2'})")"""
                        % (statusline_win.id, sep2_start, sep_len, self._category))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_cwd'})")""" % (statusline_win.id))
            lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_cwd'})")"""
                    % (statusline_win.id, cwd_start, cwd_len))

            if sep != "":
                lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_sep3'})")""" % (statusline_win.id, self._category))
                lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_%s_sep3'})")"""
                        % (statusline_win.id, sep3_start, sep_len, self._category))
        elif self._win_pos == 'floatwin':
            statusline_win.buffer[0] = text

            if self._stl_buf_namespace is None:
                self._stl_buf_namespace = int(lfEval("nvim_create_namespace('')"))
            else:
                lfCmd("call nvim_buf_clear_namespace(%d, %d, 0, -1)"
                        % (statusline_win.buffer.number, self._stl_buf_namespace))

            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_mode', 0, 0, %d)"
                    % (statusline_win.buffer.number, self._stl_buf_namespace, self._category,
                        lfBytesLen(current_mode) + 2))

            if sep != "":
                lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_sep0', 0, %d, %d)"
                        % (statusline_win.buffer.number, self._stl_buf_namespace, self._category,
                            sep0_start, sep0_start + sep_len))

            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_category', 0, %d, %d)"
                    % (statusline_win.buffer.number, self._stl_buf_namespace,
                        category_start, category_start + category_len))

            if sep != "":
                lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_sep1', 0, %d, %d)"
                        % (statusline_win.buffer.number, self._stl_buf_namespace, self._category,
                            sep1_start, sep1_start + sep_len))

            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_matchMode', 0, %d, %d)"
                    % (statusline_win.buffer.number, self._stl_buf_namespace, self._category,
                        match_mode_start, match_mode_start + match_mode_len))

            if sep != "":
                lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_sep2', 0, %d, %d)"
                        % (statusline_win.buffer.number, self._stl_buf_namespace, self._category,
                            sep2_start, sep2_start + sep_len))

            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_cwd', 0, %d, %d)"
                    % (statusline_win.buffer.number, self._stl_buf_namespace,
                        cwd_start, cwd_start + cwd_len))

            if sep != "":
                lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_sep3', 0, %d, %d)"
                        % (statusline_win.buffer.number, self._stl_buf_namespace, self._category,
                            sep3_start, sep3_start + sep_len))

    def setStlCategory(self, category):
        lfCmd("let g:Lf_{}_StlCategory = '{}'".format(self._category, category) )

    def setStlMode(self, mode):
        lfCmd("let g:Lf_{}_StlMode = '{}'".format(self._category, mode))
        if self._win_pos in ('popup', 'floatwin'):
            lfCmd("call leaderf#colorscheme#popup#hiMatchMode('{0}', g:Lf_{0}_StlMode)".format(self._category))
        else:
            lfCmd("call leaderf#colorscheme#highlightMode('{0}', g:Lf_{0}_StlMode)".format(self._category))

    def setStlCwd(self, cwd):
        lfCmd("let g:Lf_{}_StlCwd = '{}'".format(self._category, cwd))

    def setStlTotal(self, total):
        lfCmd("let g:Lf_{}_StlTotal = '{}'".format(self._category, total))

    def setStlResultsCount(self, count, check_ignored=False):
        if check_ignored and self._cur_buffer_name_ignored:
            count -= 1
        lfCmd("let g:Lf_{}_StlResultsCount = '{}'".format(self._category, count))
        if lfEval("has('nvim')") == '1' and self._win_pos != 'floatwin':
            lfCmd("redrawstatus")

        if self._win_pos in ('popup', 'floatwin'):
            self._cli.buildPopupPrompt()

    def setStlRunning(self, running):
        if self._win_pos in ('popup', 'floatwin'):
            if running:
                lfCmd("let g:Lf_{}_IsRunning = 1".format(self._category))
            else:
                lfCmd("let g:Lf_{}_IsRunning = 0".format(self._category))
            return

        if running:
            spin = "{}".format(self._cli._spin_symbols[self._running_status])
            self._running_status = (self._running_status + 1) % len(self._cli._spin_symbols)
            lfCmd("let g:Lf_{}_StlRunning = '{}'".format(self._category, spin))
        else:
            self._running_status = 0
            lfCmd("let g:Lf_{}_StlRunning = ''".format(self._category))

    def enterBuffer(self, win_pos, clear):
        if self._enterOpeningBuffer():
            return

        lfCmd("let g:Lf_{}_StlLineNumber = '1'".format(self._category))
        self._orig_pos = (vim.current.tabpage, vim.current.window, vim.current.buffer)
        self._orig_cursor = vim.current.window.cursor
        self._orig_buffer_name = os.path.normpath(lfDecode(vim.current.buffer.name))
        if lfEval("g:Lf_ShowRelativePath") == '1':
            try:
                self._orig_buffer_name = os.path.relpath(self._orig_buffer_name)
            except ValueError:
                pass
        self._orig_buffer_name = lfEncode(self._orig_buffer_name)

        self._before_enter()

        if win_pos in ('popup', 'floatwin'):
            if lfEval("exists('g:lf_gcr_stack')") == '0':
                lfCmd("let g:lf_gcr_stack = []")
            lfCmd("call add(g:lf_gcr_stack, &gcr)")
            lfCmd("set gcr=a:invisible")
            if lfEval("exists('g:lf_t_ve_stack')") == '0':
                lfCmd("let g:lf_t_ve_stack = []")
            lfCmd("call add(g:lf_t_ve_stack, &t_ve)")
            lfCmd("set t_ve=")
            self._orig_win_nr = vim.current.window.number
            self._orig_win_id = lfWinId(self._orig_win_nr)
            self._createPopupWindow(clear)
            self._arguments["popup_winid"] = self._popup_winid
        elif win_pos == 'fullScreen':
            self._orig_tabpage = vim.current.tabpage
            if len(vim.tabpages) < 2:
                lfCmd("set showtabline=0")
            self._createBufWindow(win_pos)
        else:
            self._orig_win_nr = vim.current.window.number
            self._orig_win_id = lfWinId(self._orig_win_nr)
            self._createBufWindow(win_pos)

        if not self._is_icon_colorscheme_autocmd_set:
            self._is_icon_colorscheme_autocmd_set = True
            if lfEval("get(g:, 'Lf_highlightDevIconsLoad', 0)") == '0' or lfEval("hlexists('Lf_hl_devIcons_c')") == '0':
                highlightDevIcons()
            lfCmd("augroup Lf_DevIcons_Colorscheme")
            lfCmd("autocmd! ColorScheme * call leaderf#highlightDevIcons()")
            lfCmd("augroup END")

        if lfEval("get(g:, 'Lf_DisableStl', 0)")=="0":
            self._setStatusline()
        self._after_enter()

    def exitBuffer(self):
        self._before_exit()

        if self._win_pos == 'popup':
            lfCmd("set gcr&")
            lfCmd("let &gcr = remove(g:lf_gcr_stack, -1)")
            lfCmd("set t_ve&")
            lfCmd("let &t_ve = remove(g:lf_t_ve_stack, -1)")
            self._popup_instance.hide()
            self._after_exit()
            return
        elif self._win_pos == 'floatwin':
            lfCmd("set gcr&")
            lfCmd("let &gcr = remove(g:lf_gcr_stack, -1)")
            lfCmd("set t_ve&")
            lfCmd("let &t_ve = remove(g:lf_t_ve_stack, -1)")
            self._popup_instance.close()
            if self._orig_win_id is not None:
                lfCmd("call win_gotoid(%d)" % self._orig_win_id)
            self._after_exit()
            return
        elif self._win_pos == 'fullScreen':
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
        columns = self._window_object.width - int(lfEval("&numberwidth")) - int(lfEval("&foldcolumn"))
        for i in buffer:
            try:
                num += (int(lfEval("strdisplaywidth('%s')" % escQuote(i))) + columns - 1)// columns
            except:
                num += (int(lfEval("strdisplaywidth('%s')" % escQuote(i).replace('\x00', '\x01'))) + columns - 1)// columns
        return num

    def setBuffer(self, content, need_copy=False):
        self._cur_buffer_name_ignored = False
        if self._ignore_cur_buffer_name:
            if self._win_pos == 'popup':
                end = self._popup_maxheight
            else:
                end = self._window_object.height
            orig_buffer_name = iconLine(self._orig_buffer_name)
            if orig_buffer_name in content[:end]:
                self._cur_buffer_name_ignored = True
                if need_copy:
                    content = content[:]
                content.remove(orig_buffer_name)
            elif os.name == 'nt':
                buffer_name = orig_buffer_name.replace('\\', '/')
                if buffer_name in content[:end]:
                    self._cur_buffer_name_ignored = True
                    if need_copy:
                        content = content[:]
                    content.remove(buffer_name)

        self.buffer.options['modifiable'] = True
        if lfEval("has('nvim')") == '1':
            if len(content) > 0 and len(content[0]) != len(content[0].rstrip("\r\n")):
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
                orig_row = self._window_object.cursor[0]
                self._buffer_object[:] = content

                if self._auto_resize and self._win_pos not in ('popup', 'floatwin'):
                    buffer_len = len(self._buffer_object)
                    if buffer_len < self._initial_win_height:
                        if "--nowrap" not in self._arguments:
                            self._window_object.height = min(self._initial_win_height, self._actualLength(self._buffer_object))
                        else:
                            self._window_object.height = buffer_len
                    elif self._window_object.height < self._initial_win_height:
                        self._window_object.height = self._initial_win_height

                    try:
                        self._window_object.cursor = (orig_row, 0)
                    except vim.error:
                        self._window_object.cursor = (1, 0)

                # I don't know how to minimize the steps to reproduce the issue,
                # I believe there must be a bug in vim
                if self._win_pos == 'popup':
                    self._orig_pos[1].options["foldmethod"] = self._orig_pos[1].options["foldmethod"]
        finally:
            self.refreshPopupStatusline()
            self.buffer.options['modifiable'] = False

    def refreshPopupStatusline(self):
        statusline_win = self._popup_instance.statusline_win
        buffer_len = len(self._buffer_object)
        if self._win_pos == 'popup':
            if "--nowrap" not in self._arguments:
                lfCmd("call leaderf#ResetPopupOptions(%d, 'minheight', %d)" % (self._popup_winid,
                    min(self._popup_maxheight, self._actualLength(self._buffer_object[:self._popup_maxheight]))))
            else:
                lfCmd("call leaderf#ResetPopupOptions(%d, 'minheight', %d)" % (self._popup_winid, min(self._popup_maxheight, buffer_len)))

            if statusline_win:
                expected_line = self._window_object.initialLine + self._window_object.height
                if expected_line != int(lfEval("popup_getpos(%d).line" % statusline_win.id)):
                    lfCmd("call leaderf#ResetPopupOptions(%d, 'line', %d)" % (statusline_win.id, expected_line))
        elif self._win_pos == 'floatwin':
            if buffer_len < self._popup_maxheight:
                if "--nowrap" not in self._arguments:
                    self._window_object.height = min(self._popup_maxheight, self._actualLength(self._buffer_object))
                else:
                    self._window_object.height = buffer_len

                if statusline_win:
                    expected_line = self._window_object.initialLine + self._window_object.height
                    if expected_line != int(float(lfEval("nvim_win_get_config(%d).row" % statusline_win.id))):
                        lfCmd("call leaderf#ResetFloatwinOptions(%d, 'row', %d)" % (statusline_win.id, expected_line))
            elif self._window_object.height < self._popup_maxheight:
                self._window_object.height = self._popup_maxheight

                if statusline_win:
                    expected_line = self._window_object.initialLine + self._window_object.height
                    if expected_line != int(float(lfEval("nvim_win_get_config(%d).row" % statusline_win.id))):
                        lfCmd("call leaderf#ResetFloatwinOptions(%d, 'row', %d)" % (statusline_win.id, expected_line))

    def appendBuffer(self, content):
        self.buffer.options['modifiable'] = True
        if lfEval("has('nvim')") == '1':
            if len(content) > 0 and len(content[0]) != len(content[0].rstrip("\r\n")):
                # NvimError: string cannot contain newlines
                content = [ line.rstrip("\r\n") for line in content ]

        try:
            if self._reverse_order:
                orig_row = self._window_object.cursor[0]
                orig_buf_len = len(self._buffer_object)

                if self.empty():
                    self._buffer_object[:] = content[::-1]
                else:
                    self._buffer_object.append(content[::-1], 0)
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
                orig_row = self._window_object.cursor[0]
                if self.empty():
                    self._buffer_object[:] = content
                else:
                    self._buffer_object.append(content)

                if self._auto_resize and self._win_pos not in ('popup', 'floatwin'):
                    buffer_len = len(self._buffer_object)
                    if buffer_len < self._initial_win_height:
                        if "--nowrap" not in self._arguments:
                            self._window_object.height = min(self._initial_win_height, self._actualLength(self._buffer_object))
                        else:
                            self._window_object.height = buffer_len
                    elif self._window_object.height < self._initial_win_height:
                        self._window_object.height = self._initial_win_height

                    try:
                        self._window_object.cursor = (orig_row, 0)
                    except vim.error:
                        self._window_object.cursor = (1, 0)

        finally:
            self.refreshPopupStatusline()
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
            self.setBuffer(content, need_copy=True)
            self.setStlTotal(len(content)//unit)
            self.setStlResultsCount(len(content)//unit, True)
            return content

        self.buffer.options['modifiable'] = True
        self._buffer_object[:] = []

        try:
            start = time.time()
            cur_content = []
            for line in content:
                cur_content.append(line)
                if time.time() - start > 0.1:
                    start = time.time()
                    if len(self._buffer_object) <= self._window_object.height:
                        self.setBuffer(cur_content, need_copy=True)
                        if self._reverse_order:
                            lfCmd("normal! G")

                    self.setStlRunning(True)
                    self.setStlTotal(len(cur_content)//unit)
                    self.setStlResultsCount(len(cur_content)//unit)
                    if self._win_pos not in ('popup', 'floatwin'):
                        lfCmd("redrawstatus")
            self.setBuffer(cur_content, need_copy=True)
            self.setStlTotal(len(self._buffer_object)//unit)
            self.setStlRunning(False)
            self.setStlResultsCount(len(self._buffer_object)//unit, True)
            if self._win_pos not in ('popup', 'floatwin'):
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
        if self._win_pos == 'popup':
            return self._buffer_object[self._window_object.cursor[0] - 1]
        else:
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
            lfCmd("keepj call win_gotoid(%d)" % self._orig_win_id)
        else:
            # 'silent!' is used to skip error E16.
            lfCmd("keepj silent! exec '%d wincmd w'" % self._orig_win_nr)

    def getWinPos(self):
        return self._win_pos

    def getPopupWinId(self):
        return self._popup_winid

    def getPopupInstance(self):
        return self._popup_instance

#  vim: set ts=4 sw=4 tw=0 et :
