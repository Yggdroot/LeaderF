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
# TagExplorer
#*****************************************************
class TagExplorer(Explorer):
    def __init__(self):
        self._tag_list = []
        self._file_tags = {}    # a dict with (key, value) = (tag file name, [mtime,taglist])

    def getContent(self, *args, **kwargs):
        return self.getFreshContent(*args, **kwargs)

    def getFreshContent(self, *args, **kwargs):
        has_new_tagfile = False
        has_changed_tagfile = False
        filenames = [name for name in self._file_tags]
        for tagfile in vim.eval("tagfiles()"):
            tagfile = os.path.abspath(tagfile)
            mtime = os.path.getmtime(tagfile)
            if tagfile not in self._file_tags:
                has_new_tagfile = True
                with lfOpen(tagfile, 'r', encoding='utf-8', errors='ignore') as f:
                    self._file_tags[tagfile] = [mtime, f.readlines()[6:]]
            else:
                filenames.remove(tagfile)
                if mtime != self._file_tags[tagfile][0]:
                    has_changed_tagfile = True
                    with lfOpen(tagfile, 'r', encoding='utf-8', errors='ignore') as f:
                        self._file_tags[tagfile] = [mtime, f.readlines()[6:]]

        for name in filenames:
            del self._file_tags[name]

        if has_new_tagfile == False and has_changed_tagfile == False:
            return self._tag_list
        else:
            self._tag_list = list(itertools.chain.from_iterable((i[1] for i in self._file_tags.values())))
            return self._tag_list

    def getStlCategory(self):
        return 'Tag'

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))


#*****************************************************
# TagExplManager
#*****************************************************
class TagExplManager(Manager):
    def __init__(self):
        super(TagExplManager, self).__init__()

    def _getExplClass(self):
        return TagExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Tag#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        # {tagname}<Tab>{tagfile}<Tab>{tagaddress}[;"<Tab>{tagfield}..]
        tagname, tagfile, right = line.split('\t', 2)
        res = right.split(';"\t', 1)
        tagaddress = res[0]
        try:
            if kwargs.get("mode", '') == 't':
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(tagfile)) == '1':
                    lfDrop('tab', tagfile)
                else:
                    lfCmd("tabe %s" % escSpecial(tagfile))
            else:
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(tagfile)) == '1':
                    lfDrop('', tagfile)
                else:
                    lfCmd("hide edit %s" % escSpecial(tagfile))
        except vim.error as e: # E37
            if 'E325' not in str(e).split(':'):
                lfPrintTraceback()

        if tagaddress[0] not in '/?':
            lfCmd(tagaddress)
        else:
            self._gotoFirstLine()

            # In case there are mutiple matches.
            if len(res) > 1:
                result = re.search('(?<=\t)line:\d+', res[1])
                if result:
                    line_nr = result.group(0).split(':')[1]
                    lfCmd(line_nr)
                else: # for c, c++
                    keyword = "(class|enum|struct|union)"
                    result = re.search('(?<=\t)%s:\S+' % keyword, res[1])
                    if result:
                        tagfield = result.group(0).split(":")
                        name = tagfield[0]
                        value = tagfield[-1]
                        lfCmd("call search('\m%s\_s\+%s\_[^;{]*{', 'w')" % (name, value))

            pattern = "\M" + tagaddress[1:-1]
            lfCmd("call search('%s', 'w')" % escQuote(pattern))

        if lfEval("search('\V%s', 'wc')" % escQuote(tagname)) == '0':
            lfCmd("norm! ^")
        lfCmd("norm! zv")
        lfCmd("norm! zz")

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
        return line[:line.find('\t')]

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
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F5> : refresh the cache')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(TagExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_tagFile'', ''^.\{-}\t\zs.\{-}\ze\t'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_tagType'', '';"\t\zs[cdefFgmpstuv]\ze\(\t\|$\)'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            keyword = ["namespace", "class", "enum", "file", "function", "kind", "struct", "union"]
            for i in keyword:
                lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_tagKeyword'', ''\(;"\t.\{-}\)\@<=%s:'')')"""
                    % (self._getInstance().getPopupWinId(), i))
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
        else:
            id = int(lfEval('''matchadd('Lf_hl_tagFile', '^.\{-}\t\zs.\{-}\ze\t')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_tagType', ';"\t\zs[cdefFgmpstuv]\ze\(\t\|$\)')'''))
            self._match_ids.append(id)
            keyword = ["namespace", "class", "enum", "file", "function", "kind", "struct", "union"]
            for i in keyword:
                id = int(lfEval('''matchadd('Lf_hl_tagKeyword', '\(;"\t.\{-}\)\@<=%s:')''' % i))
                self._match_ids.append(id)

    def _beforeExit(self):
        super(TagExplManager, self)._beforeExit()
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()

    def _bangEnter(self):
        super(TagExplManager, self)._bangEnter()

        instance = self._getInstance()
        if instance.isLastReverseOrder():
            instance.window.cursor = (min(instance.cursorRow, len(instance.buffer)), 0)
        else:
            instance.window.cursor = (instance.cursorRow, 0)

        if instance.getWinPos() == 'popup':
            lfCmd("call win_execute(%d, 'setlocal cursorline')" % instance.getPopupWinId())
        elif instance.getWinPos() == 'floatwin':
            lfCmd("call nvim_win_set_option(%d, 'cursorline', v:true)" % instance.getPopupWinId())
        else:
            instance.window.options["cursorline"] = True

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        # {tagname}<Tab>{tagfile}<Tab>{tagaddress}[;"<Tab>{tagfield}..]
        tagname, tagfile, right = line.split('\t', 2)
        res = right.split(';"\t', 1)
        tagaddress = res[0]
        if tagaddress[0] not in '/?':
            self._createPopupPreview("", tagfile, tagaddress)
        else:
            # In case there are mutiple matches.
            if len(res) > 1:
                result = re.search('(?<=\t)line:\d+', res[1])
                if result:
                    line_nr = result.group(0).split(':')[1]
                    self._createPopupPreview("", tagfile, line_nr)
                else: # for c, c++
                    keyword = "(class|enum|struct|union)"
                    result = re.search('(?<=\t)%s:\S+' % keyword, res[1])
                    jump_cmd = 'exec "norm! gg"'
                    if result:
                        tagfield = result.group(0).split(":")
                        name = tagfield[0]
                        value = tagfield[-1]
                        jump_cmd += " | call search('\m%s\_s\+%s\_[^;{]*{', 'w')" % (name, value)

                    pattern = "\M" + tagaddress[1:-1]
                    jump_cmd += " | call search('%s', 'w')" % escQuote(pattern)
                    self._createPopupPreview("", tagfile, 0, jump_cmd)


#*****************************************************
# tagExplManager is a singleton
#*****************************************************
tagExplManager = TagExplManager()

__all__ = ['tagExplManager']
