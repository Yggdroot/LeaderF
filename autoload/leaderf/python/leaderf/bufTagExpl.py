#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import sys
import os.path
import tempfile
import itertools
import multiprocessing
from .utils import *
from .explorer import *
from .manager import *
from .asyncExecutor import AsyncExecutor


#*****************************************************
# BufTagExplorer
#*****************************************************
class BufTagExplorer(Explorer):
    def __init__(self):
        self._ctags = lfEval("g:Lf_Ctags")
        self._supports_preview = int(lfEval("g:Lf_PreviewCode"))
        self._tag_list = {}        # a dict with (key, value) = (buffer number, taglist)
        self._buf_changedtick = {} # a dict with (key, value) = (buffer number, changedtick)
        self._executor = []

    def getContent(self, *args, **kwargs):
        if "--all" in kwargs.get("arguments", {}): # all buffers
            cur_buffer = vim.current.buffer
            for b in vim.buffers:
                if b.options["buflisted"]:
                    if lfEval("bufloaded(%d)" % b.number) == '0':
                        vim.current.buffer = b
            if vim.current.buffer != cur_buffer:
                vim.current.buffer = cur_buffer

            for b in vim.buffers:
                if b.options["buflisted"] and b.name:
                    changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % b.number))
                    if changedtick != self._buf_changedtick.get(b.number, -1):
                        break
            else:
                return itertools.chain.from_iterable(self._tag_list.values())

            return itertools.chain.from_iterable(self._getTagList())
        else:
            result = self._getTagResult(vim.current.buffer)
            if not isinstance(result, list):
                result = self._formatResult(*result)
            tag_list = []
            for i, line in enumerate(result):
                if self._supports_preview and i & 1:
                    tag_list.append(line)
                else:
                    first, second = line.rsplit(":", 1)
                    tag_list.append("{}\t  :{}".format(first.rsplit("\t", 1)[0], second))
            return tag_list

    def _getTagList(self):
        buffers = [b for b in vim.buffers]
        n = multiprocessing.cpu_count()
        for i in range(0, len(vim.buffers), n):
            tag_list = []
            exe_result = []
            for b in buffers[i:i+n]:
                if b.options["buflisted"] and b.name:
                    result = self._getTagResult(b)
                    if isinstance(result, list):
                        tag_list.extend(result)
                    else:
                        exe_result.append(result)
            if not exe_result:
                yield tag_list
            else:
                exe_taglist = (self._formatResult(*r) for r in exe_result)
                yield itertools.chain(tag_list, itertools.chain.from_iterable(exe_taglist))

    def _getTagResult(self, buffer):
        if not buffer.name or lfEval("bufloaded(%d)" % buffer.number) == '0':
            return []
        changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % buffer.number))
        # there is no change since last call
        if changedtick == self._buf_changedtick.get(buffer.number, -1):
            if buffer.number in self._tag_list:
                return self._tag_list[buffer.number]
            else:
                return []
        else:
            self._buf_changedtick[buffer.number] = changedtick

        if lfEval("getbufvar(%d, '&filetype')" % buffer.number) == "cpp":
            extra_options = "--language-force=C++ --c++-kinds=+p"
        elif lfEval("getbufvar(%d, '&filetype')" % buffer.number) == "c":
            extra_options = "--c-kinds=+p"
        elif lfEval("getbufvar(%d, '&filetype')" % buffer.number) == "python":
            extra_options = "--language-force=Python"
        else:
            extra_options = ""

        executor = AsyncExecutor()
        self._executor.append(executor)
        if buffer.options["modified"] == True:
            if sys.version_info >= (3, 0):
                tmp_file = partial(tempfile.NamedTemporaryFile, encoding=lfEval("&encoding"))
            else:
                tmp_file = tempfile.NamedTemporaryFile

            with tmp_file(mode='w+', suffix='_'+os.path.basename(buffer.name), delete=False) as f:
                for line in buffer[:]:
                    f.write(line + '\n')
                file_name = f.name
            # {tagname}<Tab>{tagfile}<Tab>{tagaddress}[;"<Tab>{tagfield}..]
            # {tagname}<Tab>{tagfile}<Tab>{tagaddress};"<Tab>{kind}<Tab>{scope}
            cmd = '{} -n -u --fields=Ks {} -f- "{}"'.format(self._ctags, extra_options, lfDecode(file_name))
            result = executor.execute(cmd, cleanup=partial(os.remove, file_name))
        else:
            cmd = '{} -n -u --fields=Ks {} -f- "{}"'.format(self._ctags, extra_options, lfDecode(buffer.name))
            result = executor.execute(cmd)

        return (buffer, result)

    def _formatResult(self, buffer, result):
        if not buffer.name or lfEval("bufloaded(%d)" % buffer.number) == '0':
            return []

        # a list of [tag, file, line, kind, scope]
        output = [line.split('\t') for line in result]
        if not output:
            return []

        if len(output[0]) < 4:
            lfCmd("echoerr '%s'" % escQuote(str(output[0])))
            return []

        tag_total_len = 0
        max_kind_len = 0
        max_tag_len = 0
        for _, item  in enumerate(output):
            tag_len = len(item[0])
            tag_total_len += tag_len
            if tag_len > max_tag_len:
                max_tag_len = tag_len
            kind_len = len(item[3])
            if kind_len > max_kind_len:
                max_kind_len = kind_len
        ave_taglen = tag_total_len // len(output)
        tag_len = min(max_tag_len, ave_taglen * 2)

        tab_len = buffer.options["shiftwidth"]
        if tab_len == 0:
            tab_len = 4
        std_tag_kind_len = tag_len // tab_len * tab_len + tab_len + max_kind_len

        tag_list = []
        for _, item  in enumerate(output):
            scope = item[4] if len(item) > 4 else "Global"
            tag_kind = "{:{taglen}s}\t{}".format(item[0],   # tag
                                                 item[3],   # kind
                                                 taglen=tag_len
                                                 )
            tag_kind_len = int(lfEval("strdisplaywidth('%s')" % escQuote(tag_kind)))
            num = std_tag_kind_len - tag_kind_len
            space_num = num if num > 0 else 0
            bufname = buffer.name if vim.options["autochdir"] else lfRelpath(buffer.name)
            line = "{}{}\t{}\t{:2s}{}:{}\t{}".format(tag_kind,
                                                     ' ' * space_num,
                                                     scope,          # scope
                                                     ' ',
                                                     bufname,        # file
                                                     item[2][:-2],   # line
                                                     buffer.number
                                                     )
            tag_list.append(line)
            if self._supports_preview:
                # code = "{:{taglen}s}\t{}".format(' ' * len(item[0]),
                #                                  buffer[int(item[2][:-2]) - 1].lstrip(),
                #                                  taglen=tag_len
                #                                  )
                code = "\t\t{}".format(buffer[int(item[2][:-2]) - 1].lstrip())
                tag_list.append(code)

        self._tag_list[buffer.number] = tag_list

        return tag_list

    def getStlCategory(self):
        return 'BufTag'

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))

    def removeCache(self, buf_number):
        if buf_number in self._tag_list:
            del self._tag_list[buf_number]

        if buf_number in self._buf_changedtick:
            del self._buf_changedtick[buf_number]

    def cleanup(self):
        for exe in self._executor:
            exe.killProcess()
        self._executor = []


#*****************************************************
# BufTagExplManager
#*****************************************************
class BufTagExplManager(Manager):
    def __init__(self):
        super(BufTagExplManager, self).__init__()
        self._supports_preview = int(lfEval("g:Lf_PreviewCode"))

    def _getExplClass(self):
        return BufTagExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#BufTag#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        if line[0].isspace(): # if g:Lf_PreviewCode == 1
            buffer = args[1]
            line_num = args[2]
            if self._getInstance().isReverseOrder():
                line = buffer[line_num]
            else:
                line = buffer[line_num - 2]
        # {tag} {kind} {scope} {file}:{line} {buf_number}
        items = re.split(" *\t *", line)
        tagname = items[0]
        line_num = items[3].rsplit(":", 1)[1]
        buf_number = items[4]
        if kwargs.get("mode", '') == 't':
            buf_name = lfEval("bufname(%s)" % buf_number)
            lfDrop('tab', buf_name, line_num)
        else:
            lfCmd("hide buffer +%s %s" % (line_num, buf_number))
        if "preview" not in kwargs:
            lfCmd("norm! ^")
            lfCmd(r"call search('\V%s', 'Wc', line('.'))" % escQuote(tagname))
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
            mode: 0, return the whole line
                  1, return the tagname
                  2, return the remaining part
        """
        if mode == 0:
            return line
        elif mode == 1:
            return re.split(" *\t *", line, 1)[0]
        else:
            return re.split(" *\t *", line, 1)[1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start position of the whole line
                  1, return the start position of tagname
                  2, return the start position remaining part
        """
        if mode == 0:
            return 0
        elif mode == 1:
            return 0
        else:
            return len(line) - len(re.split(" *\t *", line, 1)[1])

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" p : preview the result')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(BufTagExplManager, self)._afterEnter()
        lfCmd("augroup Lf_BufTag")
        lfCmd("autocmd!")
        lfCmd("autocmd BufWipeout * call leaderf#BufTag#removeCache(expand('<abuf>'))")
        lfCmd("autocmd VimLeavePre * call leaderf#BufTag#cleanup()")
        lfCmd("augroup END")
        if self._getInstance().getWinPos() == 'popup':
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_buftagKind'', ''^[^\t]*\t\zs\S\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_buftagScopeType'', ''[^\t]*\t\S\+\s*\zs\w\+:'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_buftagScope'', ''^[^\t]*\t\S\+\s*\(\w\+:\)\=\zs\S\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_buftagDirname'', ''[^\t]*\t\S\+\s*\S\+\s*\zs[^\t]\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_buftagLineNum'', ''\d\+\t\ze\d\+$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_buftagCode'', ''^\s\+.*'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval(r'''matchadd('Lf_hl_buftagKind', '^[^\t]*\t\zs\S\+')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_buftagScopeType', '[^\t]*\t\S\+\s*\zs\w\+:')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_buftagScope', '^[^\t]*\t\S\+\s*\(\w\+:\)\=\zs\S\+')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_buftagDirname', '[^\t]*\t\S\+\s*\S\+\s*\zs[^\t]\+')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_buftagLineNum', '\d\+\t\ze\d\+$')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_buftagCode', '^\s\+.*')'''))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(BufTagExplManager, self)._beforeExit()
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()

    def _getUnit(self):
        """
        indicates how many lines are considered as a unit
        """
        if self._supports_preview:
            return 2
        else:
            return 1

    def _supportsRefine(self):
        return True

    def _fuzzyFilter(self, is_full_path, get_weight, iterable):
        """
        return a list, each item is a pair (weight, (line1, line2))
        """
        if self._supports_preview:
            if len(iterable) < 2:
                return []
            getDigest = partial(self._getDigest, mode=0 if is_full_path else 1)
            pairs = ((get_weight(getDigest(line)), (line, iterable[2*i+1]))
                       for i, line in enumerate(iterable[::2]))
            MIN_WEIGHT = fuzzyMatchC.MIN_WEIGHT if is_fuzzyMatch_C else FuzzyMatch.MIN_WEIGHT
            return (t for t in pairs if t[0] > MIN_WEIGHT)
        else:
            return super(BufTagExplManager, self)._fuzzyFilter(is_full_path,
                                                               get_weight,
                                                               iterable)

    def _refineFilter(self, first_get_weight, get_weight, iterable):
        if self._supports_preview:
            if len(iterable) < 2:
                return []
            getDigest = self._getDigest
            tuples = ((first_get_weight(getDigest(line, 1)), get_weight(getDigest(line, 2)),
                       line, iterable[2*i+1]) for i, line in enumerate(iterable[::2]))
            MIN_WEIGHT = fuzzyMatchC.MIN_WEIGHT if is_fuzzyMatch_C else FuzzyMatch.MIN_WEIGHT
            return ((i[0] + i[1], (i[2], i[3])) for i in tuples if i[0] > MIN_WEIGHT and i[1] > MIN_WEIGHT)
        else:
            return super(BufTagExplManager, self)._refineFilter(first_get_weight,
                                                                get_weight,
                                                                iterable)

    def _regexFilter(self, iterable):
        if self._supports_preview:
            try:
                if ('-2' == lfEval("g:LfNoErrMsgMatch('', '%s')" % escQuote(self._cli.pattern))):
                    return iter([])
                else:
                    result = []
                    for i, line in enumerate(iterable[::2]):
                        if ('-1' != lfEval("g:LfNoErrMsgMatch('%s', '%s')" %
                            (escQuote(self._getDigest(line, 1).strip()),
                                escQuote(self._cli.pattern)))):
                            result.append(line)
                            result.append(iterable[2*i+1])
                    return result
            except vim.error:
                return iter([])
        else:
            return super(BufTagExplManager, self)._regexFilter(iterable)

    def _getList(self, pairs):
        """
        return a list constructed from `pairs`
        Args:
            pairs: a list of tuple(weight, (line1, line2))
        """
        if self._supports_preview:
            result = []
            for _, p in enumerate(pairs):
                result.extend(p[1])
            return result
        else:
            return super(BufTagExplManager, self)._getList(pairs)

    def _toUp(self):
        if self._supports_preview:
            if self._getInstance().isReverseOrder() and self._getInstance().getCurrentPos()[0] <= 3:
                self._setResultContent()
                if self._cli.pattern and len(self._highlight_pos) < len(self._getInstance().buffer) // 2 \
                        and len(self._highlight_pos) < int(lfEval("g:Lf_NumberOfHighlight")):
                    self._highlight_method()

            if self._getInstance().isReverseOrder():
                lfCmd("norm! 3kj")
                self._getInstance().setLineNumber()
            else:
                if self._getInstance().getWinPos() == 'popup':
                    lfCmd("call win_execute(%d, 'norm! 2k')" % (self._getInstance().getPopupWinId()))
                else:
                    lfCmd("norm! 2k")
        else:
            super(BufTagExplManager, self)._toUp()

        lfCmd("setlocal cursorline!")   # these two help to redraw the statusline,
        lfCmd("setlocal cursorline!")   # also fix a weird bug of vim

    def _toDown(self):
        if self._supports_preview:
            if self._getInstance().isReverseOrder():
                lfCmd("norm! 2j")
                self._getInstance().setLineNumber()
            else:
                if self._getInstance().getWinPos() == 'popup':
                    lfCmd("call win_execute(%d, 'norm! 3jk')" % (self._getInstance().getPopupWinId()))
                else:
                    lfCmd("norm! 3jk")
        else:
            super(BufTagExplManager, self)._toDown()

        lfCmd("setlocal cursorline!")   # these two help to redraw the statusline,
        lfCmd("setlocal cursorline!")   # also fix a weird bug of vim

    def removeCache(self, buf_number):
        self._getExplorer().removeCache(buf_number)

    def _bangEnter(self):
        super(BufTagExplManager, self)._bangEnter()
        if "--all" in self._arguments and not self._is_content_list:
            if lfEval("exists('*timer_start')") == '0':
                lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
                return
            self._callback(bang=True)
            if self._read_finished < 2:
                self._timer_id = lfEval("timer_start(1, 'leaderf#BufTag#TimerCallback', {'repeat': -1})")
        else:
            self._relocateCursor()

    def _bangReadFinished(self):
        super(BufTagExplManager, self)._bangReadFinished()
        self._relocateCursor()

    def _relocateCursor(self):
        remember_last_status = "--recall" in self._arguments \
                or lfEval("g:Lf_RememberLastSearch") == '1' and self._cli.pattern
        if remember_last_status:
            return

        inst = self._getInstance()
        if inst.empty():
            return
        orig_buf_num = inst.getOriginalPos()[2].number
        orig_line = inst.getOriginalCursor()[0]
        tags = []
        for index, line in enumerate(inst.buffer, 1):
            if self._supports_preview:
                if self._getInstance().isReverseOrder():
                    if index & 1 == 1:
                        continue
                elif index & 1 == 0:
                    continue
            items = re.split(" *\t *", line)
            line_num = int(items[3].rsplit(":", 1)[1])
            buf_number = int(items[4])
            if orig_buf_num == buf_number:
                tags.append((index, buf_number, line_num))

        if self._getInstance().isReverseOrder():
            tags = tags[::-1]

        last = len(tags) - 1
        while last >= 0:
            if tags[last][2] <= orig_line:
                break
            last -= 1
        if last >= 0:
            index = tags[last][0]
            if self._getInstance().getWinPos() == 'popup':
                lfCmd("call leaderf#ResetPopupOptions(%d, 'filter', '%s')"
                        % (self._getInstance().getPopupWinId(), 'leaderf#PopupFilter'))
                lfCmd("""call win_execute(%d, "exec 'norm! %dG'")""" % (self._getInstance().getPopupWinId(), int(index)))

                if lfEval("exists('*leaderf#%s#NormalModeFilter')" % self._getExplorer().getStlCategory()) == '1':
                    lfCmd("call leaderf#ResetPopupOptions(%d, 'filter', '%s')" % (self._getInstance().getPopupWinId(),
                            'leaderf#%s#NormalModeFilter' % self._getExplorer().getStlCategory()))
                else:
                    lfCmd("call leaderf#ResetPopupOptions(%d, 'filter', function('leaderf#NormalModeFilter', [%d]))"
                            % (self._getInstance().getPopupWinId(), id(self)))
            else:
                lfCmd(str(index))
                lfCmd("norm! zz")

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0 or args[0] == '':
            return

        line = args[0]
        if line[0].isspace(): # if g:Lf_PreviewCode == 1
            buffer = args[1]
            line_num = args[2]
            if self._getInstance().isReverseOrder():
                line = buffer[line_num]
            else:
                line = buffer[line_num - 2]
        # {tag} {kind} {scope} {file}:{line} {buf_number}
        items = re.split(" *\t *", line)
        tagname = items[0]
        line_num = items[3].rsplit(":", 1)[1]
        buf_number = int(items[4])

        self._createPopupPreview(tagname, buf_number, line_num)


#*****************************************************
# bufTagExplManager is a singleton
#*****************************************************
bufTagExplManager = BufTagExplManager()

__all__ = ['bufTagExplManager']
