#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import tempfile
import json
from functools import wraps
from .utils import *
from .explorer import *
from .manager import *
from .devicons import (
    webDevIconsGetFileTypeSymbol,
    removeDevIcons,
    matchaddDevIconsDefault,
    matchaddDevIconsExact,
    matchaddDevIconsExtension,
)

#*****************************************************
# GitExplorer
#*****************************************************
class GitExplorer(Explorer):
    def __init__(self):
        self._executor = []
        self._pattern_regex = []
        self._context_separator = "..."
        self._display_multi = False
        self._cmd_work_dir = ""
        self._show_icon = lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1"

    def getContent(self, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        arg_list = arguments_dict.get("arg_line", 'git').split(maxsplit=2)
        if len(arg_list) == 1:
            return

        executor = AsyncExecutor()
        self._executor.append(executor)

        subcommand = arg_list[1]
        if subcommand == "diff":
            cmd = "git diff --name-status"
            if "--cached" in arguments_dict:
                cmd += " --cached"
            content = executor.execute(cmd, encoding=lfEval("&encoding"), format_line=self.formatLine)
            return content

    def formatLine(self, line):
        """
        R098    README.txt      README.txt.hello
        A       abc.txt
        M       src/fold.c
        """
        name_status = line.split('\t')
        file_name = name_status[1]
        icon = webDevIconsGetFileTypeSymbol(file_name) if self._show_icon else ""
        return "{:<4} {}{}{}".format(name_status[0], icon, name_status[1],
                                     " -> " + name_status[2] if len(name_status) == 3 else "")

    def getStlCategory(self):
        return 'Git'

    def getStlCurDir(self):
        return escQuote(lfEncode(self._cmd_work_dir))

    def supportsNameOnly(self):
        return False

    def cleanup(self):
        for exe in self._executor:
            exe.killProcess()
        self._executor = []

    def getPatternRegex(self):
        return self._pattern_regex

    def getContextSeparator(self):
        return self._context_separator

    def displayMulti(self):
        return self._display_multi


class GitCommandView(object):
    def __init__(self, owner, cmd, file_type, buffer_name, window_id):
        self._owner = owner
        self._cmd = cmd
        self._file_type = file_type
        self._buffer_name = buffer_name
        self._window_id = window_id
        self._executor = AsyncExecutor()
        self._buffer = None
        self.init()
        owner.register(self)

    def init(self):
        self._content = []
        self._reader_thread = None
        self._offset_in_content = 0
        self._read_finished = 0
        self._stop_reader_thread = False

    def getBufferName(self):
        return self._buffer_name

    def create(self):
        if self._buffer is not None:
            self._buffer.options['modifiable'] = True
            del self._buffer[:]
            self._buffer.options['modifiable'] = False
            self.cleanup()

        self.init()

        lfCmd("call win_execute({}, 'let cur_buf_number = bufnr()')".format(self._window_id))

        if self._file_type:
            lfCmd("call win_execute({}, 'setlocal filetype={}')".format(self._window_id, self._file_type))

        if self._buffer is None:
            lfCmd("call win_execute({}, 'setlocal nobuflisted')".format(self._window_id))
            lfCmd("call win_execute({}, 'setlocal buftype=nofile')".format(self._window_id))
            lfCmd("call win_execute({}, 'setlocal bufhidden=wipe')".format(self._window_id))
            lfCmd("call win_execute({}, 'setlocal undolevels=-1')".format(self._window_id))
            lfCmd("call win_execute({}, 'setlocal noswapfile')".format(self._window_id))
            lfCmd("call win_execute({}, 'setlocal nospell')".format(self._window_id))
            lfCmd("call win_execute({}, 'setlocal nomodifiable')".format(self._window_id))
            lfCmd("call win_execute({}, 'setlocal nofoldenable')".format(self._window_id))
            lfCmd("call win_execute({}, 'autocmd BufWipeout <buffer> call leaderf#Git#Suicide({})')".format(self._window_id, id(self)))

        self._buffer = vim.buffers[int(lfEval("cur_buf_number"))]

        content = self._executor.execute(self._cmd, encoding=lfEval("&encoding"))

        self._timer_id = lfEval("timer_start(100, function('leaderf#Git#WriteBuffer', [%d]), {'repeat': -1})" % id(self))

        self._reader_thread = threading.Thread(target=self._readContent, args=(content,))
        self._reader_thread.daemon = True
        self._reader_thread.start()

    def writeBuffer(self):
        if self._read_finished == 2:
            return

        if not self._buffer.valid:
            self.stopTimer()
            return

        self._buffer.options['modifiable'] = True
        try:
            cur_len = len(self._content)
            if cur_len > self._offset_in_content:
                if self._offset_in_content == 0:
                    self._buffer[:] = self._content[:cur_len]
                else:
                    self._buffer.append(self._content[self._offset_in_content:cur_len])

                self._offset_in_content = cur_len
        finally:
            self._buffer.options['modifiable'] = False

        if self._read_finished == 1 and self._offset_in_content == len(self._content):
            self._read_finished = 2
            self.stopTimer()

    def _readContent(self, content):
        try:
            for line in content:
                self._content.append(line)
                if self._stop_reader_thread:
                    break
            else:
                self._read_finished = 1
        except Exception as e:
            self._read_finished = 1
            lfPrintError(e)

    def stopThread(self):
        if self._reader_thread and self._reader_thread.is_alive():
            self._stop_reader_thread = True
            self._reader_thread.join()

    def stopTimer(self):
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None

    def cleanup(self):
        self._executor.killProcess()
        self.stopTimer()
        self.stopThread()

    def suicide(self):
        self._owner.deregister(self)
        self.cleanup()

#*****************************************************
# GitExplManager
#*****************************************************
class GitExplManager(Manager):
    def __init__(self):
        super(GitExplManager, self).__init__()
        self._views = {}

    def register(self, view):
        self._views[view.getBufferName()] = view

    def deregister(self, view):
        name = view.getBufferName()
        if name in self._views:
            del self._views[name]

    def _getExplClass(self):
        return GitExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Git#Maps()")

    def _createWindow(self, win_pos, buffer_name):
        if win_pos == 'top':
            lfCmd("silent! noa keepa keepj abo sp {}".format(buffer_name))
        elif win_pos == 'bottom':
            lfCmd("silent! noa keepa keepj bel sp {}".format(buffer_name))
        elif win_pos == 'left':
            lfCmd("silent! noa keepa keepj abo vsp {}".format(buffer_name))
        elif win_pos == 'right':
            lfCmd("silent! noa keepa keepj bel vsp {}".format(buffer_name))
        else:
            pass

        return int(lfEval("win_getid()"))

    def _workInIdle(self, content=None, bang=False):
        for v in self._views.values():
            v.writeBuffer()

        super(GitExplManager, self)._workInIdle(content, bang)

    def _afterEnter(self):
        super(GitExplManager, self)._afterEnter()

        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
            winid = self._getInstance().getPopupWinId() if self._getInstance().getWinPos() == 'popup' else None
            icon_pattern = r'^\S*\s*\zs__icon__'
            self._match_ids.extend(matchaddDevIconsExtension(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsExact(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsDefault(icon_pattern, winid))

    def _beforeExit(self):
        super(GitExplManager, self)._beforeExit()

    def startGitDiff(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--directly" in arguments_dict:
            cmd = "git diff"
            if "--cached" in arguments_dict:
                cmd += " --cached"

            if ("--current-file" in arguments_dict
                and vim.current.buffer.name
                and not vim.current.buffer.options['bt']):
                cmd += " -- {}".format(vim.current.buffer.name)

            if "extra" in arguments_dict:
                cmd += " " + " ".join(arguments_dict["extra"])

            buffer_name = "LeaderF://" + cmd
            if buffer_name in self._views:
                self._views[buffer_name].create()
            else:
                winid = self._createWindow(arguments_dict.get("--position", ["top"])[0], buffer_name)
                diff_view = GitCommandView(self, cmd, "diff", buffer_name, winid)
                diff_view.create()
        elif "--tree" in arguments_dict:
            pass
        else:
            super(GitExplManager, self).startExplorer(win_pos, *args, **kwargs)


    def startGitLog(self, win_pos, *args, **kwargs):
        pass

    def startGitBlame(self, win_pos, *args, **kwargs):
        pass

    def startExplorer(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        arg_list = arguments_dict.get("arg_line", 'git').split(maxsplit=2)
        if len(arg_list) == 1:
            return

        subcommand = arg_list[1]
        if subcommand == "diff":
            self.startGitDiff(win_pos, *args, **kwargs)
        elif subcommand == "log":
            self.startGitLog(win_pos, *args, **kwargs)
        elif subcommand == "blame":
            self.startGitBlame(win_pos, *args, **kwargs)

    def _bangEnter(self):
        super(GitExplManager, self)._bangEnter()

        if lfEval("exists('*timer_start')") == '0':
            lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
            return

        self._callback(bang=True)
        if self._read_finished < 2:
            self._timer_id = lfEval("timer_start(10, 'leaderf#Git#TimerCallback', {'repeat': -1})")

    def _getFineName(self, line):
        return line.split()[2]

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0 or args[0] == '':
            return

        line = args[0]
        filename = self._getFineName(line)

        self._createPopupPreview("", filename, 0)

    def _createPreviewWindow(self, config, source, line_num, jump_cmd):
        self._preview_config = config
        filename = source

        if lfEval("has('nvim')") == '1':
            lfCmd("noautocmd let g:Lf_preview_scratch_buffer = nvim_create_buf(0, 1)")
            self._preview_winid = int(lfEval("nvim_open_win(g:Lf_preview_scratch_buffer, 0, %s)" % str(config)))
            diff_view = GitCommandView(self, "git diff", "diff", 'aa', self._preview_winid)
            diff_view.create()

            # cur_winid = lfEval("win_getid()")
            # lfCmd("noautocmd call win_gotoid(%d)" % self._preview_winid)
            # if not isinstance(source, int):
            #     lfCmd("silent! doautocmd filetypedetect BufNewFile %s" % source)
            # lfCmd("noautocmd call win_gotoid(%s)" % cur_winid)

            self._setWinOptions(self._preview_winid)
            self._preview_filetype = lfEval("getbufvar(winbufnr(%d), '&ft')" % self._preview_winid)
        else:
            lfCmd("noautocmd silent! let winid = popup_create([], %s)" % json.dumps(config))
            self._preview_winid = int(lfEval("winid"))
            diff_view = GitCommandView(self, "git diff", "diff", 'aa', self._preview_winid)
            diff_view.create()

            # lfCmd("call win_execute(winid, 'silent! doautocmd filetypedetect BufNewFile %s')" % escQuote(filename))

            self._setWinOptions(self._preview_winid)
            self._preview_filetype = lfEval("getbufvar(winbufnr(winid), '&ft')")


#*****************************************************
# gitExplManager is a singleton
#*****************************************************
gitExplManager = GitExplManager()

__all__ = ['gitExplManager']
