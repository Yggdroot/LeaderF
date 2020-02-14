#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import re
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


# *****************************************************
# WindowExplorer
# *****************************************************
class WindowExplorer(Explorer):
    def __init__(self):
        self._content = []

    def getContent(self, *args, **kwargs):
        lines = []
        self._max_bufname_len = self._get_max_bufname_len()

        for tab in vim.tabpages:

            for win in tab.windows:
                buf = win.buffer
                bufnr = buf.number
                buf_name = buf.name

                if not buf_name:
                    buf_name = "[No Name]"
                if lfEval("g:Lf_ShowRelativePath") == "1":
                    buf_name = lfRelpath(buf_name)

                basename = getBasename(buf_name)
                dirname = getDirname(buf_name)

                space_num = self._max_bufname_len - int(
                    lfEval("strdisplaywidth('%s')" % escQuote(basename))
                )

                # e,g,. ` 1  1 %+- windowExpl.py ".\"`
                lines.append(
                    '{:>2d} {:>2d} {:1s}{:1s}{:1s} {:s}{:s} "{:s}"'.format(
                        tab.number,
                        win.number,
                        "%"
                        if int(lfEval("bufnr('%')")) == bufnr
                        else "#"
                        if int(lfEval("bufnr('#')")) == bufnr
                        else "",
                        "+" if buf.options["modified"] else "",
                        "-" if not buf.options["modifiable"] else "",
                        basename,
                        " " * space_num,
                        dirname if dirname else "." + os.sep,
                    )
                )
        return lines

    def getStlCategory(self):
        return "Window"

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return True

    def _get_max_bufname_len(self):
        bufnr_list = []
        for tab in vim.tabpages:
            bufnr_list.extend(
                [int(nr) for nr in lfEval("tabpagebuflist('{}')".format(tab.number))]
            )

        return max(
            [
                int(
                    lfEval(
                        "strdisplaywidth('{}')".format(
                            escQuote(getBasename(vim.buffers[nr].name))
                        )
                    )
                )
                for nr in bufnr_list
            ]
            + [len("[No Name]")]
            or [0]
        )


# *****************************************************
# WindowExplManager
# *****************************************************
class WindowExplManager(Manager):
    def __init__(self):
        super(WindowExplManager, self).__init__()
        self._prefix_len = 10

    def _getExplClass(self):
        return WindowExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Window#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        match = re.search(r"^\s?(\d+) \s?(\d+)", line)

        tab = match.group(1)
        win = match.group(2)

        # jump
        lfCmd("{}tabnext".format(tab))
        lfCmd("{}wincmd w".format(win))

    def _createHelp(self):
        help = []
        help.append('" <CR>/o : goto window under cursor')
        help.append('" q : quit')
        help.append('" i : switch to input mode')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

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

        pref_len = self._prefix_len
        if mode == 0:
            return line[pref_len:]
        elif mode == 1:
            return line[pref_len: line.find(' "', pref_len)].strip()
        else:
            start_pos = line.find(' "')
            return line[start_pos+2:-1]

    def _getDigestStartPos(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return 0

        pref_len = self._prefix_len
        if mode == 0:
            return pref_len
        elif mode == 1:
            return pref_len
        else:
            start_pos = line.find(' "')
            return lfBytesLen(line[:start_pos+3])

    def _afterEnter(self):
        super(WindowExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == "popup":
            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_winNumber'', ''^\v\s?\zs\d+'')')"""
                % self._getInstance().getPopupWinId()
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_winNumber'', ''^\v\s?\d+ \s?\zs\d+'')')"""
                % self._getInstance().getPopupWinId()
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_winIndicators'', ''^\v\s?\d+ \s?\d+\s*\zs[#%%]=..\ze '')')"""
                % self._getInstance().getPopupWinId()
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_winModified'', ''^\v\s?\d+ \s?\d+\s*[#%%]=\+. \zs.*$'')')"""
                % self._getInstance().getPopupWinId()
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_winNomodifiable'', ''^\v\s?\d+ \s?\d+\s*[#%%]=.- \zs.*$'')')"""
                % self._getInstance().getPopupWinId()
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_winDirname'', '' \zs".*"$'')')"""
                % self._getInstance().getPopupWinId()
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval(r"matchadd('Lf_hl_winNumber',       '^\v\s?\zs\d+')"))
            self._match_ids.append(id)
            id = int(
                lfEval(r"matchadd('Lf_hl_winNumber',       '^\v\s?\d+ \s?\zs\d+')")
            )
            self._match_ids.append(id)
            id = int(
                lfEval(
                    r"matchadd('Lf_hl_winIndicators',   '^\v\s?\d+ \s?\d+\s*\zs[#%%]=..\ze ')"
                )
            )
            self._match_ids.append(id)
            id = int(
                lfEval(
                    r"matchadd('Lf_hl_winModified',     '^\v\s?\d+ \s?\d+\s*[#%%]=\+. \zs.*$')"
                )
            )
            self._match_ids.append(id)
            id = int(
                lfEval(
                    r"matchadd('Lf_hl_winNomodifiable', '^\v\s?\d+ \s?\d+\s*[#%%]=.- *\zs.*$')"
                )
            )
            self._match_ids.append(id)
            id = int(lfEval(r"""matchadd('Lf_hl_winDirname', ' \zs".*"$')"""))
            self._match_ids.append(id)


# *****************************************************
# windowExplManager is a singleton
# *****************************************************
windowExplManager = WindowExplManager()

__all__ = ["windowExplManager"]
