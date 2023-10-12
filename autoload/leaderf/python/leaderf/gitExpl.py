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

def workingDirectory(func):
    @wraps(func)
    def deco(self, *args, **kwargs):
        if self._getExplorer()._cmd_work_dir == lfGetCwd():
            return func(self, *args, **kwargs)

        # https://github.com/neovim/neovim/issues/8336
        if lfEval("has('nvim')") == '1':
            chdir = vim.chdir
        else:
            chdir = os.chdir
        orig_cwd = lfGetCwd()
        chdir(self._getExplorer()._cmd_work_dir)
        try:
            return func(self, *args, **kwargs)
        finally:
            chdir(orig_cwd)

    return deco


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
    def __init__(self, cmd, cmd_type, buffer_name, window_id):
        self._cmd = cmd
        self._cmd_type = cmd_type
        self._buffer_name = buffer_name
        self._window_id = window_id
        self._executor = AsyncExecutor()
        self._buffer = None

    def create(self):
        lfCmd("call win_gotoid(%d)" % self._window_id)
        buf_exists = lfEval("bufexists('{}')".format(self._buffer_name)) == '1'

        if self._buffer is not None:
            del self._buffer[:] # ignore autocmd ?

        lfCmd("noautocmd edit {}".format(self._buffer_name))

        if self._buffer is None:
            if self._cmd_type == "diff":
                lfCmd("setlocal filetype=diff")

            lfCmd("setlocal nobuflisted")
            lfCmd("setlocal buftype=nofile")
            lfCmd("setlocal bufhidden=hide")
            lfCmd("setlocal undolevels=-1")
            lfCmd("setlocal noswapfile")
            lfCmd("setlocal nospell")
            lfCmd("setlocal nomodifiable")
            lfCmd("setlocal nofoldenable")

        self._buffer = vim.current.buffer

    def cleanup(self):
        self._executor.killProcess()

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
            self._diff_view = GitCommandView(........)

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
