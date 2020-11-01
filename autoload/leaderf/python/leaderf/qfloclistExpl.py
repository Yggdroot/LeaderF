#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from .utils import *
from .explorer import *
from .manager import *

#*****************************************************
# QfLocListExplorer
#*****************************************************
class QfLocListExplorer(Explorer):
    def __init__(self):
        self._list_type = "QuickFix"

    def getContent(self, *args, **kwargs):
        return self.getFreshContent(*args, **kwargs)

    def getFreshContent(self, *args, **kwargs):
        if "list_type" not in kwargs:
            return []

        if kwargs.get("list_type") == "loclist":
            self._list_type = "LocList"
            cmd = 'getloclist(0)'
        else:
            self._list_type = "QuickFix"
            cmd = 'getqflist()'
        return lfEval(
            """map({}, 'bufname(v:val.bufnr) . ":" . v:val.lnum . ":" . v:val.col . ":" . v:val.text')""".format(cmd)
        )

    def getStlCategory(self):
        return self._list_type

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))

    def supportsNameOnly(self):
        return True

    def getListType(self):
        return self._list_type


# *****************************************************
# QfLocListExplManager
# *****************************************************
class QfLocListExplManager(Manager):
    def __init__(self):
        super(QfLocListExplManager, self).__init__()

    def _getExplClass(self):
        return QfLocListExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#QfLocList#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]

        m = re.match(r'^(.+?):(\d+):(\d+):', line)
        file, line_num, col = m.group(1, 2, 3)

        try:
            if not os.path.isabs(file):
                file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
                file = os.path.normpath(lfEncode(file))

            if kwargs.get("mode", '') == 't':
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    lfDrop('tab', file)
                else:
                    lfCmd("tabe %s" % escSpecial(file))
            else:
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    lfDrop('', file)
                else:
                    lfCmd("hide edit %s" % escSpecial(file))
            lfCmd("call cursor(%s, %s)" % (line_num, col))
            lfCmd("norm! zv")
            lfCmd("norm! zz")
        except vim.error: # E37
            lfPrintTraceback()

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path (ilne)
                  1, return the name only (text)
                  2, return the directory name (filepath)
        """
        if len(line) == 0:
            return line

        if mode == 0:
            # line
            return line
        elif mode == 1:
            # text
            return line.split(":", 3)[3]
        else:
            # filepath
            return line.split(":", 3)[0]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if len(line) == 0:
            return 0

        if mode == 0:
            # line
            return 0
        elif mode == 1:
            # text
            m = re.match(r"^.+?:\d+:\d+:", line)
            if m:
                return lfBytesLen(m.group())
            return 0
        else:
            # filepath
            return lfBytesLen(line.split(":")[0])

    def _afterEnter(self):
        super(QfLocListExplManager, self)._afterEnter()

        list_type = self._getExplorer().getListType().lower()

        if self._getInstance().getWinPos() == "popup":
            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_%sFileName'', ''^.\{-}:\ze\d\+:'')')"""
                % (self._getInstance().getPopupWinId(), list_type)
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)

            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_%sLineNumber'', ''^.\{-}:\zs\d\+:'')')"""
                % (self._getInstance().getPopupWinId(), list_type)
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)

            lfCmd(
                r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_%sColumnNumber'', ''^.\{-}:\d\+:\zs\d\+:'')')"""
                % (self._getInstance().getPopupWinId(), list_type)
            )
            id = int(lfEval("matchid"))
            self._match_ids.append(id)

        else:
            id = int(
                lfEval(r"""matchadd('Lf_hl_%sFileName', '^.\{-}:\ze\d\+:')""" % list_type)
            )
            self._match_ids.append(id)

            id = int(
                lfEval(r"""matchadd('Lf_hl_%sLineNumber', '^.\{-}:\zs\d\+:')""" % list_type)
            )
            self._match_ids.append(id)

            id = int(
                lfEval(r"""matchadd('Lf_hl_%sColumnNumber', '^.\{-}:\d\+:\zs\d\+:')""" % list_type)
            )
            self._match_ids.append(id)

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" p : preview the result')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]

        m = re.match(r'^(.+?):(\d+):', line)
        file, line_num = m.group(1, 2)

        if not os.path.isabs(file):
            file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
            file = os.path.normpath(lfEncode(file))

        if lfEval("bufloaded('%s')" % escQuote(file)) == '1':
            source = int(lfEval("bufadd('%s')" % escQuote(file)))
        else:
            source = file
        self._createPopupPreview("", source, line_num)


# *****************************************************
# qfloclistExplManager is a singleton
# *****************************************************
qfloclistExplManager = QfLocListExplManager()

__all__ = ["qfloclistExplManager"]
