#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *
from .asyncExecutor import AsyncExecutor


"""
let g:Lf_Extensions = {
    \ "apple": {
    \       "source": [], "git ls-files", funcref (...)
    \       "format": funcref ([], ...),
    \       "accept": funcref (line, ...),
    \       "options": [],
    \       "preview": funcref,
    \       "supports_name_only": 0,
    \       "get_digest": funcref (line, mode),
    \       "before_enter": funcref (...),
    \       "after_enter": funcref (orig_buf_nr, orig_cursor, ...),
    \       "bang_enter": funcref (orig_buf_nr, orig_cursor, ...),
    \       "before_exit": funcref (orig_buf_nr, orig_cursor, ...),
    \       "after_exit": funcref (...),
    \       "highlights_def": {
    \               "Lf_hl_apple": '^\s*\zs\d\+',
    \               "Lf_hl_appleId": '\d\+$',
    \       },
    \       "highlights_cmd": [
    \               "hi Lf_hl_apple guifg=red",
    \               "hi Lf_hl_appleId guifg=green",
    \       ],
    \       "supports_multi": 0,
    \       "supports_refine": 0,
    \ },
    \ "orange": {}
\}
"""
#*****************************************************
# AnyExplorer
#*****************************************************
class AnyExplorer(Explorer):
    def __init__(self):
        self._executor = []

    def setConfig(self, category, config):
        self._category, self._config = category, config

    def getContent(self, *args, **kwargs):
        source = self._config.get("source")
        if not source:
            return None

        if isinstance(source, vim.List):
            result = list(lfEncode(lfBytes2Str(line)) for line in source)
        elif isinstance(source, vim.Function):
            result = list(lfBytes2Str(line) for line in list(source(*kwargs["options"])))
        elif type(source) == type(b"string"): # "grep -r '%s' *"
            executor = AsyncExecutor()
            self._executor.append(executor)
            source = lfBytes2Str(source)
            if re.search(r'\brg\b|\bag\b|\bpt\b|\bfd\b|\bgit\b', source): # encoding of output is utf-8
                result = executor.execute(source, encoding=lfEval("&encoding"))
            else: # buildin command such as dir, grep ...
                result = executor.execute(source)
        else:
            return None

        format = self._config.get("format")
        if format:
            result = list(format(list(result), *kwargs["options"]))

        return result

    def getStlCategory(self):
        return self._category

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return bool(self._config.get("supports_name_only", False))

    def supportsMulti(self):
        return bool(self._config.get("supports_multi", False))


#*****************************************************
# AnyExplManager
#*****************************************************
class AnyExplManager(Manager):
    def __init__(self, category, config):
        super(AnyExplManager, self).__init__()
        self._getExplorer().setConfig(category, config)
        self._category = category
        self._config = config
        self._match_ids = []

    def _getExplClass(self):
        return AnyExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Any#Maps('%s')" % self._category)

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        accept = self._config.get("accept")
        if accept:
            accept(line, *self._options)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return ""

        get_digest = self._config.get("get_digest")
        if get_digest:
            return lfBytes2Str(get_digest(line, mode)[0])
        else:
            return super(AnyExplManager, self)._getDigest(line, mode)

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

        get_digest = self._config.get("get_digest")
        if get_digest:
            return int(get_digest(line, mode)[1])
        else:
            return super(AnyExplManager, self)._getDigestStartPos(line, mode)

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q/<Esc> : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _beforeEnter(self):
        super(AnyExplManager, self)._beforeEnter()
        before_enter = self._config.get("before_enter")
        if before_enter:
            before_enter(*self._options)

    def _afterEnter(self):
        super(AnyExplManager, self)._afterEnter()
        after_enter = self._config.get("after_enter")
        if after_enter:
            orig_buf_nr = self._getInstance().getOriginalPos()[2].number
            line, col = self._getInstance().getOriginalCursor()
            after_enter(orig_buf_nr, [line, col+1], *self._options)

        highlights_cmd = self._config.get("highlights_cmd", [])
        for cmd in highlights_cmd:
            lfCmd(cmd)
        highlights_def = self._config.get("highlights_def", {})
        for group, pattern in highlights_def.items():
            id = int(lfEval("matchadd('%s', '%s')" %
                        (lfBytes2Str(group), escQuote(lfBytes2Str(pattern)))))
            self._match_ids.append(id)

    def _bangEnter(self):
        bang_enter = self._config.get("bang_enter")
        if bang_enter:
            orig_buf_nr = self._getInstance().getOriginalPos()[2].number
            line, col = self._getInstance().getOriginalCursor()
            bang_enter(orig_buf_nr, [line, col+1], *self._options)

    def _beforeExit(self):
        super(AnyExplManager, self)._beforeExit()
        before_exit = self._config.get("before_exit")
        if before_exit:
            orig_buf_nr = self._getInstance().getOriginalPos()[2].number
            line, col = self._getInstance().getOriginalCursor()
            before_exit(orig_buf_nr, [line, col+1], *self._options)

        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def _afterExit(self):
        super(AnyExplManager, self)._afterExit()
        after_exit = self._config.get("after_exit")
        if after_exit:
            after_exit(*self._options)

    def _supportsRefine(self):
        return bool(self._config.get("supports_refine", False))

    def startExplorer(self, win_pos, *args, **kwargs):
        self._options = kwargs["options"]
        super(AnyExplManager, self).startExplorer(win_pos, *args, **kwargs)


class AnyHub(object):
    def __init__(self):
        self._managers = {}

    def start(self, category, *args, **kwargs):
        self._extensions = vim.bindeval("g:Lf_Extensions")
        if category in self._extensions:
            if category not in self._managers:
                self._managers[category] = AnyExplManager(category, self._extensions[category])
            manager = self._managers[category]
        else:
            if category == "file":
                from .fileExpl import fileExplManager
                manager = fileExplManager
            elif category == "buffer":
                from .bufExpl import bufExplManager
                manager = bufExplManager
            elif category == "mru":
                from .mruExpl import mruExplManager
                manager = mruExplManager
                kwargs["cb_name"] = vim.current.buffer.name
            elif category == "tag":
                from .tagExpl import tagExplManager
                manager = tagExplManager
            elif category == "bufTag":
                from .bufTagExpl import bufTagExplManager
                manager = bufTagExplManager
            elif category == "function":
                from .functionExpl import functionExplManager
                manager = functionExplManager
            elif category == "line":
                from .lineExpl import lineExplManager
                manager = lineExplManager
            elif category == "cmdHistory":
                from .historyExpl import historyExplManager
                manager = historyExplManager
                kwargs["history"] = "cmd"
            elif category == "searchHistory":
                from .historyExpl import historyExplManager
                manager = historyExplManager
                kwargs["history"] = "search"
            elif category == "help":
                from .helpExpl import helpExplManager
                manager = helpExplManager
            elif category == "colorscheme":
                from .colorschemeExpl import colorschemeExplManager
                manager = colorschemeExplManager

        positions = {"--top", "--bottom", "--left", "--right", "--belowright", "--aboveleft", "--fullScreen"}
        win_pos = "--" + lfEval("g:Lf_WindowPosition")
        for i in kwargs["options"]:
            if i in positions:
                win_pos = i
                kwargs["options"].remove(i)
                break

        if "--cword" in kwargs["options"]:
            kwargs["options"].remove("--cword")
            kwargs["pattern"] = lfEval("expand('<cword>')")

        manager.startExplorer(win_pos[2:], *args, **kwargs)


#*****************************************************
# anyHub is a singleton
#*****************************************************
anyHub = AnyHub()

__all__ = ['anyHub']
