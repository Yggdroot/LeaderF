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
from .mru import *


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

    def getContent(self, *args, **kwargs):
        pass

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
    def __init__(self, cmd, file_type, buffer_name, window_id):
        self._cmd = cmd
        self._file_type = file_type
        self._buffer_name = buffer_name
        self._window_id = window_id
        self._executor = AsyncExecutor()
        self._buffer = None
        self._reader_thread = None
        self._read_finished = False

    def create(self):
        self._content = []
        self._offset_in_content = 0
        self._read_finished = False
        self._stop_reader_thread = False

        # buf_exists = lfEval("bufexists('{}')".format(self._buffer_name)) == '1'
        lfCmd("call win_gotoid(%d)" % self._window_id)

        if self._buffer is not None:
            del self._buffer[:]

        lfCmd("noautocmd edit {}".format(self._buffer_name))

        if self._buffer is None:
            if self._file_type:
                lfCmd("setlocal filetype={}".format(self._file_type))

            lfCmd("setlocal nobuflisted")
            lfCmd("setlocal buftype=nofile")
            lfCmd("setlocal bufhidden=wipe")
            lfCmd("setlocal undolevels=-1")
            lfCmd("setlocal noswapfile")
            lfCmd("setlocal nospell")
            lfCmd("setlocal nomodifiable")
            lfCmd("setlocal nofoldenable")
            lfCmd("autocmd BufHidden,BufDelete,BufWipeout <buffer> call leaderf#Git#Cleanup(%d)" % id(self))

        self._buffer = vim.current.buffer

        content = self._executor.execute(self._cmd, encoding=lfEval("&encoding"))

        self._timer_id = lfEval("timer_start(100, function('leaderf#Git#TimerCallback', [%d]), {'repeat': -1})" % id(self))

        self._stop_reader_thread = False
        self._reader_thread = threading.Thread(target=self._readContent, args=(content,))
        self._reader_thread.daemon = True
        self._reader_thread.start()

    def writeBuffer(self):
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

        if self._read_finished and self._offset_in_content == len(self._content):
            self.stopTimer()

    def _readContent(self, content):
        try:
            for line in content:
                self._content.append(line)
                if self._stop_reader_thread:
                    break
            else:
                self._read_finished = True
        except Exception as e:
            self._read_finished = True
            lfPrintError(e)

    def stopTimer(self):
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None

    def cleanup(self):
        self._executor.killProcess()
        self._stop_reader_thread = True
        self.stopTimer()

#*****************************************************
# GitExplManager
#*****************************************************
class GitExplManager(Manager):
    def __init__(self):
        super(GitExplManager, self).__init__()
        self._diff_view = None

    def _getExplClass(self):
        return GitExplorer

    def _defineMaps(self):
        pass

    def _createWindow(self, win_pos):
        if win_pos == 'top':
            lfCmd("silent! noa keepa keepj abo sp")
        elif win_pos == 'bottom':
            lfCmd("silent! noa keepa keepj bel sp")
        elif win_pos == 'left':
            lfCmd("silent! noa keepa keepj abo vsp")
        elif win_pos == 'right':
            lfCmd("silent! noa keepa keepj bel vsp")
        else:
            pass

        return int(lfEval("win_getid()"))

    def startGitDiff(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--directly" in arguments_dict:
            winid = self._createWindow(arguments_dict.get("--position", ["top"])[0])
            cmd = "git diff "
            if "--cached" in arguments_dict:
                cmd += "--cached"
            self._diff_view = GitCommandView(cmd, "diff", "LeaderF://git/diff", winid)
            self._diff_view.create()

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


#*****************************************************
# gitExplManager is a singleton
#*****************************************************
gitExplManager = GitExplManager()

__all__ = ['gitExplManager']
