#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import os
import os.path
import time
import operator
from fnmatch import fnmatch
from functools import partial
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
# MruExplorer
#*****************************************************
class MruExplorer(Explorer):
    def __init__(self):
        self._prefix_length = 0
        self._max_bufname_len = 0
        self._root_markers = lfEval("g:Lf_RootMarkers")

    def getFrecency(self, current_time, item):
        """
        item is [time, rank, filename]
        """
        rank = int(item[1])
        delta_time = int(current_time) - int(item[0])
        frecency = 0
        if delta_time < 3600:
            frecency = rank * 4
        elif delta_time < 86400:
            frecency = rank * 2
        elif delta_time < 604800:
            frecency = rank * 0.5
        else:
            frecency = rank * 0.25

        return frecency

    def getContent(self, *args, **kwargs):
        mru.saveToCache(lfEval("readfile(lfMru#CacheFileName())"))
        lfCmd("call writefile([], lfMru#CacheFileName())")

        with lfOpen(mru.getCacheFileName(), 'r+', errors='ignore', encoding='utf8') as f:
            data_list = []
            for line in f.readlines():
                data = line.split(None, 2)
                if os.path.exists(lfDecode(data[2].rstrip())):
                    data[0] = int(data[0])
                    data_list.append(data)

            if len(data_list) == 0:
                # import old data
                try:
                    with lfOpen(mru.getOldCacheFileName(), 'r+', errors='ignore', encoding='utf8') as old_f:
                        current_time = time.time()
                        data_list = [[int(current_time), 1, filename] for filename in old_f.readlines()
                                     if os.path.exists(lfDecode(filename.rstrip()))
                                     ]
                except FileNotFoundError:
                    pass

            arguments_dict = kwargs.get("arguments", {})
            if "--frecency" in arguments_dict or lfEval("get(g:, 'Lf_MruEnableFrecency', 0)") == '1':
                data_list.sort(key=partial(self.getFrecency, time.time()), reverse=True)
            else:
                data_list.sort(key=operator.itemgetter(0), reverse=True)

            max_files = int(lfEval("g:Lf_MruMaxFiles"))
            if len(data_list) > max_files:
                del data_list[max_files:]

            f.seek(0)
            f.truncate(0)
            f.writelines(["{} {} {}".format(data[0], data[1], data[2]) for data in data_list])

        lines = [data[2].rstrip() for data in data_list]

        if "--cwd" in arguments_dict:
            lines = [name for name in lines if lfDecode(name).startswith(lfGetCwd())]
        elif "--project" in arguments_dict:
            project_root = lfGetCwd()
            ancestor = nearestAncestor(self._root_markers, project_root)
            if ancestor != "":
                project_root = ancestor
            lines = [name for name in lines if lfDecode(name).startswith(os.path.join(project_root, ''))]

        wildignore = lfEval("g:Lf_MruWildIgnore")
        lines = [name for name in lines if True not in (fnmatch(name, j) for j in wildignore.get('file', []))
                    and True not in (fnmatch(name, "*/" + j + "/*") for j in wildignore.get('dir', []))]

        if len(lines) == 0:
            return lines

        if kwargs["cb_name"] == lines[0]:
            lines = lines[1:] + lines[0:1]

        self._prefix_length = 0
        self.show_icon = False
        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
            self.show_icon = True
            self._prefix_length = webDevIconsStrLen()

        show_absolute = "--absolute-path" in arguments_dict
        if "--no-split-path" in arguments_dict:
            if lfEval("g:Lf_ShowRelativePath") == '1' and show_absolute == False:
                lines = [lfRelpath(line) for line in lines]
            if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1":
                lines = [
                    webDevIconsGetFileTypeSymbol(getBasename(line)) + line
                    for line in lines
                ]
            return lines

        self._max_bufname_len = max(int(lfEval("strdisplaywidth('%s')"
                                        % escQuote(getBasename(line))))
                                    for line in lines)
        for i, line in enumerate(lines):
            if lfEval("g:Lf_ShowRelativePath") == '1' and show_absolute == False:
                line = lfRelpath(line)
            basename = getBasename(line)
            dirname = getDirname(line)
            space_num = self._max_bufname_len \
                        - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))

            if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
                icon = webDevIconsGetFileTypeSymbol(basename)
            else:
                icon = ""

            lines[i] = '{}{}{} "{}"'.format(icon, getBasename(line), ' ' * space_num,
                                          dirname if dirname else '.' + os.sep)
        return lines

    def getStlCategory(self):
        return 'Mru'

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))

    def supportsMulti(self):
        return True

    def supportsNameOnly(self):
        return True

    def delFromCache(self, name):
        with lfOpen(mru.getCacheFileName(), 'r+', errors='ignore', encoding='utf8') as f:
            lines = f.readlines()
            lines.remove(lfEncode(os.path.abspath(lfDecode(name))) + '\n')
            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

    def getPrefixLength(self):
        return self._prefix_length

    def getMaxBufnameLen(self):
        return self._max_bufname_len


#*****************************************************
# MruExplManager
#*****************************************************
class MruExplManager(Manager):
    def __init__(self):
        super(MruExplManager, self).__init__()

    def _getExplClass(self):
        return MruExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Mru#Maps()")

    def _argaddFiles(self, files):
        # It will raise E480 without 'silent!'
        lfCmd("silent! argdelete *")
        for file in files:
            dirname = self._getDigest(file, 2)
            basename = self._getDigest(file, 1)
            lfCmd("argadd %s" % escSpecial(dirname + basename))

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        dirname = self._getDigest(line, 2)
        basename = self._getDigest(line, 1)
        try:
            file = dirname + basename
            if not os.path.isabs(file):
                file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
                file = os.path.normpath(lfEncode(file))

            if kwargs.get("mode", '') == 't':
                if (lfEval("get(g:, 'Lf_DiscardEmptyBuffer', 1)") == '1' and vim.current.buffer.name == ''
                        and vim.current.buffer.number == 1
                        and len(vim.current.tabpage.windows) == 1 and len(vim.current.buffer) == 1
                        and vim.current.buffer[0] == '' and not vim.current.buffer.options["modified"]
                        and not (lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1'
                            and lfEval("bufloaded('%s')" % escQuote(file)) == '1'
                            and len([w for tp in vim.tabpages for w in tp.windows if w.buffer.name == file]) > 0)):
                    lfCmd("setlocal bufhidden=wipe")
                    lfCmd("hide edit %s" % escSpecial(file))
                elif lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    lfDrop('tab', file)
                else:
                    lfCmd("tabe %s" % escSpecial(file))
            else:
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    if (kwargs.get("mode", '') == '' and lfEval("get(g:, 'Lf_DiscardEmptyBuffer', 1)") == '1'
                            and vim.current.buffer.name == ''
                            and vim.current.buffer.number == 1
                            and len(vim.current.buffer) == 1 and vim.current.buffer[0] == ''
                            and not vim.current.buffer.options["modified"]
                            and len([w for w in vim.windows if w.buffer.name == file]) == 0):
                        lfCmd("setlocal bufhidden=wipe")

                    lfDrop('', file)
                else:
                    if (kwargs.get("mode", '') == '' and lfEval("get(g:, 'Lf_DiscardEmptyBuffer', 1)") == '1'
                            and vim.current.buffer.name == ''
                            and vim.current.buffer.number == 1
                            and len(vim.current.buffer) == 1 and vim.current.buffer[0] == ''
                            and not vim.current.buffer.options["modified"]):
                        lfCmd("setlocal bufhidden=wipe")

                    lfCmd("hide edit %s" % escSpecial(file))
        except vim.error as e: # E37
            if 'E325' not in str(e).split(':'):
                lfPrintTraceback()

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
        if "--no-split-path" in self._arguments:
            line = line[prefix_len:]
            if mode == 0:
                return line
            elif mode == 1:
                return getBasename(line)
            else:
                return getDirname(line)
        else:
            if mode == 0:
                return line[prefix_len:]
            elif mode == 1:
                start_pos = line.find(' "') # what if there is " in file name?
                return line[prefix_len:start_pos].rstrip()
            else:
                start_pos = line.find(' "') # what if there is " in file name?
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
        if "--no-split-path" in self._arguments:
            if mode == 0 or mode == 2:
                return webDevIconsBytesLen()
            else:
                return lfBytesLen(getDirname(line))
        else:
            if self._getExplorer().show_icon:
                prefix_len = self._getExplorer().getPrefixLength() - webDevIconsStrLen() + webDevIconsBytesLen()
            else:
                prefix_len = self._getExplorer().getPrefixLength()

            if mode == 0:
                return prefix_len
            elif mode == 1:
                return prefix_len
            else:
                start_pos = line.find(' "') # what if there is " in file name?
                return lfBytesLen(line[:start_pos+2])

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" d : remove from mru list')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" s : select multiple files')
        help.append('" a : select all files')
        help.append('" c : clear all selections')
        help.append('" p : preview the file')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(MruExplManager, self)._afterEnter()

        if "--no-split-path" not in self._arguments:
            if self._getInstance().getWinPos() == 'popup':
                lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_bufDirname'', '' \zs".*"$'')')"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
            else:
                id = int(lfEval(r'''matchadd('Lf_hl_bufDirname', ' \zs".*"$')'''))
                self._match_ids.append(id)

        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
            winid = self._getInstance().getPopupWinId() if self._getInstance().getWinPos() == 'popup' else None
            icon_pattern = r'^__icon__'
            self._match_ids.extend(matchaddDevIconsExtension(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsExact(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsDefault(icon_pattern, winid))

    def _beforeExit(self):
        super(MruExplManager, self)._beforeExit()

    def deleteMru(self):
        instance = self._getInstance()
        if self._inHelpLines():
            return
        if instance.getWinPos() == 'popup':
            lfCmd("call win_execute(%d, 'setlocal modifiable')" % instance.getPopupWinId())
        else:
            lfCmd("setlocal modifiable")
        line = instance._buffer_object[instance.window.cursor[0] - 1]

        if line == '':
            return

        dirname = self._getDigest(line, 2)
        basename = self._getDigest(line, 1)
        self._explorer.delFromCache(dirname + basename)
        if len(self._content) > 0:
            self._content.remove(line)
            self._getInstance().setStlTotal(len(self._content)//self._getUnit())
            self._getInstance().setStlResultsCount(len(self._content)//self._getUnit())
        # `del vim.current.line` does not work in neovim
        # https://github.com/neovim/neovim/issues/9361
        del instance._buffer_object[instance.window.cursor[0] - 1]
        if instance.getWinPos() == 'popup':
            instance.refreshPopupStatusline()
            lfCmd("call win_execute(%d, 'setlocal nomodifiable')" % instance.getPopupWinId())
        else:
            lfCmd("setlocal nomodifiable")

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0 or args[0] == '':
            return

        line = args[0]
        dirname = self._getDigest(line, 2)
        basename = self._getDigest(line, 1)

        file = dirname + basename
        if not os.path.isabs(file):
            file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
            file = os.path.normpath(lfEncode(file))

        if lfEval("bufloaded('%s')" % escQuote(file)) == '1':
            source = int(lfEval("bufadd('%s')" % escQuote(file)))
        else:
            source = file
        self._createPopupPreview(file, source, 0)


#*****************************************************
# mruExplManager is a singleton
#*****************************************************
mruExplManager = MruExplManager()

__all__ = ['mruExplManager']
